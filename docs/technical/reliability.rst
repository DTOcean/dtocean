.. _tech_reliability:

Reliability Assessment Module
-----------------------------

In this section the requirements, architecture and functional specification of
the Reliability Assessment sub-module (RAM) are summarised.

Requirements
^^^^^^^^^^^^

In this section the requirements, architecture and functional specification of
the Reliability Assessment sub-module (RAM) are summarised.

User Requirements
'''''''''''''''''

Reliability assessment is one of the three main thematic assessment requirements
of the DTOcean software. At first, the design modules (Electrical Sub-Systems
and Moorings and Foundations) will produce a solution which is unconstrained in
terms of environmental impact and reliability but focused on achieving the
lowest possible capital cost. Installation and O&M scheduling will take place
in the respective module by making use of the logistic functions. The role of
the RAM sub-module will be to conduct reliability calculations for i) the user
and ii) to inform operations and maintenance requirements of the O&M module.

The purpose of the RAM is to:

* Generate a system-level reliability equation based on the
  inter-relationships between sub-systems and components (as specified by the
  Electrical Sub-Systems and Moorings and Foundations component hierarchies and
  by the user)
* Provide the user with the opportunity to populate sub-systems not covered by
  the DTOcean software (e.g. power take-off, control system) using a GUI-based
  Reliability Block Diagram
* Consider multiple failure severity classes (i.e. critical and non-critical)
  to inform repair action maintenance scheduling. This will represent a
  simplified approach to Failure Mode and Effects Analysis (FMEA)
* Carry out normal, optimistic and pessimistic reliability calculations to
  determine estimation sensitivity to failure rate variability and quality
  analysis
* Provide the time-dependent failure estimation model (in the O&M module) with
  the Time to failure (TTF) of components within the system

It will produce:

* A pass/fail Boolean compared to user-defined threshold
* Distribution of system reliability (%) from mission start to mission end
  (:math:`0 \le t \le T`).
* Mean time to failure (MTTF) of the system, sub-systems and components
  presented to the user in a tree format
* Risk Priority Numbers (RPNs)


Software Design Requirements
''''''''''''''''''''''''''''

The RAM has been developed to calculate reliability metrics for each component
or sub-system provided by the database and/or user. It is a separate module
which is fed input specified by the user, database and design modules (via the
core for the global design) and provides reliability statistics to the O&M
module and user GUI (again via the Core, see :numref:`fig-reliability`).

If a proposed design solution is not feasible in terms of reliability (i.e. it
does not match the threshold set by the user) after the initial run of the
software, an alternative solution will be sought by initializing a subsequent
run of the software. For example, if the reliability of a proposed mooring
system is unacceptable then a constraint could be fed back to the Moorings and
Foundations module. Therefore, only components with a reliability level above a
certain threshold (based on the required level of system reliability set by the
user) would be available for selection when the Moorings and Foundations module
is re-run.

.. _fig-reliability:

.. figure:: /images/technical/reliability.png

   Interaction of the Reliability Assessment sub-module with the other components in the software
   
The 3rd party Python packages used by the RAM are as follows:

* matplotlib
* numpy
* pandas

Starting with the lowest analysed level (component level), the algorithms used
to calculated reliability at a specified time (i.e. mission time) are
introduced in the following subsections.

Component reliability
'''''''''''''''''''''

Assuming an exponential distribution of failures component reliability is
calculated as:

.. math::

   R(T) = e^{-\lambda T}
 
where :math:`\lambda` is the component failure rate.


Reliability of higher system levels
'''''''''''''''''''''''''''''''''''

For higher system levels (sub-system, device, device cluster, string and array)
reliability at mission time is calculated in several ways depending on the
relationships between adjacent system elements, as defined by the User,
Electrical System Architecture and Mooring and Foundation system hierarchies.

For series relationships comprising n elements:

.. math::

   R_{ser}(T) = \prod^n_{i=1} (\exp^{-\lambda_i T} )


For parallel relationships comprising n elements:

.. math::

   R_{par}(T) = 1 - \prod^n_{i=1} (1 - R_i (T) )
   
For the special case of ‘m of n’ relationships, such as multiple mooring lines:

