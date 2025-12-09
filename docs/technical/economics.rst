.. _tech_economics:

Economics Module (EM)
---------------------

Requirements
^^^^^^^^^^^^

User Requirements
'''''''''''''''''

The ‘economic assessment’ module takes the array configuration determined by the
design modules previously described and estimates the LCOE for the project. The
LCOE is the indicator used for benchmarking different possible solutions, and
the global optimization routine objective is to minimize it.

Within each design module there are economic functions that calculate the
lifetime costs of the corresponding subsystem. These will be used as input for
the LCOE calculation.

The ‘economic assessment’ module is composed of a set of functions that are used
to calculate the LCOE, which can be called separately or as a whole. It
requires information from all the other modules, as well as user inputs.


Software Design Requirements
''''''''''''''''''''''''''''

For the total LCOE calculation, a list of components used for the project is to
be provided from the other com- putation design modules, with the required
quantities and the related cost, which will have been calculated within each of
these modules or provided by the database or the end-user.

The current ‘economic assessment’ module includes four separate functions,
although “df_lcoe” is the integration of the other three:

 * item_total_cost
 * present_value
 * simple_lcoe
 * df_lcoe

The functions and their interactions with the inputs are presented in a
diagrammatic form in :numref:`fig-arch-economic`. A more detailed explanation
of each component can be found further in this document.

The first three functions can take single or multiple values as inputs, while
the last one assumes that the inputs are in the format of pandas tables, with
specific columns.

For the df_lcoe function, two tables are expected as inputs:

 * **Bill of materials** table, including the following columns:

   * **item**: identifier column, not used in the function
   * **quantity**: number of units of item
   * **unitary_cost**: cost per unit of the item. It assumes that it
     matches the units of the quantity
   * **project_year**: year relative to the start of the project when the
     cost occurs (from year 0 to the end of the project)

 * **Energy output table**, including the following columns:

   * **project_year**: year relative to the start of the project when the
     cost occurs (from year 0 to the end of the project)
   * **energy**: final annual energy output. This value accounts for the
     hydrodynamic interaction, transmis- sion losses and downtime losses

The other input of the df_lcoe function is the discount rate, which is assumed
to remain constant during the lifetime of the project, and is a single float
value from 0. to 1. to represent the discount rate percentage.


Architecture
^^^^^^^^^^^^

.. _fig-arch-economic:

.. figure:: /images/technical/arch_economic.png

   Detailed flowchart of the economic assessment module
   
The function **item_total_cost** takes the information of quantity and unitary
cost and calculates the total cost within the context of the array in analysis.
At this stage it is a simple multiplication, but it could be expanded to
account for scaling factors or bulk discounts.

Furthermore, the function assumes that all cost data is presented in the right
units to match the quantities, and that the currency is the same. Further
functions dealing with units and currency conversion could be developed.

The cost values can, at most, be grouped by year, as the present value function
will have to be applied before the LCOE calculation. However, it can be
interesting for the user and for the other modules to have the total cost
values detailed by activity (or by design module) or even at an item level.

The function **present_value** transforms any future value into a present value
assuming a specific discount rate. The present value function is applied to
costs and energy output, using the discount rate set by the user. To calculate
the present value of the costs, this function assumes that the total cost has
already been calculated using the previous function. If the year-on-year costs
are equal, the present value can be calculated for lump sums, instead of on an
item by item basis.

The function **simple_lcoe** uses the sum of the present values, as in the
formula below, calculated with the previous function as inputs: sum of all
costs and sum of all energy outputs.


.. math::

   LCOE = \frac{(CAPEX_0 + OPEX_0) + \sum^n_{i=1} \frac{CAPEX_i + OPEX_i}{(1+r)^i}}{\sum^n_{i=1}\frac{AEP_i}{(1+r)^i}}


The function **df_lcoe** takes the preformatted inputs in the format of pandas
DataFrame tables (bill of materials, energy output), as described in the
previous section and applies the previous functions.

For the BoM table, the function creates a new column (‘cost’) for present value
of the total cost, by applying first the item_total_cost function, and then the
present_value one. It then sums all the cost calculated, which will be the
first input for the simple_lcoe function.

