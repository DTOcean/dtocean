# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Francesco Ferri
#    Copyright (C) 2017-2024 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import abc

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import nearest_points, polylabel

try:
    import dtocean_hydro.utils.bathymetry_utility as bathymetry_utility  # type:ignore
except ImportError:
    err_msg = (
        "The DTOcean hydrodynamics module must be installed in order "
        "to use this module"
    )
    raise ImportError(err_msg)


class DevicePositioner:
    __metaclass__ = abc.ABCMeta

    def __init__(
        self,
        lease_polygon,
        layer_depths,
        min_depth=None,
        max_depth=None,
        nogo_polygons=None,
        lease_padding=None,
        turbine_interdistance=None,
    ):
        if min_depth is None:
            min_depth = -1 * np.inf
        if max_depth is None:
            max_depth = 0

        self._lease_polygon = lease_polygon
        self._bounding_box = box(*lease_polygon.bounds)
        self._layer_depths = layer_depths
        self._min_depth = min_depth
        self._max_depth = max_depth
        self._valid_poly = None

        self._set_valid_polygon(
            nogo_polygons, lease_padding, turbine_interdistance
        )

        return

    def _set_valid_polygon(
        self, nogo_polygons, lease_padding, turbine_interdistance
    ):
        depth_exclude_poly = _get_depth_exclusion_poly(
            self._layer_depths,
            min_depth=self._min_depth,
            max_depth=self._max_depth,
        )

        if depth_exclude_poly is None:
            valid_poly = Polygon(self._lease_polygon)
        else:
            valid_poly = self._lease_polygon.difference(depth_exclude_poly)

        if nogo_polygons is None:
            self._valid_poly = _buffer_lease_polygon(
                valid_poly, lease_padding, turbine_interdistance
            )
            return

        for nogo_poly in nogo_polygons:
            valid_poly = valid_poly.difference(nogo_poly)

        self._valid_poly = _buffer_lease_polygon(
            valid_poly, lease_padding, turbine_interdistance
        )

        return

    def _make_grid_nodes(
        self, grid_orientation, delta_row, delta_col, beta, psi
    ):
        return _make_grid_nodes(
            self._bounding_box,
            grid_orientation,
            delta_row,
            delta_col,
            beta,
            psi,
        )

    def _get_valid_nodes(self, nodes):
        new_nodes = [
            (x, y) for x, y in nodes if Point(x, y).intersects(self._valid_poly)
        ]
        nodes_array = np.array(new_nodes)

        return nodes_array

    @abc.abstractmethod
    def _adapt_nodes(self, nodes, *args, **kwargs):
        """Method for adapting the zero centred grid"""
        return nodes

    def _select_nodes_hook(self, nodes, *args, **kwargs):  # pylint: disable=no-self-use,unused-argument
        """Hook method for selecting the final nodes"""
        return nodes

    def __call__(self, *args, **kwargs):
        (grid_orientation, delta_row, delta_col, beta, psi) = args[:5]

        _check_grid_dims(delta_row, delta_col, beta, psi)

        nodes = self._make_grid_nodes(
            grid_orientation, delta_row, delta_col, beta, psi
        )
        nodes = self._adapt_nodes(nodes, *args, **kwargs)
        nodes = self._get_valid_nodes(nodes)
        nodes = self._select_nodes_hook(nodes, *args, **kwargs)

        return nodes


def _buffer_lease_polygon(
    lease_polygon, lease_padding=None, turbine_interdistance=None
):
    if lease_padding is None and turbine_interdistance is None:
        return lease_polygon

    if lease_padding is None:
        lease_padding = 0.0
    if turbine_interdistance is None:
        turbine_interdistance = 0.0

    total_buffer = max(lease_padding, turbine_interdistance)
    lease_polygon_buffered = lease_polygon.buffer(-total_buffer)

    return lease_polygon_buffered


def _get_depth_exclusion_poly(layer_depths, min_depth=-np.inf, max_depth=0):
    bathy = _extract_bathymetry(layer_depths)
    zv = bathy.depth.values.T
    xv, yv = np.meshgrid(layer_depths["x"].values, layer_depths["y"].values)
    xyz = np.dstack([xv.flatten(), yv.flatten(), zv.flatten()])[0]
    safe_xyz = xyz[~np.isnan(xyz).any(axis=1)]

    exclude, _ = bathymetry_utility.get_unfeasible_regions(
        safe_xyz,
        [min_depth, max_depth],
    )

    return exclude


def _extract_bathymetry(layer_depths):
    return layer_depths.sel(layer="layer 1")


