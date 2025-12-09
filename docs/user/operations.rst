.. _user_operations:

Operations and maintenance module (OMCO)
----------------------------------------

Introduction
^^^^^^^^^^^^

The purpose of the OMCO module is to simulate the time domain based full life
cycle operation and maintenance (O&M) activities of a Marine Renewable Energy
(MRE) array. This will consider the costs for the following items:

 * OPEX:

   * Vessels (crew transfer, construction, heavy transport, etc.)
   * Equipment (special tools, ROVs, etc.)
   * Personnel (technicians, specialists)
   * Spare parts, materials

 * CAPEX:

    * Condition monitoring hardware

The OMCO module simulates all O&M activities of the MRE array over its lifetime
in the time domain. Cost related to the O&M activities will be calculated and
added to the overall LCOE costs. The OMCO module can be used to understand and
optimise the O&M strategy of MRE arrays in the planning phase of a project. The
minimisation of the O&M costs will help the decision maker to choose
cost-optimal solutions.

Maintenance is defined as the combination of all technical and administrative
actions intended to retain an item in, or restore it to, a state in which it
can perform its required function. :numref:`fig-maintenance` illustrates a
common classification of maintenance strategies, which is based on the standard
SS-EN 13306.


.. _fig-maintenance:

.. figure:: /images/user/maintenance.png

   Types of maintenance strategies


The maintenance strategies are considered as defined below:

 * **Corrective maintenance** is due to an unexpected failure and is intended
   to restore an item/component to a state in which it can perform its required
   function1.
 * **Condition-based maintenance** is a type of preventive maintenance based
   on a response to the monitoring information available . It consists of all
   maintenance strategies involving inspections (noise, visual, etc.) or
   permanently installed Condition Monitoring Systems (CMS) to decide on the
   maintenance actions.
 * **Calendar-based (Time-based) maintenance** is a type of preventive
   maintenance carried out in accordance with established intervals of time or
   number of units independent of any conditioning investigation2. It is
   suitable for failures that are age-related and for which the probability
   distribution of failure can be established based on fixed time intervals.

The O&M costs are known to be an important part of the life cycle OPEX cost of
MRE projects. In offshore wind farms, O&M contributes 15-30 % of the total
levelised cost of energy (LCOE) . Therefore it is important to develop
cost-effective O&M concepts to help MRE projects to be competitive with
offshore wind. The optimization of these concepts should address the overall
resources required to execute the maintenance activities, which necessarily
have to include the logistical support.

To model the individual behaviour of components of MRE array devices, the
following items need to be considered:

 * Component annual failure rate
 * Effect of the failure of the component to other components or devices
 * The optimised mixture of the above mentioned strategies to keep the array
   devices operational
 * the requirements of the maintenance processes of all components with
   respect to time/duration, vessels/equipment, spare parts and personnel

A typical maintenance process is depicted schematically in
:numref:`fig-maintenance-proc`. All maintenance strategies can be simulated
with this process plan. The difference in handling the strategies is mostly
setting the time parameters to the respective values. For example, for a
calendar based or condition based maintenance, the “T_Organisation” will be
significantly shorter, since the organisational and preparatory tasks (booking
of vessels & equipment, mobilising personnel, ordering of spare parts, etc.)
can be done before the scheduled operation starts. Another example is a simple
inspection, for which the “T_Logistic” can be set to zero because there is no
need for ordering spare parts.


.. _fig-maintenance-proc:

.. figure:: /images/user/maintenance_proc.png

   Typical maintenance process


The definition of the calendar based maintenance is simply done by setting the
interval (e. g. “annual”, “semi-Annual”, etc.). The condition based maintenance
required the definition of a “state of health” (SOH) threshold, below which
maintenance is mandatory for the component. For this, it is assumed that at the
installation / commissioning of a MRE device or after repair / replacement
activities, the SOH of a component will be 100%. A linear interpolation
simulates the SOH of the considered component. The SOH limit in % that triggers
the condition based maintenance is a parameter of the OMCO module and will be
set by the user. The slope of the SOH degradation curve is also defined by the
user.


.. _fig-inspection:

.. figure:: /images/user/inspection.png

   Handling of automated inspection in case of condition-based maintenance


In the time domain simulation the occurrence of failures has to be estimated
over the lifetime of the device. To translate the statistical based failure
rates back to the time domain, a Binomial or Poisson process is used. A Poisson
process is a stochastic process that counts the number of events and the time
points at which these events occur in a given time interval. The time between
each pair of consecutive events has an exponential distribution with parameter
λ (intensity) and each of them inter-arrival times is assumed to be independent
of other inter-arrival times. :numref:`fig-poisson` depicts an example of a
Poisson process.


.. _fig-poisson:

.. figure:: /images/user/poisson.png

   Paths of Poisson process for a 30 year period and a number of 44 events


