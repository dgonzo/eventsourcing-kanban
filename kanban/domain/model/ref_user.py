from uuid import uuid4, UUID

from eventsourcing.domain.model.aggregate import AggregateRoot
from eventsourcing.domain.model.entity import WithReflexiveMutator
# =============================================================================
# Aggregate root
from eventsourcing.domain.model.events import publish

from utility.parse import valid_email, valid_domain, valid_encrypted_password


class User(WithReflexiveMutator, AggregateRoot):
    """Aggregate root for user.
    A user is a namespace for accessing all workflow platform resources.
    """

    def __init__(self, user_id, name, password, email, default_domain, **kwargs):
        super(User, self).__init__(**kwargs)
        self.user_id = self._validate_user_id(user_id)
        self.name = self._validate_name(name)
        self.password = self._validate_password(password)
        self.email = self._validate_email(email)
        self.default_domain = self._validate_domain(default_domain)
        self.domains = set()

    def __repr__(self):
        return "<{discarded}{name}(pending_events=[n..{n}], {data})>".format(
            discarded="*Discarded* " if self._is_discarded else "",
            name=self.__class__.__name__,
            n=len(self._pending_events),
            data=', '.join(sorted(["{0}={1}".format(k, v) for (k, v) in
                                   {k: v for k, v
                                    in self.__dict__.items()
                                    if k != '_pending_events'}.items()
                                   ])))

    #
    # Domain events.
    #
    class Event(AggregateRoot.Event):
        """Layer supertype
        """

    class Created(Event, AggregateRoot.Created):
        """Published when a user is created."""

        @property
        def user_id(self):
            return self.__dict__['user_id']

        @property
        def name(self):
            return self.__dict__['name']

        @property
        def password(self):
            return self.__dict__['password']

        @property
        def email(self):
            return self.__dict__['email']

        @property
        def default_domain(self):
            return self.__dict__['default_domain']

        def mutate(self, cls):
            entity = cls(**self.__dict__)
            entity.domains.add(self.default_domain)
            entity.increment_version()
            return entity

    class AttributeChanged(AggregateRoot.AttributeChanged):
        """Published when a user attribute changes."""

        @property
        def name(self):
            return self.__dict__['name']

        @property
        def value(self):
            return self.__dict__['value']

        def mutate(self, entity):
            setattr(entity, self.name, self.value)
            entity.increment_version()
            return entity

    class Discarded(Event, AggregateRoot.Discarded):
        """Published when a user is discarded."""

        @property
        def domain_namespace(self):
            return self.__dict__['domain_namespace']

        def mutate(self, entity):
            entity._is_discarded = True
            return None

    class DomainAdded(Event):
        """Published when a domain is added."""

        @property
        def domain(self):
            return self.__dict__['domain']

        def mutate(self, entity):
            entity.domains.add(self.domain)
            entity.increment_version()

    class DomainDiscarded(Event):
        """Published when a domain is removed."""

        @property
        def domain(self):
            return self.__dict__['domain']

        def mutate(self, entity):
            entity.domains.discard(self.domain)
            entity.increment_version()

    #
    # Commands
    #
    @staticmethod
    def create(name, password, email, default_domain, **kwargs):
        """Creates a new user."""
        user_id = uuid4()
        event = User.Created(
            originator_id=uuid4(),
            user_id=user_id,
            name=name,
            password=password,
            email=email,
            default_domain=default_domain,
            **kwargs
        )
        entity = event.mutate(cls=User)
        publish(event)
        return entity

    def change_attribute(self, name, value, **kwargs):
        """Updates user attributes."""
        self._apply_and_publish(
            self._construct_event(
                User.AttributeChanged,
                name=name,
                value=value,
                **kwargs
            )
        )

    def discard(self):
        self._apply_and_publish(
            self._construct_event(
                User.Discarded,
                domain_namespace=self.default_domain
            )
        )

    #
    # Domain Commands
    #
    def add_domain(self, domain: str) -> None:
        """Add a new domain to a user's list of domains.
        :param domain: Valid domain string.
        :raises AttributeError: If domain is not a valid domain.
        :returns: None
        """
        self._apply_and_publish(
            self._construct_event(
                User.DomainAdded,
                domain=self._validate_domain(domain)
            )
        )

    def discard_domain(self, domain: str) -> None:
        """Remove a domain from a user's list of domains.
        :param domain: Valid domain string.
        :raises AttributeError: If domain not found in domains.
        :raises AttributeError: If domain is not a valid domain.
        :returns: None
        """
        assert self.default_domain != domain, "Cannot discard 'default_domain'."
        self._apply_and_publish(
            self._construct_event(
                User.DomainDiscarded,
                domain=self._validate_domain(domain)
            )
        )

    @staticmethod
    def _validate_user_id(value):
        if not value or not isinstance(value, UUID):
            raise AttributeError(f"{value!r} is not a valid User user_id. User ID must be a valid UUID.")
        else:
            return value

    @staticmethod
    def _validate_name(value):
        if not value or not isinstance(value, str):
            raise AttributeError(f"{value!r} is not a valid User name. User names must be a valid non-empty string.")
        else:
            return value

    @staticmethod
    def _validate_email(value):
        if not value or not isinstance(value, str) or not valid_email(value):
            raise AttributeError(
                f"{value!r} is not a valid User email address. User email must be a valid non-empty string like "
                f"'name@domain.com'.")
        else:
            return value

    @staticmethod
    def _validate_password(value):
        if not value or not valid_encrypted_password(value):
            raise AttributeError(
                f"{value!r} is not a valid User password."
            )
        else:
            return value

    @staticmethod
    def _validate_domain(value):
        if valid_domain(value):
            return value
        else:
            raise AttributeError(f"{value!r} is not a valid User domain. "
                                 f"User domains must be non-empty string like 'domain.com'")

    def increment_version(self):
        self._increment_version()

    def _construct_event(self, event_class, **kwargs):
        return event_class(
            originator_id=self.id,
            originator_version=self.version,
            **kwargs
        )
