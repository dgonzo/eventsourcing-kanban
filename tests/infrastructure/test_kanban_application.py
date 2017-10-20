from hypothesis import settings, given
from hypothesis.extra.fakefactory import fake_factory
from hypothesis.strategies import sampled_from

from infrastructure.kanban_application import get_kanban_application
from tests.test_app import VALID_PASSWORDS

init_kanban_application_w_sqlalchemy()


@settings(max_examples=2)
@given(name=fake_factory('name'),
       password=sampled_from(VALID_PASSWORDS),
       email=fake_factory('email'),
       default_domain=fake_factory('domain_name'))
def test_new_user(name, password, email, default_domain):
   app = get_kanban_application()
