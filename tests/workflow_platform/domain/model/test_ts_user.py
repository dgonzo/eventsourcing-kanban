from hypothesis import settings, given
from hypothesis.strategies import text

from kanban.domain.model.ts_user import create_user


@settings(max_examples=1)
@given(name=text(),
       default_domain=text())
def create_new_user(name, default_domain):
    user = create_user(name, default_domain)
    print(user)