def _check_grid_dims(delta_row, delta_col, beta, psi):
    if delta_row <= 0:
        err_str = "Argument 'delta_row' must be greater than zero"
        raise ValueError(err_str)

    if delta_col <= 0:
        err_str = "Argument 'delta_col' must be greater than zero"
        raise ValueError(err_str)

    if not 0 < beta < np.pi:
        err_str = "Argument 'beta' must lie in the range (0, pi)"
        raise ValueError(err_str)

    if not np.pi / -2 < psi < np.pi / 2:
        err_str = "Argument 'psi' must lie in the range (-pi / 2, pi / 2)"
        raise ValueError(err_str)

    return


def _make_grid_nodes(
    bounding_box, grid_orientation, delta_row, delta_col, beta, psi
):
    # Estimate number of rows and cols using bounding box
    minx, miny, maxx, maxy = bounding_box.bounds

    xdiff = maxx - minx
    ydiff = maxy - miny
    ddiff = 2 * np.sqrt(xdiff**2 + ydiff**2)

    cos_beta = np.cos(beta)
    sin_beta = np.sin(beta)
    tan_inv_beta = abs(np.tan(np.pi / 2 - beta))
    cos_psi = np.cos(psi)
    sin_psi = np.sin(psi)
    tan_psi = abs(np.tan(psi))

    # Expand the grids to account for skew
    n_rows_beta = int(np.ceil((ddiff + ddiff * tan_inv_beta) / delta_row)) + 1
    n_cols_beta = int(np.ceil(ddiff / delta_col / sin_beta)) + 1

    n_rows_psi = int(np.ceil((ddiff + ddiff * tan_psi) / delta_row)) + 1
    n_cols_psi = int(np.ceil(ddiff / delta_col / cos_psi)) + 1

    # Ensure there is an odd number of rows and cols
    if n_rows_beta % 2 == 0:
        n_rows_beta += 1
    if n_cols_beta % 2 == 0:
        n_cols_beta += 1
    if n_rows_psi % 2 == 0:
        n_rows_psi += 1
    if n_cols_psi % 2 == 0:
        n_cols_psi += 1

    n_rows = max(n_rows_beta, n_rows_psi)
    n_cols = max(n_cols_beta, n_cols_psi)

    # Initiate the grid vertices
    j, i = np.meshgrid(np.arange(n_rows), np.arange(n_cols))

    # Centre indicies
    i = i - (n_cols - 1) / 2.0
    j = j - (n_rows - 1) / 2.0

    # Apply skew and scaling
    x = delta_col * cos_beta * i + delta_row * cos_psi * j
    y = delta_col * sin_beta * i + delta_row * sin_psi * j

    # 2D rotation matrix to apply grid orientation rotation
    rot_angle = grid_orientation

    cos_array = np.cos(rot_angle)
    sin_array = np.sin(rot_angle)

    Rz = np.array([[cos_array, -1 * sin_array], [sin_array, cos_array]])

    coord_raw = np.zeros((2, n_rows * n_cols))
    coord_raw[0, :] = x.ravel()
    coord_raw[1, :] = y.ravel()
    coords = np.dot(Rz, coord_raw).T

    return coords


class DummyPositioner(DevicePositioner):
    def _adapt_nodes(self, nodes, *args, **kwargs):
        nodes = nodes + self._bounding_box.centroid
        return nodes


class ParaPositioner(DevicePositioner):
    def __init__(
        self,
        lease_polygon,
        layer_depths,
        min_depth=None,
        max_depth=None,
        nogo_polygons=None,
        lease_padding=None,
        turbine_interdistance=None,
    ):
        super(ParaPositioner, self).__init__(
            lease_polygon,
            layer_depths,
            min_depth=min_depth,
            max_depth=max_depth,
            nogo_polygons=nogo_polygons,
            lease_padding=lease_padding,
            turbine_interdistance=turbine_interdistance,
        )

        self._start_coords = None

    def _adapt_nodes(self, nodes, *args, **kwargs):
        assert self._valid_poly is not None

        t1 = args[5]
        t2 = args[6]

        if self._valid_poly.is_empty:
            return np.array([])

        self._start_coords = _parametric_point_in_polygon(
            self._valid_poly, t1, t2
        )

        if not Point(self._start_coords).intersects(self._valid_poly):
            err_str = (
                "Start point ({}, {}) lies outside of valid " "domain"
            ).format(*self._start_coords)
            raise RuntimeError(err_str)

        nodes = nodes + self._start_coords

        return nodes

    def _select_nodes_hook(self, nodes, *args, **kwargs):
        n_nodes = args[7]

        nearest_nodes = _nearest_n_nodes(nodes, self._start_coords, n_nodes)
        actual_n_nodes = len(nearest_nodes)

        if actual_n_nodes < n_nodes:
            _raise_insufficient_nodes_error(actual_n_nodes, n_nodes)

        return nearest_nodes


