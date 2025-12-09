.. _tech_operations:

Operations and Maintenance
--------------------------

The purpose of the “Operations and Maintenance” (O&M) module is to minimise the
impact of the O&M activities on the LCOE. This will be done by calculation /
simulation of a cost optimised full operational cycle O&M approach, where
different strategies are combined and the actual dates of performance for the
individual O&M actions (inspections, maintenance, repair) are optimised with
respect to the starting dates and the possibility of parallel scheduling. In an
early stage of the DTOcean project, it was decided to perform this optimisation
process on a time based approached. Therefore, the module is designed to
simulate the full O&M life cycle of an OEC device array by distributing the
possible maintenance operations over the entire operational phase (e. g. 25
years) of the array.

The following sections describe the required setup steps and the data to be
provided by the user.  Furthermore, the implementation of the module with a
description of the developed algorithms, the software structure and the
definition of the interface for data exchange with other modules (via the core
module) is given.


Requirements
^^^^^^^^^^^^

User Requirements
'''''''''''''''''

The purpose of the O&M module is to simulate the time domain based full life
cycle O&M activities of an OEC array. For this purpose, a maintenance plan will
be generated for each relevant component as defined by the user. Everything
inside the array will be handled as a component, i.e. a component can be:

 * an infra structure item, e. g. the export cable, the sub-station(s),
   subsea connectors, switch gear, cable sections in the internal array grid,
   etc.
 * an entire device (if no deeper level of detail is required)
 * components of a device (level of detail will be restricted to the Equimar
   (Ingram et al., 2011) definition with the four major sub-systems:
   hydrodynamic converter, PTO, reaction and controller)

The user is can select one of three desired maintenance approaches
(“corrective”, “calendar based”, “condition based” (DTOcean, 2014a)) or
meaningful combinations of it. The individual maintenance approaches will be
further detailed by use of a few parameters, which are described in the
following sections. For each component a maintenance plan is generated, and an
example can be seen in the :numref:`fig-maintenance-plan-tech`.

.. _fig-maintenance-plan-tech:

.. figure:: /images/technical/maintenance_plan.png

   The Schematic overview of a maintenance plan


Software Design Requirements
''''''''''''''''''''''''''''

The purpose of the O&M module is the modelling of the time domain lifecycle O&M
methodology. The O&M module simulates all operation and maintenance activities
of the OEC array over its lifetime in the time domain. Costs related to the O&M
activities will be calculated and added to the overall LCOE figure. The O&M
module can be used to understand and optimise the O&M strategy of OEC array in
the planning phase of a project. The minimisation of the maintenance cost will
help the decision maker to choose cost-optimal solutions.

Maintenance is defined as the combination of all technical and administrative
actions intended to retain an item in, or restore it to, a state in which it
can perform its required function (IEEE, 2000). The
:numref:`fig-maintenance-strategies` illustrates a common classification of
maintenance strategies, which is based on the standard SS-EN 13306 (SIS Forlag,
2001).

.. _fig-maintenance-strategies:

.. figure:: /images/technical/maintenance_strategies.png

   Types of maintenance strategies, partly adapted from (SIS Forlag, 2001).

The maintenance strategies considered in the DTOcean project are defined as:

 * **Corrective maintenance** is due to an unexpected failure and is intended to
   restore an item/component to a state in which it can perform its required
   function (IEEE, 2000)
 * **Condition-based maintenance** is a type of preventive maintenance based on a
   response to the monitoring information available (SIS Forlag, 2001). It
   consists of all maintenance strategies involving inspections (noise, visual,
   etc.) or permanently installed Condition Monitoring Systems (CMS) to decide
   on the main- tenance actions
 * **Calendar-based (Time-based) maintenance** is a type of preventive
   maintenance carried out in accordance with established intervals of time or
   number of units independent of any conditioning investigation (SIS Forlag,
   2001). It is suitable for failures that are age-related and for which the
   probability distribution of failure can be established based on fixed time
   intervals

