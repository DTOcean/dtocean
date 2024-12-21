import os
from copy import deepcopy

import pytest
from mdo_engine.entity import Pipeline

from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ModuleMenu, ProjectMenu, ThemeMenu
from dtocean_core.pipeline import Tree
from dtocean_plugins.modules.modules import ModuleInterface
from dtocean_plugins.themes.themes import ThemeInterface

dir_path = os.path.dirname(__file__)


class MockModule(ModuleInterface):
    @classmethod
    def get_name(cls):
        return "Mock Module"

    @classmethod
    def declare_weight(cls):
        return 998

    @classmethod
    def declare_inputs(cls):
        input_list = [
            "device.turbine_performance",
            "device.cut_in_velocity",
            "device.system_type",
        ]

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
        id_map = {
            "dummy1": "device.turbine_performance",
            "dummy2": "device.cut_in_velocity",
            "dummy3": "device.system_type",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        pass


class MockTheme(ThemeInterface):
    @classmethod
    def get_name(cls):
        return "Mock Theme"

    @classmethod
    def declare_weight(cls):
        return 998

    @classmethod
    def declare_inputs(cls):
        input_list = ["project.discount_rate"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = ["project.capex_total"]

        return output_list

    @classmethod
    def declare_optional(cls):
        option_list = ["project.discount_rate"]

        return option_list

    @classmethod
    def declare_id_map(cls):
        id_map = {
            "dummy1": "project.discount_rate",
            "dummy2": "project.capex_total",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        self.data.dummy2 = 1.0


class MockTheme2(ThemeInterface):
    @classmethod
    def get_name(cls):
        return "Mock Theme 2"

    @classmethod
    def declare_weight(cls):
        return 999

    @classmethod
    def declare_inputs(cls):
        input_list = ["project.discount_rate"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        output_list = ["project.discounted_capex"]

        return output_list

    @classmethod
    def declare_optional(cls):
        option_list = ["project.discount_rate"]

        return option_list

    @classmethod
    def declare_id_map(cls):
        id_map = {
            "dummy1": "project.discount_rate",
            "dummy2": "project.discounted_capex",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        self.data.dummy2 = 2.0


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    """Share a Core object"""

    new_core = Core()

    socket = new_core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)

    socket = new_core.control._sequencer.get_socket("ThemeInterface")
    socket.add_interface(MockTheme)
    socket.add_interface(MockTheme2)

    return new_core


@pytest.fixture(scope="module")
def project(core):
    """Share a Project object"""

    project_title = "Test"

    project_menu = ProjectMenu()
    var_tree = Tree()

    new_project = project_menu.new_project(core, project_title)

    options_branch = var_tree.get_branch(
        core, new_project, "System Type Selection"
    )
    device_type = options_branch.get_input_variable(
        core, new_project, "device.system_type"
    )

    assert device_type is not None
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)

    project_menu.initiate_pipeline(core, new_project)

    return new_project


@pytest.fixture(scope="module")
def module_menu(core):
    """Share a ModuleMenu object"""

    return ModuleMenu()


@pytest.fixture(scope="module")
def theme_menu(core):
    """Share a ThemeMenu object"""

    return ThemeMenu()


def test_ProjectMenu_new_project():
    project_title = "Test"

    new_core = Core()
    new_project = new_core.new_project(project_title)

    assert new_project.title == project_title


def test_ProjectMenu_initiate_pipeline(core, project):
    project = deepcopy(project)
    simulation = project.get_simulation()
    assert isinstance(simulation._hubs["modules"], Pipeline)


def test_ModuleMenu_get_available_modules(core, project, module_menu):
    project = deepcopy(project)
    names = module_menu.get_available(core, project)

    assert "Mock Module" in names


def test_ModuleMenu_activate_module(core, project, module_menu):
    mod_name = "Mock Module"

    project = deepcopy(project)
    module_menu.activate(core, project, mod_name)
    simulation = project.get_simulation()
    pipeline = simulation.get_hub("modules")
    module = pipeline._scheduled_interface_map.popitem(last=False)[1]

    assert isinstance(module, MockModule)


def test_ModuleMenu_execute_current_nothemes(
    core,
    project,
    module_menu,
    inputs_wp2_tidal,
):
    var_tree = Tree()
    project = deepcopy(project)
    mod_name = "Mock Module"

    module_menu.activate(core, project, mod_name)
    mod_branch = var_tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core, project, inputs_wp2_tidal)

    module_menu.execute_current(core, project, execute_themes=False)

    assert True


def test_ThemeMenu_get_available_themes(core, project, theme_menu):
    project = deepcopy(project)
    names = theme_menu.get_available(core, project)

    assert "Mock Theme" in names


def test_ThemeMenu_activate_theme(core, project, theme_menu):
    mod_name = "Mock Theme"

    project = deepcopy(project)
    theme_menu.activate(core, project, mod_name)
    simulation = project.get_simulation()
    hub = simulation.get_hub("themes")
    module = hub._scheduled_interface_map["MockTheme"]

    assert isinstance(module, MockTheme)


def test_ThemeMenu_execute_all(core, project, theme_menu):
    var_tree = Tree()
    project = deepcopy(project)

    theme_menu.activate(core, project, "Mock Theme")
    theme_menu.activate(core, project, "Mock Theme 2")

    theme_menu.execute_all(core, project)

    theme_branch = var_tree.get_branch(core, project, "Mock Theme")
    var = theme_branch.get_output_variable(core, project, "project.capex_total")
    result = var.get_value(core, project)

    assert result == 1

    theme_branch = var_tree.get_branch(core, project, "Mock Theme 2")
    var = theme_branch.get_output_variable(
        core, project, "project.discounted_capex"
    )
    result = var.get_value(core, project)

    assert result == 2


def test_DataMenu_get_available_databases(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    data_menu = DataMenu()

    dbs = data_menu.get_available_databases()

    assert len(dbs) > 0


def test_DataMenu_get_database_dict(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    data_menu = DataMenu()

    dbs = data_menu.get_available_databases()
    db_id = dbs[0]

    db_dict = data_menu.get_database_dict(db_id)

    assert "host" in db_dict.keys()


def test_DataMenu_update_database(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    data_menu = DataMenu()

    dbs = data_menu.get_available_databases()
    db_id = dbs[0]

    db_dict = data_menu.get_database_dict(db_id)
    data_menu.update_database(db_id, db_dict)

    assert len(list(config_tmpdir.iterdir())) == 1


def test_DataMenu_select_database(mocker, tmp_path, project):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    # Create mock connection
    mocker.patch(
        "dtocean_core.menu.check_host_port",
        return_value=(True, "Mock connection returned"),
    )

    data_menu = DataMenu()
    project = deepcopy(project)

    assert project.get_database_credentials() is None

    dbs = data_menu.get_available_databases()
    db_id = dbs[0]
    data_menu.select_database(project, db_id)

    assert project.get_database_credentials()


def test_DataMenu_select_database_no_info(mocker, tmp_path, project):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    data_menu = DataMenu()
    project = deepcopy(project)

    with pytest.raises(ValueError):
        data_menu.select_database(project)


def test_DataMenu_select_database_bad_id(mocker, tmp_path, project):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    data_menu = DataMenu()
    project = deepcopy(project)

    with pytest.raises(ValueError):
        data_menu.select_database(project, "bad_id")


def test_DataMenu_select_database_no_port(mocker, tmp_path, project):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    data_menu = DataMenu()
    project = deepcopy(project)

    with pytest.raises(RuntimeError):
        data_menu.select_database(
            project, credentials={"dbname": "badhost", "host": "-1.-1.-1.-1"}
        )


def test_DataMenu_select_database_no_port_dbname(mocker, tmp_path, project):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    data_menu = DataMenu()
    project = deepcopy(project)

    with pytest.raises(RuntimeError):
        data_menu.select_database(project, credentials={"host": "-1.-1.-1.-1"})


def test_DataMenu_deselect_database(mocker, tmp_path, project):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    # Create mock connection
    mocker.patch(
        "dtocean_core.menu.check_host_port",
        return_value=(True, "Mock connection returned"),
    )

    data_menu = DataMenu()
    project = deepcopy(project)

    assert project.get_database_credentials() is None

    dbs = data_menu.get_available_databases()
    db_id = dbs[0]
    data_menu.select_database(project, db_id)

    assert project.get_database_credentials()

    data_menu.deselect_database(project)

    assert project.get_database_credentials() is None


def test_DataMenu_export_data(
    mocker,
    tmp_path,
    core,
    project,
    module_menu,
    inputs_wp2_tidal,
):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    data_menu = DataMenu()
    var_tree = Tree()
    project = deepcopy(project)
    mod_name = "Mock Module"

    module_menu.activate(core, project, mod_name)
    mod_branch = var_tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core, project, inputs_wp2_tidal)

    dts_path = os.path.join(str(tmp_path), "test.dts")

    data_menu.export_data(core, project, dts_path)

    assert os.path.isfile(dts_path)


def test_DataMenu_import_data(
    mocker,
    tmp_path,
    core,
    project,
    module_menu,
    inputs_wp2_tidal,
):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    data_menu = DataMenu()
    var_tree = Tree()
    project = deepcopy(project)
    mod_name = "Mock Module"

    core.register_level(project, core._markers["register"], "Mock Module")

    module_menu.activate(core, project, mod_name)
    mod_branch = var_tree.get_branch(core, project, mod_name)
    mod_branch.read_test_data(core, project, inputs_wp2_tidal)

    pre_length = len(project._pool)

    dts_path = os.path.join(str(tmp_path), "test.dts")

    data_menu.export_data(core, project, dts_path)

    assert os.path.isfile(dts_path)

    data_menu.import_data(core, project, dts_path)

    assert len(project._pool) > pre_length
