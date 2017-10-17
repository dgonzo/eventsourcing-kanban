import os
from uuid import uuid5, UUID

from eventsourcing.domain.model.collection import register_new_collection, Collection
from eventsourcing.domain.model.events import subscribe, unsubscribe

from kanban.domain.model.ref_user import User

LOCAL_NAMESPACE = UUID(os.getenv('LOCAL_NAMESPACE', 'c48268a6-e2a6-4898-98b9-3c3440ee1e99'))
USER_NAMESPACE = UUID(os.getenv('USER_NAMESPACE', '8800a281-84d4-4c62-8a21-731548b57a70'))


class DomainSnapshottingPolicy:
    def __init__(self, repository, period=2):
        self.repository = repository
        self.period = period
        subscribe(predicate=self.trigger, handler=self.take_snapshot)

    def close(self):
        unsubscribe(predicate=self.trigger, handler=self.take_snapshot)

    def trigger(self, event):
        if isinstance(event, list):
            return True
        is_period = not (event.originator_version + 1) % self.period
        is_type = isinstance(event, User.Event)
        is_trigger = is_type and is_period
        return is_trigger

    def take_snapshot(self, event):
        if isinstance(event, list):
            for e in event:
                if self.trigger(e):
                    self.take_snapshot(e)
        else:
            self.repository.take_snapshot(event.originator_id, lte=event.originator_version)


class UserProjectionPolicy:
    """Updates user collection whenever a user is created or discarded.
    """

    def __init__(self, user_collections):
        self.user_collections = user_collections
        subscribe(self.add_user_to_collection, self.is_user_created)
        subscribe(self.remove_user_from_collection, self.is_user_discarded)

    def close(self):
        unsubscribe(self.add_user_to_collection, self.is_user_created)
        unsubscribe(self.remove_user_from_collection, self.is_user_discarded)

    def is_user_created(self, event):
        if isinstance(event, (list, tuple)):
            return all(map(self.is_user_created, event))
        return isinstance(event, User.Created)

    def is_user_discarded(self, event):
        if isinstance(event, (list, tuple)):
            return all(map(self.is_user_discarded, event))
        return isinstance(event, User.Discarded)

    def add_user_to_collection(self, event):
        assert isinstance(event, User.Created), event
        domain_namespace = event.default_domain
        collection_id = make_user_collection_id(domain_namespace)
        try:
            collection = self.user_collections[collection_id]
        except KeyError:
            collection = register_new_collection(collection_id=collection_id)

        assert isinstance(collection, Collection)
        collection.add_item(event.originator_id)

    def remove_user_from_collection(self, event):
        if isinstance(event, (list, tuple)) and len(event) < 1:
            return None
        elif isinstance(event, (list, tuple)):
            event = event.pop()
        assert isinstance(event, User.Discarded), event
        domain_namespace = event.domain_namespace
        collection_id = make_user_collection_id(domain_namespace)
        try:
            collection = self.user_collections[collection_id]
        except KeyError:
            pass
        else:
            assert isinstance(collection, Collection)
            collection.remove_item(event.originator_id)


def make_user_collection_id(domain_namespace, collections_ns=USER_NAMESPACE):
    return uuid5(collections_ns, domain_namespace)

