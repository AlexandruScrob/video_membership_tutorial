import pathlib
import config

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection


settings = config.get_settings()

BASE_DIR = pathlib.Path(__file__).resolve().parent

ASTRADB_CONNECT_BUNDLE: str = BASE_DIR / "unencrypted" / "astradb_connect.zip"

ASTRADB_CLIENT_ID: str = settings.db_client_id
ASTRADB_CLIENT_SECRET: str = settings.db_client_secret


def get_session():
    cloud_config = {"secure_connect_bundle": ASTRADB_CONNECT_BUNDLE}
    auth_provider = PlainTextAuthProvider(ASTRADB_CLIENT_ID, ASTRADB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    connection.register_connection(str(session), session=session)
    connection.set_default_connection(str(session))
    return session
