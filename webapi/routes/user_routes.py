from apistar import Response, Route

from infrastructure.kanban_application import get_kanban_application
from webapi.models.user_model import CreateUser, User


def new_user(user: CreateUser):
    """Create a User within the default_domain. Default domain is 'public.example.com'."""
    default_domain = 'public.example.com' if 'default_domain' not in user else user['default_domain']
    try:
        app = get_kanban_application()
        user = app.new_user(name=user['name'], password=user['password'], email=user['email'],
                            default_domain=default_domain)
    except KeyError as e:
        error = {"error": "MissingRequiredParameterError", "message": str(e)}
        return Response(error, 400)
    except AttributeError as e:
        error = {"error": "AttributeError", "message": str(e)}
        return Response(error, 400)
    else:
        data = {"data": User(user)}
        return Response(data, 202)


user_routes = [
    Route('/NewUser', 'POST', new_user),
]
