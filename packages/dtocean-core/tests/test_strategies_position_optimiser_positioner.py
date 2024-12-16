# -*- coding: utf-8 -*-

# pylint: disable=redefined-outer-name,protected-access,bad-whitespace

import numpy as np
import pytest
from shapely.affinity import translate
from shapely.geometry import Point, Polygon, box

from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import Strata
from dtocean_core.strategies.position_optimiser.positioner import (
    CompassPositioner,
    DummyPositioner,
    ParaPositioner,
    PolyCompass,
    _buffer_lease_polygon,
    _check_grid_dims,
    _get_depth_exclusion_poly,
    _get_p0_index,
    _get_para_points,
    _make_grid_nodes,
    _nearest_n_nodes,
    _parametric_point_in_polygon,
)

# Check for module
pytest.importorskip("dtocean_hydro")


@pytest.fixture
def lease_polygon():
    return Polygon([(100, 50), (900, 50), (900, 250), (100, 250)])


@pytest.fixture
def lease_polygon_tri():
    return Polygon([(100, 50), (900, 50), (500, 250)])


@pytest.fixture
def layer_depths():
    x = np.linspace(0.0, 1000.0, 101)
    y = np.linspace(0.0, 300.0, 31)
    nx = len(x)
    ny = len(y)

    X, _ = np.meshgrid(x, y)
    Z = -X * 0.1 - 1
    depths = Z.T[:, :, np.newaxis]

    sediments = np.chararray((nx, ny, 1), itemsize=20)
    sediments[:] = "rock"

    raw = {
        "values": {"depth": depths, "sediment": sediments},
        "coords": [x, y, ["layer 1"]],
    }

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "labels": ["x", "y", "layer", "depth", "sediment"],
        }
    )

    test = Strata()
    a = test.get_data(raw, meta)

    return test.get_value(a)


@pytest.fixture
def nogo_polygons():
    return (
        Polygon([(800, 0), (1000, 0), (1000, 150), (800, 150)]),
        Polygon([(800, 150), (1000, 150), (1000, 300), (800, 300)]),
    )


def test_buffer_lease_polygon(lease_polygon):
    test = _buffer_lease_polygon(lease_polygon)
    assert test == lease_polygon


def test_buffer_lease_polygon_lease_padding(lease_polygon):
    test = _buffer_lease_polygon(lease_polygon, 10)
    assert test.area == 780 * 180


def test_buffer_lease_polygon_turbine_interdistance(lease_polygon):
    test = _buffer_lease_polygon(lease_polygon, 10, 20)
    assert test.area == 760 * 160


def test_get_depth_exclusion_poly(layer_depths):
    test = _get_depth_exclusion_poly(layer_depths, max_depth=-21)

    assert test.bounds == (0.0, 0.0, 200.0, 300.0)


@pytest.mark.parametrize(
    "delta_row, delta_col, beta, psi, expected",
    [
        (-1, 1, 0, 0, "'delta_row' must be greater"),
        (1, -1, 0, 0, "'delta_col' must be greater"),
        (1, 1, -1, 0, "in the range (0, pi)"),
        (1, 1, 2 * np.pi, 0, "in the range (0, pi)"),
        (1, 1, 0.5 * np.pi, -1 * np.pi, "in the range (-pi / 2, pi / 2)"),
        (1, 1, 0.5 * np.pi, np.pi, "in the range (-pi / 2, pi / 2)"),
    ],
)
def test_check_grid_dims(delta_row, delta_col, beta, psi, expected):
    with pytest.raises(ValueError) as excinfo:
        _check_grid_dims(delta_row, delta_col, beta, psi)

    assert expected in str(excinfo)


