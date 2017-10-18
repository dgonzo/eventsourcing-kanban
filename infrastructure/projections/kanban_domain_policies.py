from eventsourcing.domain.model.events import subscribe, unsubscribe

from kanban.domain.model.user import User


class KanbanSnapshottingPolicy(object):
    def __init__(self, repository, period=2):
        self.repository = repository
        self.period = period
        subscribe(predicate=self.trigger, handler=self.take_snapshot)

    def close(self):
        unsubscribe(predicate=self.trigger, handler=self.take_snapshot)

    def trigger(self, event):
        if isinstance(event, (list)):
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
