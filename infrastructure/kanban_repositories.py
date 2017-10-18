from eventsourcing.example.domainmodel import AbstractExampleRepository
from eventsourcing.infrastructure.eventsourcedrepository import EventSourcedRepository

from kanban.domain.model.user import User


class UserRepository(EventSourcedRepository, AbstractExampleRepository):
    """
    Event sourced repository for the User domain model entity.
    """
    __page_size__ = 1000
    mutator = User._mutate