def _parametric_point_in_polygon(poly, t1, t2):
    def tparam(x0, x1, x2):
        return x0 + t1 * (x1 - x0) + t2 * (x2 - x0)

    coords = poly.minimum_rotated_rectangle.exterior.coords
    p0_idx = _get_p0_index(coords)
    p0, p1, p2 = _get_para_points(coords, p0_idx)

    return (tparam(p0[0], p1[0], p2[0]), tparam(p0[1], p1[1], p2[1]))


def _get_p0_index(coords):
    # The p0 index is the coordinate with minimum y, and then minimum x
    # if more than one point has minimum y. It is assumed that coords
    # is a CoordinateSequence.

    is_min_y = np.isclose(coords.xy[1][:-1], min(coords.xy[1]), rtol=1e-10)
    min_y_indexs = np.where(is_min_y)[0]

    if len(min_y_indexs) > 1:
        min_y_xs = np.array(coords.xy[0])[min_y_indexs]
        is_min_x = np.isclose(min_y_xs, min(min_y_xs), rtol=1e-10)
        min_x_index = np.where(is_min_x)[0]
        min_y_index = min_y_indexs[min_x_index[0]]
    else:
        min_y_index = min_y_indexs[0]

    return min_y_index


def _get_para_points(coords, p0_idx):
    # Define the points at the extremes of the parametric space. p1 is
    # anti-clockwise to p0 and p2 is clockwise. It is assumed that coords
    # is an ordered CoordinateSequence with one overlapping node.

    def next_idx():
        if p0_idx == len(coords) - 2:
            return 0
        return p0_idx + 1

    def prev_idx():
        if p0_idx == 0:
            return -2
        return p0_idx - 1

    if _clockwise(coords.xy[0][:-1], coords.xy[1][:-1]):
        p1_idx = prev_idx()
        p2_idx = next_idx()
    else:
        p1_idx = next_idx()
        p2_idx = prev_idx()

    p0 = coords.xy[0][p0_idx], coords.xy[1][p0_idx]
    p1 = coords.xy[0][p1_idx], coords.xy[1][p1_idx]
    p2 = coords.xy[0][p2_idx], coords.xy[1][p2_idx]

    return p0, p1, p2


def _clockwise(x, y):
    """Use the shoelace formula to determine whether the polygon points are
    defined in a clockwise direction"""
    # https://stackoverflow.com/a/1165943/3215152
    # https://stackoverflow.com/a/19875560/3215152
    if sum(x[i] * (y[i + 1] - y[i - 1]) for i in range(-1, len(x) - 1)) < 0:  # pylint: disable=undefined-variable
        return True
    return False


class CompassPositioner(DevicePositioner):
    def __init__(
        self,
        lease_polygon,
        layer_depths,
        min_depth=None,
        max_depth=None,
        nogo_polygons=None,
        lease_padding=None,
        turbine_interdistance=None,
    ):
        super(CompassPositioner, self).__init__(
            lease_polygon,
            layer_depths,
            min_depth=min_depth,
            max_depth=max_depth,
            nogo_polygons=nogo_polygons,
            lease_padding=lease_padding,
            turbine_interdistance=turbine_interdistance,
        )

        self._start_coords = None

    def _adapt_nodes(self, nodes, *args, **kwargs):
        assert self._valid_poly is not None
        point_code = args[5]

        if point_code.lower() == "centre" or point_code == "C":
            start_point = polylabel(self._valid_poly)
        else:
            start_point_maker = PolyCompass(self._valid_poly)
            start_point = start_point_maker(point_code)

        self._start_coords = nearest_points(
            Point(start_point), self._valid_poly
        )[1].coords[:][0]

        nodes = nodes + self._start_coords

        return nodes

    def _select_nodes_hook(self, nodes, *args, **kwargs):
        n_nodes = args[6]

        nearest_nodes = _nearest_n_nodes(nodes, self._start_coords, n_nodes)
        actual_n_nodes = len(nearest_nodes)

        if actual_n_nodes < n_nodes:
            _raise_insufficient_nodes_error(actual_n_nodes, n_nodes)

        return nearest_nodes


