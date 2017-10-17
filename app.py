from apistar import Include
from apistar.frameworks.wsgi import WSGIApp as App
from apistar.handlers import docs_urls, static_urls

from webapi.routes.user_routes import user_routes

routes = [
    Include('/docs', docs_urls),
    Include('/static', static_urls),
]

routes += user_routes

app = App(routes=routes)

if __name__ == '__main__':
    app.main()