def test_make_grid_nodes():
    minx = miny = 0
    maxx = 20
    maxy = 10

    bounding_box = box(minx, miny, maxx, maxy)

    beta = 90 * np.pi / 180
    psi = 0 * np.pi / 180

    coords = _make_grid_nodes(bounding_box, 0, 1, 2, beta, psi)

    centre = np.array([0, 0])
    ranges = np.ptp(coords, axis=0)
    vector = (1, 0)
    point = coords[0, :] + (1, 0)

    centroid = list(bounding_box.centroid.coords)[0]
    centre_box = translate(bounding_box, -centroid[0], -centroid[1])

    n_point = 0

    for xy in coords:
        point = Point(xy)
        if centre_box.intersects(point):
            n_point += 1

    density = float(n_point) / 132

    assert (coords == centre).all(axis=1).any()
    assert ranges[0] > (maxx - minx)
    assert ranges[1] > (maxy - miny)
    assert np.isclose(coords[1, :] - coords[0, :], vector).all()
    assert (coords == point).all(axis=1).any()
    assert density > 0.75


def test_make_grid_nodes_rotate():
    minx = miny = 0
    maxx = 20
    maxy = 10

    bounding_box = box(minx, miny, maxx, maxy)

    beta = 90 * np.pi / 180
    psi = 0 * np.pi / 180

    coords = _make_grid_nodes(bounding_box, np.pi / 4, 1, 2, beta, psi)

    centre = np.array([0, 0])
    ranges = np.ptp(coords, axis=0)
    vector = (1 / np.sqrt(2), 1 / np.sqrt(2))
    point = coords[47, :] + (2 * np.sqrt(2), 0)

    centroid = list(bounding_box.centroid.coords)[0]
    centre_box = translate(bounding_box, -centroid[0], -centroid[1])

    n_point = 0

    for xy in coords:
        point = Point(xy)
        if centre_box.intersects(point):
            n_point += 1

    density = float(n_point) / 132

    assert (coords == centre).all(axis=1).any()
    assert ranges[0] > (maxx - minx)
    assert ranges[1] > (maxy - miny)
    assert np.isclose(coords[1, :] - coords[0, :], vector).all()
    assert np.isclose(coords, point).all(axis=1).any()
    assert density > 0.75


def test_make_grid_nodes_skew():
    minx = miny = 0
    maxx = 20
    maxy = 10

    bounding_box = box(minx, miny, maxx, maxy)

    beta = 45 * np.pi / 180
    psi = 0 * np.pi / 180

    coords = _make_grid_nodes(bounding_box, 0, 1, 2, beta, psi)

    centre = np.array([0, 0])
    ranges = np.ptp(coords, axis=0)
    vector = (2 / np.sqrt(2), 2 / np.sqrt(2))
    point = coords[0, :] + (1, 0)

    centroid = list(bounding_box.centroid.coords)[0]
    centre_box = translate(bounding_box, -centroid[0], -centroid[1])

    n_point = 0

    for xy in coords:
        point = Point(xy)
        if centre_box.intersects(point):
            n_point += 1

    density = float(n_point) / 132

    assert (coords == centre).all(axis=1).any()
    assert ranges[0] > (maxx - minx)
    assert ranges[1] > (maxy - miny)
    assert np.isclose(coords[91, :] - coords[0, :], vector).all()
    assert (coords == point).all(axis=1).any()
    assert density > 0.75


def test_DummyPositioner_valid_poly(lease_polygon, layer_depths):
    test = DummyPositioner(
        lease_polygon, layer_depths, max_depth=-21, lease_padding=10
    )

    assert test._valid_poly.bounds == (210.0, 60.0, 890.0, 240.0)


def test_DummyPositioner_valid_poly_nogo(
    lease_polygon, layer_depths, nogo_polygons
):
    test = DummyPositioner(
        lease_polygon,
        layer_depths,
        max_depth=-21,
        nogo_polygons=nogo_polygons,
        lease_padding=10,
    )

    assert test._valid_poly.bounds == (210.0, 60.0, 790.0, 240.0)


def test_DummyPositioner(lease_polygon, layer_depths):
    test = DummyPositioner(lease_polygon, layer_depths, max_depth=-21)

    grid_orientation = np.pi / 2
    delta_row = 20
    delta_col = 10
    beta = 90 * np.pi / 180
    psi = 0 * np.pi / 180

    pre_coords = _make_grid_nodes(
        test._bounding_box, grid_orientation, delta_row, delta_col, beta, psi
    )

    coords = test(grid_orientation, delta_row, delta_col, beta, psi)

    centroid = list(test._bounding_box.centroid.coords)[0]

    assert coords.shape[0] < pre_coords.shape[0]
    assert 0.75 < float(coords.shape[0]) / 781 < 1
    assert (coords == centroid).all(axis=1).any()


