import errno
import os

from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def yaml_to_py(yaml_path):
    """Return the python object interpretation of a yaml file"""

    with open(yaml_path, "r") as yaml_stream:
        try:
            pyfmt = load(yaml_stream, Loader=Loader)
        except Exception as e:
            errStr = "File {} produced error:\n{}".format(yaml_path, e)
            raise Exception(errStr)

    return pyfmt


def mkdir_p(path):
    """Create a directory structure based on path. Analagous to mkdir -p.

    Args:
      path (str): directory tree to create.

    """

    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
