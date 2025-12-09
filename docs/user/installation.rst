.. _user_install:

Installation module
-------------------

Introduction
^^^^^^^^^^^^

The installation module is seeking to minimize the cost of installation of all
components/sub-systems chosen by the upstream modules. It covers the following
elements:

 * Installation of wave or tidal devices as positioned by the array
   hydrodynamics module,
 * Installation of the electrical infrastructure components as designed by
   the electrical sub-systems module,
 * Installation of the moorings & foundations as arranged by the module.

It should be noted that if the user wishes to use the installation module to
assess the installation of only a restricted part of the entire bill of
material (comprising devices, moorings & foundations and the electrical
infrastructure), then the quantity of the item to be ignored (specified by the
user through the GUI of the core module) by the installation module should be
set to “zero” by the core. This allows the user to evaluate only the
installation of the devices while disregarding the installation of the other
components, for example. However, the installation module must always have
information about the ocean energy devices to install since it will assume that
the starting time for the commissioning will be the latest ending time of all
components analysed by the installation module. To facilitate the understanding
of the remaining of the user manual for the installation module, here are two
definitions of key concepts:

 * Logistic operation: refers to a specific task carried out in-land or at
   sea, e.g the ‘vessel preparation & loading’ or the ‘transportation from port
   to site’

Logistic phase: is composed of a group of several logistic operations which
ultimately forms a marine operation during the installation or O&M stage of a
MRE project, e.g ‘installation of the export cable’ or ‘inspection or
maintenance of a top-side element on-site’.


Architecture
^^^^^^^^^^^^

The installation module comprises complementary features:

 * A pre-defined logistic phase sub-module: this is where the logistic
   operation sequences and vessels & equipment combinations are defined for all
   logistic phases.
 * An installation procedure definition sub-module: it is divided into two
   functions; one defining the scheduling rules to determine the chronological
   order of the logistic phases and another function selecting the base
   installation port.
 * An optimization routine: the most inexpensive feasible logistic solution
   (set of vessel(s), equipment(s) and port) is chosen for each logistic phase.


.. _fig-install:

.. figure:: /images/user/install.png

   High level flow chart of the installation module


As shown in :numref:`fig-install`, once the inputs are loaded (first bloc on the
left), the installation module runs the two initial sub-modules which serves to
define the logistic phases to be considered, their chronological (‘Gantt
chart’) relationships and the base installation port.  Following this
initialization, the assessment of the logistic phases is performed in three
steps:

 * STEP 1 “selection of suitable maritime infrastructure sub-module”:
   characterization of the logistic requirements relating the array physical
   parameters to the characteristics of the maritime infrastructure (ports,
   vessels and equipment). This step is followed with the matching of the
   logistic requirements previously determined with the database of vessels,
   ports and equipment purposely built-in for the DTOcean tool. To avoid
   unnecessary verification, the selection of the individual vessel(s), port
   and equipment is constrained by the pre-defined type of vessels and
   equipment. It can be noted that an advanced user has the opportunity to
   specify its own set of type of vessel(s) and equipmentby updating existing
   logistic phase definition Python file or by creating new ones that mimic the
   existing ones. 

 * STEP 2 “performance assessment of logistic phase sub-module”: this
   assessment is three fold:

   * Firstly, an estimation of the schedule of the marine operation is
     conducted. The mobilization time associated with the availability of the
     maritime infrastructure (vessels and equipment) is straightforwardly
     evaluated, based on average values in the vessel database. Similarly, the
     transportation times are readily computed through the average speed values
     along with an assessment of the distance from port to site. By combining
     the total duration of the sea logistic operations and the associated
     operational limit conditions (e.g max H_s), the expected waiting time
     associated with the logistic phase can be predicted. This is done through
     the weather window function which requires the requested starting time and
     the total sea duration of the logistic phase to return an estimate of the
     waiting time.
   * Secondly, the cost functions produce estimates of the costs incurred
     by the utilization of the maritime infrastructure. Both fixed and variable
     costs are accounted for by making use of relevant economic parameters
     available in the database of ports, vessels and equipment.
   * Thirdly, a qualitative assessment of the environmental impact
     associated with the use of the vessel and equipment returns an
     environmental score for five potential impacts, namely: the risk of
     chemical pollution, the collision risk, the footprint, the underwater
     noise and the potential raise of turbidity.

 * STEP 3 “optimization routine”: in the logistic module, the objective
   function is to find the feasible logistic solutions which minimize the total
   cost (C_lp) of a given logistic phase.

