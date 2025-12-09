.. _tech_installation:

Installation
------------

As any other computational module, the Installation module aims to solve a given
physical problem and return the required outputs. However, unlike the upstream
computational modules, no physical array sub-component is selected nor designed
as part of the BoM. In contrast, the Installation module provides optimal
logistic solutions by selecting feasible vessels, ports and equipment to
accomplish the installation phase. The optimal logistic solutions are those
minimising the overall cost of each logistic phase.


Requirements
^^^^^^^^^^^^

User Requirements
'''''''''''''''''

The Installation module seeks to minimise the cost of installing all
components/sub-systems chosen by the three upstream computational modules (i.e.
Hydrodynamics, the Electrical Sub-Systems and Moorings and Foundations). In
other words, the Installation module covers the following elements:

* Installation of wave or tidal devices; as positioned by the Hydrodynamics
  module
* Installation of the electrical infrastructure components; as designed by the
  Electrical Sub-Systems module
* Installation of the moorings & foundations; as designed by the Moorings and
  Foundations module

There are nine logistic phases under consideration which cover the OEC device
and the entire BoM as compiled by upstream computational modules, as listed
below:

* Installation of OEC devices
* Installation of driven pile foundations
* Installation of gravity based structures
* Installation of mooring systems
* Installation of static export power cables
* Installation of static inter-array power cables
* Installation of dynamic power cables
* Installation of offshore collection points
* Installation of cable external protection

It should be noted that if the user wishes to use the Installation module to
assess the installation of only a restricted part of the entire BoM (comprising
devices, moorings & foundations and the electrical infrastructure), then the
quantity of the item to be ignored by the Installation module should be set to
“None”. For example, this allows the user to evaluate only the installation of
the devices while disregarding the installation of the other components. In
this mode of operation, the commissioning date will be given as the moment when
all the components required to be installed, have been completed. There is no
estimation of the duration of installation phases that have not been requested
for simulation.


Software Design Requirements
''''''''''''''''''''''''''''

As for the logistic functions, details of the algorithms embedded in the
Installation module can be found in Deliverable 5.6 (DTOcean, 2015h). Only
minor features extend the logistic functions to form the Installation module,
which are:

* an installation procedure definition sub-module
* the selection of the base installation port corresponding to the port from
  which all marine operations necessary to complete the installation phase will
  be departing from and
* an optimisation routine to find the most economically attractive logistic
  solution to carry out all steps of the installation phase


Architecture
^^^^^^^^^^^^

The working principle of the Installation module progresses from the collection
of all inputs until the generation of the formatted outputs.

In summary, the Installation module comprises the following components:

* An external logistic phase sub-module: this is where the operation sequences
  and vessels & equipment combinations are defined for all logistic phases
* An installation procedure definition sub-module which is divided into two
  functions;

   * One defining the scheduling rules to determine the sequence of the
     logistic phases; this function makes use of default “Gant chart” rules to
     establish the relationship between logistic phases in terms of
     requirements to have some components of the bill of material already
     installed prior to install another one. For instance, this function
     assumes by default that the OECs must always be installed only once the
     entire electrical infrastructure and the moorings/foundations have been
     deployed at site
   * Another function selecting the base installation port; the selection
     of the base installation port follows a twofold sequence. First, only
     ports having at least one quay that can accommodate the largest item from
     the bill of material are kept (it is also verified that the port possesses
     a dry dock if it is a requirement for the device assembly/load out).
     Secondly, the nearest port to the centre of the lease area specified by
     the user is selected

* Logistic functions assessment sub-module: it contains the core assessment of
  all marine operations required to complete the installation phase and must
  complete two roles: 

   * The selection of suitable maritime infrastructure: characterises the
     logistic requirements associated with the port, vessel(s) and equipment
     for each logistic phase and subsequently filters out only the technically
     feasible solutions
   * The performance assessment of logistic phases: performs the assessment
     of each logistic phase respectively in terms of time scheduling, cost,
     environmental impact and risk value

* An optimisation routine: the most inexpensive feasible logistic solution is
  chosen for each logistic phase. Ultimately, the combination of the optimal
  solutions for each logistic phase forms the overall optimal installation
  phase solution

The optimisation routine internal to the Installation module simply consists of
isolating the feasible logistic solutions which returned the minimum total cost
for a given logistic phase :math:`C_{lp}`. At the end of the Installation
module, the outputs are sorted and formatted in the most convenient way for
future results presentations. Full details of the calculation of :math:`C_{lp}`
can be found in (DTOcean, 2015h). Furthermore, the default values tables are
also available in the same deliverable.


Logistic Functions
''''''''''''''''''

