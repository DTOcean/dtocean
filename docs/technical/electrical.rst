.. _tech_electric:

Electrical Sub-Systems
----------------------

Requirements
^^^^^^^^^^^^

User Requirements
'''''''''''''''''

The purpose of the Electrical Sub-Systems module is to identify and compare
technically feasible offshore electrical network configurations for a given
device, site and array layout. The scope covers all electrical sub-systems from
the OEC array coupling up to the onshore landing point, including: the
umbilical cable, static subsea intra-array cables, electrical connectors,
offshore collection points and the transmission cables to the onshore grid.

Ultimately, the network design process is defined by the following factors:

* The transmission voltage, capacity and number of transmission cables;
* The number, location and type of offshore collection points;
* The intra-array network topology, i.e. number of OEC devices per string,
  number of strings, voltage level, and umbilical geometry (for floating
  devices);
* Optimal cable routing and protection for the transmission system and
  intra-array cable networks.

These design criteria must be constrained by the physical environment, power
flow constraints and available components. Once the solutions have been
produced, a local best solution should be obtained by calculating and comparing
the overall network efficiency (i.e. network losses) and component costs. The
DTOcean tool remit does not consider the capital cost of onshore electrical
infrastructure, but, if so desired, the user can enter a cost of these
subsystems to be included when assessing the system LCOE.

Software Design Requirements
''''''''''''''''''''''''''''

An offshore electrical network can be represented by a number of connected
subsystems, shown in :numref:`fig-elec-network-tech`.

.. _fig-elec-network-tech:

.. figure:: /images/technical/elec_network.png

   Simplified generic offshore electrical network for OEC arrays

Network design will typically proceed from onshore to the offshore array,
although some iteration between possible designs can be expected. Following
this approach allows the design process to be broken down and requirements
clearly defined:

* Seabed processing for cable routes
* Selection of suitable transmission and array voltages
* Design of feasible intra-array networks
* Power flow analysis of networks

The flow chart in :numref:`fig-elec-model-tech` , based on [IET], summarises the
design process.

.. _fig-elec-model-tech:

.. figure:: /images/technical/elec_model.png

   Electrical Sub-Systems model top level view.

Architecture
^^^^^^^^^^^^

The structure of the Electrical Sub-Systems module reflects the modular design
approach. Seabed processing is performed prior to any electrical design in
order prepare design areas. The network design stage is separated into two,
with specific design processes defined for radial and star network topologies.
The design work flow is unified again when preparing networks for power flow
and analysis. 

An overview of the structure of the Electrical Sub-Systems module is presented
in :numref:`fig-electrical-uml`.

.. _fig-electrical-uml:

.. figure:: /images/technical/electrical_uml_large.png

   UML diagram of the Electrical Sub-Systems model.

The python package is structured accordingly::

   dtocean_electrical/
   |-- dtocean_electrical/
   |
   |  |-- __init__.py
   |  |-- main.py
   |  |-- inputs.py
   |  | 
   |  |-- grid/
   |  |  |-- __init__.py
   |  |  |-- grid.py
   |  |  |-- grid_processing.py
   |  |
   |  |-- network/
   |  |  |-- __init__.py
   |  |  |-- cable.py
   |  |  |-- collection_point.py
   |  |  |-- connector.py
   |  |  |-- network.py
   |  |
   |  |-- optim_codes/
   |  |  |--_ _init__.py
   |  |  |-- array_layout.py
   |  |  |-- optimiser.py
   |  |  |-- power_flow.py
   |  |  |-- umbilical.py
   |
   |-- setup.py
   |-- README


Overview
''''''''

**Electrical**:
The Electrical class is composed of six input classes:
ElectricalComponentDatabase, ElectricalMachineData, ElectricalArrayData,
ConfigurationOptions, ElectricalSiteData, ElectricalExportData. The input
classes contain all data and data processes required to create and run an
instance of the Electrical class. Upon initialisation the Electrical class
will run a number of input data checks (contained in input_tests) and also
align the device layout and landing point with the x-y grid.

The Electrical class also initialises the Grid class and the GridPoint class
via the grid_processing utility class. Once the data has been prepared and
checked, the Electrical class creates and executes an instance of the
Optimiser class.

**ElectricalComponentDatabase**: This is a structured data container for the
electrical component database. This consists of eight individual component
tables for the main electrical components of an offshore network: static
cables, dynamic cables, wet-mate connectors, dry-mate connectors, collection
points, switchgear, transformers and power quality equipment. Each component
table is stored as a pandas DataFrame object. Details of the individual fields
are included in APPENDIX.

**ElectricalSiteData**: Define the electrical systems site data object. This
includes all geotechnical and geophysical data.

**ElectricalExportData**: Define the electrical systems export data object. This
includes all geotechnical and geophysical data.

**ElectricalMachineData**: Container class to carry the OEC device object.

