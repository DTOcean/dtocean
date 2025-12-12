import importlib.metadata


def get_version():
    return importlib.metadata.version(__name__)
