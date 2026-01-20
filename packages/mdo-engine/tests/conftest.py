def pytest_addoption(parser):
    parser.addoption(
        "--postgresql-path",
        dest="postgresql_path",
        help="path to postgresql database setup files",
    )