The O&M costs are known to be an important part of the life cycle OPEX cost of
MRE projects. In offshore wind farms, O&M contributes 15-30 % of the total LCOE
(Engels et al., 2009). Therefore it is important to develop cost-effective O&M
concepts to help MRE projects to be competitive with offshore wind. The
optimisation of these concepts addresses the overall resources (personnel and
equipment) required to execute the maintenance activities, which inherently
include the logistical support.

To model the individual behaviour of components of OEC array devices, the
following items need to be considered:

 * Component annual failure rate
 * Effect of the failure of the component to other components or devices
 * The optimised mixture of maintenance strategies to keep the array devices
   operational
 * The requirements of the maintenance processes of all components with
   respect to time/duration, ves- sels/equipment, spare parts and personnel

A typical maintenance process is depicted schematically in the
:numref:`fig-maintenance-process` below. All maintenance strategies can be
simulated with this process plan. The difference in handling the strategies is
mostly setting the time parameters to the respective values. For example, for a
calendar/condition based maintenance activity, the “T_Organisation” will be
significantly shorter, since the organisational and preparatory tasks (booking
of vessels & equipment, mobilising personnel, ordering of spare parts, etc.)
can be done before the scheduled operation starts. Another example is a simple
inspection, for which the “T_Logistic” can be set to zero because there is no
need for ordering spare parts.

.. _fig-maintenance-process:

.. figure:: /images/technical/maintenance_process.png

   Typical maintenance process

The definition of calendar based maintenance is simply done by setting the
interval (e. g. “annual”, “semi-annual”, etc.). Condition based maintenance
requires the definition of a “state of health” (SOH) threshold, below which
maintenance is mandatory for the component. For this, it is assumed that at the
installation / commissioning of an OEC device or after repair / replacement
activities, the SOH of a component will be 100%. A linear interpolation
simulates the SOH of the considered component. The SOH limit in % that triggers
the condition based maintenance is a parameter of the O&M module and will be
set by user. The slope of the SOH degradation curve is also defined by the user
(see :numref:`fig-automated-maintenance`). 

In time domain simulation the occurrence of a failure has to be estimated over
the lifetime of the device. To translate the statistical based failure rates
back to the time domain, a Binomial or Poisson process can be used. A Poisson
process is a stochastic process that counts the number of events and the time
points at which these events occur in a given time interval. The time between
each pair of consecutive events has an exponential distribution with parameter
λ (intensity) and each of the inter-arrival times is assumed to be independent
of other inter-arrival times. :numref:`fig-poisson-process` depicts an example
for the given random parameters.


.. _fig-automated-maintenance:

.. figure:: /images/technical/automated_maintenance.png

   Handling of automated inspection in case of condition-based maintenance


.. _fig-poisson-process:

.. figure:: /images/technical/poisson_process.png

   Paths of Poisson process for a 30 year period and a number of 44 events


The optimisation algorithm used to minimise the cost of the O&M for the OEC
array has to fulfil the following case:

 * Optimisation in case of corrective maintenance
 * Optimisation in case of condition-based maintenance
 * Optimisation in case of calendar-based maintenance
 * Optimisation of the interaction between different maintenance strategies
   (mix strategies)

The user has the option to define different combinations of maintenance
strategies. The user may only be interested in the cost optimisation of
“unplanned corrective maintenance”, for instance. In this case, no optimisation
of mixed maintenance strategy is necessary because the user is required to
enforce such a choice. In a second example, the user may be interested in the
cost optimisation of a mix of “Unplanned corrective maintenance” and “Calendar-
based maintenance” strategy, in which case the module will calculate the
optimised solution for the mixed strategy.

**Optimisation in case of corrective maintenance**

The optimisation approach is based on the clustering of corrective maintenance
events with those of the two other strategies considered in scope, i.e.
calendar based and condition based. A criterion will be defined by the user as
the number of days, which will be the time distance to allow clustering. For
example, if a corrective maintenance action is followed by a calendar based
maintenance action and/or a foreseeable condition based maintenance action
within the next “K” days, the two/three operations will be combined to save
costs for logistics (vessel(s) & equipment charges, transportation, etc.).
Parameter “K” is user defined.

