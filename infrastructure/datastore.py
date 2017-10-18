import os

from eventsourcing.domain.services.aes_cipher import AESCipher
from eventsourcing.infrastructure.sqlalchemy.activerecords import IntegerSequencedItemRecord, SnapshotRecord
from eventsourcing.infrastructure.sqlalchemy.datastore import SQLAlchemyDatastore, SQLAlchemySettings

DB_HOST = os.getenv('DB_HOST', 'sqlite:///:memory:')
AES_KEY = os.getenv('AES_KEY', '0123456789abcdef')

event_datastore = SQLAlchemyDatastore(
    settings=SQLAlchemySettings(uri=DB_HOST),
    tables=(IntegerSequencedItemRecord, SnapshotRecord,)
)

cipher = AESCipher(AES_KEY)