def test_get_p0_index():
    minx = miny = 0
    maxx = 200
    maxy = 100

    poly = box(minx, miny, maxx, maxy)
    coords = poly.exterior.coords
    p0_idx = _get_p0_index(coords)

    assert list(coords)[p0_idx] == (0.0, 0.0)


def test_get_p0_index_unique():
    poly = Polygon([(0, 50), (200, 50), (100, 0)])

    coords = poly.exterior.coords
    p0_idx = _get_p0_index(coords)

    assert list(coords)[p0_idx] == (100.0, 0.0)


@pytest.mark.parametrize("ccw", [True, False])
def test_get_para_points(ccw):
    minx = miny = 0
    maxx = 200
    maxy = 100

    poly = box(minx, miny, maxx, maxy, ccw=ccw)
    coords = poly.exterior.coords
    p0_idx = _get_p0_index(coords)

    p0, p1, p2 = _get_para_points(coords, p0_idx)

    assert p0 == (0.0, 0.0)
    assert p1 == (200.0, 0.0)
    assert p2 == (0.0, 100.0)


@pytest.mark.parametrize(
    "t1,  t2,  expected",
    [
        (0.5, 0.5, (100, 25)),
        (0, 0, (0, 0)),
        (1, 0, (200, 0)),
        (0.5, 1, (100, 50)),
    ],
)
def test_parametric_point_in_polygon(t1, t2, expected):
    poly = Polygon([(0, 0), (200, 0), (100, 50)])
    xy = _parametric_point_in_polygon(poly, t1, t2)

    assert np.isclose(xy, expected).all()


@pytest.mark.parametrize(
    "start_coords, number_of_nodes, expected_idxs",
    [((0, 0), 2, (0, 1)), ((100, 0), 2, (8, 9)), ((56, 0), 3, (5, 6, 7))],
)
def test_nearest_n_nodes(start_coords, number_of_nodes, expected_idxs):
    node_list = []

    for i in range(10):  # pylint: disable=undefined-variable
        node_list.append((i * 10, 0))

    nodes = np.array(node_list)
    test = _nearest_n_nodes(nodes, start_coords, number_of_nodes)

    coords = set([tuple(row) for row in test])
    expected = set([tuple(nodes[i, :]) for i in expected_idxs])

    assert coords == expected


def test_ParaPositioner(lease_polygon_tri, layer_depths):
    test = ParaPositioner(lease_polygon_tri, layer_depths)

    grid_orientation = np.pi / 2
    delta_row = 20
    delta_col = 10
    beta = 90 * np.pi / 180
    psi = 0 * np.pi / 180
    t1 = 0.5
    t2 = 0.5
    n_nodes = 9

    coords = test(
        grid_orientation, delta_row, delta_col, beta, psi, t1, t2, n_nodes
    )

    centre = (500, 150)
    distances = [np.linalg.norm(x - centre) for x in coords]

    assert max(distances) <= 10 * np.sqrt(5)
    assert (coords == centre).all(axis=1).any()
    assert coords.shape[0] == n_nodes


def test_ParaPositioner_outside(lease_polygon_tri, layer_depths):
    test = ParaPositioner(lease_polygon_tri, layer_depths)

    grid_orientation = np.pi / 2
    delta_row = 20
    delta_col = 10
    beta = 90 * np.pi / 180
    psi = 0 * np.pi / 180
    t1 = 0
    t2 = 1
    n_nodes = 9

    with pytest.raises(RuntimeError) as excinfo:
        test(grid_orientation, delta_row, delta_col, beta, psi, t1, t2, n_nodes)

    assert "lies outside of valid" in str(excinfo)


