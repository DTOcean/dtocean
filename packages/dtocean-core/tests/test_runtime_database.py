
import pytest

from copy import deepcopy

from sqlalchemy.engine import Engine

from aneris.boundary.interface import QueryInterface
from dtocean_core.core import Core
from dtocean_core.menu import DataMenu, ProjectMenu 
from dtocean_core.pipeline import Tree
from dtocean_core.utils.database import get_database

class MuleInterface(QueryInterface):
    
    '''Test database interface.   
    '''
        
    @classmethod         
    def get_name(cls):
        
        return "Test"

    @classmethod         
    def declare_inputs(cls):
        
        input_list  =  ["test"]
                                                
        return input_list

    @classmethod        
    def declare_outputs(cls):
                
        return None
        
    @classmethod        
    def declare_optional(cls):
        
        return None
        
    @classmethod 
    def declare_id_map(self):
        
        id_map = {"result": "test"}
                  
        return id_map
        
    def connect(self):
        
        return None


# Test for a database connection
def _is_port_open(dbname):
    
    data_menu = DataMenu()
    
    return data_menu.check_database(dbname)
   
local_port_open = _is_port_open("local")

# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def core():
    '''Share a Core object'''
    
    new_core = Core()    
    
    return new_core
    
@pytest.fixture(scope="module")
def project(core):
    '''Share a Project object'''

    project_title = "Test"  
    
    project_menu = ProjectMenu()
    var_tree = Tree()
    
    new_project = project_menu.new_project(core, project_title)
    
    options_branch = var_tree.get_branch(core,
                                         new_project,
                                         "System Type Selection")
    device_type = options_branch.get_input_variable(core,
                                                    new_project,
                                                    "device.system_type")
    device_type.set_raw_interface(core, "Tidal Fixed")
    device_type.read(core, new_project)
    
    project_menu.initiate_pipeline(core, new_project)
    
    return new_project

# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def database(core, project):
    
    project = deepcopy(project) 
    data_menu = DataMenu()
    
    data_menu.select_database(project, "testing")
    database = get_database(project.get_database_credentials())
    
    return database
    
# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def localhost(core, project):

    project = deepcopy(project) 
    data_menu = DataMenu()
    
    credentials = data_menu._dbconfig["local"]
    project.set_database_credentials(credentials)
    
    database = get_database(project.get_database_credentials(), echo=True)
    
    return database


@pytest.mark.skipif(local_port_open == False,
                    reason="Can't connect to DB")
def test_connect_local(localhost):
    
    assert isinstance(localhost._engine, Engine)

#@pytest.mark.skipif(local_port_open == False,
#                    reason="Can't connect to local DB")    
#def test_polygon(localhost):
#    
#    test_interface = MuleInterface()
#
#    meta_dict = {"identifier": "test",
#                 "title": "test",
#                 "structure": "Polygon",
#                 "tables": ["polygons", "polygon"]}
#    meta = CoreMetaData(meta_dict)
#    test_interface.put_meta("test", meta)
#    test_interface.put_database(localhost)
#    
#    with pytest.warns(None) as record:
#        
#        PolygonDataColumn.auto_db(test_interface)
#        
#    polygon = PolygonDataColumn()
#    test = polygon.get_data(test_interface.data.result, None)
#    
#    assert len(record) == 0
#    assert isinstance(test, Polygon)
#    assert len(test.exterior.coords) == 4
    
#def test_stored_proceedure(database):
#    
#    result = database.call_stored_proceedure(
#                                        "beta.sp_get_farm_by_site_id",
#                                        [1]
#                                        )
#    assert len(result[0]) == 52
    
#def test_plot_bathy(test_db):
#    
#    result = test_db.call_stored_proceedure(
#                                        "public.__select_bathymetry_by_box",
#                                        [455400,0,999999,9999999]
#                                            )
#                                            
#    print result[0]
#    
#    all_lists = map(list, zip(*result))
#    xys = [ast.literal_eval(x) for x in all_lists[0]]
#    xy_lists = map(list, zip(*xys))
#    
#    xs = np.array(xy_lists[0])
#    ys = np.array(xy_lists[1])
#    zs = np.array(all_lists[1])
#    
#    print xs[0], ys[0], zs[0]
#        
#    test_bathy = PointBathymetry(xs, ys, zs, 20, 300,
#                                 proj_string=("+proj=utm +zone=29 +ellps=WGS84"
#                                              " +datum=WGS84 +units=m "
#                                              "+no_defs")
#                                )
#                                
#                            
#    # Make a UTM basemap at 9W (UTM-29)
#    m = UTMmap( llcrnrlon=-9.67, llcrnrlat=52.725,
#                urcrnrlon=-9.55, urcrnrlat=52.825,
#                resolution='f', central_meridian=-9.0)
#
#    
#    # create figure, axes instances.
#    fig = plt.figure()
#    ax1 = fig.add_axes([0.05,0.1,0.9,0.85])
#    
#    im1 = test_bathy.plot_bathy(ax1, m, cmap=cm.GMT_haxby)
# 
#    m.fillcontinents(color='#cc9966',lake_color='#afeeee', ax=ax1)
#    m.drawcoastlines(ax=ax1)
#    m.drawmapboundary(fill_color='#afeeee', ax=ax1)
#    m.drawgrid(ax=ax1)
#    plt.xticks(rotation=90)
#    
#    # add colorbar
#    cb = m.colorbar(im1, "right", size="10%", pad='5%', ax=ax1)
#    cb.set_label('Depth (m)')
#    
#    ax1.set_title('County Clare - UTM-29')
#    
#    plt.show()
    
#    assert False
