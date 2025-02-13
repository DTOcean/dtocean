from dtocean_hydro import start_logging


def test_start_logging(mocker, tmp_path):
    mocker.patch("dtocean_hydro.UserDataPath", return_value=tmp_path)
    start_logging()

    files = list(tmp_path.iterdir())
    assert len(files) == 1
