from uuid import UUID

from apistar import Response, Route

from infrastructure.datastore import get_session
from infrastructure.unit_of_work import UnitOfWork, EntityNotFoundError
from webapi.models.user_model import CreateUser, User, ModifyUser, ChangeUserPassword, DomainNamespace, UserIdList, \
    UserId


def list_users(domain_namespace: DomainNamespace):
    """List users within a domain_namespace. Default namespace is 'public.example.com."""
    if not domain_namespace:
        domain_namespace = 'public.example.com'

    with UnitOfWork(session=get_session().session) as do:
        user_ids = do.get_user_ids(domain_namespace=domain_namespace)

    users = [str(_id) for _id in user_ids]
    return {"data": UserIdList(users)}


def new_user(user: CreateUser):
    """Create a User within the default_domain. Default domain is 'public.example.com'."""
    try:
        with UnitOfWork(session=get_session().session) as do:
            user = do.new_user(name=user['name'], password=user['password'], email=user['email'],
                               default_domain=user['default_domain'])
    except AttributeError as e:
        error = {"error": "AttributeError", "message": str(e)}
        return Response({"data", error}, 400)
    else:
        data = {"data": User(user)}
        return Response(data, 202)


def get_user(user_id: UserId):
    """Retrieve a user object."""
    try:
        with UnitOfWork(session=get_session().session) as do:
            user = do.get_user(UUID(user_id))
    except EntityNotFoundError as e:
        error = {"error": "EntityNotFoundError", "message": str(e)}
        return Response({"data": error}, 404)
    else:
        return {"data": User(user)}


def modify_user(user_id: UserId, attribute: ModifyUser):
    """Modify user attributes."""
    try:
        with UnitOfWork(session=get_session().session) as do:
            user = do.modify_user(user_id=user_id, attribute_name=attribute['attribute_name'],
                                  attribute_value=attribute['attribute_value'])
    except AttributeError as e:
        error = {"error": "AttributeError", "message": str(e)}
        return Response({"data": error}, 400)
    except NotImplementedError as e:
        error = {"error": "NotImplementedError", "message": str(e)}
        return Response({"data": error}, 501)
    else:
        data = {"data": User(user)}
        return Response(data, 200)


def change_password(user_id: UserId, user: ChangeUserPassword):
    """Change a user's password."""
    try:
        with UnitOfWork(session=get_session().session) as do:
            do.change_password(user_id=user_id, new_password=user['new_password'])
    except AttributeError as e:
        error = {"error": "AttributeError", "message": str(e)}
        return Response({"data": error}, 400)
    else:
        return Response("", 204)


def discard_user(user_id: UserId):
    """Permanently discard a user."""
    try:
        with UnitOfWork(session=get_session().session) as do:
            do.discard_user(UUID(user_id))
    except EntityNotFoundError as e:
        error = {"error": "EntityNotFoundError", "message": str(e)}
        return Response({"data": error}, 404)
    else:
        return Response("", 204)


user_routes = [
    Route('/ListUsers', 'GET', list_users),
    Route('/NewUser', 'POST', new_user),
    Route('/User/{user_id}', 'GET', get_user),
    Route('/User/{user_id}/Modify', 'PUT', modify_user),
    Route('/User/{user_id}/ChangePassword', 'PUT', change_password),
    Route('/User/{user_id}/Delete', 'DELETE', discard_user)
]
