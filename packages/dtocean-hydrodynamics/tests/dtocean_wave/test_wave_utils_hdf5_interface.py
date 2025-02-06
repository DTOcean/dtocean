import numpy as np

from dtocean_wave.utils.hdf5_interface import (
    load_dict_from_hdf5,
    save_dict_to_hdf5,
)


def test_save_load(tmp_path):
    data = {
        "x": "astring",
        "y": np.arange(10),
        "d": {
            "z": np.ones((2, 3)),
            "b": b"bytestring",
        },
    }
    filename = tmp_path / "test.h5"
    save_dict_to_hdf5(data, filename)
    dd = load_dict_from_hdf5(filename, decode_bytes=False)

    assert dd["x"].decode() == data["x"]
    assert np.all(dd["y"] == data["y"])
    assert np.all(dd["d"]["z"] == data["d"]["z"])
    assert dd["d"]["b"] == data["d"]["b"]
