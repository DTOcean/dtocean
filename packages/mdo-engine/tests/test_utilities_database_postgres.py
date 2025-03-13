import pytest

from mdo_engine.utilities.database import PostgreSQL, check_host_port

port_open, _ = check_host_port("localhost", 5432)


@pytest.fixture
def postgres():
    db = PostgreSQL("psycopg")
    db.set_credentials(
        {
            "host": "localhost",
        }
    )
    db.set_echo(True)

    return db


@pytest.mark.skipif(not port_open, reason="can't connect to DB")
def test_postgresql_configure(postgres):
    postgres.configure()
    assert postgres.session is not None