**ElectricalArrayData**: Container class to carry the array object. The
ElectricalMachineData object is included within this class.

**ConfigurationOptions**: Container class for the configuration options.

**Grid**: Data structure for the grid. This is composed of a number of GridPoint
objects. While a GridPoint object contains only local information, a Grid
object contains more useful information of the area as a complete entity.
Special methods allow for creating specific design areas by removing
constraints and filtering the seabed based on installation equipment
functionality.

**GridPoint**: Data structure for grid point data. A GridPoint is created to
carry the information of every x-y coordinate in the lease area and the cable
corridor. For each point, neighbours are defined in either four or eight
directions, with four taken by default. Spatial distances and gradients for all
neighbours are calculated in order to create a series of edges and vertices for
graph analysis.

**grid_processing**: This is utility class controls the data flow and
manipulation required to convert the input geophysical and geotechnical data
into the coherent dataset required by the cable routing algorithms. The
processes in grid_processing are divided into three main tasks: collecting all
exclusion zones, merging the lease area and cable corridor bathymetry data and
creating a NetworkX graph object for cable routing analysis. The GridPoint and
Grid objects are also created during this final stage, and the graph object is
assigned to an attribute of the Grid class.

**Optimiser**: Controller class to define search space and find the network
solution. This takes configuration options as constraints and searches within a
predefined search space for a best solution. The search space is realised as
look-up table developed with respect to the maximum power transfer of an
electrical system a function of voltage and distance. These static values are
compared against the spatial characteristics of the array to be designed in
order to construct technically feasible voltage levels for the network. More
than one voltage level is proposed for each section of the network to produce
variation in the solutions. This process is controlled by the
set_design_limits() method.

This class also extracts data from the ElectricalComponentDatabase object and
creates a number of component sets for analysis. This is realised in the
Optimiser class by creating and executing instances of the PyPower class. The
final role of the Optimiser class is to create Network objects to analyse and
store detailed information of the designed networks.

**RadialNetwork**: Special instance of the Optimiser class. This contains
methods which handle the connection of devices within the array to produce a
radial network. Most of this work is outsourced to the array_layout utility
class. In the radial network, a maximum of two voltage levels are considered,
with a shared voltage level between the devices and the array systems.

**StarNetwork**: Special instance of the Optimiser class. This contains methods
which handle the connection of devices to a number of offshore collection
points to produce a star network. The devices are clustered and connected to a
local collection point before . Methods to set voltage levels and component
values are inherited from the Optimiser class. In the StarNetwork, a maximum of
three voltage levels are considered, i.e. the export, array and device systems
can have a different voltage.

**UmbilicalDesign**: This class acts as an interface to the Umbilical object,
which must be instantiated prior to execution. The umbilical seabed connection
point is defined by terminating a projected static cable route at a given
distance (1.5 x sea depth) from the device. This termination point is used to
reduce the distance paths of the static cable between the umbilical seabed
connection and the downstream component in the update_static_cables() method of
the Optimiser class.

**array_layout**: The array_layout utility class provides a series of functions
to connect a number of objects to a single target point and is based on the
hop-indexed integer programming method described in [Bauer]. This applies
vehicle routing approaches to provide the shortest distance travelled, i.e.
cable distance, while avoid path crossing. Although cable crossing may be
acceptable it has inherent impacts on installation and reliability, as well as
on heat characteristics during operation.

This set of functions is realised in two environments: one which utilises the
gridded nature of the seabed bathymetry provided by the input data to place the
cables along the seabed and one which operates in an empty space using only the
Euclidean distance between the points represented by the devices. To retain the
best representation of the real world considerations of this stage of the
design process the cable routing algorithms default to using the gridded seabed
bathymetry. All routing functionalities are implemented using Dijkstra’s
algorithm, a widely applied shortest path routine, which is available from the
NetworkX library.

**PyPower**: RadialNetwork and StarNetwork have their own methods, denoted
convert_to_pypower(), for converting the network configuration into a unified
format for converting into PyPower data structures. This is achieved using a
collection of Boolean matrices, representing connections between the onshore
landing point, the collection point(s) and device(s). Four matrices define
these connections:

* shore_to_device;
* shore_to_cp;
* cp_to_cp;
* device_to_device.

The dimensions are set by the number of devices and collections in network.

The PyPower object is instantiated by the create_pypower_object() method of the
Optimiser class. The distance matrices also produced in RadialNetwork and
StarNetwork are combined with the Boolean matrices by the PyPower object to
produce an impedance matrix and then simulated by a steady-state three-phase ac
power flow solver. Access to a full three-phase power flow solver allows for
accurate analysis of the electrical performance of the network.

Further details of the PyPower methods and data structures is available at:
http://www.pserc.cornell.edu/matpower/MATPOWER-manual.pdf

**ComponentLoading**: Utilises the power flow results to assess component
loading. Current flow values are calculated from the power flow results as they
are not directly available.