For the energy output table, the function creates a new column
(‘discounted_energy’) by applying the present_value function. Like in the
previous table, it then sums all the calculated energy outputs. This sum will
be the second input for the simple_lcoe function.

The output of this function is the LCOE, expressed in €/MWh.

Intermediate or other functions could be developed to evaluate how the LCOE
changes during the project lifetime as an extension to the base functionality.


Functional Specification
^^^^^^^^^^^^^^^^^^^^^^^^

The cost of the OEC devices can be provided by the user as an optional input. As
with the other costs assumed in the software, these are expected to be given in
Euro currency.

The discount rate is also to be provided by the user, as it is dependent on the
investor’s valuation of risk and investment opportunities. Typical values of
discount rate for marine energy projects range between 8-15% (Allan et al.,
2011; Andrés et al., 2014; Carbon Trust, 2011, 2006; Ernst & Young and Black &
Veatch, 2010; SQWenergy, 2010) but in LCOE evolution analysis is typical to use
values between 10% and 12% (Carbon Trust, 2006, p. 200; OES, 2015; SI-OCEAN,
2013). More information on the discount rate can be found elsewhere (DTOcean,
2015j).

The dates at which costs are incurred are also required as an input and will be
an output from the Installation and O&M modules. Alternatively, for capital
expenditures, it could be assumed that all costs occur in year zero.

The final input required from the other design modules is the annual energy
output. To the calculation of the LCOE only the final energy output is needed,
which to be provided by the operations and maintenance module after the
downtime has been assessed. However, the input of the LCOE function could also
be the unconstrained energy, but it should be noted that then the LCOE will be
underestimated. There is value is calculating this overoptimistic LCOE, as it
provides a metric on the impact of downtime and other losses calculated by the
software.

The main output of the ‘economic assessment module’ is the LCOE, presented in
terms of €/MWh. Other outputs can be produced from the building blocks of the
LCOE function, such as total lifetime costs (presented in €) and the total
expected electricity production (expressed in MWh).


Inputs
''''''

The Economics module requires inputs from other modules and from the user. The
inputs from other modules can always be overwritten by the user.

The Bill of Materials is generated by the core from the outputs of the other
design modules. It is formatted as a pandas tables, with the following fields:

 * **item**: identifier column, not used in the function
 * **quantity**: number of units of item
 * **unitary_cost**: cost per unit of the item. It assumes that it matches
   the units of the quantity
 * **project_year**: year relative to the start of the project when the cost
   occurs (from year 0 to the end of the project)

The second set of inputs generated by the tool relates to the energy production.
It also formatted as a pandas table, with the following columns

 * **project_year**: year relative to the start of the project when the cost
   occurs (from year 0 to the end of the project)
 * **energy**: final annual energy output. This value accounts for the
   hydrodynamic interaction, transmission losses and downtime losses

The **project_capacity** input, referring to project capacity in MW, is an
output from the Array Hydrodynamic module, by using the number of devices
output and the user input on device rating.

The inputs **a_energy_wo_elosses** and **a_energy_wo_availability** are outputs
from the the Array hydrodynamic and Electrical sub-systems modules,
respectively. The input a_energy_wo_elosses indicates the average annual
unconstrained energy production, before electrical losses; while
a_energy_wo_availability indicates the average annual energy production
accounting for electrical losses, but without accounting for availability. 

From the user, the following inputs are required:

 * **project_lifetime**: duration of the project in number of years
 * **discount_rate**: discount rate for the project in analysis. The discount
   rate is dependent on the investor’s valuation of risk and other investment
   opportunities.


Outputs
'''''''

The main output of the economics theme module is the
**levelized cost of energy** (LCOE) of the project, expressed in €/MW. The
building blocks of the LCOE calculation,
**CAPEX, OPEX and Annual Energy Production**, are also outputs of the module

This allows for the representation of the contribution of CAPEX and OPEX to the
LCOE, the contribution of each sub-system/module, or the evaluation per device.
