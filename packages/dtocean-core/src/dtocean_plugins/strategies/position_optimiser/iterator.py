# -*- coding: utf-8 -*-

#    Copyright (C) 2021-2024 Mathew Topper
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
.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

import argparse
import os

import numpy as np
import yaml

from dtocean_core.core import Core
from dtocean_core.extensions import StrategyManager
from dtocean_core.menu import ModuleMenu
from dtocean_core.pipeline import Tree

from .positioner import ParaPositioner

try:
    import dtocean_hydro  # type: ignore # pylint: disable=unused-import  # noqa: F401
except ImportError:
    err_msg = (
        "The DTOcean hydrodynamics module must be installed in order "
        "to use this module"
    )
    raise ImportError(err_msg)


def main(
    core,
    prj_file_path,
    grid_orientation,
    delta_row,
    delta_col,
    n_nodes,
    t1,
    t2,
    dev_per_string=None,
    n_evals=None,
    raise_exc=False,
    save_project=False,
    write_results=True,
):
    grid_orientation = float(grid_orientation)
    delta_row = float(delta_row)
    delta_col = float(delta_col)
    n_nodes = int(float(n_nodes))
    t1 = float(t1)
    t2 = float(t2)

    params_dict = {
        "theta": grid_orientation,
        "dr": delta_row,
        "dc": delta_col,
        "n_nodes": n_nodes,
        "t1": t1,
        "t2": t2,
    }

    if dev_per_string is not None:
        dev_per_string = int(float(dev_per_string))
        params_dict["dev_per_string"] = dev_per_string

    if n_evals is not None:
        n_evals = int(float(n_evals))
        params_dict["n_evals"] = n_evals

    e = None
    project = None

    try:
        project = core.load_project(prj_file_path)

        positioner = get_positioner(core, project)

        iterate(
            core,
            project,
            positioner,
            grid_orientation,
            delta_row,
            delta_col,
            n_nodes,
            t1,
            t2,
            dev_per_string,
            n_evals,
        )

        flag = "Success"

    except Exception as e:  # pylint: disable=broad-except
        flag = "Exception"

        if raise_exc:
            raise e

    if save_project and project is not None:
        core.dump_project(project, prj_file_path)

    if not write_results:
        return

    prj_base_path, _ = os.path.splitext(prj_file_path)

    write_result_file(core, project, prj_base_path, params_dict, flag, e)


def iterate(
    core,
    project,
    positioner,
    grid_orientation,
    delta_row,
    delta_col,
    n_nodes,
    t1,
    t2,
    dev_per_string=None,
    n_evals=None,
):
    prepare(
        core,
        project,
        positioner,
        grid_orientation,
        delta_row,
        delta_col,
        n_nodes,
        t1,
        t2,
        dev_per_string,
        n_evals,
    )

    basic_strategy = _get_basic_strategy()
    basic_strategy.execute(core, project)


def prepare(
    core,
    project,
    positioner,
    grid_orientation,
    delta_row,
    delta_col,
    n_nodes,
    t1,
    t2,
    dev_per_string=None,
    n_evals=None,
):
    menu = ModuleMenu()
    active_modules = menu.get_active(core, project)

    beta = 90 * np.pi / 180
    psi = 0 * np.pi / 180

    positions = positioner(
        grid_orientation, delta_row, delta_col, beta, psi, t1, t2, n_nodes
    )

    hydro_branch = _get_branch(core, project, "Hydrodynamics")
    user_array_layout = hydro_branch.get_input_variable(
        core, project, "options.user_array_layout"
    )

    assert user_array_layout is not None
    user_array_layout.set_raw_interface(core, positions)
    user_array_layout.read(core, project)

    power_rating = core.get_data_value(project, "device.power_rating")

    rated_power = hydro_branch.get_input_variable(
        core, project, "project.rated_power"
    )

    assert rated_power is not None
    rated_power.set_raw_interface(core, power_rating * n_nodes)
    rated_power.read(core, project)

    if (
        "Electrical Sub-Systems" in active_modules
        and dev_per_string is not None
    ):
        elec_branch = _get_branch(core, project, "Electrical Sub-Systems")
        devices_per_string = elec_branch.get_input_variable(
            core, project, "project.devices_per_string"
        )

        assert devices_per_string is not None
        devices_per_string.set_raw_interface(core, dev_per_string)
        devices_per_string.read(core, project)

    if "Operations and Maintenance" in active_modules and n_evals is not None:
        oandm_branch = _get_branch(core, project, "Operations and Maintenance")
        data_points = oandm_branch.get_input_variable(
            core, project, "options.maintenance_data_points"
        )

        assert data_points is not None
        data_points.set_raw_interface(core, n_evals)
        data_points.read(core, project)