**Network**: Data structure for the network description. This is composed of a
number of network component objects and contains all data required to describe
the network structure and performance. It is created by the Optimiser class
object and its main role is to store and process the network data into both
human readable form and the data structures required for further analysis
within the DTOCEAN tool.

**Cable**: Class to define all attributes of a cable object. StaticCable and
UmbilicalCable are defined as subclasses; ArrayCable and ExportCable are
instances of StaticCable.

**CollectionPoint**: Class to define all properties of the offshore collection
point. This assumes that switchgear and transformers are included as part of
the input data. PassiveHub and Substation are subclasses.

**Connector**: Class to define all properties of connectors. WetMateConnector
and DryMateConnector are subclasses.

Input data
''''''''''

The inputs are listed in :numref:`tab-wp3-technical-inputs`.

.. _tab-wp3-technical-inputs:

.. figure:: /images/technical/wp3_technical_inputs.png

   Inputs


Some users options available to constrain the solution are shown in
:numref:`tab-wp3-technical-options`. In this table, the name of the
ConfigurationOptions attribute is also included for completeness.


.. _tab-wp3-technical-options:

.. figure:: /images/technical/wp3_technical_options.png

   Options

Execution
'''''''''

The sequence of commands to run the Electrical Sub-Systems moduleis as follows:

   >>> electrical_instance = Electrical(site, array, export, options,
   database) >>> solution = electrical_instance.run_module(plot = True)

The inputs to Electrical are the classes described in the previous section. The
solution returned is an instance of the Network class, which corresponds to the
best obtained network.

A basic plot of cable routes and collection point locations is available for
display when running outwith the DTOCEAN tool. The visibility of this is
controlled by the plot argument of run_module() method.

As part of the global optimisation process, it is necessary to pass control of a
number of design variables to the core. This workflow is handled within the
core and, if necessary, will constrain certain electrical options in response
to the outputs of other modules and overall assessment of array performance
(with respect to economic, reliability and environmental thematic indices).

The parameters of influence in the Electrical Sub-Systems module are defined in
Table 6.8. In normal execution, these variables form part of the Electrical
Sub-Systems module output and should be not constrained; however, they must be
defined at the module interface for use in the global optimisation process.
Accordingly, these are considered optional, with default None values, and the
Electrical Sub-Systems module is designed to check the status and value of
these parameters at initiation. It should be noted that this parameter list is
not finalised and is subject to further research, both at a local and global
optimisation level.

Other parameters which may have an influence on the electrical network, e.g. OEC
rated voltage, are already defined as project specific variables. As such,
modifying these parameters is considered only as part of the process of
creating a new project.

Output data
'''''''''''

As the solution returned by the Electical Sub-Systems modules is an instance of
the Network class, specific results can be accessed using the Network object
attributes. A printed summary is available by using the print_result() method::

	>>> solution.print_result()

The values included in this display are:

* Annual Yield: The annual yield at the onshore landing point;
* Bill of materials: A summary of the economic data;
* Component Data: A table which includes x and y coordinates of all components
  and quantity/length values. A database reference is included to allow the
  user to access additional information. The marker can be used in combination
  with the Hierarchy and Network design data structures to locate the component
  within the network layout;
* Hierarchy: A dictionary structure representing the connections between the
  different sub-systems. Nested lists are used to denote series and parallel
  combinations of components/sub-systems: components at the same level are in
  series with each other and in parallel with components at other levels. The
  in this structure are the database keys from the Component Data table. This
  should be read from the array level down;
* Network design: Similar to Hierarchy data structure but using component
  markers to allow identification of specific components;
* Cable routes: A summary table of the cable routes;
* Collection points: A summary table of the collection point data;
* Umbilical cables: A summary table of the umbilical cable designs.

A high level overview of the output data is included in
:numref:`tab-wp3-technical-outputs`, which matches the parameter from the output
display with the Network class attribute.


.. _tab-wp3-technical-outputs:

.. figure:: /images/technical/wp3_technical_outputs.png

   Outputs

Tables of Database Fields
^^^^^^^^^^^^^^^^^^^^^^^^^

Electrical component description tables

.. figure:: /images/technical/elec1.png

   Static and dynamic cable component database fields.

.. figure:: /images/technical/elec2.png

   Wet and dry-mate connector component database fields.

.. figure:: /images/technical/elec3.png

   Transformer component database fields.

.. figure:: /images/technical/elec4.png

   Collection point component database fields.

.. figure:: /images/technical/elec5.png

   Switchgear component database fields.

.. figure:: /images/technical/elec6.png

   Power quality equipment component database fields.



*References*

 * R. Alcorn and D. O’Sullivan, Electrical Design for Ocean Wave and Tidal
   Energy Systems, vol. 1, London: IET, 2013.

 * J. Bauer, J. Lysgaard, "The offshore wind farm array cable layout
   problem: a planar open vehicle routing problem," J Oper Res Soc (2015) 66: 360