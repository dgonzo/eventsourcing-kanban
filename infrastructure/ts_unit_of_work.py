from eventsourcing.application.base import ApplicationWithPersistencePolicies
from eventsourcing.infrastructure.eventsourcedrepository import EventSourcedRepository
from eventsourcing.infrastructure.snapshotting import EventSourcedSnapshotStrategy
from eventsourcing.infrastructure.sqlalchemy.activerecords import SQLAlchemyActiveRecordStrategy, \
    IntegerSequencedItemRecord, SnapshotRecord

from infrastructure.datastore import get_session
from infrastructure.projections.kanban_domain_policies import KanbanSnapshottingPolicy
from kanban.domain.model.ts_user import User, create_user


class UnitOfWork(ApplicationWithPersistencePolicies):
    def __init__(self, **kwargs):
        session = get_session().session
        entity_active_record_strategy = SQLAlchemyActiveRecordStrategy(
            active_record_class=IntegerSequencedItemRecord,
            session=session
        )
        snapshot_active_record_strategy = SQLAlchemyActiveRecordStrategy(
            active_record_class=SnapshotRecord,
            session=session
        )
        super(UnitOfWork, self).__init__(
            entity_active_record_strategy=entity_active_record_strategy,
            snapshot_active_record_strategy=snapshot_active_record_strategy,
            **kwargs
        )

        self.snapshot_strategy = EventSourcedSnapshotStrategy(
            event_store=self.snapshot_event_store
        )

        self.users = EventSourcedRepository(
            event_store=self.entity_event_store,
            mutator=User._mutate,
            snapshot_strategy=self.snapshot_strategy
        )

        self.snapshotting_policy = KanbanSnapshottingPolicy(
            repository=self.users
        )

    def close(self):
        super(UnitOfWork, self).close()
        self.snapshotting_policy.close()

    @staticmethod
    def new_user(name, domain):
        user = create_user(name, domain)
        user.save()
        return user

    def add_domain_to_user(self, user_id, domain):
        user = self.users[user_id]
        user.add_domain(domain)
        user.save()
        return user

    def change_name(self, user_id, name):
        user = self.users[user_id]
        user.name = name
        user.save()
        return user