At the end of this process, the outputs of the installation module are sorted
and formatted in the a convenient way for post-processing and results
visualization purposes. The outputs include a set of optimal feasible logistic
solutions along with their schedule, cost and environmental impact assessment.

To cover the scope of the installation of a wave or tidal energy farm, a total
of nine logistic phases have been characterized, in terms of:

 * List of inputs required to run the logistic phase
 * Combinations of vessel(s) & equipment(s) types suitable to carry out the
   logistic phase 
 * Feasibility functions pertaining to the selection of individual vessel or
   equipment that satisfy some requirements such as deck space must be superior
   to the estimated footprint of one element to be installed
 * Feasibility matching to verify the compatibility between vessel(s) and
   equipment (e.g deck cargo must be superior to the estimated total mass of
   the equipment and the elements to be installed that are on deck)
 * Performance functions depicting the methods (e.g default fixed value or
   distance multiplied by transit speed) employed to estimate the time and cost
   per logistic operation.


Any array configuration that can possibly be proposed to the installation module
is currently limited to these nine logistic phases characterized.
:numref:`fig-logistic` displays the list of the nine logistic phases, split
within 3 main categories:

.. _fig-logistic:

.. figure:: /images/user/logistic.png

   Scope of the logistic phases considered for the installation module


Functional specifications
^^^^^^^^^^^^^^^^^^^^^^^^^

Inputs
''''''

The installation module takes a relatively large number of inputs. As a result,
the present user manual is only summarizing the nature and content of these
required inputs while specifying their origin (end-user entry, upstream module
or database). Details of the full list of inputs (parameter description,
variable name, unit, format and requirements) can be found in the DTOcean Technical
Manual. It should be noted that all input type listed below correspond to a
single ‘panda dataframe’ Python format when they are passed to the installation
module.

Four types of mandatory inputs originate from the end-user via the GUI:

 * “site”; bathymetry and soil type at each point of the lease area 
 * “metocean”: time-series of wave conditions (H_s and T_p), wind speed and
   current speed
 * “device”: type and main specification of the ocean energy device (e.g
   dimensions and dry mass). Also includes information about logistic matters
   such as the assembly and load-out strategies, the transportation method, the
   estimated time to connect the device at sea and the operational limit
   conditions during this operation among few others 
 * “sub_device”: dimensions, dry mass, assembly duration and location of each
   device sub-system. The device sub-systems were defined generically as
   follows: A = Main structure, B = Power-Take-Off, C = Control system and D =
   Support structure (if any)

Three pre-populated databases of mandatory inputs which can be over-written or
expanded by the user through the GUI:

 * Port database: detailed information about European ports with the
   following parameter categories: 

   * General Information (13 parameters),
   * Port Terminal Specification (17 parameters),
   * Port Cranes, Support, Accessibilities and Certifications (16 parameters),
   * Manufacturing capabilities (8 parameters),
   * Economic Assessment (8 parameters),
   * Contact details (4 parameters),

 * Vessel database: detailed information about each vessel types considered
   in DTOcean with the following parameter categories:

   * General Information (9 parameters),
   * Main Dimensions and Technical Capabilities (18 parameters),
   * Maximum Operational Working Conditions (8 parameters),
   * On-board Equipment Specifications (~34 parameters),
   * Economic Assessment (4 parameters),

 * Equipment database: detailed information about each equipment types
   considered in DTOcean with the following parameter categories (the number of
   parameters varies from one equipment type to another): 

   * Metrology (min. 4 parameters),
   * Performance (min. 2 parameters),
   * Support systems (min. 2 parameters),
   * Economic Assessment (min. 2 parameters),

