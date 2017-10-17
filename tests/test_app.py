from uuid import UUID

from apistar import TestClient
from hypothesis import given, settings
from hypothesis.extra.fakefactory import fake_factory
from hypothesis.strategies import sampled_from

from app import app
from infrastructure.datastore import get_session
from infrastructure.unit_of_work import UnitOfWork
from tests.infrastructure.test_unit_of_work import VALID_PASSWORDS, INVALID_PASSWORDS


@settings(max_examples=10)
@given(name=fake_factory('name'),
       password=sampled_from(VALID_PASSWORDS),
       email=fake_factory('email'),
       default_domain=fake_factory('domain_name'))
def test_new_user(name, password, email, default_domain):
    client = TestClient(app)
    payload = {
        "name": name,
        "password": password,
        "email": email,
        "default_domain": default_domain
    }
    response = client.post('/NewUser', json=payload)
    assert response.status_code == 202
    record = response.json()
    assert record['data']['name'] == payload['name']
    assert record['data']['password'] == '********'
    assert record['data']['email'] == payload['email']
    assert record['data']['default_domain'] == payload['default_domain']
    assert isinstance(UUID(record['data']['user_id']), UUID)
    assert '_created_on' in record['data']
    assert '_last_modified_on' in record['data']


@settings(max_examples=10)
@given(name=fake_factory('name'),
       password=sampled_from(VALID_PASSWORDS),
       email=fake_factory('email'),
       default_domain=fake_factory('domain_name'))
def test_list_users(name, password, email, default_domain):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user(name, password, email, default_domain)

    user_id = str(new_user.id)

    client = TestClient(app)
    params = {
        'domain_namespace': default_domain
    }
    response = client.get('/ListUsers', params=params)
    assert response.status_code == 200
    users = response.json()['data']
    assert user_id in users


@settings(max_examples=10)
@given(name=fake_factory('name'),
       password=sampled_from(VALID_PASSWORDS),
       email=fake_factory('email'),
       default_domain=fake_factory('domain_name'))
def test_get_user(name, password, email, default_domain):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user(name, password, email, default_domain)

    user_id = str(new_user.id)

    client = TestClient(app)
    response = client.get(f"/User/{user_id}")
    user = response.json()['data']
    assert user['name'] == name
    assert user['email'] == email
    assert user['password'] == '********'
    assert user['default_domain'] == default_domain


@settings(max_examples=10)
@given(initial_name=fake_factory('name'),
       initial_email=fake_factory('email'),
       changed_name=fake_factory('name'),
       changed_email=fake_factory('email'),
       password=sampled_from(VALID_PASSWORDS),
       initial_default_domain=fake_factory('domain_name'),
       changed_default_domain=fake_factory('domain_name'))
def test_modify_user(initial_name, initial_email, changed_name, changed_email, password, initial_default_domain,
                     changed_default_domain):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user(initial_name, password, initial_email, initial_default_domain)

    new_user_id = str(new_user.id)

    client = TestClient(app)

    modify_name = {
        "attribute_name": "name",
        "attribute_value": changed_name
    }
    name_response = client.put(f'/User/{new_user_id}/Modify', json=modify_name)
    modified_name = name_response.json()['data']['name']

    modify_email = {
        "attribute_name": "email",
        "attribute_value": changed_email
    }
    email_response = client.put(f'/User/{new_user_id}/Modify', json=modify_email)
    modified_email = email_response.json()['data']['email']

    modify_default_domain = {
        "attribute_name": "default_domain",
        "attribute_value": changed_default_domain
    }
    default_domain_response = client.put(f'/User/{new_user_id}/Modify', json=modify_default_domain)
    modified_default_domain = default_domain_response.json()['data']['default_domain']

    assert modified_name == changed_name
    assert modified_email == changed_email
    assert modified_default_domain == changed_default_domain


def test_modify_user_password_returns_not_implemented_error():
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user("Name", VALID_PASSWORDS[0], "email@dot.com")

    new_user_id = str(new_user.id)

    client = TestClient(app)

    modify_password = {
        "attribute_name": "password",
        "attribute_value": "shouldn't matter"
    }
    response = client.put(f'/User/{new_user_id}/Modify', json=modify_password)
    assert response.json()['data']['error'] == "NotImplementedError"
    assert response.status_code == 501


def test_modify_user_domains_raises_not_implemented_error():
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user("Name", VALID_PASSWORDS[0], "email@dot.com")

    new_user_id = str(new_user.id)

    client = TestClient(app)

    modify_domains = {
        "attribute_name": "domains",
        "attribute_value": "shouldn't matter"
    }
    response = client.put(f'/User/{new_user_id}/Modify', json=modify_domains)
    assert response.json()['data']['error'] == "NotImplementedError"
    assert response.status_code == 501


@settings(max_examples=1)
@given(password=sampled_from(VALID_PASSWORDS),
       new_password=sampled_from(VALID_PASSWORDS))
def test_change_password(password, new_password):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user("Name", password, "email@dot.com")

    new_user_id = str(new_user.id)

    client = TestClient(app)

    change_password = {
        "new_password": new_password
    }
    response = client.put(f'/User/{new_user_id}/ChangePassword', json=change_password)
    assert response.status_code == 204


@settings(max_examples=2)
@given(password=sampled_from(VALID_PASSWORDS),
       bad_password=sampled_from(INVALID_PASSWORDS))
def test_change_password_w_bad_password_returns_attribute_error(password, bad_password):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user("Name", password, "email@dot.com")

    new_user_id = str(new_user.id)

    client = TestClient(app)

    change_password = {
        "new_password": bad_password
    }
    response = client.put(f'/User/{new_user_id}/ChangePassword', json=change_password)
    assert response.json()['data']['error'] == "AttributeError"
    assert response.status_code == 400


@settings(max_examples=2)
@given(password=sampled_from(VALID_PASSWORDS))
def test_discard_user(password):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user("Name", password, "email@dot.com")

    new_user_id = str(new_user.id)

    client = TestClient(app)

    response = client.delete(f'/User/{new_user_id}/Delete')
    assert response.status_code == 204

    response = client.get('/ListUsers')
    users = response.json()['data']
    assert new_user_id not in users