The purpose of the logistic functions is to provide both the Installation module and the Operations and Maintenance module with the means to evaluate marine operations that are called “logistic phases”. For each logistic phase, a common set of logistic functions are designed. These logistic functions consist of:

 * Defining the default operation sequences (breakdown of the logistic phase into individual task starting from mobilisation until demobilisation) as well as defining the default vessel(s) & equipment combinations that can carry out the logistic phase
 * Characterizing the logistic requirements in terms of port, vessel(s) and equipment
 * Selecting technically and physically feasible solutions of port/vessel(s)/equipment
 * Assessing the performance of these feasible solutions in terms of:

   * Schedule (or time efficiency)
   * Cost
   * Environmental impact

It is not expected for the calling computational modules to define the default operation sequences and vessel(s) & equipment combinations, thus the first scientific operations underlying the logistic functions is the characterization of the logistic requirements and subsequent selection of the feasible maritime infrastructure. This process is governed by the “feasibility functions”. For each logistic phase, a set of dedicated feasibility functions, responding to the specific characteristics of the logistic operations to be conducted, are defined. It should be noted that a large number of feasibility functions are shared across logistic phases.

Table 6.14 below exemplifies how such feasibility functions are implemented for the port, vessel and equipment, respectively.

In essence, the feasibility functions consist of Boolean operations and inequalities relating array design inputs (typically provided by the end-user or computed by upstream computational modules) to parameters of the mar- itime infrastructure database (ports, vessels and equipment).

In this manual, the comprehensive list of all feasibility functions will
not be depicted. For further information, the reader is invited to refer to
Deliverable 5.4 for the Installation module (DTOcean, 2015f) and Deliverable
6.5 for the O&M module (DTOcean, 2015g).

Nevertheless, for illustration the tables below exemplify how such
feasibility functions are implemented for the port, vessel and equipment,
respectively.

In essence, the feasibility functions consist of Boolean operations and
inequalities relating array design inputs (typically provided by the end-user
or computed by upstream computational modules) to parameters of the maritime
infrastructure database (ports, vessels and equipment).


.. figure:: /images/technical/port_feasibility.png

   Port feasibility functions during the installation of wave or tidal energy devices


.. figure:: /images/technical/vessel_feasibility.png

   Crane barge or vessel feasibility functions for the installation of wave or tidal energy devices


.. figure:: /images/technical/rov_feasibility.png

   ROV feasibility functions for the installation of a mooring system

A subset of feasibility functions are also defined in order to ensure the
compatibility of the port/vessel(s)/equipment combinations. These functions are
also inequalities and Boolean operations which essentially verify that the
vessel(s) can be accommodated by the port and that the equipment will fit in
the corresponding vessel(s).

In addition to the feasibility functions, there exists a second category of
algorithms which are named the “performance functions”. Once technically and
physically suitable combinations of port/vessel(s)/equipment have been
identified, the purpose of the performance functions to discriminate between
them based on performance.

The first executed performance function provides a time duration estimate of the
logistic phase, denoted :math:`T_{lp}`. The total time :math:`T_{lp}` is the
sum of the time spend at port :math:`T_{port}`, the waiting time for a
satisfactory weather window :math:`T_{wind}` and the time spent at sea
:math:`T_{sea}`, as summarised in (9) below:

.. math:: T_{lp} = T_{port} + T_{wait} + T_{sea}

To access the details of how each element introduced in (9) is calculated, the
reader is encouraged to read through the section about the “scheduling
functions” in Deliverable 5.6 (DTOcean, 2015h).

The second performance function concerns the cost estimation. In its generic
form, the cost of a logistic phase :math:`C_{lp}` simply aggregates the port
charges :math:`C_{port}` and the expenses due to the marine operations
:math:`C_{sea}`. This can be expressed as shown in (10):

.. math:: C_{lp} = C_{port} + C_{sea}

A description of each element of (10) can be found in Deliverable 5.6 (DTOcean,
2015h). It also details the requirements for the environmental functions, the
last item of the performance functions. Five environmental impacts are assessed
by the logistic functions, the results of which are delivered to the
environmental impact assessment thematic algorithm.

The logistic functions are required to:

* Define the logistic phase in terms of operation sequencing and default
  vessel(s) & equipment combinations
* Characterise the logistic requirements (first step of the feasibility
  functions)
* Select suitable maritime infrastructure (second step of the feasibility
  functions)
* Conduct a performance assessment of all feasible logistic solutions in terms
  of time efficiency, cost and environmental impact

The inputs, outputs and internal dataflow of the logistic functions are
schematically represented in Appendix E. On the left side, all “external”
inputs, originating from the end-user or generated by upstream computational
modules (including the Hydrodynamics, the Electrical sub-system and the
Moorings & Foundations modules), are shown. On the right side, the “internal”
inputs, accounting for the maritime infrastructure database and default values,
are placed. Unlike “external” inputs, “internal” inputs are established by the
developers of the logistic functions and the Installation module, i.e. they
will not be exposed to the user.


