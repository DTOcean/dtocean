from unittest.mock import MagicMock, call

import pytest

import dtocean_hydro.configure as configure
from dtocean_hydro.configure import (
    _URL_BASE_DATA,
    _URL_BASE_NEMOH,
    get_data,
    get_install_paths,
)


def test_get_data_linux(mocker, tmp_path):
    mocker.patch("dtocean_hydro.configure.system", return_value="linux")
    extract_tar: MagicMock = mocker.patch(
        "dtocean_hydro.configure.extract_tar",
        autospec=True,
    )
    extract_zip: MagicMock = mocker.patch(
        "dtocean_hydro.configure.extract_zip",
        autospec=True,
    )
    mocker.patch.object(configure, "_DIR_DATA", tmp_path)
    mocker.patch.object(configure, "_DIR_NEMOH", tmp_path)

    get_data()

    assert extract_tar.call_count == 2
    assert extract_zip.call_count == 0

    expected = [
        call(_URL_BASE_DATA + ".tar.gz", tmp_path),
        call(_URL_BASE_NEMOH + ".tar.gz", tmp_path),
    ]
    assert extract_tar.call_args_list == expected


def test_get_data_windows(mocker, tmp_path):
    mocker.patch("dtocean_hydro.configure.system", return_value="windows")
    extract_tar: MagicMock = mocker.patch(
        "dtocean_hydro.configure.extract_tar",
        autospec=True,
    )
    extract_zip: MagicMock = mocker.patch(
        "dtocean_hydro.configure.extract_zip",
        autospec=True,
    )
    mocker.patch.object(configure, "_DIR_DATA", tmp_path)
    mocker.patch.object(configure, "_DIR_NEMOH", tmp_path)

    get_data()

    assert extract_tar.call_count == 0
    assert extract_zip.call_count == 2

    expected = [
        call(_URL_BASE_DATA + ".zip", tmp_path),
        call(_URL_BASE_NEMOH + ".zip", tmp_path),
    ]
    assert extract_zip.call_args_list == expected


def test_get_data_skip(mocker, tmp_path):
    mocker.patch("dtocean_hydro.configure.system", return_value="linux")
    extract_tar: MagicMock = mocker.patch(
        "dtocean_hydro.configure.extract_tar",
        autospec=True,
    )
    extract_zip: MagicMock = mocker.patch(
        "dtocean_hydro.configure.extract_zip",
        autospec=True,
    )

    data_dir = tmp_path / "non-empty"
    nemoh_dir = tmp_path / "empty"
    data_dir.mkdir()
    p = data_dir / "mock.txt"
    p.write_text("Mock")

    mocker.patch.object(configure, "_DIR_DATA", data_dir)
    mocker.patch.object(configure, "_DIR_NEMOH", nemoh_dir)

    get_data()

    assert extract_tar.call_count == 1
    assert extract_zip.call_count == 0

    expected = [
        call(_URL_BASE_NEMOH + ".tar.gz", nemoh_dir),
    ]
    assert extract_tar.call_args_list == expected


def test_get_data_force(mocker, tmp_path):
    mocker.patch("dtocean_hydro.configure.system", return_value="linux")
    extract_tar: MagicMock = mocker.patch(
        "dtocean_hydro.configure.extract_tar",
        autospec=True,
    )
    extract_zip: MagicMock = mocker.patch(
        "dtocean_hydro.configure.extract_zip",
        autospec=True,
    )

    data_dir = tmp_path / "non-empty"
    nemoh_dir = tmp_path / "empty"
    data_dir.mkdir()
    p = data_dir / "mock.txt"
    p.write_text("Mock")

    mocker.patch.object(configure, "_DIR_DATA", data_dir)
    mocker.patch.object(configure, "_DIR_NEMOH", nemoh_dir)

    get_data(force=True)

    assert extract_tar.call_count == 2
    assert extract_zip.call_count == 0

    expected = [
        call(_URL_BASE_DATA + ".tar.gz", data_dir),
        call(_URL_BASE_NEMOH + ".tar.gz", nemoh_dir),
    ]
    assert extract_tar.call_args_list == expected
    assert not p.is_file()


