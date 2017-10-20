import os

from eventsourcing.domain.services.aes_cipher import AESCipher
from eventsourcing.infrastructure.sqlalchemy.activerecords import IntegerSequencedItemRecord, SnapshotRecord
from eventsourcing.infrastructure.sqlalchemy.datastore import SQLAlchemyDatastore, SQLAlchemySettings

BASEDIR = os.path.dirname(os.path.abspath(__file__))
DB_HOST = os.getenv('DB_HOST', f'sqlite:///{BASEDIR}/event.db')
AES_KEY = os.getenv('AES_KEY', '0123456789abcdef')
cipher = AESCipher(AES_KEY)

_event_datastore = None


def init_database(**kwargs):
    global _event_datastore
    if kwargs['uri'] is None:
        kwargs.pop('uri')
        uri = f'sqlite:///{BASEDIR}/event.db'
    else:
        uri = kwargs.pop('uri')
    if _event_datastore is not None:
        raise AssertionError("init_database() has already been called.")
    _event_datastore = SQLAlchemyDatastore(
        settings=SQLAlchemySettings(uri=uri),
        tables=(IntegerSequencedItemRecord, SnapshotRecord,),
        **kwargs
    )
    return _event_datastore


def get_database():
    global _event_datastore
    if _event_datastore is None:
        raise AssertionError("init_database() needs to be called first.")
    assert isinstance(_event_datastore, SQLAlchemyDatastore)
    return _event_datastore