**Optimisation in case of condition-based maintenance**

In addition to the above mentioned clustering, the value for the SOH threshold,
at which the condition based main- tenance will be triggered, is an
optimisation issue. The reason for this is that from a certain SOH on
downwards, the power output of an OEC will be reduced (“de-rating”) to extend
the remaining life time of the OEC and its components. This will result in less
power production and, therefore, reduced energy revenue.

The de-rating process and the condition based maintenance trigger threshold are
controlled by user defined pa- rameters. For example, from a SOH value of “X”
(in “%”) the power output set point will be reduced linearly from rated power
to zero. At a value of “Y” % SOH, the device will be shut down to avoid serious
consequential damages. It is 100% > X > Y (Y should be at least 25%).

**Optimisation in case of calendar-based**

To optimise the calendar based maintenance, either the time interval between two
maintenance actions (when a scalar parameter is defined) or the fixed dates for
the start of all calendar based maintenance actions during the operational
phase can be defined (vector parameter). In principle, a smaller interval for
the calendar based main- tenance reduces the probability for the occurrence of
device faults and resulting shut downs. On the other hand, it requires more
frequent maintenance actions and, therefore, causes higher costs. The parameter
for controlling the calendar based maintenance interval is defined by the user.
The vector parameter option allows to model individ- ual maintenance
approaches/intervals, e. g. the first calendar based maintenance after five
years and then every two years.

**Optimisation of the interaction between different maintenance strategies (mixed strategies)**

In order to handle the interaction between different maintenance strategies
(mixed strategies), the following con- cepts are integrated into the
optimisation process:

 * Priority definition of maintenance activities
 * Priority definition of OEC devices
 * Time shifting (postponing) of maintenance action on time axis
 * Parallel shift, number of crew

**Priority definition of maintenance activities**

Some priorities for maintenance actions will be defined due to the limitation of
resources (e.g. vessels, crews). Some examples are:

 * All maintenance tasks that have already started have highest priority
 * Corrective maintenance has the highest priority, then condition-based
   maintenance, and then calendar-based maintenance

**Priority definition of OEC devices**

A priority parameter controls which device will be repaired first when there is
only limited resources or time (weather) windows to perform maintenance
activities.  For example, if there is a problem with the electrical connection
(circuit break) at two OEC devices, the one which is closer to the hub /
transformer will be repaired with higher priority since all the following
devices in the electrical string will also be affected from the damage. The
priority value for an OEC device will be calculated with respect to its
position in the electrical string (see :numref:`fig-failure-occurrence`).

Another item to be considered when calculating the priority is the
availability of spare parts. If a spare part for the component to be repaired
in device 1 is higher than for another component in device 2, than device 2
will get a higher priority and will be maintained first.

**Time shifting**

Shifting of a repair action in case of corrective maintenance to the planned
calendar based maintenance is an optimisation task and is not trivial. Calendar
based maintenance will be done in a defined time section in a year (start and
end date are user parameters). For a shifting of the repair action in case of
corrective maintenance the device downtime due to the time shifting and,
therefore, the revenue losses have to be calculated depending on the position
of device in the electrical grid cable string (see
:numref:`fig-failure-occurrence` and :numref:`fig-time-shifting`). These losses
should be compared with the cost advantage of time shifting (e.g. mobilisation
cost). The result of this comparison controls if time shifting is required.

**Parallel shift, number of crew**

Working with parallel shifts means increasing the number of crew required to
carry out the work. This results in less time for performing the maintenance
action (and, consequently, reduced device downtimes) but will result in higher
personnel costs. The optimisation task is to find the minimum LCOE between the
loss of energy revenue and the additional personnel costs.


.. _fig-failure-occurrence:

.. figure:: /images/technical/failure_occurrence.png

   Failure occurrence in n.2 device
   

.. _fig-time-shifting:

.. figure:: /images/technical/time_shifting.png

   Time shifting of maintenance action


