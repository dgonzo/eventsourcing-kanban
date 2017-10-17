from hypothesis import given
from hypothesis.extra.fakefactory import fake_factory
from hypothesis.strategies import sampled_from
from pytest import raises

from kanban.domain.model.ref_user import User

PASSWORDS = [
    '$pbkdf2-sha512$200000$rrU25pxTSsn5n5NyjvH.Pw$PKLSamXKl5S/guVvYVAodJr3tcCGkvEdRt0OtnZizsuGrWowhqVxzumih13hfnssE2jbJONXaAYXcm0ZZTa/dw',
    '$pbkdf2-sha512$200000$9b43hhCCsPb./z.ntDbGmA$613qQeZZpUOwsuauA1mwMFJM5r/hJt4sOV3agBEOVC84ix.sxISGCeo/wrXM2mIJ3PVQR.7Y92YPdC1XYxph0g'
]


@given(name=fake_factory('name'),
       email=fake_factory('email'),
       password=sampled_from(PASSWORDS),
       default_domain=fake_factory('domain_name'))
def test_create_user(name, email, password, default_domain):
    user = User.create(name=name, password=password, email=email, default_domain=default_domain)
    assert user.name == name
    assert user.email == email
    assert user.password == password
    assert user.default_domain == default_domain
    assert default_domain in user.domains


@given(password=sampled_from(PASSWORDS))
def test_create_user_w_invalid_name_raises_attribute_error(password):
    with raises(AttributeError):
        User.create(name="", password=password, email="", default_domain="")


@given(password=sampled_from(PASSWORDS))
def test_create_user_w_invalid_email_raises_attribute_error(password):
    with raises(AttributeError):
        User.create(name="", password=password, email="", default_domain="")
    with raises(AttributeError):
        User.create(name="", password=password, email="not_email", default_domain="")


def test_create_user_w_unencrypted_email_raise_attribute_error():
    with raises(AttributeError):
        User.create(name="Name", password="password", email="email@dot.com", default_domain="dot.com")


@given(initial_name=fake_factory('name'),
       initial_email=fake_factory('email'),
       changed_name=fake_factory('name'),
       changed_email=fake_factory('email'),
       initial_password=sampled_from(PASSWORDS),
       changed_password=sampled_from(PASSWORDS),
       initial_default_domain=fake_factory('domain_name'),
       changed_default_domain=fake_factory('domain_name'))
def test_modify_user(initial_name, initial_email, changed_name, changed_email, initial_password, changed_password,
                     initial_default_domain, changed_default_domain):
    user = User.create(name=initial_name, password=initial_password, email=initial_email,
                       default_domain=initial_default_domain)
    user.change_attribute('name', changed_name)
    user.change_attribute('password', changed_password)
    user.change_attribute('email', changed_email)
    user.change_attribute('default_domain', changed_default_domain)
    assert user.name == changed_name
    assert user.password == changed_password
    assert user.email == changed_email
    assert user.default_domain == changed_default_domain


@given(name=fake_factory('name'),
       email=fake_factory('email'),
       password=sampled_from(PASSWORDS),
       default_domain=fake_factory('domain_name'))
def test_discard_user(name, email, password, default_domain):
    user = User.create(name=name, password=password, email=email, default_domain=default_domain)
    user.discard()
    assert user._is_discarded


#
# Domains
#
@given(name=fake_factory('name'),
       email=fake_factory('email'),
       password=sampled_from(PASSWORDS),
       default_domain=fake_factory('domain_name'),
       new_domain=fake_factory('domain_name'))
def test_add_domain_to_user(name, email, password, default_domain, new_domain):
    user = User.create(name=name, password=password, email=email, default_domain=default_domain)
    user.add_domain(new_domain)
    assert new_domain in user.domains


@given(password=sampled_from(PASSWORDS),
       other_domain=fake_factory('domain_name'))
def test_discard_user_domain(password, other_domain):
    user = User.create(name="Name", password=password, email="email@dot.com", default_domain="public.example.com")
    user.add_domain(other_domain)
    assert other_domain in user.domains
    user.discard_domain(other_domain)
    assert other_domain not in user.domains


@given(name=fake_factory('name'),
       email=fake_factory('email'),
       password=sampled_from(PASSWORDS),
       default_domain=fake_factory('domain_name'))
def test_add_invalid_domain_to_user_raises_attribute_error(name, email, password, default_domain):
    user = User.create(name=name, password=password, email=email, default_domain=default_domain)
    with raises(AttributeError):
        user.add_domain('not_domain')
