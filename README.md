# Event Sourcing Kanban Example

# Serialization Error when using TimestampedVersionedEntity
See:
 * [TimestamedVersionedEntity Class](kanban/domain/model/ts_user.py)
 * [Repository Configuration](infrastructure/ts_unit_of_work.py)
 * [Policies](infrastructure/projections/kanban_domain_policies.py)

```python
from infrastructure.ts_unit_of_work import UnitOfWork
with UnitOfWork() as do:
    user = do.new_user("Name", "Domain")
    
with UnitOfWork() as do:
    modified_user = do.change_name(user.id, "New Name")
    
Traceback (most recent call last):
  File "<input>", line 2, in <module>
  File "/Users/gonzo/Projects/eventsourcing-kanban/infrastructure/ts_unit_of_work.py", line 62, in change_name
    user.save()
  File "/Users/gonzo/Projects/eventsourcing-kanban/kanban/domain/model/ts_user.py", line 61, in save
    publish(self._pending_events[:])
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/domain/model/events.py", line 208, in publish
    handler(event)
  File "/Users/gonzo/Projects/eventsourcing-kanban/infrastructure/projections/kanban_domain_policies.py", line 27, in take_snapshot
    self.take_snapshot(e)
  File "/Users/gonzo/Projects/eventsourcing-kanban/infrastructure/projections/kanban_domain_policies.py", line 29, in take_snapshot
    self.repository.take_snapshot(event.originator_id, lte=event.originator_version)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/eventsourcedrepository.py", line 107, in take_snapshot
    return self.event_player.take_snapshot(entity_id, lt=lt, lte=lte)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/eventplayer.py", line 115, in take_snapshot
    snapshot = self.snapshot_strategy.take_snapshot(entity_id, entity, last_version)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/snapshotting.py", line 63, in take_snapshot
    publish(snapshot)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/domain/model/events.py", line 208, in publish
    handler(event)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/application/policies.py", line 22, in store_event
    self.event_store.append(event)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/eventstore.py", line 59, in append
    sequenced_item_or_items = self.to_sequenced_item(domain_event_or_events)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/eventstore.py", line 68, in to_sequenced_item
    return self.sequenced_item_mapper.to_sequenced_item(domain_event)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/sequenceditemmapper.py", line 53, in to_sequenced_item
    item_args = self.construct_item_args(domain_event)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/sequenceditemmapper.py", line 71, in construct_item_args
    data = self.serialize_event_attrs(domain_event.__dict__, is_encrypted=is_encrypted)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/sequenceditemmapper.py", line 102, in serialize_event_attrs
    cls=self.json_encoder_class,
  File "/usr/local/Cellar/python3/3.6.1/Frameworks/Python.framework/Versions/3.6/lib/python3.6/json/__init__.py", line 238, in dumps
    **kw).encode(obj)
  File "/usr/local/Cellar/python3/3.6.1/Frameworks/Python.framework/Versions/3.6/lib/python3.6/json/encoder.py", line 199, in encode
    chunks = self.iterencode(o, _one_shot=True)
  File "/usr/local/Cellar/python3/3.6.1/Frameworks/Python.framework/Versions/3.6/lib/python3.6/json/encoder.py", line 257, in iterencode
    return _iterencode(o, 0)
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/transcoding.py", line 28, in default
    return JSONEncoder.default(self, obj)
  File "/usr/local/Cellar/python3/3.6.1/Frameworks/Python.framework/Versions/3.6/lib/python3.6/json/encoder.py", line 180, in default
    o.__class__.__name__)
TypeError: Object of type 'set' is not JSON serializable

```

# EntityNotFoundError (corrupted repository) when using WithReflexiveMutator
See:
* [WithReflexiveMutator Class](kanban/domain/model/ref_user.py)
* [Repository Configuration](infrastructure/unit_of_work.py)
* [Policies](infrastructure/projections/workflow_platform_domain_policies.py)
```python
from infrastructure.unit_of_work import UnitOfWork
from infrastructure.datastore import get_session
with UnitOfWork(session=get_session().session) as do:
    new_user = do.new_user("Name", "Mk91Q^U%", "email@dot.com")
    
new_user
<User(pending_events=[n..0], _created_on=1508231589.20031, _id=bcb5d660-c44b-4da8-a054-55aaee4b5f6e, _is_discarded=False, _last_modified_on=1508231589.20031, _version=1, default_domain=public.example.com, domains={'public.example.com'}, email=email@dot.com, name=Name, password=********, user_id=3df2e083-8615-41e7-bce0-58a9953dda29)>
with UnitOfWork(session=get_session().session) as do:
    modified_user = do.modify_user(new_user.id, "name", "New")
    
modified_user
<User(pending_events=[n..0], _created_on=1508231589.20031, _id=bcb5d660-c44b-4da8-a054-55aaee4b5f6e, _is_discarded=False, _last_modified_on=1508231589.20031, _version=2, default_domain=public.example.com, domains={'public.example.com'}, email=email@dot.com, name=New, password=********, user_id=3df2e083-8615-41e7-bce0-58a9953dda29)>
modified_user.id
UUID('bcb5d660-c44b-4da8-a054-55aaee4b5f6e')
with UnitOfWork(session=get_session().session) as do:
    found_user = do.get_user(modified_user.id)
    
with UnitOfWork(session=get_session().session) as do:
    modified_user = do.add_domain_to_user(modified_user.id, "example.domain.com")
    
with UnitOfWork(session=get_session().session) as do:
    found_user = do.get_user(modified_user.id)
    
Traceback (most recent call last):
  File "/Users/gonzo/Projects/eventsourcing-kanban/infrastructure/unit_of_work.py", line 127, in get_user
    user = self.users[user_id]
  File "/Users/gonzo/Projects/eventsourcing-kanban/.venv/lib/python3.6/site-packages/eventsourcing/infrastructure/eventsourcedrepository.py", line 71, in __getitem__
    raise RepositoryKeyError(entity_id)
eventsourcing.exceptions.RepositoryKeyError: UUID('bcb5d660-c44b-4da8-a054-55aaee4b5f6e')
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  File "<input>", line 2, in <module>
  File "/Users/gonzo/Projects/eventsourcing-kanban/infrastructure/unit_of_work.py", line 129, in get_user
    raise EntityNotFoundError(f"No user found with id: {user_id}.")
NameError: name 'EntityNotFoundError' is not defined

```
