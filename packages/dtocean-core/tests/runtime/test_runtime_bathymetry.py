from pathlib import Path
from typing import Any

import numpy as np
import psycopg
import psycopg.sql as sql
import pytest
import xarray as xr

from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ModuleMenu, ProjectMenu
from dtocean_core.pipeline import InputVariable, Tree
from dtocean_core.utils.database import (
    MIN_DB_VERSION,
)
from dtocean_plugins.modules.base import ModuleInterface

pytestmark = pytest.mark.skipif(
    (
        "not (config.getoption('postgresql_path') and "
        "config.getoption('postgresql_password'))"
    ),
    reason=(
        "Arguments --postgresql-path and --postgresql-password are required "
        "for database tests"
    ),
)


class MockSiteModule(ModuleInterface):
    @classmethod
    def get_name(cls):
        return "Mock Site Module"

    @classmethod
    def declare_weight(cls):
        return 999

    @classmethod
    def declare_inputs(cls):
        input_list = ["bathymetry.layers"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = None

        return output_list

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(cls):
        id_map = {"dummy1": "bathymetry.layers"}
        return id_map

    def connect(self, debug_entry=False, export_data=True):
        pass


class MockCorridorModule(ModuleInterface):
    @classmethod
    def get_name(cls):
        return "Mock Corridor Module"

    @classmethod
    def declare_weight(cls):
        return 9999

    @classmethod
    def declare_inputs(cls):
        input_list = ["corridor.layers"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = None

        return output_list

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(cls):
        id_map = {"dummy1": "corridor.layers"}
        return id_map

    def connect(self, debug_entry=False, export_data=True):
        pass


class MockTidalModule(ModuleInterface):
    @classmethod
    def get_name(cls):
        return "Mock Tidal Module"

    @classmethod
    def declare_weight(cls):
        return 99999

    @classmethod
    def declare_inputs(cls):
        input_list = ["farm.tidal_series"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = None

        return output_list

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_id_map(cls):
        id_map = {"dummy1": "farm.tidal_series"}
        return id_map

    def connect(self, debug_entry=False, export_data=True):
        pass


def _set_database_version(**kwargs: Any) -> None:
    """Prepare the database for tests."""
    db_connection: psycopg.Connection = psycopg.connect(**kwargs)
    query = sql.SQL("COMMENT ON DATABASE {} IS '{{\"version\": {}}}';").format(
        sql.Identifier(kwargs["dbname"]),
        sql.Identifier(MIN_DB_VERSION),
    )
    with db_connection.cursor() as cur:
        cur.execute(query)
        db_connection.commit()


def _load_database_tables(**kwargs: Any) -> None:
    """Prepare the database for tests."""
    db_connection: psycopg.Connection = psycopg.connect(**kwargs)
    query = sql.SQL("""SELECT public.db_from_csv(
    '/home/postgres/export',
    'reference.soil_type',
    'project.device',
    'project.site',
    'project.bathymetry',
    'project.bathymetry_layer',
    'project.cable_corridor_bathymetry',
    'project.cable_corridor_bathymetry_layer',
    'project.time_series_energy_tidal'
);""")
    with db_connection.cursor() as cur:
        cur.execute(query)
        db_connection.commit()


@pytest.fixture(scope="module")
def core():
    new_core = Core()

    socket = new_core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockSiteModule)
    socket.add_interface(MockCorridorModule)
    socket.add_interface(MockTidalModule)

    return new_core


@pytest.fixture(scope="module")
def postgresql_path(request):
    return Path(request.config.getoption("postgresql_path"))


@pytest.fixture(scope="module")
def db_config(postgresql_noproc, postgresql_path):
    from pytest_postgresql.janitor import DatabaseJanitor

    dbname = f"{postgresql_noproc.dbname}_bathymetry"
    janitor = DatabaseJanitor(
        user=postgresql_noproc.user,
        host=postgresql_noproc.host,
        port=postgresql_noproc.port,
        version=postgresql_noproc.version,
        dbname=dbname,
        password=postgresql_noproc.password,
    )
    pg_load = [
        postgresql_path / "postgresql" / "admin.sql",
        postgresql_path / "postgresql" / "schema.sql",
        _set_database_version,
        _load_database_tables,
    ]

    with janitor:
        for load_element in pg_load:
            janitor.load(load_element)

        db_config = {
            "host": postgresql_noproc.host,
            "port": postgresql_noproc.port,
            "dbname": dbname,
            "user": postgresql_noproc.user,
            "pwd": postgresql_noproc.password,
        }

        yield db_config


@pytest.fixture
def wave_project(core, db_config):
    project_menu = ProjectMenu()
    var_tree = Tree()
    data_menu = DataMenu()
    project_menu = ProjectMenu()
    var_tree = Tree()

    new_project = project_menu.new_project(core, "test wave")

    options_branch = var_tree.get_branch(
        core, new_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        core, new_project, "device.system_type"
    )

    assert device_type is not None
    device_type.set_raw_interface(core, "Wave Floating")
    device_type.read(core, new_project)

    data_menu.select_database(new_project, credentials=db_config)

    project_menu.initiate_pipeline(core, new_project)
    project_menu.initiate_options(core, new_project)

    filter_branch = var_tree.get_branch(
        core,
        new_project,
        "Database Filtering Interface",
    )
    new_var = filter_branch.get_input_variable(
        core,
        new_project,
        "device.selected_name",
    )
    assert new_var is not None

    new_var.set_raw_interface(core, "RM3")
    new_var.read(core, new_project)

    new_var = filter_branch.get_input_variable(
        core,
        new_project,
        "site.selected_name",
    )
    assert new_var is not None

    new_var.set_raw_interface(core, "Eureka, CA")
    new_var.read(core, new_project)

    project_menu.initiate_bathymetry(core, new_project)
    boundaries_branch = var_tree.get_branch(
        core,
        new_project,
        "Project Boundaries Interface",
    )
    new_var = boundaries_branch.get_input_variable(
        core,
        new_project,
        "site.lease_boundary",
    )
    assert new_var is not None

    # Reduce the lease area size
    lease_area = np.array(
        [
            [391810.0, 4522035.0],
            [393550.0, 4521100.0],
            [393730.0, 4525490.0],
            [395490.0, 4524555.0],
        ],
    )
    new_var.set_raw_interface(core, lease_area)
    new_var.read(core, new_project)

    print(boundaries_branch.get_input_status(core, new_project))

    project_menu.initiate_filter(core, new_project)

    return new_project


def test_LeaseBathyInterface(core, wave_project):
    data_menu = DataMenu()
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()
    var_tree = Tree()

    mod_name = "Mock Site Module"
    module_menu.activate(core, wave_project, mod_name)

    mod_branch = var_tree.get_branch(core, wave_project, mod_name)
    bathy = mod_branch.get_input_variable(
        core,
        wave_project,
        "bathymetry.layers",
    )
    assert isinstance(bathy, InputVariable)

    project_menu.initiate_dataflow(core, wave_project)
    data_menu.load_data(core, wave_project)
    value = bathy.get_value(core, wave_project)

    assert isinstance(value, xr.Dataset)


def test_CorridorBathyInterface(core, wave_project):
    data_menu = DataMenu()
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()
    var_tree = Tree()

    mod_name = "Mock Corridor Module"
    module_menu.activate(core, wave_project, mod_name)

    mod_branch = var_tree.get_branch(core, wave_project, mod_name)
    bathy = mod_branch.get_input_variable(
        core,
        wave_project,
        "corridor.layers",
    )
    assert isinstance(bathy, InputVariable)

    project_menu.initiate_dataflow(core, wave_project)
    data_menu.load_data(core, wave_project)
    value = bathy.get_value(core, wave_project)

    assert isinstance(value, xr.Dataset)


@pytest.fixture
def tidal_project(core, db_config):
    project_menu = ProjectMenu()
    var_tree = Tree()
    data_menu = DataMenu()
    project_menu = ProjectMenu()
    var_tree = Tree()

    new_project = project_menu.new_project(core, "test tidal")

    options_branch = var_tree.get_branch(
        core, new_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        core, new_project, "device.system_type"
    )

    assert device_type is not None
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)

    data_menu.select_database(new_project, credentials=db_config)

    project_menu.initiate_pipeline(core, new_project)
    project_menu.initiate_options(core, new_project)

    filter_branch = var_tree.get_branch(
        core,
        new_project,
        "Database Filtering Interface",
    )
    new_var = filter_branch.get_input_variable(
        core,
        new_project,
        "device.selected_name",
    )
    assert new_var is not None

    new_var.set_raw_interface(core, "RM1 Device")
    new_var.read(core, new_project)

    new_var = filter_branch.get_input_variable(
        core,
        new_project,
        "site.selected_name",
    )
    assert new_var is not None

    new_var.set_raw_interface(core, "Tacoma Narrows")
    new_var.read(core, new_project)

    project_menu.initiate_bathymetry(core, new_project)
    boundaries_branch = var_tree.get_branch(
        core,
        new_project,
        "Project Boundaries Interface",
    )
    new_var = boundaries_branch.get_input_variable(
        core,
        new_project,
        "site.lease_boundary",
    )
    assert new_var is not None

    # Reduce the lease area size
    lease_area = np.array(
        [
            [533022.323813, 5234555.75055],
            [533883.184247, 5234048.36335],
            [533422.555718, 5235254.90394],
            [534284.807795, 5234743.34186],
        ]
    )
    new_var.set_raw_interface(core, lease_area)
    new_var.read(core, new_project)

    print(boundaries_branch.get_input_status(core, new_project))

    project_menu.initiate_filter(core, new_project)

    return new_project


def test_TidalEnergyInterface(core, tidal_project):
    data_menu = DataMenu()
    module_menu = ModuleMenu()
    project_menu = ProjectMenu()
    var_tree = Tree()

    mod_name = "Mock Tidal Module"
    module_menu.activate(core, tidal_project, mod_name)

    mod_branch = var_tree.get_branch(core, tidal_project, mod_name)
    time_series = mod_branch.get_input_variable(
        core,
        tidal_project,
        "farm.tidal_series",
    )
    assert isinstance(time_series, InputVariable)

    project_menu.initiate_dataflow(core, tidal_project)
    data_menu.load_data(core, tidal_project)
    value = time_series.get_value(core, tidal_project)

    assert isinstance(value, xr.Dataset)
