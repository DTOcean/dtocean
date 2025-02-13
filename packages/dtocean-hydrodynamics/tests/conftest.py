def pytest_addoption(parser):
    parser.addoption(
        "--no-gpu",
        action="store_true",
        help="disable tests requiring GPU support",
    )
