import numpy as np
import pytest

from dtocean_hydro.utils.convert.tidestats import (
    _get_bin_centers,
    _get_n_samples,
    _get_nearest_xy_idx,
    _get_range_at_interval,
    make_tide_statistics,
)


@pytest.mark.parametrize(
    "nx, ny, nt, ns",
    [
        (100, 100, 48, 6),
        #                          (20, 50, 48, 2)
    ],
)
def test_make_tide_statistics_propability(nx, ny, nt, ns):
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    t = np.linspace(0, 1, nt)

    U = 2.0 * np.random.randn(nx, ny, nt)
    V = 2.0 * np.random.randn(nx, ny, nt)
    TI = 2.0 * np.random.randn(nx, ny, nt)
    SSH = 2.0 * np.random.randn(nx, ny, nt)

    xc = x[int(nx / 2)]
    yc = y[int(ny / 2)]

    dictinput = {
        "U": U,
        "V": V,
        "TI": TI,
        "SSH": SSH,
        "t": t,
        "xc": xc,
        "yc": yc,
        "x": x,
        "y": y,
        "ns": ns,
    }

    test = make_tide_statistics(dictinput)
    ns = len(test["p"])

    assert test["U"].shape == (nx, ny, ns)
    assert np.allclose(np.sum(test["p"]), 1)


def test_make_tide_statistics_zero_V():
    nx = 50
    ny = 25
    nt = 24
    ns = 4

    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    t = np.linspace(0, 1, nt)

    U = 2.0 * np.random.randn(nx, ny, nt)
    V = np.zeros((nx, ny, nt))
    TI = 2.0 * np.random.randn(nx, ny, nt)
    SSH = 2.0 * np.random.randn(nx, ny, nt)

    xc = x[int(nx / 2)]
    yc = y[int(ny / 2)]

    dictinput = {
        "U": U,
        "V": V,
        "TI": TI,
        "SSH": SSH,
        "t": t,
        "xc": xc,
        "yc": yc,
        "x": x,
        "y": y,
        "ns": ns,
    }

    test = make_tide_statistics(dictinput)
    ns = len(test["p"])

    assert test["U"].shape == (nx, ny, ns)
    assert np.allclose(np.sum(test["p"]), 1)


def test_make_tide_statistics_zero_U():
    nx = 50
    ny = 25
    nt = 24
    ns = 4

    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    t = np.linspace(0, 1, nt)

    U = np.zeros((nx, ny, nt))
    V = 2.0 * np.random.randn(nx, ny, nt)
    TI = 2.0 * np.random.randn(nx, ny, nt)
    SSH = 2.0 * np.random.randn(nx, ny, nt)

    xc = x[int(nx / 2)]
    yc = y[int(ny / 2)]

    dictinput = {
        "U": U,
        "V": V,
        "TI": TI,
        "SSH": SSH,
        "t": t,
        "xc": xc,
        "yc": yc,
        "x": x,
        "y": y,
        "ns": ns,
    }

    test = make_tide_statistics(dictinput)
    ns = len(test["p"])

    assert test["U"].shape == (nx, ny, ns)
    assert np.allclose(np.sum(test["p"]), 1)


@pytest.mark.parametrize(
    "xc, yc, xexp, yexp",
    [(0.5001, 0.4999, 0.5, 0.5), (1.1, 1.1, 1, 1), (-0.1, -0.1, 0.0, 0.0)],
)
def test_get_nearest_xy_idx(xc, yc, xexp, yexp):
    nx = 51
    ny = 25

    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)

    test_x_idx, test_y_idx = _get_nearest_xy_idx(x, y, xc, yc)

    assert np.isclose(x[test_x_idx], xexp)
    assert np.isclose(y[test_y_idx], yexp)


@pytest.mark.parametrize(
    "interval, minexp, maxexp",
    [
        (0.1, 0, 2),
        (0.3001, -0.05035, 2.05035),
    ],
)
def test_get_range(interval, minexp, maxexp):
    nt = 24

    t = np.linspace(0, 1, nt)
    v = np.linspace(0, 2, nt)
    V = np.column_stack((v, t))

    range_min, range_max = _get_range_at_interval(V, interval)

    assert np.isclose(float(range_min), minexp)
    assert np.isclose(float(range_max), maxexp)


def test_get_n_samples():
    range_min = -2
    range_max = 10
    interval = 0.2

    n_samples = _get_n_samples(range_min, range_max, interval)

    assert n_samples == 61


def test_get_n_samples_error():
    range_min = -2
    range_max = 10
    interval = 0.7

    with pytest.raises(ValueError):
        _get_n_samples(range_min, range_max, interval)


def test_get_bin_centers():
    bins = np.array([0, 1, 2, 3, 4, 5])
    expected = np.array([0.5, 1.5, 2.5, 3.5, 4.5])
    result = _get_bin_centers(bins)

    assert np.isclose(result, expected).all()