In addition to the external inputs, there are a number of “internal” inputs
within the logistic functions. The maritime infrastructure is a core object
that must be accessed when running the logistic functions. While the
comprehensive list of the inputs can be found in Deliverable 5.3, these can be
summarised as:

* Port database: detailed information about European ports with the following
  parameter categories:

   * General Information (13 parameters)
   * Port Terminal Specification (17 parameters)
   * Port Cranes, Support, Accessibilities and Certifications (16
     parameters)
   * Manufacturing Capabilities (8 parameters)
   * Economic Assessment (8 parameters)
   * Contact Details (4 parameters)

* Vessel database: detailed information about each vessel type considered in
  DTOcean with the following parameter categories:

   * General Information (9 parameters)
   * Main Dimensions and Technical Capabilities (18 parameters)
   * Maximum Operational Working Conditions (8 parameters)
   * On-board Equipment Specifications (~34 parameters)
   * Economic Assessment (4 parameters)

* Equipment database: detailed information about each equipment types
  considered in DTOcean with the following parameter categories (the number of
  parameters varies from one equipment type to another):

   * Metrology (min. 4 parameters)
   * Performance (min. 2 parameters)
   * Support Systems (min. 2 parameters)
   * Economic Assessment (min. 2 parameters)

Finally, default input values must also be provided to the logistic functions.
It is import that the user is aware of these default values and so they should
be made available to them prior to using the sub-module or by any module that
interfaces with it. Common default values pertaining to logistic phases
associated with both the installation and O&M modules include:

* Average fixed duration values of individual logistic operations
* Safety factors relating to selected feasibility functions
* Operational Limit Condition (OLC) values for specific individual logistic
  operations

Once all inputs are correctly passed into the logistic functions, the evaluation
of the feasible logistic solutions and performance assessment will
approximately consume between 2 to 10 seconds for a single logistic phase. It
should be noted that this rough wall-clock time estimation is based on
preliminary test run cases which do not represent the full scope (i.e. not all
logistic phases covered in the installation and O&M modules have been tested
to-date). The more feasible logistic solutions (i.e. the number of suitable
combinations of port/vessel(s)/equipment) and the more OLC, the more time is
required for the logistic functions to run for a given logistic phase. Finally,
it should be noted that this computational time estimate excludes the estimate
of the time spent at sea.

The outputs of the logistic functions are:

* The list of all logistic requirements associated with the logistic phase
* The selected suitable combinations of port/vessel(s)/equipment associated
  with the logistic phase
* The schedule assessment (including the total time :math:`T_{lp}`) of each
  feasible logistic solution associated with the logistic phase
* The cost assessment (including the total cost :math:`C_{lp}`) of each
  feasible logistic solution associated with the logistic phase
* The environmental impact assessment (including the final score of the five
  environmental functions concerned with the logistic functions) of each
  feasible logistic solution associated with the logistic phase


These outputs are assembled in a dictionary with the characteristics shown in the next table.


.. figure:: /images/technical/output_logistic.png

   Output dictionary of the logistic functions



Functional Specification
^^^^^^^^^^^^^^^^^^^^^^^^

In essence, the list of inputs for the Installation module is the same as the
one for the logistic functions provided before with only three
additional pandas DataFrame tables:

* Vertical penetration rates for all piling equipment in all soil types
  considered in the scope of the DTOcean project
* Horizontal progress rates for all cable trenching/laying equipment in all
  soil types considered in the scope of the DTOcean project
* Default Gantt chart rules for the installation planning

Similar to the logistic functions, the main effort to get the Installation
module running resides in the preparation of the numerous inputs. Further to
the four pandas DataFrames (‘site’, ‘metocean’, ’device’, ‘sub_device’ as
depicted in Appendix F) the user must enter, it is also strongly recommended
that the user overrides the default values when more accurate data concerning
the ocean energy project is available.

Assuming all upstream computational modules have successfully generated the
outputs required to feed the Installation module, no intervention from the user
is required other than inputting the aforementioned four tables. The
Installation module terminates with the formatting of the outputs. Results
obtained through the feasibility functions for the nine installation logistic
phases convene in a predicted installation plan which contains:

* starting and ending dates of all sub-array components installation phases
  together with the estimated waiting time
* selected maritime infrastructure per marine operation
* cost breakdown per logistic phase, and
* environmental scores per logistic phase

The Installation module returns the dictionary output of the logistic functions
presented in Section 6.5.3 for each logistic phase the user wishes to be
considered by the Installation module.