def _get_branch(core, project, branch_name):
    tree = Tree()
    hydro_branch = tree.get_branch(core, project, branch_name)

    return hydro_branch


def _get_basic_strategy():
    strategy_manager = StrategyManager()
    basic_strategy = strategy_manager.get_strategy("Basic")

    return basic_strategy


def get_positioner(core, project):
    lease_boundary = core.get_data_value(project, "site.lease_boundary")
    bathymetry = core.get_data_value(project, "bathymetry.layers")
    installation_depth_max = core.get_data_value(
        project, "device.installation_depth_max"
    )
    installation_depth_min = core.get_data_value(
        project, "device.installation_depth_min"
    )

    nogo_areas = None
    boundary_padding = None
    turbine_interdistance = None

    if core.has_data(project, "farm.nogo_areas"):
        nogo_areas = core.get_data_value(project, "farm.nogo_areas")

    if core.has_data(project, "options.boundary_padding"):
        boundary_padding = core.get_data_value(
            project, "options.boundary_padding"
        )

    if core.has_data(project, "device.turbine_interdistance"):
        turbine_interdistance = core.get_data_value(
            project, "device.turbine_interdistance"
        )

    positioner = ParaPositioner(
        lease_boundary,
        bathymetry,
        min_depth=installation_depth_min,
        max_depth=installation_depth_max,
        nogo_polygons=nogo_areas,
        lease_padding=boundary_padding,
        turbine_interdistance=turbine_interdistance,
    )

    return positioner


def write_result_file(
    core,
    project,
    prj_base_path,
    params_dict,
    flag,
    e,
    control_fname="results_control.txt",
):
    yaml_path = "{}.yaml".format(prj_base_path)
    worker_dir = os.path.dirname(prj_base_path)
    control_path = os.path.join(worker_dir, control_fname)

    yaml_dict = {"params": params_dict, "status": flag}

    if flag == "Success":
        results_dict = {}

        # Get the required variables
        with open(control_path, "r") as f:
            var_strs = f.read().splitlines()

        for var_str in var_strs:
            if not core.has_data(project, var_str):
                var_value = None
            else:
                var_value = core.get_data_value(project, var_str)

            results_dict[var_str] = var_value

        yaml_dict["results"] = results_dict

    elif flag == "Exception":
        yaml_dict["error"] = str(e)

    else:
        raise RuntimeError("Unrecognised flag '{}'".format(flag))

    with open(yaml_path, "w") as stream:
        yaml.dump(yaml_dict, stream, default_flow_style=False)


def interface():
    parser = argparse.ArgumentParser()

    parser.add_argument("prj_file_path")
    parser.add_argument("grid_orientation")
    parser.add_argument("delta_row")
    parser.add_argument("delta_col")
    parser.add_argument("n_nodes")
    parser.add_argument("t1")
    parser.add_argument("t2")
    parser.add_argument("--dev_per_string", type=int)
    parser.add_argument("--n_evals", type=int)

    core = Core()
    args = parser.parse_args()

    main(
        core,
        args.prj_file_path,
        args.grid_orientation,
        args.delta_row,
        args.delta_col,
        args.n_nodes,
        args.t1,
        args.t2,
        args.dev_per_string,
        args.n_evals,
    )