class PolyCompass:
    def __init__(self, polygon, centre=None):
        self._polygon = polygon
        self._cx = None
        self._cy = None
        self._ns_intersections = None
        self._we_intersections = None
        self._swne_intersections = None
        self._nwse_intersections = None

        if centre is None:
            self._cx, self._cy = self._get_bbox_centroid()
        else:
            self._cx, self._cy = centre

        return

    def _get_bbox_centroid(self):
        return box(*self._polygon.bounds).centroid.coords[:][0]

    def _add_ns_intersections(self):
        assert isinstance(self._cx, float)
        ns_line_ends = [(self._cx, -9e8), (self._cx, 9e8)]
        ns_line = LineString(ns_line_ends)
        self._ns_intersections = [
            point.y for point in self._polygon.exterior.intersection(ns_line)
        ]

        return

    def _add_we_intersections(self):
        assert isinstance(self._cy, float)
        we_line_ends = [(-9e8, self._cy), (9e8, self._cy)]
        we_line = LineString(we_line_ends)
        self._we_intersections = [
            point.x for point in self._polygon.exterior.intersection(we_line)
        ]

        return

    def _add_swne_intersections(self):
        def f(x):
            return x + self._cy - self._cx

        swne_line_ends = [(-9e8, f(-9e8)), (9e8, f(9e8))]
        swne_line = LineString(swne_line_ends)
        self._swne_intersections = self._polygon.exterior.intersection(
            swne_line
        )

        return

    def _add_nwse_intersections(self):
        def f(x):
            return -x + self._cy + self._cx

        nwse_line_ends = [(-9e8, f(-9e8)), (9e8, f(9e8))]
        nwse_line = LineString(nwse_line_ends)
        self._nwse_intersections = self._polygon.exterior.intersection(
            nwse_line
        )

        return

    def _get_north(self):
        if self._ns_intersections is None:
            self._add_ns_intersections()

        assert isinstance(self._ns_intersections, list)
        return (self._cx, max(self._ns_intersections))

    def _get_east(self):
        if self._we_intersections is None:
            self._add_we_intersections()

        assert isinstance(self._we_intersections, list)
        return (max(self._we_intersections), self._cy)

    def _get_south(self):
        if self._ns_intersections is None:
            self._add_ns_intersections()

        assert isinstance(self._ns_intersections, list)
        return (self._cx, min(self._ns_intersections))

    def _get_west(self):
        if self._we_intersections is None:
            self._add_we_intersections()

        assert isinstance(self._we_intersections, list)
        return (min(self._we_intersections), self._cy)

    def _get_northeast(self):
        if self._swne_intersections is None:
            self._add_swne_intersections()

        assert isinstance(self._swne_intersections, list)
        sorted_intersections = sorted(
            self._swne_intersections, key=lambda p: p.y
        )

        return sorted_intersections[-1].coords[0]

    def _get_southeast(self):
        if self._nwse_intersections is None:
            self._add_nwse_intersections()

        assert isinstance(self._nwse_intersections, list)
        sorted_intersections = sorted(
            self._nwse_intersections, key=lambda p: p.y
        )

        return sorted_intersections[0].coords[0]

    def _get_southwest(self):
        if self._swne_intersections is None:
            self._add_swne_intersections()

        assert isinstance(self._swne_intersections, list)
        sorted_intersections = sorted(
            self._swne_intersections, key=lambda p: p.y
        )

        return sorted_intersections[0].coords[0]

    def _get_northwest(self):
        if self._nwse_intersections is None:
            self._add_nwse_intersections()

        assert isinstance(self._nwse_intersections, list)
        sorted_intersections = sorted(
            self._nwse_intersections, key=lambda p: p.y
        )

        return sorted_intersections[-1].coords[0]

    def __call__(self, point_code):
        code_map = {
            "north": "N",
            "east": "E",
            "south": "S",
            "west": "W",
            "northeast": "NE",
            "southeast": "SE",
            "southwest": "SW",
            "northwest": "NW",
        }

        call_map = {
            "N": self._get_north,
            "E": self._get_east,
            "S": self._get_south,
            "W": self._get_west,
            "NE": self._get_northeast,
            "SE": self._get_southeast,
            "SW": self._get_southwest,
            "NW": self._get_northwest,
        }

        point_code_local = point_code

        if point_code.lower() in code_map:
            point_code_local = code_map[point_code.lower()]

        if point_code_local not in code_map.values():
            err_str = "Invalid point code entered"
            raise ValueError(err_str)

        func = call_map[point_code_local]

        return func()


def _nearest_n_nodes(nodes, start_coords, number_of_nodes):
    def get_distance(xy):
        end_point = Point(xy)
        return start_point.distance(end_point)

    start_point = Point(start_coords)

    distances = np.apply_along_axis(get_distance, 1, nodes)
    order = np.argsort(distances)
    nodes_sorted = nodes[order, :]

    return nodes_sorted[: int(number_of_nodes), :]


def _raise_insufficient_nodes_error(actual, expected, Error=RuntimeError):
    err_str = (
        "Expected number of nodes not found. Expected {} but found " "{}"
    ).format(expected, actual)
    raise Error(err_str)
