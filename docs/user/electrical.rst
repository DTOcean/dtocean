.. _user_elec:

Electrical Sub-Systems module
-----------------------------

Introduction
^^^^^^^^^^^^

The purpose of the Electrical Sub-Systems module is to identify and compare
technically feasible offshore electrical network configurations for a given
device, site and array layout. The scope covers all electrical sub-systems from
the OEC array coupling up to the onshore landing point, including: the
umbilical cable, static subsea intra-array cables, electrical connectors,
offshore collection points and the transmission cables to the onshore grid. The
DTOcean tool remit does not consider the capital cost of onshore electrical
infrastructure, but, if so desired, the user can enter a cost of these
subsystems to be included when assessing the system LCOE.

Architecture
^^^^^^^^^^^^

The design philosophy of the Electrical Sub-Systems module complements real
world design approaches by separating the design process into a number of
discrete phases. In the automated network design process developed for the
DTOcean tool, the electrical network is divided into three main subsystems: the
intra-array network, a number of offshore collection points and the
transmission cable system. A simplified schematic of the subsystems and the
connection between them is shown in :numref:`fig-elec-network-user`.


.. _fig-elec-network-user:

.. figure:: /images/user/elec_network.png

   Simplified generic offshore electrical network for OEC arrays

   
Ultimately, the network design process is defined by the following factors:

 * The transmission voltage, capacity and  number of transmission cables;
 * The number, location and type of offshore collection points;
 * The intra-array network topology, i.e. number of OEC devices per string,
   number of strings, voltage level, and umbilical geometry (for floating
   devices);
 * Optimal cable routing and protection for the transmission system and
   intra-array cable networks.

These design criteria are constrained by the physical environment, power flow
constraints and available components. In order to produce a valid solution
within the available design space, the Electrical Sub-System module is driven
by the following key concepts.

 * Seabed filtering: This filtering process incorporates user-defined
   exclusion zones and installation equipment compatibility to provide a
   suitable seabed area for placing electrical components.
 * Physical design: The cable routing algorithm designs a route for cables
   along the seabed.
 * Network design: Two network design topologies are considered: radial
   strings and hub layouts. The network design process utilises a number of
   heuristics to limit the number of design options; using the relationship
   between transmission distance, power and voltage to determine acceptable
   voltage levels for collection point design.
 * Power flow analysis: A three-phase steady-state power flow solver is
   included within the DTOcean tool. This provides AC and DC power flow
   solution routines.

Using these concepts the Electrical Sub-Systems module selects a toplogy and
components in order to produce a local level best solution. This local solution
is obtained by calculating and comparing the overall network efficiency (i.e.
network losses) and component costs. The realisation of this as structured
software is outlined in :numref:`fig-elec-model-user`, with cable routing and
collection point design functionality shared between the transmission system
and intra-array network design.

.. _fig-elec-model-user:

.. figure:: /images/user/elec_model.png

   Electrical Sub-Systems model top level view.


Functional specifications
^^^^^^^^^^^^^^^^^^^^^^^^^

Inputs
''''''

The required input data to execute the Electrical Sub-Systems modules is given
in :numref:`tab-elec-inputs`.

.. _tab-elec-inputs:

.. figure:: /images/user/elec_inputs.png

   Inputs of the Electrical Sub-Systems module.


Execution
'''''''''

Once the Electrical Sub-Systems module has been selected and data loaded in the
GUI, the user can define a number of options to target the solution in a
particular direction. These are defined in :numref:`tab-elec-options`. These
options are also compatible with the DTOCEAN strategy scenario analysis defined
in N.N.


.. _tab-elec-options:

.. figure:: /images/user/elec_options.png

   User options of the Electrical Sub-Systems module.
   

Outputs
'''''''

The output data returned by the Electrical Sub-Systems modules is given in
:numref:`tab-elec-outputs`.

.. _tab-elec-outputs:

.. figure:: /images/user/elec_outputs.png

   Outputs of the Electrical Sub-Systems module.

