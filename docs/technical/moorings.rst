.. _tech_moorings:

Moorings and Foundations
------------------------

In this section, the requirements, architecture and functional specification of
the Moorings and Foundations module are summarized. For further information the
reader is directed towards Deliverable 4.5 (DTOcean, 2015e).

Requirements
^^^^^^^^^^^^

User Requirements
'''''''''''''''''

The main aim of the DTOcean Moorings and Foundations design module is to perform
static and quasi-static analysis to inform or develop mooring and foundation
solutions that:

 * are suitable for a given site, the OEC device (and substation), and
   expected loading conditions
 * retain the integrity of the electrical umbilical that connects the OEC
   device to the subsea cable
 * are compatible with the array layout (i.e., prevents clashing of
   neighboring devices) and subsea cable layout
 * fulfil requirements and/or constraints determined by the user and/or in
   terms of reliability and/or environ- mental concerns; and
 * possess the lowest capital cost

By default the module identifies a suitable mooring and foundation configuration
based on the supplied characteristics of the site and devices which make up the
array. However it is possible for the user to shortcut certain decisions that
would be made by the module in order to constrain the design space to a
preferred set of pre-selected parameters, such as mooring or foundation type
and foundation locations. Furthermore, whilst the database will be preloaded
with a set of mooring and foundation components it will be possible for the
user to constrain the component selection process to a desired set of
components.


Software Design Requirements
''''''''''''''''''''''''''''

The design of the moorings and foundations design module is outlined in this
section. At first, dataflow through the module will be linear, utilizing inputs
originating from:

1. the user (via the graphical user interface or GUI),

2. the Hydrodynamics and Electrical Sub-Systems modules (umbilical requirements
   and subsea infrastructure details) and

3. from the global database. As part of the global design process, all these
   inputs will be passed to the Moorings and Foundations module through the core.
   In addition the Moorings and Foundations module also interacts with the
   Umbilical module. The priority in the first instance will be to select a
   solution with the lowest capital cost and to pass this (via the core) to the
   O&M module to determine configuration reliability and LCOE (see economics
   module section below for more information). The environmental impact of the
   configuration will also be assessed (see environmental module section for more
   information), albeit externally to the module.

 
.. figure:: /images/technical/dataflow_moorings.png

   High-level dataflow to and from the Moorings and Foundations module showing constraint feedback


If the solution is not feasible in terms of its economic, reliability or
environmental impact metrics or logistical feasibility, an alternative mooring
or foundation solution will be sought by initializing a subsequent run of the
DTOcean software. Subsequent runs of the Moorings and Foundations module will
be constrained by feedback provided by the O&M module and the environmental
impact algorithms (e.g. setting a reliability constraint so that only
components with reliabilities above a certain threshold can be selected).

The Moorings and Foundations module comprises four interlinked sub-modules
including: the System and environmental loads sub-module, Substation
sub-module, Mooring sub-module and Foundation sub-module. In addition the
Mooring sub-module communicates with the Umbilical module located outside of
the Moorings and Foundations module (with communication occurring via the
core). The class of the Umbilical module is described below. The figure below
shows the general dataflow between these sub-modules. The module operates on a
device-by-device basis until all of the devices within the array have been
analyzed.


.. figure:: /images/technical/dataflow_external_moorings.png

   High-level dataflow within and external to the Moorings and Foundations module

The calculation procedure invoked within the Moorings and Foundations module
will depend on whether the system is floating or fixed. Floating systems
require a mooring system and anchors to keep the system on station. It can be
seen in the dataflow graphic that dataflow occurs between the Mooring
sub-module and Foundation sub-module to allow suitable anchors to be selected.
Fixed systems require a foundation to provide a permanent connection between
the system support structure and seafloor. Both fixed and floating systems
require an umbilical, whilst an array may require a substation. The type of
system is therefore a specific input defined by the user and hence determines
which of the sub-modules within the Moorings and Foundations module will be
used (e.g. in the case of a fixed system the mooring sub-module is redundant
and therefore not used).

Each potential design within the Moorings and Foundations module is assessed in
order to make an informed decision regarding its suitability. Several
standardized design approaches have been adopted for this, drawing from
certification guidance, recommended practices and published literature (e.g.
(Det Norske Veritas, 2010; Det Norske Veritas, 1992; Det Norske Veritas, 2013a;
Det Norske Veritas, 2013b; Bureau Veritas, 2015; Health and Safety Executive,
2001), see also :numref:`tab-documentation-moorings`). Further discussion of
limit states used in mooring and foundation design and the applicability of
existing standards can be found in Deliverable 4.5 (DTOcean, 2015e).


