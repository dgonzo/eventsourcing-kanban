from eventsourcing.application.base import ApplicationWithPersistencePolicies
from eventsourcing.infrastructure.snapshotting import EventSourcedSnapshotStrategy
from eventsourcing.infrastructure.sqlalchemy.activerecords import SQLAlchemyActiveRecordStrategy, \
    IntegerSequencedItemRecord
from passlib.handlers.pbkdf2 import pbkdf2_sha512

from infrastructure import datastore
from infrastructure.datastore import get_database
from infrastructure.kanban_repositories import UserRepository
from kanban.domain.model.user import User
from utility.parse import valid_unencrypted_password, whitelist_domain

PASSWORD_VALIDATION_MESSAGE = """Invalid password. Password must be at least 8 characters and contain:
* Capital Letter
* Number
* Non-alphanumeric character: !@#$%^&*<>?"""
SANITIZED_PASSWORD = "********"


class KanbanApplication(ApplicationWithPersistencePolicies):
    """
    An event source application
    """

    def __init__(self, **kwargs):
        super(KanbanApplication, self).__init__(**kwargs)
        self.snapshot_strategy = None
        if self.snapshot_event_store:
            self.snapshot_strategy = EventSourcedSnapshotStrategy(
                event_store=self.snapshot_event_store
            )
        assert self.entity_event_store is not None
        self.user_repository = UserRepository(
            event_store=self.entity_event_store,
            snapshot_strategy=self.snapshot_strategy,

        )

    @staticmethod
    def _sanitize_user(user):
        if user.password != SANITIZED_PASSWORD:
            user.password = SANITIZED_PASSWORD
            return user
        else:
            return user

    @staticmethod
    def get_encrypted_password(password):
        return pbkdf2_sha512.encrypt(password, rounds=200000, salt_size=16)

    def new_user(self, name, password, email, default_domain) -> User:
        # def new_user(self, name, default_domain='public.example.com') -> User:
        """Creates a new user.
        :param name: Full name of user.
        :param email: Valid email of user.
        :param password: Unencrypted password.
        :param default_domain: Valid domain name.
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


def construct_kanban_application(**kwargs):
    """Application object factory"""
    return KanbanApplication(**kwargs)


_kanban_application = None


def init_kanban_application(**kwargs):
    """
    Constructs single global instance of application.
    """
    global _kanban_application
    if _kanban_application is not None:
        raise AssertionError("init_kanban_application() has already been called.")
    _kanban_application = construct_kanban_application(**kwargs)


def get_kanban_application():
    """
    Returns single global instance of application.
    """
    if _kanban_application is None:
        raise AssertionError("init_kanban_application() must be called first.")
    assert isinstance(_kanban_application, KanbanApplication)
    return _kanban_application


def close_kanban_application():
    """
    Shuts down global instance of application
    """
    global _kanban_application
    if _kanban_application is not None:
        _kanban_application.close()
    _kanban_application = None


def init_kanban_application_w_sqlalchemy(db_host=None):
    datastore.init_database(uri=db_host)
    db = get_database()
    db.setup_connection()
    db.setup_tables()
    init_kanban_application(
        entity_active_record_strategy=SQLAlchemyActiveRecordStrategy(
            active_record_class=IntegerSequencedItemRecord,
            session=db.session
        )
    )
