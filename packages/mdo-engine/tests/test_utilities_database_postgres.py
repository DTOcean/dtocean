import pytest

from mdo_engine.utilities.database import PostgreSQL


@pytest.fixture(scope="module")
def postgres():
    yield PostgreSQL("psycopg")


def test_postgresql_get_credentials_defaults(postgres):
    assert postgres.get_credentials() == {
        "host": None,
        "port": 5432,
        "dbname": "postgres",
        "user": "postgres",
        "pwd": "postgres",
    }


def test_postgresql_valid_adapters(postgres):
    assert postgres.valid_adapters == ["psycopg"]


def test_postgresql_set_echo(postgres):
    postgres.set_echo(True)
    assert postgres._echo


def test_postgresql_set_timeout(postgres):
    six_seven = 67
    postgres.set_timeout(six_seven)
    assert postgres._timeout == six_seven


def test_postgresql_set_credentials(postgres):
    new_creds = {"host": "mock", "port": 67}
    postgres.set_credentials(new_creds)

    assert postgres.get_credentials() == {
        "host": "mock",
        "port": 67,
        "dbname": "postgres",
        "user": "postgres",
        "pwd": "postgres",
    }


def test_postgresql_get_connection_string(postgres):
    host = "mock"
    port = 67
    pwd = "trala6741"

    new_creds = {"host": host, "port": port, "pwd": pwd}
    postgres.set_credentials(new_creds)

    test = postgres.get_connection_string()
    expected = (
        f"postgresql+psycopg://{postgres.default_user_id}:"
        f"{pwd}@{host}:{port}/{postgres.default_database}"
    )

    assert test == expected
