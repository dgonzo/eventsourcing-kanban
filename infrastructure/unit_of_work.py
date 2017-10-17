from typing import List
from uuid import UUID

from eventsourcing.application.base import ApplicationWithPersistencePolicies
from eventsourcing.domain.model.collection import Collection
from eventsourcing.infrastructure.eventsourcedrepository import EventSourcedRepository
from eventsourcing.infrastructure.repositories.collection_repo import CollectionRepository
from eventsourcing.infrastructure.snapshotting import EventSourcedSnapshotStrategy
from eventsourcing.infrastructure.sqlalchemy.activerecords import SQLAlchemyActiveRecordStrategy, \
    IntegerSequencedItemRecord, SnapshotRecord
from passlib.hash import pbkdf2_sha512

from infrastructure.projections.workflow_platform_domain_policies import DomainSnapshottingPolicy, UserProjectionPolicy, \
    make_user_collection_id
from kanban.domain.model.ref_user import User
from utility.parse import valid_unencrypted_password, whitelist_domain, valid_domain

PASSWORD_VALIDATION_MESSAGE = """Invalid password. Password must be at least 8 characters and contain:
* Capital Letter
* Number
* Non-alphanumeric character: !@#$%^&*<>?"""
SANITIZED_PASSWORD = "********"


class UnitOfWork(ApplicationWithPersistencePolicies):
    def __init__(self, session, **kwargs):
        # Construct infrastructure objects for storing events with SQLAlchemy
        entity_active_record_strategy = SQLAlchemyActiveRecordStrategy(
            active_record_class=IntegerSequencedItemRecord,
            session=session
        )
        snapshot_active_record_strategy = SQLAlchemyActiveRecordStrategy(
            active_record_class=SnapshotRecord,
            session=session
        )
        # Initialize
        super(UnitOfWork, self).__init__(
            entity_active_record_strategy=entity_active_record_strategy,
            snapshot_active_record_strategy=snapshot_active_record_strategy,
            **kwargs
        )
        # Construct repositories
        self.snapshot_strategy = EventSourcedSnapshotStrategy(
            event_store=self.snapshot_event_store
        )
        # -- User
        self.users = EventSourcedRepository(
            event_store=self.entity_event_store,
            mutator=User._mutate,
            snapshot_strategy=self.snapshot_strategy
        )
        self.user_collections = CollectionRepository(
            event_store=self.entity_event_store
        )
        self.user_projection_policy = UserProjectionPolicy(
            user_collections=self.user_collections
        )
        self.user_snapshotting_policy = DomainSnapshottingPolicy(
            repository=self.users
        )

    #
    # Services
    #
    def close(self):
        super(UnitOfWork, self).close()
        self.user_projection_policy.close()
        self.user_snapshotting_policy.close()

    @staticmethod
    def _sanitize_user(user):
        if user.password != SANITIZED_PASSWORD:
            user.password = SANITIZED_PASSWORD
            return user
        else:
            return user

    #
    # users
    #
    @staticmethod
    def get_encrypted_password(password):
        return pbkdf2_sha512.encrypt(password, rounds=200000, salt_size=16)

    def new_user(self, name, password, email, default_domain='public.example.com') -> User:
        """Creates a new user.
        :param name: Full name of user.
        :param email: Valid email of user.
        :param password: Unencrypted password.
        :param default_domain: Optional valid domain name. Defaults to 'public.example.com'.
        :raises AttributeError: If any user attributes are invalid.
        :returns: User object.
        """
        # TODO: Make email unique constraint
        try:
            assert valid_unencrypted_password(password)
        except AssertionError:
            raise AttributeError(PASSWORD_VALIDATION_MESSAGE)
        else:
            whitelisted_domain = whitelist_domain(default_domain)
            password_hash = self.get_encrypted_password(password)
            user = User.create(name, password_hash, email, whitelisted_domain)
            user.save()
            return self._sanitize_user(user)

    def get_user_ids(self, domain_namespace: str = 'public.example.com') -> List[str]:
        """Returns a list of user IDs in domain_namespace.
        :param domain_namespace: A valid domain_namespace.
        :raise AttributeError: If domain_namespace not a valid domain.
        :returns: List of IDs.
        """
        try:
            collection_id = make_user_collection_id(domain_namespace)
            collection = self.user_collections[collection_id]
            assert isinstance(collection, Collection)
            return collection.items
        except KeyError:
            return []

    def get_user(self, user_id: UUID) -> User:
        """Return a user from users collection.
        :param user_id: User ID.
        :raise EntityNotFoundError: If no user found in namespace.
        :returns: User object.
        """
        try:
            user = self.users[user_id]
        except KeyError:
            raise EntityNotFoundError(f"No user found with id: {user_id}.")
        else:
            return self._sanitize_user(user)

    def discard_user(self, user_id) -> None:
        """Discard a user.
        :param user_id: User ID.
        :raises EntityNotFoundError: If user not found in domain namespace.
        :returns: None
        """
        try:
            user = self.users[user_id]
        except KeyError:
            raise EntityNotFoundError(f"No user found with id: {user_id}.")
        else:
            user.discard()
            user.save()

    def modify_user(self, user_id, attribute_name, attribute_value) -> User:
        """Modify existing user.
        :param user_id: User ID.
        :param attribute_name: Name of User attribute to modify.
        :param attribute_value: Modified attribute value.
        :raise AttributeError: If attribute is invalid.
        :returns: Current User object.
        """
        if attribute_name in ["password", "domains"]:
            if attribute_name == "password":
                raise NotImplementedError(
                    "ModifyUser cannot be used to change a user's password. Instead use ChangePassword."
                )
            elif attribute_name == "domains":
                raise NotImplementedError(
                    "ModifyUser cannot be used to change a user's domains. "
                    "Instead use `/Organization/{organization_id}/AddUser`"
                )

        user = self.users[user_id]
        user.change_attribute(attribute_name, attribute_value)
        user.save()
        return self._sanitize_user(user)

    def change_password(self, user_id, new_password) -> None:
        """Modify existing user's password.
        :param user_id: User ID.
        :param new_password: New password value.
        :raise AttributeError: If password is invalid.
        :returns: None
        """
        try:
            assert valid_unencrypted_password(new_password)
        except AssertionError:
            raise AttributeError(PASSWORD_VALIDATION_MESSAGE)

        password_hash = self.get_encrypted_password(new_password)
        user = self.users[user_id]
        user.change_attribute("password", password_hash)
        user.save()
        return None

    def add_domain_to_user(self, user_id, domain):
        try:
            assert valid_domain(domain)
        except AssertionError:
            raise AttributeError(f"{domain!r} is not a valid User domain.")

        user = self.users[user_id]
        user.add_domain(domain)
        user.save()
        return user

    def remove_domain_from_user(self, user_id, domain):
        try:
            assert valid_domain(domain)
        except AssertionError:
            raise AttributeError(f"{domain!r} is not a valid User domain.")

        user = self.users[user_id]
        user.discard_domain(domain)
        user.save()
        return user