.. _tab-documentation-moorings:

.. figure:: /images/technical/documentation_moorings.png

   Guidance documentation used to develop the Moorings and Foundations module


The external Python libraries employed by the Moorings and Foundations module
are as follows:

* numpy
* pandas
* scipy


Architecture
^^^^^^^^^^^^

Overview
''''''''

The Moorings and Foundations module comprises two main Python modules.
MoorFound_Main.py acts as an interface between the user or core and the module
and also calls the classes within the Moorings and Foundations module.
MoorFound_Core.py comprises the classes and functions required to carry out
design and analysis of the Moorings and Foundations sub-system. As can be seen
from the following figure with MoorFound_Core.py there is interaction between
the classes within the Loads, Moor, Subst and Found classes. These processes
are summarized in the module processes table.


.. figure:: /images/technical/interaction_moorings.png

   Interaction between the various classes and functions of the Moorings and Foundations module


.. figure:: /images/technical/internal_moorings.png

   Summary of internal Moorings and Foundations module processes


Dataflow between the functions
''''''''''''''''''''''''''''''

Dataflow between the internal Moorings and Foundations functions is shown in
detail in the above figure. A discussion of the submodules within the Mooring
and Foundation module is provided in the following subsections.

All calculations performed within the Moorings and Foundations module are
associated to a Device ID number (e.g. device0001) which is utilized by all of
the modules within the software. The Main class within Moor- Found_Main.py has
a global for loop to sequentially analyze each device, starting at device0001
and ending at deviceN.


Loads class
'''''''''''

The global position of the device (from the Hydrodynamics module), site
parameters (i.e. bathymetry and tidal range), in addition to the system
properties (i.e. mass, centre of gravity and geometry) as specified by the
user, are used to determine the static loads experienced by the device and any
eccentric loading. These results are utilised by the Moor and Found classes.
For the Subst class the same static, steady and wave calculations are carried
out for the substation using information provided by the user or Electrical
Sub-Systems module.

Calculation of the design loads is carried out according to the general
methodology outlined in (Det Norske Veritas, 2013b) and (Det Norske Veritas,
2011) (Det Norske Veritas, 2011). Two simplified geometries are considered by
the Moorings and Foundations module for devices and support structures; cuboids
and vertical cylinders. If the device is a tidal turbine, the thrust
experienced by the support structure is estimated based on the prescribed
surface current, the rotor swept area, hub height and either a thrust
coefficient or the maximum value of the user-supplied thrust curve. By default,
a 1/7 power law depth distribution is used. This result contributes to the
calculation of steady loads on the system.

Static loads are calculated in the sysstat function. In the sysstead function
the specified wind and wave conditions3 in addition to current are used to
estimate the steady loads on the system. These calculations utilise drag and
inertia coefficients stored in the database4 as well as the user-specified wet
and dry frontal areas. Mean drift loads are estimated using appropriate
analytical approaches.

The next stage is the syswave function, which for floating devices is used by
the Moor class to estimate displacement of the device about the mean offset
position. The approach used to calculate wave loads on the device or structure
depends on whether diffraction is important, and this is judged by the size of
the structure in relation to the incident wave parameters and water depth at
the device location. If diffraction should be considered, hydrodynamic
parameters calculated by the Hydrodynamics module, including added mass,
radiation damping and first- order wave load RAOs are used (if available for
the translation mode being analysed. If the diffraction regime is not relevant,
wave loads on the structure are estimated using the Morison equation and the
aforementioned drag and inertia coefficients. Slow drift wave forces are also
estimated using the approach given in Chakrabarti (Chakrabarti, 2005).


Moor class
''''''''''

If the device is floating, mooring systems with anchors are considered. The user
may have a particular mooring system type in mind, perhaps from laboratory
experiments or field trials of a single device.

If the location of the anchors or a maximum footprint radius has been specified
by the user then these values are used in the definition of the mooring system
geometry. Alternatively, an anchor radius is set by the Moor class using a
relationship between the mooring line length and water depth (Fitzgerald &
Bergdahl, 2007), based on the supplied site bathymetry as well as maximum and
minimum water level values.

The moorsel function determines if a catenary or taut moored system is most
suitable for the application, based on the maximum tidal range of the site and
whether the device must remain at the same specified level in the water column
throughout all states of tide.