For time domain simulation purpose, a **maintenance plan** will be generated for
each relevant component as defined by the user. Everything inside the array
will be handled as a component, i. e. a component can be:

 * an infrastructure item, e. g. the export cable, the sub-station(s), subsea
   connectors, switch gear, cable sections in the internal array grid, etc.
 * an entire device (if no deeper level of detail is required)
 * components of a device (level of detail will be restricted to the Equimar
   definition with the four major sub-systems: hydrodynamic converter, PTO,
   reaction and controller)

For each component, a maintenance plan will be generated.
:numref:`fig-maintenance-plan-user` shows an example. Each maintenance type has 
its own colour code:. 

.. image:: /images/user/color_code.png

.. _fig-maintenance-plan-user:

.. figure:: /images/user/maintenance_plan.png

   The Schematic overview of a maintenance plan


Architecture
^^^^^^^^^^^^

The functional structure of the OMCO module is shown in
:numref:`fig-ocmo-structure`. The module at hand here is a “computational
package”. This means that all input for the module comes via the core module as
represented by the grey “User Definitions” block. Such user definitions need to
be stored in the global data base and will be read out by the core module and
then passed to the OMCO. Any output calculated in the OMCO will be passed back
to the core (“Results” block).

The module uses embedded code, i. e. it reads the array configuration and the
failure rates for all components from the “Reliability Assessment Module”
(RAM), which is an external module providing information about the array layout
and the failure probability (as annual failure rates). 

For each of the components in scope, an individual maintenance plans will be
initialised. In a first request, the logistic functions will be called to
retrieve the availability of vessels and equipment (V&E). If required, the
maintenance plans will be updated. In a second step, the optimisation loop(s)
will be performed

In the “Maintenance Strategies” block, the array structure will be translated in
several module objects. With this objects, each representing one component, all
relevant elements will be generated as class instances in the executable code. 


.. _fig-ocmo-structure:

.. figure:: /images/user/ocmo_structure.png

   OMCO module functional structure


Once all the classes are implemented, the optimisation loop (“Calculation”
block) runs and sequentially calls several logistic functions to execute the
O&M cost calculation. The loop runs until there is a minimum LCOE is achieved.


Functional specifications
^^^^^^^^^^^^^^^^^^^^^^^^^

Inputs
''''''

The following table contains the description of the parameters which are common
for all components in the array


.. image:: /images/user/ocmo_inputs.png


The following tables contain the description of the parameters for definition of
the electrical components in the array’s balance of plant. There are four
parameter categories to be considered:

Category 1: “Component”

.. image:: /images/user/cat1.png

Category 2: “FailureModes”

.. image:: /images/user/cat2.png

Category 3: “RepairActions”

.. image:: /images/user/cat3.png

Category 4: “Inspections”

.. image:: /images/user/cat4.png


The following tables contain the description of the parameters for definition of
the devices in the array and, if applicable, their individual components. There
are four parameter categories to be considered (there structure is very similar
to the one as for the electrical components. For better readability, the
deviating parts are highlighted in light blue):

Category 1: “Component”

.. image:: /images/user/cat12.png

Category 2: “FailureModes”

.. image:: /images/user/cat22.png

Category 3: “RepairActions”

.. image:: /images/user/cat32.png

Category 4: “Inspections”

.. image:: /images/user/cat42.png


Notes:

1. allowed values are “Substation”, “Export Cable”, “Subhub”

2. Definition of FM IDs 

.. image:: /images/user/fm_id.png


3. CAPEX costs for condition monitoring hardware: it is assumed that the
   hardware is not installed in the component/device during production. If the
   device is purchased with an already installed condition monitoring hardware,
   set value(s) to “0”; 

4. allowed values for component type

   * Hydrodynamic
   * Pto
   * Control
   * Support structure
   * Mooring line
   * Foundation
   * Dynamic cable
   * Array elec sub-System


Execution
'''''''''

After adding the “Operation and Maintenance” module  to the list of active
modules and of the proper setting up of the required data base parameters (as
described in the section above), the only thing remaining is the selection of
the desired maintenance strategy (or all possible combinations of multiple
strategies) by the user. This can be done by using checkboxes like in the
example given below.


.. _fig-ocmo-strategie:

.. figure:: /images/user/ocmo_strategie.png

   Checkbox for the selection of different combinations of maintenance strategies

When all setup is done, the “Operation and Maintenance” module can be executed
in the frame of an optimisation run of the core program.


Outputs
'''''''

After execution of the “Operation and Maintenance” module, the following output
parameters will be passed to the user via the core module:

.. image:: /images/user/ocmo_out1.png

The table below gives some examples for values resulting from a test run with
two devices defined in an array.

.. image:: /images/user/ocmo_out2.png

