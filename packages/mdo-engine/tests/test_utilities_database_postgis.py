import pytest

from mdo_engine.utilities.database import PostGIS


@pytest.fixture(scope="module")
def postgis():
    yield PostGIS("psycopg")


def test_postgresql_get_connection_string(postgis):
    host = "mock"
    port = 67
    pwd = "trala6741"

    new_creds = {"host": host, "port": port, "pwd": pwd}
    postgis.set_credentials(new_creds)

    test = postgis.get_connection_string()
    expected = (
        f"postgresql+psycopg://{postgis.default_user_id}:"
        f"{pwd}@{host}:{port}/{postgis.default_database}?plugin=geoalchemy2"
    )

    assert test == expected
