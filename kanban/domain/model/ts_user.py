from uuid import uuid4

from eventsourcing.domain.model.decorators import attribute, mutator
from eventsourcing.domain.model.entity import TimestampedVersionedEntity, mutate_entity
from eventsourcing.domain.model.events import publish


class User(TimestampedVersionedEntity):
    class Event(TimestampedVersionedEntity.Event):
        """Layer supertype"""

    class Created(TimestampedVersionedEntity.Created):
        """Created"""

    class AttributeChanged(Event, TimestampedVersionedEntity.AttributeChanged):
        """Changed"""

    class Discarded(Event, TimestampedVersionedEntity.Discarded):
        """Discarded"""

    class DomainAdded(Event):
        """Domain added"""

        @property
        def domain(self):
            return self.__dict__['domain']

    class DomainDiscarded(Event):
        """Domain discarded"""

    def __init__(self, name, default_domain, **kwargs):
        super(User, self).__init__(**kwargs)
        self._name = self._validate_name(name)
        self._default_domain = self._validate_domain(default_domain)
        self._domains = set()
        self._pending_events = []

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

    @attribute
    def name(self):
        pass

    @attribute
    def default_domain(self):
        pass

    def _publish(self, event):
        self._pending_events.append(event)

    def save(self):
        publish(self._pending_events[:])
        self._pending_events = []

    @classmethod
    def _mutate(cls, initial, event):
        return mutate_aggregate(initial or cls, event)

    @staticmethod
    def _validate_name(value):
        return value

    @staticmethod
    def _validate_domain(value):
        return value

    def add_domain(self, value):
        assert not self._is_discarded
        event = User.DomainAdded(
            originator_id=self.id,
            originator_version=self.version,
            domain=self._validate_domain(value)
        )
        self._apply_and_publish(event)
        self._publish(event)


def create_user(name, default_domain):
    event = User.Created(
        originator_id=uuid4(),
        name=name,
        default_domain=default_domain
    )
    user = mutate_aggregate(User, event)
    user._publish(event)
    return user


@mutator
def mutate_aggregate(user, event):
    return mutate_entity(user, event)


@mutate_entity.register(User.DomainAdded)
def _(user, event):
    try:
        user._assert_not_discarded()
    except TypeError:
        raise Exception(user)
    user._domains.add(event.domain)
    user._version += 1
    user._last_modified_on = event.timestamp
    return user
