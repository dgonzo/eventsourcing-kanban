from hypothesis import given, settings
from hypothesis.extra.fakefactory import fake_factory
from hypothesis.strategies import sampled_from, uuids, lists
from pytest import raises

from infrastructure.datastore import get_session
from infrastructure.unit_of_work import UnitOfWork, EntityNotFoundError, SANITIZED_PASSWORD

VALID_PASSWORDS = ['z$XsntEXK%I73Z$c', 'Mk91Q^U%']
INVALID_PASSWORDS = ['bK0j4$M', 'password']


#
# User
#
@settings(max_examples=10)
@given(name=fake_factory('name'),
       password=sampled_from(VALID_PASSWORDS),
       email=fake_factory('email'),
       default_domain=fake_factory('domain_name'))
def test_new_user(name, password, email, default_domain):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user(name, password, email, default_domain)
    assert new_user.name == name
    assert new_user.email == email
    assert new_user.password == SANITIZED_PASSWORD
    assert new_user.default_domain == default_domain
    assert default_domain in new_user.domains


def test_get_user_ids_returns_all_user_ids_in_a_domain_namespace():
    emails = ['a@gmail.com', 'b@gmail.com']
    for email in emails:
        with UnitOfWork(session=get_session().session) as do:
            _ = do.new_user("Name", VALID_PASSWORDS[0], email)
    with UnitOfWork(session=get_session().session) as do:
        users = do.get_user_ids()
    assert len(users) == len(emails)


@settings(max_examples=10)
@given(name=fake_factory('name'),
       password=sampled_from(VALID_PASSWORDS),
       email=fake_factory('email'),
       default_domain=fake_factory('domain_name'))
def test_get_user(name, password, email, default_domain):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user(name, password, email, default_domain)

    with UnitOfWork(session=get_session().session) as do:
        found_user = do.get_user(new_user.id)
    assert found_user.id == new_user.id


@settings(max_examples=10)
@given(user_id=uuids())
def test_get_non_existent_user_raises_entity_not_found_error(user_id):
    with raises(EntityNotFoundError):
        with UnitOfWork(session=get_session().session) as do:
            do.get_user(user_id)


@settings(max_examples=1)
@given(initial_name=fake_factory('name'),
       changed_name=fake_factory('name'),
       password=sampled_from(VALID_PASSWORDS),
       initial_email=fake_factory('email'),
       changed_email=fake_factory('email'),
       initial_default_domain=fake_factory('domain_name'),
       changed_default_domain=fake_factory('domain_name'))
def test_modify_user(initial_name, changed_name, password, initial_email, changed_email,
                     initial_default_domain, changed_default_domain):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user(initial_name, password, initial_email, initial_default_domain)

    with UnitOfWork(session=get_session().session) as do:
        do.modify_user(new_user.id, 'name', changed_name)

    with UnitOfWork(session=get_session().session) as do:
        do.modify_user(new_user.id, 'email', changed_email)

    with UnitOfWork(session=get_session().session) as do:
        do.modify_user(new_user.id, 'default_domain', changed_default_domain)

    with UnitOfWork(session=get_session().session) as do:
        modified_user = do.get_user(new_user.id)

    assert modified_user.name == changed_name
    assert modified_user.email == changed_email
    assert modified_user.default_domain == changed_default_domain


def test_modify_user_reserved_fields_raises_not_implemented_error():
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user("Name", VALID_PASSWORDS[0], "email@dot.com")

    with raises(NotImplementedError):
        with UnitOfWork(session=get_session().session) as do:
            do.modify_user(new_user.id, 'password', "shouldn't matter")

    with raises(NotImplementedError):
        with UnitOfWork(session=get_session().session) as do:
            do.modify_user(new_user.id, 'domains', "shouldn't matter")


@settings(max_examples=1)
@given(initial_password=sampled_from(VALID_PASSWORDS),
       changed_password=sampled_from(VALID_PASSWORDS))
def test_change_password(initial_password, changed_password):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user("Name", initial_password, "email@dot.com")

    initial_version = new_user.version

    with UnitOfWork(session=get_session().session) as do:
        do.change_password(new_user.id, changed_password)

    with UnitOfWork(session=get_session().session) as do:
        modified_user = do.get_user(new_user.id)

    assert modified_user.version > initial_version


@settings(max_examples=2)
@given(domain=fake_factory('domain_name'))
def test_add_domain_to_user(domain):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user("Name", VALID_PASSWORDS[0], "email@dot.com")

    with UnitOfWork(session=get_session().session) as do:
        modified_user = do.add_domain_to_user(new_user.id, domain)

    assert domain in modified_user.domains


@settings(max_examples=2)
@given(domain=fake_factory('domain_name'))
def test_remove_domain_from_user(domain):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user("Name", VALID_PASSWORDS[0], "email@dot.com")
        do.add_domain_to_user(new_user.id, domain)

    with UnitOfWork(session=get_session().session) as do:
        do.add_domain_to_user(new_user.id, domain)

    with UnitOfWork(session=get_session().session) as do:
        modified_user = do.remove_domain_from_user(new_user.id, domain)

    assert domain not in modified_user.domains


@settings(max_examples=10)
@given(name=fake_factory('name'),
       password=sampled_from(VALID_PASSWORDS),
       email=fake_factory('email'))
def test_discard_user(name, password, email):
    with UnitOfWork(session=get_session().session) as do:
        new_user = do.new_user(name, password, email)

    user_id = new_user.id

    with UnitOfWork(session=get_session().session) as do:
        do.discard_user(new_user.id)

    with UnitOfWork(session=get_session().session) as do:
        users = do.get_user_ids('public.example.com')
    assert user_id not in users