The moordes function first considers a mooring system comprising chain only
using the user-supplied fairlead locations. The umbilical will be included in
the analysis as an additional line. For comparative purposes chain- synthetic
rope configurations will also be considered. The selection of components which
make up each configuration will be based on connecting sizes accessed from the
database to prevent incompatible components from being selected.

The first calculation step determines the static equilibrium and pretension of
the lines without the device in place. The geometry in combination with the
static system loads calculated by the Loads class is used to determine the
equilibrium position and mooring system tensions. The moorcompret function is
used to generate an initial mooring system configuration. If the mooring line
tensions exceed any of the component minimum break loads (with a factor of
safety applied) alternative components are sought. The moorcompret function
also ensures that connecting components are compatible by only selecting
components of the same nominal size from the database.

Once static equilibrium has been achieved, the steady wind, current and mean
drift loads calculated in the Loads class are used to determine the new
equilibrium position and line tensions. A check is made to ensure that the
calculated horizontal offset (surge/sway) is within the maximum displacement
amplitude limits set by the user and compatible with the specified array
layout. Again if the configuration is unsuitable in terms of line tensions,
alternative components will be sought from the database function. Two main
calculation steps are carried out by the moordes function, corresponding to
Ultimate Limit State (ULS) and Accidental Limit State (ALS) analyses. The line
with the highest tension calculated in the ULS run is removed for ALS analysis.

The quasi-static calculations performed by mooreqav are inherently simple and do
not consider the dynamic behaviour of the mooring lines. Therefore a fully
coupled dynamic calculation is not carried out by the module. Instead the
module provides a first approximation to mooring system loads and configuration
suitability by approximating the (quasi-static) limits of motion and mooring
tensions due to a first-order wave excitation and second-order wave drift
forces. The criteria which will be used to determine the suitability of the
mooring configuration are listed in Deliverable 4.5 (DTOcean, 2015e). The Moor
class includes an iterative scheme to specify alternative mooring components if
the mooring configuration is unsuitable.


Found class
'''''''''''

If the device is fixed, foundations instead of anchors are considered. The user
may have a particular foundation type in mind in order for the foundation to be
compatible with the support structure and in this case the decision tree in the
foundsel function is not used. For a fixed system it will be necessary for the
user to specify the location of the foundation points with respect to the local
system origin and orientation.

The foundation type decision tree uses site information (i.e. bathymetry, soil
type, soil depth and layering) specified by the user as well as accessing the
database for available foundation and anchor components to determine the most
suitable range of foundation or anchor technologies. The decision tree
comprises a number of matrices to aid the selection process and exclude
unsuitable technologies (for further details see Deliverable 4.5 (DTOcean,
2015e)).

In the case of a moored device, anchor positions and maximum load vectors are
used to determine suitable anchoring systems, which are determined based on
soil type, soil depth and layering in addition to load direction (with the
latter originating from the Moor class). If shared anchoring points are deemed
to be feasible by the Moor class then this will also limit the selection of
anchor types to those which are compatible with multi-directional loads. For
fixed structures, soil type (including depth and layering) is the main deciding
factor. Soil heterogeneity across the site could result in several different
foundation or anchor solutions. For an array of devices a large selection of
foundation or anchor types will not be practical nor economically viable, and
hence the free selection will probably have to be constrained as part of the
global optimization process, particularly for large footprint, spread mooring
systems.

Within the founddes function each foundation type has its own calculation
procedure. Most approaches involve first determining the applied loads,
applying safety factors and then based on the supplied soil parameters, the
size and/or penetration depth of the foundation are adjusted iteratively to
suit the application. Basic structural (stress) analysis is only conducted for
pile foundations.


Subst class
'''''''''''

This operates in a similar way to the Found class, albeit it considers only pile
foundations (i.e. monopiles for above-water substations gravity foundations for
substations mounted directly on the seafloor). The location and features of the
substation are determined by the Electrical Sub-Systems module, with static,
steady and wave induced loads calculated within the Loads class. To avoid
repetition of code the Subst class calls the same functions used for device
analysis.