Other input tables consist of default values which are assumed by the
installation module but can be over-written by the user via the GUI:

 * Average fixed duration values and OLC values of individual logistic
   operations (in the table called ‘operations_time_OLC’)
 * Vertical penetration rates in all DTOcean soil types for all piling
   equipment (in the tab ’penet’ of the table ’equipment_perf_rate’),
 * Horizontal progress rates in all DTOcean soil types for all cable
   trenching/laying equipment (in the tab ’laying’ of the table
   ’equipment_perf_rate’),
 * Other generic and diverse costing and time default value assumptions (in
   the tab ’other’ of the table ’equipment_perf_rate’),
 * Safety factors to apply on selected feasibility functions (in the table
   ‘safety_factors’),
 * Default Gantt chart rules (in the table ‘installation order’) for the
   installation planning.

Finally, there is another type of inputs which can either be generated by
upstream modules (i.e “array hydrodynamic module”, “electrical sub-systems
module” and “moorings and foundations module”) or specified by the user if the
upstream module have not been selected for the run. While the complete detailed
list of these inputs can be found in the DTOcean Technical Manual, a summary of their
content is provided below. 

The inputs expected from the array hydrodynamic module are summarized in
:numref:`fig-inst-table`. It must be noted that this input is compulsory and
must contain at least one device since the installation module must always
install minimum one device to set the commissioning time for the O&M module and
LCOE calculation. Hence, if the user has chosen NOT to select the array
hydrodynamic module for the run, it will be necessary to fill out the table
below if the installation module is expected to run. 


.. _fig-inst-table:

.. figure:: /images/user/inst_table.png

   Panda DataFrame containing all required input data generated by the array hydrodynamic module to the installation module

   
Six panda dataframe Python tables should be passed to the installation module by
the electrical sub-system module. Each table refer to a sub-system of an
electrical layout of an array of ocean energy devices. Their content can be
succinctly described as follows:

 * “collection point”: type, coordinates, dry mass, dimensions, interfaces
   description (upstream and downstream connectors type) and pigtails
   specifications
 * “dynamic cable”: coordinates, dry masses, dimensions, Minimum Bending
   Radius (MBR). Maximum Breaking Load (MBL), interfaces description (upstream
   and downstream connectors type) and buoyancy modules specifications
 * “static cable”: type, coordinates, dry masses, dimensions, MBR, MBL,
   interfaces description (upstream and downstream connectors type) and
   pigtails specifications
 * “cable route”: coordinates, soil type, bathymetry, burial depth, split
   pipe and static cable id
 * “external protection”: type and coordinates
 * “connectors”: type, dry mass, dimensions and mating/demating forces

Similarly, two panda dataframe Python tables result from the outputs generated
by the moorings and foundations module. Below is a summary description (as for
all other inputs full details description can be found in the technical manual):

 * “foundation”: corresponding device ID, type/subtype, coordinates, dry
   mass, dimensions, penetration depth, grout type and volume 
 * “line”: corresponding device ID, type, components list, coordinates, dry
   mass, length

All the tables originating from upstream module are compulsory but it is
possible to have them not populated (i.e empty, except for the table “layout”
which must contain at least one device) to signify that there is no need to
consider any array-element of one type (e.g collection point or mooring line)
for the installation module.


Outputs
'''''''

The list of the outputs from the installation module is given in
:numref:`fig-inst-out1` and :numref:`fig-inst-out2`: it consists of two
dictionaries. The first dictionary (see :numref:`fig-inst-out1`) is generated
for each logistic phase considered by the installation module (i.e there will
be between 1 and 9 of these tables depending on the array elements to be
installed). The second output (see :numref:`fig-inst-out2`) contains a summary
of the global outputs for the entire installation phase. Both outputs provide
information about estimated cost, time and dates of the various operations.
Information about the selection of feasible vessel(s), equipment and the base
installation port is also given.   

.. _fig-inst-out1:

.. figure:: /images/user/inst_out1.png

   Dictionary output generated  for each logistic phase considered by the installation module



.. _fig-inst-out2:

.. figure:: /images/user/inst_out2.png

   Global dictionary output generated by the installation module

   