def test_ParaPositioner_insufficient_nodes(lease_polygon_tri, layer_depths):
    test = ParaPositioner(lease_polygon_tri, layer_depths)

    grid_orientation = np.pi / 2
    delta_row = 20
    delta_col = 10
    beta = 90 * np.pi / 180
    psi = 0 * np.pi / 180
    t1 = 0.5
    t2 = 0.5
    n_nodes = 2000

    with pytest.raises(RuntimeError) as excinfo:
        test(grid_orientation, delta_row, delta_col, beta, psi, t1, t2, n_nodes)

    assert "Expected number of nodes not found" in str(excinfo)


@pytest.mark.parametrize(
    "direction,   expected",
    [
        ("north", (1, 2)),
        ("east", (2, 1)),
        ("south", (1, 0)),
        ("west", (0, 1)),
        ("northeast", (2, 2)),
        ("southeast", (2, 0)),
        ("southwest", (0, 0)),
        ("northwest", (0, 2)),
        ("N", (1, 2)),
        ("E", (2, 1)),
        ("S", (1, 0)),
        ("W", (0, 1)),
        ("NE", (2, 2)),
        ("SE", (2, 0)),
        ("SW", (0, 0)),
        ("NW", (0, 2)),
    ],
)
def test_PolyCompass(direction, expected):
    polygon = box(0, 0, 2, 2)
    test = PolyCompass(polygon)

    assert test(direction) == expected


@pytest.mark.parametrize(
    "direction,   expected",
    [
        ("north", (1, 2)),
        ("east", (3, 1)),
        ("south", (1, 0)),
        ("west", (0, 1)),
        ("northeast", (2, 2)),
        ("southeast", (2, 0)),
        ("southwest", (0, 0)),
        ("northwest", (0, 2)),
        ("N", (1, 2)),
        ("E", (3, 1)),
        ("S", (1, 0)),
        ("W", (0, 1)),
        ("NE", (2, 2)),
        ("SE", (2, 0)),
        ("SW", (0, 0)),
        ("NW", (0, 2)),
    ],
)
def test_PolyCompass_off_centre(direction, expected):
    polygon = box(0, 0, 3, 2)
    test = PolyCompass(polygon, centre=(1, 1))

    assert test(direction) == expected


def test_PolyCompass_invalid_code():
    polygon = box(0, 0, 2, 2)
    test = PolyCompass(polygon)

    with pytest.raises(ValueError) as excinfo:
        test("left")

    assert "Invalid point code" in str(excinfo)


@pytest.mark.parametrize(
    "point_code,  expected",
    [
        ("C", (500, 150)),
        ("N", (500, 250)),
        ("E", (900, 150)),
        ("S", (500, 50)),
        ("W", (100, 150)),
        ("NE", (600, 250)),
        ("SE", (600, 50)),
        ("SW", (400, 50)),
        ("NW", (400, 250)),
    ],
)
def test_CompassPositioner(lease_polygon, layer_depths, point_code, expected):
    test = CompassPositioner(lease_polygon, layer_depths)

    grid_orientation = np.pi / 2
    delta_row = 20
    delta_col = 10
    beta = 90 * np.pi / 180
    psi = 0 * np.pi / 180
    n_nodes = 4

    coords = test(
        grid_orientation, delta_row, delta_col, beta, psi, point_code, n_nodes
    )

    distances = [np.linalg.norm(x - expected) for x in coords]

    assert (coords == expected).all(axis=1).any()
    assert max(distances) <= 10 * np.sqrt(5)
    assert coords.shape[0] == n_nodes


def test_CompassPositioner_insufficient_nodes(lease_polygon, layer_depths):
    test = CompassPositioner(lease_polygon, layer_depths)

    grid_orientation = np.pi / 2
    delta_row = 20
    delta_col = 10
    beta = 90 * np.pi / 180
    psi = 0 * np.pi / 180
    point_code = "C"
    n_nodes = 2000

    with pytest.raises(RuntimeError) as excinfo:
        test(
            grid_orientation,
            delta_row,
            delta_col,
            beta,
            psi,
            point_code,
            n_nodes,
        )

    assert "Expected number of nodes not found" in str(excinfo)
