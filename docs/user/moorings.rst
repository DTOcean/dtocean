.. _user_moor:

Moorings and Foundations module
-------------------------------

Introduction
^^^^^^^^^^^^

The main aim of the DTOcean Mooring and Foundation design module is to perform
static and quasi-static analysis to inform or develop mooring and foundation
solutions that:

 * are suitable for a given site, the MRE device (and substation), and
   expected loading conditions;
 * retain the integrity of the electrical umbilical that connects the MRE
   device to the subsea cable;
 * are compatible with the array layout (i.e., prevents clashing of
   neighbouring devices) and subsea cable layout;
 * fulfil requirements and/or constraints determined by the user and/or in
   terms of reliability and/or environmental concerns; and
 * have the lowest capital cost. 

Architecture
^^^^^^^^^^^^

Dataflow through the module is linear, utilising inputs supplied by the Tool
Core but originating from: i) the user (via the graphical user interface
(GUI)), ii) the Hydrodynamics and Electrical System Architecture modules
(umbilical requirements and subsea infrastructure details) and iii) from the
global Tool database. For floating devices the Mooring and Foundation module
interacts with the Umbilical sub-module to ensure that the solutions for
mooring system and umbilical together are suitable for the site, device and
conditions.


.. _fig-moor-module:

.. figure:: /images/user/moor_module.png

   Mooring and foundation module top level view


The Mooring and Foundation module comprises four interlinked sub-modules: the
System and environmental loads sub-module, Substation sub-module, Mooring
sub-module and Foundation sub-module. In addition the Mooring sub-module
communicates with the Umbilical module located outside of the Mooring and
Foundation module (with communication occurring via the Tool Core).
:numref:`fig-moor-module` shows the data flow through the module.


Functional specifications
^^^^^^^^^^^^^^^^^^^^^^^^^

The use defined inputs are described in the input table below. Certain inputs
are listed as optional, where the user chooses not to provide the optional
input values then default values will be provided from the database. These
inputs will be provided to the tool via the DTOcean graphical user interface.


Inputs
''''''

The :numref:`fig-moor-inputs` give an overview of the inputs required by the
user to run the Mooring and Foundation module. Some of them are compulsory and
others are optional.
 
.. _fig-moor-inputs:

.. figure:: /images/user/moor_inputs.png

   List of inputs for Mooring and foundation module


Execution
'''''''''

Outputs
'''''''

The moorings and foundations modules provides the user with output tables
detailing the selected mooring, foundation and umbilical design. Several output
Tables are created:

 * Array level mooring installation table (floating devices only): This
   details the moorings system design. For each mooring line of each device the
   type, length and mass are provided and the markers representing all of the
   individual components are listed (see example in :numref:`fig-moor-tables`).
 * Array level foundation installation table: This details the foundation
   system design. For each anchor or foundation the type, component marker,
   position, depth, dimensions, installation depth and mass are included. The
   soil type at the foundation location is listed. For pile type foundation the
   grout type and volume are provided (see example in :numref:`fig-moor-array`).
 * Array level umbilical installation table: The details the design of the
   umbilical cable.  For each device the component ID and marker number of the
   umbilical cable is specified.  Also specified is the subsea connection
   point, the depth, length and mass of the cable (see example in
   :numref:`fig-moor-umbilical`).
 * Array level economics bill of materials:  This table lists all of the
   components used in the mooring, foundation and umbilical system design, the
   quantity of each and the total cost.
 * Array level RAM bill of materials / Array level RAM hierarchy:  These
   tables provides the reliability assessment module with the list of
   components and their position in the system to enable the reliability
   calculations to be carried out.


.. _fig-moor-tables:

.. figure:: /images/user/moor_tables.png

   Example output tables : Array Level Mooring Installation Table (floating devices only)


.. image:: /images/user/moor_array1.png

.. _fig-moor-array:

.. figure:: /images/user/moor_array2.png

   Example of Array level foundation installation table
   
   
.. _fig-moor-umbilical:

.. figure:: /images/user/moor_umbilical.png

   Example of Array Level Umbilical Installation