Umbilical module
''''''''''''''''

Within the external Umbilical module the umbilical geometry is defined based on
the location of the subsea cable (as specified by the Electrical Sub-Systems
module) and required umbilical properties and the bathymetry of the site
(stored within the database). The equilibrium geometry of the umbilical is
determined iteratively. Two options are available depending on whether the
device is fixed (a ‘hang-off’-type geometry from the subsea cable up to the
J-tube) (Det Norske Veritas, 2014) or floating (‘Lazy-wave’ geometry) (Ruan,
Bai, & Cheng, 2014).

The calculated geometry and umbilical constraints (minimum break load and
minimum bend radius) are used by the Moor and Found classes.


Functional Specification
^^^^^^^^^^^^^^^^^^^^^^^^

User interaction with the Moorings and Foundations module is described within
this section.


Summary of the modelling approach
'''''''''''''''''''''''''''''''''

 * By default the module operates in an optimised mode based on the
   user-supplied site and device parameters. It is possible for the user to
   manually constrain the design space by specifying certain parameters (e.g.
   the pre-selectable foundation and mooring system technology parameters:
   prefound and premoor)
 * At first, the solution with the lowest capital cost is identified and
   passed on to the other modules
 * A similar approach to mooring (floating devices) or foundation (fixed
   devices) design is used for WECs and TECs
 * Only static and quasi-static analyses are conducted by the module
 * Only catenary or taut moored configurations are modelled for floating
   systems
 * Only load cases for ULS and ALS are considered
 * With the exception of pile foundations, structural analysis of foundations
   or anchors is not carried out and instead these components are assumed to be
   rigid. The focus of the Found class is instead the interaction between the
   foundation or anchor and soil for lateral and axial load analysis
 * The user will be able to select a series of safety factors based on their
   preference and/or the requirements of the relevant certification agency
   (i.e. API, DNV, IEC etc.)
 * Within the limits of the module the identified solution will be, in
   quasi-static terms, fit-for-purpose for the application. Using the
   configuration output data, the user will then be able to carry out dynamic
   systems analysis to confirm configuration suitability using external
   third-party software

Warnings
''''''''

The moorings and foundations module will output warning messages to the user in
situations where either the tool is unable to successfully produce a solution
or where the tool is making assumptions that the user needs to be aware of.  In
the case that the tool is unable to produce a solution then the warning message
will assist the user in locating where the issue lies and which input
parameters need to be adjusted.  A list of the warning messages is included
below:

.. image:: /images/technical/warn_moor.png


Inputs
''''''

The following table gives a comprehensive list of all inputs required by the
moorings and foundations module:


.. image:: /images/technical/input_moor1.png
.. image:: /images/technical/input_moor2.png
.. image:: /images/technical/input_moor3.png
.. image:: /images/technical/input_moor4.png
.. image:: /images/technical/input_moor5.png


Outputs
'''''''

The mooring and foundation solution is details in a number of tables. To
elucidate further, the Moor, Found and Subst classes all output the following
variables:

 * Configuration hierarchy

Nested list comprising main component names for the mooring and foundation
systems. This is used by the Reliability Assessment sub-module.

 * Configuration bill of materials

Bill of materials in dictionary format comprising mooring and foundation
elements for N foundation/anchor points:

 * foundation type (str) [-],
 * foundation subtype (str) [-],
 * dimensions (list):

   * width (float) [m],
   * length (float) [m],
   * height (float) [m],
   * cost (float) [euros],
   * total weight (float) [kg],
   * quantity (int) [-]
   * grout type (str) [-],
   * grout volume (float) [m3],
   * component identification numbers (list) [-]

 * Configuration installation parameters (including key seafloor parameters
   at installation locations) in pandas table format for N foundation/anchor
   points:

   * device number (int) [-],
   * foundation number (int) [-],
   * foundation type (str) [-]’,
   * foundation subtype (str) [-],
   * x coord (float) [-],
   * y coord (float) [-],
   * length (float) [m],
   * width (float) [m],
   * height (float) [m],
   * installation depth (float) [m],
   * dry mass (float) [kg],
   * grout type [-],
   * grout volume (float) [m3]
   * cost (float) [euros],
   * total weight (float) [kg],
   * quantity (int) [-]
   * grout type (str) [-],
   * grout volume (float) [m3],
   * component identification numbers (list) [-]

 * Configuration installation parameters (including key seafloor parameters
   at installation locations) in pandas table format for N foundation/anchor
   points:

   * device number (int) [-],
   * foundation number (int) [-],
   * foundation type (str) [-]’,
   * foundation subtype (str) [-],
   * x coord (float) [-],
   * y coord (float) [-],
   * length (float) [m],
   * width (float) [m],
   * height (float) [m],
   * installation depth (float) [m],
   * dry mass (float) [kg],
   * grout type [-],
   * grout volume (float) [m3]


Calculation time
''''''''''''''''

Calculation times are dependent on the system in question. Indicative values for
one device are provided in :numref:`tab-calculation-moorings`.


.. _tab-calculation-moorings:

.. figure:: /images/technical/calculation_moorings.png

   Indicative calculation times for a single device subjected to several wave conditions
