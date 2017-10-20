import os

from apistar import Include
from apistar.backends import sqlalchemy_backend
from apistar.frameworks.wsgi import WSGIApp as App
from apistar.handlers import docs_urls, static_urls

from infrastructure.datastore import get_database
from infrastructure.kanban_application import init_kanban_application_w_sqlalchemy
from webapi.routes.user_routes import user_routes

BASEDIR = os.path.dirname(os.path.abspath(__file__))
DB_HOST = f"sqlite:///{BASEDIR}/infrastructure/event.db"

init_kanban_application_w_sqlalchemy(db_host=DB_HOST)

routes = [
    Include('/docs', docs_urls),
    Include('/static', static_urls)
]

routes += user_routes

settings = {
    "DATABASE": {
        "URL": DB_HOST,
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
