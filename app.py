import os

from apistar import Include
from apistar.backends import sqlalchemy_backend
from apistar.frameworks.wsgi import WSGIApp as App
from apistar.handlers import docs_urls, static_urls
from eventsourcing.infrastructure.sqlalchemy.activerecords import SQLAlchemyActiveRecordStrategy, \
    IntegerSequencedItemRecord
from sqlalchemy import Column, BigInteger, String, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType

from infrastructure.datastore import event_datastore
from infrastructure.kanban_application import init_kanban_application
from webapi.routes.user_routes import user_routes

BASEDIR = os.path.dirname(os.path.abspath(__file__))

Base = declarative_base()


# Define database tables.
class IntegerSequencedItem(Base):
    __tablename__ = 'integer_sequenced_items'
    sequence_id = Column(UUIDType(), primary_key=True)
    position = Column(BigInteger(), primary_key=True)
    topic = Column(String(255))
    data = Column(Text())
    __table_args__ = Index('index', 'sequence_id', 'position'),


event_datastore.setup_connection()
event_datastore.setup_tables()


def init_kanban_application_w_sqlalchemy():
    init_kanban_application(
        entity_active_record_strategy=SQLAlchemyActiveRecordStrategy(
            active_record_class=IntegerSequencedItemRecord,
            session=event_datastore.session
        )
    )


init_kanban_application_w_sqlalchemy()

routes = [
    Include('/docs', docs_urls),
    Include('/static', static_urls)
]

routes += user_routes

settings = {
    "DATABASE": {
        "URL": f"sqlite:///{BASEDIR}/infrastructure/event.db",
        "METADATA": event_datastore._base.metadata
    }
}

app = App(
    routes=routes,
    settings=settings,
    commands=sqlalchemy_backend.commands,
    components=sqlalchemy_backend.components
)

if __name__ == '__main__':
    app.main()
