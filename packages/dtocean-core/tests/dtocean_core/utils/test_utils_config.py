from dtocean_core.utils.config import (
    init_config,
)


def test_init_config(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.config.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    init_config(logging=True, database=True)

    assert len(list(config_tmpdir.iterdir())) == 2
