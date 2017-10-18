# Event Sourcing Kanban Example

Try:

    $ pip install -r requirements.txt
    $ apistar create_tables
    $ apistar run
    $ http :8080/NewUser name="Name" password="Mk91Q^U%" email="email@dot.com"

Error:

```python
Traceback (most recent call last):
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/apistar/frameworks/wsgi.py", line 133, in __call__
    response = self.http_injector.run_all(funcs, state=state)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/apistar/components/dependency.py", line 141, in run_all
    ret = step.func(**kwargs)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/apistar/frameworks/wsgi.py", line 129, in __call__
    response = self.http_injector.run_all(funcs, state=state)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/apistar/components/dependency.py", line 141, in run_all
    ret = step.func(**kwargs)
  File "/Users/gonzo/Projects/eventsourcing-kanban/webapi/routes/user_routes.py", line 13, in new_user
    default_domain=default_domain)
  File "/Users/gonzo/Projects/eventsourcing-kanban/infrastructure/kanban_application.py", line 64, in new_user
    user = User.create(name, password_hash, email, whitelisted_domain)
  File "/Users/gonzo/Projects/eventsourcing-kanban/kanban/domain/model/user.py", line 139, in create
    publish(event)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/domain/model/events.py", line 208, in publish
    handler(event)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/application/policies.py", line 22, in store_event
    self.event_store.append(event)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/eventstore.py", line 63, in append
    self.active_record_strategy.append(sequenced_item_or_items)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/sqlalchemy/activerecords.py", line 29, in append
    self.session.commit()
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/scoping.py", line 157, in do
    return getattr(self.registry(), name)(*args, **kwargs)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/session.py", line 906, in commit
    self.transaction.commit()
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/session.py", line 461, in commit
    self._prepare_impl()
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/session.py", line 441, in _prepare_impl
    self.session.flush()
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/session.py", line 2177, in flush
    self._flush(objects)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/session.py", line 2297, in _flush
    transaction.rollback(_capture_exception=True)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/util/langhelpers.py", line 66, in __exit__
    compat.reraise(exc_type, exc_value, exc_tb)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/util/compat.py", line 187, in reraise
    raise value
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/session.py", line 2261, in _flush
    flush_context.execute()
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/unitofwork.py", line 389, in execute
    rec.execute(self)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/unitofwork.py", line 548, in execute
    uow
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/persistence.py", line 181, in save_obj
    mapper, table, insert)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/orm/persistence.py", line 799, in _emit_insert_statements
    execute(statement, multiparams)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/engine/base.py", line 945, in execute
    return meth(self, multiparams, params)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/sql/elements.py", line 263, in _execute_on_connection
    return connection._execute_clauseelement(self, multiparams, params)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/engine/base.py", line 1053, in _execute_clauseelement
    compiled_sql, distilled_params
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/engine/base.py", line 1189, in _execute_context
    context)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/engine/base.py", line 1402, in _handle_dbapi_exception
    exc_info
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/util/compat.py", line 203, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb, cause=cause)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/util/compat.py", line 186, in reraise
    raise value.with_traceback(tb)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/engine/base.py", line 1182, in _execute_context
    context)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/sqlalchemy/engine/default.py", line 470, in do_execute
    cursor.execute(statement, parameters)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: integer_sequenced_items [SQL: 'INSERT INTO integer_sequenced_items (sequence_id, position, topic, data) VALUES (?, ?, ?, ?)'] [parameters: (<memory at 0x1067c0048>, 0, 'kanban.domain.model.user#User.Created', '{"default_domain":"public.example.com","email":"email@dot.com","name":"Name","originator_id":{"UUID":"77dbc708446b45c099ecfc86ba76b21e"},"originator_ ... (91 characters truncated) ... YNp2BrI.SVzqBlNNjr/dS7hupMgUNrMAvq08ZQCdw2Lse7pTwe6ha833c8SRqLQ","timestamp":1508290312.702388,"user_id":{"UUID":"ae01058b33cf4fcdb4503e0aab55688d"}}')]
```