.. math::

   R_{mn}(T) = \sum^n_{r=k} \left(  \begin{array}{c} n\\i \end{array} \right) R^r_i (T) (1 - R_i (T))^{n-r}


.. _fig-mooring:

.. figure:: /images/technical/mooring.png

   Example mooring system comprising 3 lines


Component MTTF
''''''''''''''

Component MTTF values are calculated as the reciprocal of the specified failure
rate:

.. math::

   MTTF = \frac{1}{\lambda}


MTTF of higher system levels
''''''''''''''''''''''''''''

Similarly to the reliability metric described above for higher system levels
(sub-system, device, device cluster, string and array) the method of
calculating MTTF is dependent on if adjacent elements are in series, parallel
or belong to an ‘m of n’ system.

For series relationships:


.. math::

   MTTF_{ser} = \frac{1}{\sum^n_{i=1} \lambda_i}
   
For parallel relationships binomial expansion of terms is required:

.. math::

   MTTF_{par} = \sum^n_{i=1}\frac{1}{\lambda_i} - \sum^{n-1}_{i=1} \sum^n_{j=i+1}\frac{1}{\lambda_i+\lambda_j} + \sum^{n-2}_{i=1} \sum^{n-1}_{j=i+1} \sum^n_{k=j+1} \frac{1}{\lambda_i+\lambda_j+\lambda_k} - \dots + (-1)^{n+1} \frac{1}{\sum^n_{i=1} \lambda_i}

Finally for ‘m of n’ relationships:

.. math::

   MTTF_{mn} = \frac{1}{\sum^n_{i=1} i * \lambda_i}


Architecture
^^^^^^^^^^^^

Overview
''''''''

The RAM comprises two Python modules (:numref:`fig-RAM-tech`). RAM_Main.py acts 
as an interface between the user and the module and also calls the functions 
within the RAM. RAM_Core.py comprises the classes and functions required to 
carry out statistical analysis of the system. As can be seen from Figure 7.5 
with RAM_Core.py there is interaction between the functions within the Syshier 
class. The use of result sets by the O&M module is discussed in later sections. 


.. _fig-RAM-tech:

.. figure:: /images/technical/RAM.png

   Interaction between the various classes and methods of the Reliability Assessment sub-module

.. _tab-RAM:

.. image:: /images/technical/RAM1.png
.. figure:: /images/technical/RAM2.png

   Summary of internal RAM processes


**SYSTEM HIERARCHY**

In order to generate the reliability equations at each system level, component hierarchies defined by the Electrical Sub-Systems and Moorings and Foundations modules (which specify the inter-relationships between components and sub-systems) are used. In addition, any user-specified sub-systems are included at this stage. At the top level of the hierarchy each device will be identified by its DeviceID number. To implement this structure in Python, nested lists have been used, for example the table below shows a simple device and substation foundation example.


.. _fig-hierarchy:

.. figure:: /images/technical/hierarchy.png

   Example hierarchy configuration from the Moorings and Foundations module

Assuming that the same components are used for each of the four devices in the
example array, the Moorings and Foundations hierarchy in Python would appear
as: ::

   {'array': {'Substation foundation': ['pile', 'UHS']},
   'device001': {'Foundation': [['pile', 'UHS'], ['pile', 'UHS'], ['pile', 'UHS'], ['pile', 'UHS']],
   'Umbilical': ['submarine umbilical cable 6/10kV']},
   'device002': {'Foundation': [['pile', 'UHS'], ['pile', 'UHS'], ['pile', 'UHS'], ['pile', 'UHS']],
   'Umbilical': ['submarine umbilical cable 6/10kV']},
   'device003': {'Foundation': [['pile', 'UHS'], ['pile', 'UHS'], ['pile', 'UHS'], ['pile', 'UHS']],
   'Umbilical': ['submarine umbilical cable 6/10kV']},
   'device004': {'Foundation': [['pile', 'UHS'], ['pile', 'UHS'], ['pile', 'UHS'], ['pile', 'UHS']],
   'Umbilical': ['submarine umbilical cable 6/10kV']}}

It is possible to identify parallel and series relationships from this list
since the component names are separated: series components are separated by a
comma whereas parallel relationships are indicated by square brackets. By
default mooring systems are treated as ‘m of n’ systems (where :math:`m=n-1`)
to represent an Accident Limit State scenario (Det Norske Veritas, 2013a).


**FAILURE RATE DATA**

Reliability calculations performed within the RAM are based on the assumption
that failures follow an exponential distribution and hence that the hazard rate
is constant with time. Being open-source software, other distributions could be
included in the future to incorporate the two other main life stages (burn-in
and wear-out).

Based on the component names identified in the hierarchy list, failure rates
from the database will then be accessed. Failure data for certain components
may be sparse. A review8 of mooring component failures of production and
non-production platforms and vessels illustrates this point. Most,
if not all of these failures can be classified as critical: although redundancy
is usually taken into account while designing these types of mooring systems,
immediate intervention would be required to regain system integrity.
Assumptions will have to be made if data is not available for all components
(i.e. using the failure rates of similar components or sub-systems).

.. _tab-failures:

.. figure:: /images/technical/failures.png

   Reported non-production mooring failures 1981-2009 and estimated probability of failure (based on a 30 year interval)


**FAILURE TYPES**

Clearly not all failures will result in system downtime and some may be
sufficiently minor to warrant delaying replacement until the next maintenance
interval. The OREDA Offshore Reliability Data Handbook (OREDA, 2009) which is
widely used in the offshore oil and gas industry defines three failure severity
levels:

* Critical failure – a failure which causes immediate and complete loss of an
  equipment unit's capability of providing its output
* Degraded failure – a failure which is not critical but prevents the unit
  from providing its output within specifications. Such a failure would
  usually, but not necessarily, be gradual or partial, and may develop into a
  critical failure in time
* Incipient failure – a failure which does not immediately cause loss of an
  equipment unit's capacity of providing its output, but which, if not attend
  to, could result in a critical or degraded failure in the near future

Within the RAM, two failure mode categories are used to distinguish between the
different consequences of failure: i) critical and ii) non-critical
(encompassing failures described by the ‘degraded’ and ‘incipient’ definitions
above). The corresponding parameters are failratecrit and failratenoncrit.

Within the O&M module, O&M scheduling will be based on the probability of
failure, failure mode and required repair action. Two runs of the RAM will be
conducted using the different failure rates associated with critical or
non-critical severity levels. This is effectively a simplified version of FMEA,
but assumes that all failures are independent (i.e. there are no cascade
failures).

Furthermore, it is unlikely that failure data will be available for all severity
classes. Therefore, by default RAM calculations are based on failure rates
associated with the highest available severity levels, with subsequent runs
utilising lower severity level values (where available).


**CONFIDENCE LEVELS**

Failure rates are often specified as single values, which usually correspond to
a calculated mean of many samples, possibly from multiple installations. A
single value does not provide any information on the variability of component
reliability over multiple installations (or the presence of outlying failures)
which could have a significant impact on the overall MTTF of the system and
associated system downtime and costs. Uncertainty levels provide a measure of
confidence of the baseline failure rate. If upper and lower uncertainty levels
are specified, the RAM functions will be called several times using lower, mean
and upper level failure rates. Therefore failratecrit and failratenoncrit are 1
x 3 vectors for each component. Three estimation scenarios are hence provided,
which are ‘optimistic’, ‘normal’ and ‘pessimistic’ from which the sensitivity
of lifecycle costs over the duration of the project can be analysed.

In addition to performing calculations with lower, mean and upper uncertainty
level failure rates, these values will be reported to the user to enable the
quality of the estimate if the sample population (which the failure rate is
based upon).


Result sets and the O&M module
''''''''''''''''''''''''''''''

Considering the two severity levels (ULS, ALS) and three failure rate confidence
levels (upper, mean andlower) introduced in above, six result sets are
generated by the RAM. It is highly unlikely, given the current state of the MRE
sector, that failure rate data will be available for all six factors for all
components. To cater for the situation where data is limited for some
components, runs of the RAM for lower and upper uncertainty levels and
non-critical failures will use mean, critical failure rates for these
components. This enables full system analysis to be conducted even if a
complete set of data is not available. The time domain calculations which take
place within the O&M module are computationally demanding in terms of the time
required to simulate failure events for all components in a system. To avoid
the need to analyse all of the six result sets from the RAM, the O&M module
will only focus on a ‘best’ and ‘worst’ case scenario related to highest and
lowest calculated TTFs.

The base design of the module does not contain an optimisation function; it
simply calculates reliability metrics based on the provided information. An
extension could be provided so that if the calculated MTTF of the system does
not meet the user-specified target, the RAM will try to identify which part of
the system can be improved in terms of reliability (i.e. which sub-system has
the lowest overall reliability) and request that changes are made by the
corresponding module (Moorings and Foundations or Electrical Sub-Systems). Once
changes have been made (i.e. replacing a component with a more reliable, but
perhaps more costly equivalent) the RAM will be rerun.


Functional specification
^^^^^^^^^^^^^^^^^^^^^^^^

Inputs
''''''

The input parameters required by the RAM, their format and source (or
destination) are provided below:


.. image:: /images/technical/RAM_inputs.png


Outputs
'''''''


The output parameters provided to the O&M, Electrical Sub-Systems and Moorings
and Foundations modules and the user are described here:

.. image:: /images/technical/RAM_outputs.png


Within the following subsections several of the inputs and outputs are explained
in more detail.  The user-defined hierarchy and BoM will both be empty by
default (i.e. and hence all device sub-systems apart from the Moorings and
Foundations and Electrical Sub-Systems are assumed to never fail). If the user
wishes to populate the system with blocks to represent devices or devices
comprising multiple sub-systems (i.e. for the power take-off system, structure
etc.) this is possible via a reliability block diagram.  The minimum required
data for the RAM to function is a mean failure rate (by default this is assumed
to represent a critical failure) for each device or sub-system.


.. _fig-parallel:

.. figure:: /images/technical/parallel.png

   Example parallel configuration including Moorings and Foundations elements and user specified power take off (PTO) sub-systems for two devices. For brevity inter-array cabling and the export cable are not shown


For the example shown in :numref:`fig-parallel` the hierarchy and bill of
materials for the user-defined PTO systems are shown below: ::

   Hierarchy
   {'device001': {'Power take off system': ['generator']},
   'device002': {'Power take off system': ['generator']}}
   
   Bill of materials
   {'device001': {'quantity': Counter({'generator': 1})},
   'device002': {'quantity': Counter({'generator': 1})}}

In this way the user can specify additional elements down to component level.
For example if the user wished to include a gearbox the hierarchy and bill of
materials would become: ::

   Hierarchy
   {'device001': {'Power take off system': ['generator', ‘gearbox’]},
   'device002': {'Power take off system': ['generator', ‘gearbox’]}}
   
   Bill of materials
   {'device001': {'quantity': Counter({'generator': 1, 'gearbox': 1})},
   'device002': {'quantity': Counter({'generator': 1,'gearbox': 1})}}

The main outputs of the RAM are component MTTFs (which are used by the O&M
module), information for the user and results stored in a log file. Reliability
information is presented to the user via a tree structure. The tree provides a
breakdown of the calculated system reliability into sub-system and component
levels, thereby allowing the user to explore the system (i.e. locate components
with low reliability). The following information is provided in the tree
structure:

* System, subsystem or component name
* MTTF
* Risk priority numbers

Risk priority numbers are calculated within the RAM based on the frequency of
failure and severity level of each component. Using the approach suggested in
(National Renewable Energy Laboratory, 2014) failure frequency bands are
defined by estimated probability of failure ranges
(:numref:`tab-failure-freq`). RPNs increase with failure frequency and severity
level and can be colour-coded (:numref:`tab-risk`).

.. _tab-failure-freq:

.. figure:: /images/technical/failure_freq.png

   Failure frequencies for several probability of failure ranges (from (National Renewable Energy Laboratory, 2014))
   
.. _tab-risk:

.. figure:: /images/technical/risk.png

   Risk Priority Number matrix with possible colour coding scheme (adapted from (National Renewable Energy Laboratory, 2014))

In order for the user to be able to identify high-risk components and
sub-systems which may require unplanned corrective maintenance, the calculated
RPNs and time-varying system reliability are also presented here.

.. _fig-RPN:

.. figure:: /images/technical/RPN.png

   Example (left) RPN and (right) system reliability plots


