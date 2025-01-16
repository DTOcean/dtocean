from platform import system

import pytest

from dtocean_data import _DATA_URL_BASE, _NEMOH_URL_BASE, install


@pytest.mark.parametrize(
    "options",
    [
        ("data",),
        ("nemoh",),
        (
            "data",
            "nemoh",
        ),
    ],
)
def test_install(mocker, options):
    arch = system().lower()

    match arch:
        case "linux":
            extract = mocker.patch("dtocean_data._extract_linux")
        case "windows":
            extract = mocker.patch("dtocean_data._extract_windows")
        case _:
            pytest.skip("{} system not supported".format(arch))

    install(options)

    expected = set([_DATA_URL_BASE, _NEMOH_URL_BASE])
    test = set([call.args[0] for call in extract.call_args_list])
    assert test <= expected


def test_install_bad_option():
    with pytest.raises(ValueError) as excinfo:
        install(["bad"])
    assert "Unrecognised option" in str(excinfo.value)


def test_install_bad_arch(mocker):
    mocker.patch("dtocean_data.system", return_value="bad")
    with pytest.raises(NotImplementedError) as excinfo:
        install(["data"])
    assert "Unsupported architecture" in str(excinfo.value)