def test_get_data_bad_arch(mocker, tmp_path):
    mocker.patch("dtocean_hydro.configure.system", return_value="bad")
    mocker.patch.object(configure, "_DIR_DATA", tmp_path)
    mocker.patch.object(configure, "_DIR_NEMOH", tmp_path)

    with pytest.raises(NotImplementedError) as excinfo:
        get_data()

    assert "Unsupported architecture" in str(excinfo.value)


@pytest.mark.parametrize(
    "system, bin_path",
    [
        ("linux", ("bin",)),
        ("windows", ("x64", "Release")),
    ],
)
def test_get_install_paths(mocker, tmp_path, system, bin_path):
    bin_path = tmp_path.joinpath(*bin_path)
    tidal_share_path = tmp_path / "share" / "dtocean_tidal"
    wec_share_path = tmp_path / "share" / "dtocean_wec"

    bin_path.mkdir(parents=True)
    tidal_share_path.mkdir(parents=True)
    wec_share_path.mkdir(parents=True)

    mocker.patch.object(configure, "_DIR_DATA", tmp_path)
    mocker.patch.object(configure, "_DIR_NEMOH", tmp_path)
    mocker.patch("dtocean_hydro.configure.system", return_value=system)

    paths = get_install_paths()

    assert set(["bin_path", "wec_share_path", "tidal_share_path"]) == set(
        paths.keys()
    )
    assert paths["bin_path"] == bin_path
    assert paths["tidal_share_path"] == tidal_share_path
    assert paths["wec_share_path"] == wec_share_path


def test_get_install_paths_missing_tidal(mocker, tmp_path):
    bin_path = tmp_path / "bin"
    wec_share_path = tmp_path / "share" / "dtocean_wec"

    bin_path.mkdir(parents=True)
    wec_share_path.mkdir(parents=True)

    mocker.patch.object(configure, "_DIR_DATA", tmp_path)
    mocker.patch.object(configure, "_DIR_NEMOH", tmp_path)
    mocker.patch("dtocean_hydro.configure.system", return_value="linux")

    with pytest.raises(RuntimeError) as excinfo:
        get_install_paths()

    assert "Tidal shared data directory does not exist." in str(excinfo.value)


def test_get_install_paths_missing_wec(mocker, tmp_path):
    bin_path = tmp_path / "bin"
    tidal_share_path = tmp_path / "share" / "dtocean_tidal"

    bin_path.mkdir(parents=True)
    tidal_share_path.mkdir(parents=True)

    mocker.patch.object(configure, "_DIR_DATA", tmp_path)
    mocker.patch.object(configure, "_DIR_NEMOH", tmp_path)
    mocker.patch("dtocean_hydro.configure.system", return_value="linux")

    with pytest.raises(RuntimeError) as excinfo:
        get_install_paths()

    assert "WEC shared data directory does not exist." in str(excinfo.value)


def test_get_install_paths_missing_bin(mocker, tmp_path):
    tidal_share_path = tmp_path / "share" / "dtocean_tidal"
    wec_share_path = tmp_path / "share" / "dtocean_wec"

    tidal_share_path.mkdir(parents=True)
    wec_share_path.mkdir(parents=True)

    mocker.patch.object(configure, "_DIR_DATA", tmp_path)
    mocker.patch.object(configure, "_DIR_NEMOH", tmp_path)
    mocker.patch("dtocean_hydro.configure.system", return_value="linux")

    with pytest.raises(RuntimeError) as excinfo:
        get_install_paths()

    assert "NEMOH executables directory does not exist." in str(excinfo.value)


def test_get_install_paths_bad_arch(mocker, tmp_path):
    tidal_share_path = tmp_path / "share" / "dtocean_tidal"
    wec_share_path = tmp_path / "share" / "dtocean_wec"

    tidal_share_path.mkdir(parents=True)
    wec_share_path.mkdir(parents=True)

    mocker.patch.object(configure, "_DIR_DATA", tmp_path)
    mocker.patch.object(configure, "_DIR_NEMOH", tmp_path)
    mocker.patch("dtocean_hydro.configure.system", return_value="bad")

    with pytest.raises(NotImplementedError) as excinfo:
        get_install_paths()

    assert "Unsupported architecture" in str(excinfo.value)