Architecture
^^^^^^^^^^^^

The functional structure of the O&M module is shown in figure “O&M module
functional structure”. Inputs to the module are represented by the grey “User
Definitions” block. Such user definitions can be stored in the database (to be
read by the core) or provided by the user and then passed to the O&M module.
Any output calculated in the O&M module will be passed back to the user or the
core (“Results” block), depending on the mode of operation.

The module uses embedded code, i.e. it reads the array configuration and the
failure rates for all components from the Reliability Assessment module (see
section :ref:`tech_reliability`), which is an external module providing
information about the array layout and the failure probability (as annual
failure rates).

For each of the components in scope, an individual maintenance plans will be
initialised. In a first request, the logistic functions will be called to
retrieve the availability of vessels and equipment. If required, the
maintenance plans will be updated. In a second step, the optimisation loop(s)
will be performed.

In the “Maintenance Strategies” block, the array structure will be translated
into several module objects. With these objects, each representing one
component, all relevant elements will be generated as class instances in the
executable code.


.. _fig-om-structure:

.. figure:: /images/technical/om_structure.png

   O&M module functional structure


Once all of the required classes are initialised, the optimisation loop
(“Calculation” block) runs and sequentially calls several logistic functions to
execute the O&M cost calculation. The loop will run until the minimum LCOE is
achieved. The optimisation process is rather complex and is described in
(DTOcean, 2015i) in detail.

 
**Module structure**

The software structure of the O&M module is developed in an object oriented form
and is depicted in the :numref:`fig-om-module` below.


.. _fig-om-module:

.. figure:: /images/technical/om_module.png

   O&M module structure


**Class LCOE_Optimiser**: This class is reserved for the implementation of the
optimisation strategy of the O&M module. The function “executeOptim()” contains
the optimisation code which will be called by “ call  ” func- tion of
LCOE_Optimiser. The class LCOE_Optimiser contains an instance of class
LCOE_Calculator. The outputs of the O&M module are collected in a Python
dictionary labelled “outputWP6”.

**Class LCOE_Calculator**: This class is the realisation of the LCOE
calculation. The function “executeCalc()” will contain the calculation code of
LCOE which will be called by the “ call  ” function of LCOE_Calculator. The
class LCOE_Calculator contains an instance of array class.

**Class array (arrayClass.py)**: the class array contains all of the information
concerning the failure rates, Poisson events etc. in the form of a Python
dictionary.

**Included Libraries and DTOcean packages**

To calculate of optimal LCOE relating to the O&M activities, the
dtocean-operation-maintenance package (as the Python package name for the O&M
module) requires the estimation of the logistic efforts which will be carried
out in the dtocean-logistics package. For the estimation of the down time of
the devices the failure rates of components are required which will be
calculated in dtocean-reliability package.

Additionally, dtocean-operation-maintenance requires a number of external Python
libraries for its operation. These include:

 * pandas
 * numpy
 * SciPy


Functional Specification
^^^^^^^^^^^^^^^^^^^^^^^^

Inputs
''''''

To execute the module, the following information is required:

 * the array layout with the number of devices, the exact absolute positions of the devices and the total energy yield for each device;
 * the internal grid layout (star, loop, etc.), the type of the substation (simple connector or transformer, switch gear, etc.) and the export cable specification
 * the information about the implementation of the reaction/station-keeping subsystem
 * the information about the availability, cost and access time of any logistic items, i.e. vessels, jack-up barges, cable laying vessels, etc., but also including specialised equipment (ROVs) and expert personnel (special technicians, divers, etc.)
 * the annual failure rates for all components for the OEC of interest

To run the O&M module, the user needs to define the information describing all relevant maintenance operations which can be applied to the devices in the array. Possible maintenance operations include simple inspections with maintenance technicians using a small crew transfer vessel (CTV) up to the replacement of a nacelle of a tidal turbine using a jack-up barge and a 100t crane. The required parameters are listed in the table below:


.. figure:: /images/technical/om_inputs.png

   Required user inputs for the Operations and Maintenance module


The full list of the O&M module input parameters with their individual key
values is in the following tables. To help define this data, a respective input
mask as a template file (Excel format) will be provided on the following pages.
This template will allow the user to collect all the required information as
mentioned above.

The following table contains the description of the parameters which are common
for all components in the array.


.. image:: /images/technical/commonWP6.png


The following tables contain the description of the parameters for definition of
the electrical components in the array’s balance of plant. There are four
parameter categories to be considered:


Category 1: “Component”

.. image:: /images/technical/cat1component.png


Category 2: “FailureModes”

.. image:: /images/technical/cat2failure.png


Category 3: “RepairActions”

.. image:: /images/technical/cat3repair.png


Category 4: “Inspections”

.. image:: /images/technical/cat4inspections.png


**Notes**:

1) allowed values are “Substation”, “Export Cable”, “Subhub”

2) Definition of FM IDs 

.. image:: /images/technical/fm_id.png

3) CAPEX costs for condition monitoring hardware: it is assumed that the
   hardware is not installed in the component/device during production. If the
   device is purchased with an already installed condition monitoring hardware,
   set value(s) to “0”;

4) allowed values for component type
    * Hydrodynamic
    * Pto
    * Control
    * Support structure
    * Mooring line
    * Foundation
    * Dynamic cable
    * Array elec sub-System


Execution
^^^^^^^^^

Class inputOM: The interface of the dtocean-operation-maintenance package is
implemented as a Python class. The int function of this class takes the defined
interface parameters and saves them in internal class parameters. The
initialisation of the class is as follows: ::

   def __init__(self,
                Farm_OM,
                Component,
                Failure_Mode,
                Repair_Action,
                Inspection,
                RAM_Param,
                Logistic_Param,
                Simu_Param,
                Control_Param):
      self.__Farm_OM = Farm_OM
      self.__Component = Component
      self.__Failure_Mode = Failure_Mode
      self.__Repair_Action = Repair_Action
      self.__Inspection = Inspection
      self.__RAM_Param = RAM_Param
      self.__Logistic_Param = Logistic_Param
      self.__Simu_Param = Simu_Param
      self.__Control_Param = Control_Param

To run the dtocean-operation-maintenance package the user should make two
different instances:

1: An instance of class inputOM: ::

   inputOMPtr = inputOM(Farm_OM,
                        Component,
                        Failure_Mode,
                        Repair_Action,
                        Inspection,
                        RAM_Param,
                        Logistic_Param,
                        Simu_Param,
                        Control_Param)

2: An instance of class LCOE_Optimiser(inputOMPtr): This class contains an
instance of class inputOM in order to read the model parameters via this
pointer. ::

   ptrOptim = LCOE_Optimiser(inputOMPtr)

For reading the model parameters different getter functions are defined in class
inputOM, for instance: ::

   def get_Farm_OM(self):
      return self.__Farm_OM


Outputs
'''''''

The execution of the dtocean-operation-maintenance package model is carried out
by the following command: ::

   outputOfWP6 = ptrOptim()

outputOfWP6 is the result of the calculations in the O&M module and is a
dictionary with the keys defined in :numref:`tab-ptrOptim`. The grey shaded
variables are combined in the “oputputWP6” structure.

.. _tab-ptrOptim:

.. figure:: /images/technical/ptrOptim.png

   Dictionary keys for the output of the ptrOptim class


**Interpretation of env_assess**

The env_assess key is formatted as a pandas Series object. Each index (int
value) indicates a repair action or an inspection and contains a dictionary
with keys seen in :numref:`tab-env-assess`. The number of indexes in env_assess
will match the necessary actions (inspections or repair actions) during the O&M
module calculations.

.. _tab-env-assess:

.. figure:: /images/technical/env_assess.png

   Keys of the env_assess Series object


**Interpretation of “outputWP6”**

The table  below gives some examples for values resulting from a test run with
two devices defined in an array.


.. figure:: /images/technical/outputWP6.png

