import os

from apistar import Include
from apistar.backends import sqlalchemy_backend
from apistar.frameworks.wsgi import WSGIApp as App
from apistar.handlers import docs_urls, static_urls
from eventsourcing.infrastructure.sqlalchemy.activerecords import SQLAlchemyActiveRecordStrategy, \
    IntegerSequencedItemRecord

from infrastructure import datastore
from infrastructure.datastore import get_database
from infrastructure.kanban_application import init_kanban_application
from webapi.routes.user_routes import user_routes

BASEDIR = os.path.dirname(os.path.abspath(__file__))


def init_kanban_application_w_sqlalchemy():
    datastore.init_database()
    db = get_database()
    db.setup_connection()
    db.setup_tables()
    init_kanban_application(
        entity_active_record_strategy=SQLAlchemyActiveRecordStrategy(
            active_record_class=IntegerSequencedItemRecord,
            session=db.session
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
        "METADATA": get_database()._base.metadata
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
