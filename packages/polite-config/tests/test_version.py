# pylint: disable=redefined-outer-name

import pytest

from polite_config.version import Version


@pytest.fixture(scope="module")
def version():
    return Version("1.2.3")


@pytest.fixture(scope="module")
def version_partial():
    return Version("1a5")


def test_version_major(version):
    assert version.major == 1


def test_version_minor(version):
    assert version.minor == 2


def test_version_micro(version):
    assert version.micro == 3


def test_version_major_partial(version_partial):
    assert version_partial.major == 1


def test_version_minor_partial(version_partial):
    assert version_partial.minor == 0


def test_version_micro_partial(version_partial):
    assert version_partial.micro == 0
