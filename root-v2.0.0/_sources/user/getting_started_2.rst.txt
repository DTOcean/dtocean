.. _getting_started_2:

***********************************
Getting Started 2: Example Database
***********************************

This section provides a brief demonstration of preparing a DTOcean simulation
using the example database. Instructions for installing the database are
provided in the :ref:`database_installation` section. Two site and device
records are provided, the first being the RM3 example explored in the 
:ref:`getting_started_1` chapter and the second being an artificial tidal 
energy example. We will work with the tidal energy scenario for this tutorial.

.. _initiate_project:

Initiate the Project
====================

The first step is to create a new DTOcean project and select the required
device type, in this case a fixed tidal energy converter. As seen in 
:numref:`fig_new_action`, click the "New" button in the main toolbar to
create the project.

.. _fig_new_action:
.. figure:: /images/new_action.png

   Left-click the "New" button

The pipeline header should now display "Define scenario sections..." and a 
single variable will be visible, the "Device Technology Type". The value of 
this variable will determine the variables required for our simulations and for 
filtering the list of available technologies offered to us from the database. 
As shown in :numref:`fig_device_technology_type`, left click on the variable in 
the pipeline and then set the value to "Tidal Fixed", as shown in 
:numref:`fig_select_tidal_fixed`. 

.. _fig_device_technology_type:
.. figure:: /images/device_technology_type.png

   Left-click the "Device Technology Type" variable

.. _fig_select_tidal_fixed:
.. figure:: /images/select_tidal_fixed.png

   Set the "Device Technology Type" variable to "Tidal Fixed"

To commit the chosen value, click the "OK" button in the main window, as shown
in :numref:`fig_ok_button_2`.

.. _fig_ok_button_2:
.. figure:: /images/ok_button.png

   Left-click the "OK" button


Connect the Database
====================

The next step is to configure and connect the database. Open the database 
selection dialogue by clicking the "Select Database" button in the main 
toolbar, as shown in :numref:`fig_select_database_action`. 

.. _fig_select_database_action:
.. figure:: /images/select_database_action.png

   Left-click the "Select Database" button

The select database dialogue provides a list of saved credentials for 
databases, the ability to add, delete or modify credentials, a means to apply 
the provided credentials to the current project, and a tool for dumping and 
loading the chosen database to and from structured files. For the purposes of 
this tutorial we will use the predefined "local" database credentials and 
modify them as required. Optionally, we can save the modifications for later 
reuse. First, click the "local" database in the list of available credentials, 
as seen in :numref:`fig_local_database`. Note, if the credentials are different
to what is shown here, see the :ref:`configuration_files` section.

.. _fig_local_database:
.. figure:: /images/local_database.png

   Left-click the "local" database in the list of available databases

The saved credentials will appear in the "Credentials:" section of the dialogue 
and at this stage the password field ("pwd") will be empty. Double-click the 
cell in the "Value" column to edit this value and add the password you chose 
when setting up the "dtocean_user" login role for the database. The table 
should look similar to :numref:`fig_credentials_pwd` when finished. Note, if 
you chose a different name for the login role, then you should also edit the 
"user" field. 

.. _fig_credentials_pwd:
.. figure:: /images/credentials_pwd.png

   Add the password for login role "dtocean_user" to the "pwd" field

At this point, you can optionally save the password for later use, by 
left-clicking the "Save" button, as shown in :numref:`fig_save_credentials`.
As passwords are saved in plain text (in the users AppData folder), you should
not save your password if you have any security concerns. In this case, add
you password to the "pwd" field each time you connect to the database.

.. _fig_save_credentials:
.. figure:: /images/save_credentials.png

   Save the credentials by left-clicking the "Save" button

When the password (and any other field) has been correctly set, click the apply 
button, as shown in :numref:`fig_database_apply`. The "local" database should 
now be shown as the current database, as in 
:numref:`fig_current_database_local`. The dialogue can now be closed by 
left-clicking the "Close" button. 

.. _fig_database_apply:
.. figure:: /images/database_apply.png

   Left-click the "Apply" button

.. _fig_current_database_local:
.. figure:: /images/current_database_local.png

   The currently selected database is displayed

Select the Site and Device
==========================

To collect the list of available sites and the filtered list of devices (based 
on our technology choice), we must initiate the "pipeline" (think of this as 
building the pipework that our data will flow along). Click the "Initiate 
Pipeline" button in the toolbar, as shown in 
:numref:`fig_initiate_pipeline_action`. DTOcean will now open the data 
requirements dialogue and check if the device type has been set. Click "OK" to 
close it if shows "PASSED", otherwise click "Cancel" and go back to the 
:ref:`initiate_project` section. Note, you can initiate the pipeline without 
selecting a database, but a device type must be set. 

.. _fig_initiate_pipeline_action:
.. figure:: /images/initiate_pipeline_action.png

   Left-click the "Initiate Pipeline" button

.. _fig_database_filtering_interface:
.. figure:: /images/database_filtering_interface.png

   The "Database Filtering" variables, ready to be set

The variables "Selected Site" and "Selected Device" should now appear in the 
"Database Filtering Interface" branch of the pipeline as shown in 
:numref:`fig_database_filtering_interface`. Now set each variable using the 
values given in table :numref:`tab_database_filtering`. An example of setting
the "Selected Site" variable is shown in :numref:`fig_selected_site`.

.. _tab_database_filtering:
.. table:: Database filtering variable values

    +------------------+----------------------+
    | Variable         | Value                |
    +==================+======================+
    | Selected Site    | Example Tidal Site   |
    +------------------+----------------------+
    | Selected Device  | Example Tidal Device |
    +------------------+----------------------+

.. _fig_selected_site:
.. figure:: /images/selected_site.png

   Choose the "Example Tidal Site" in the drop-down menu, then click "OK"

Remember to click "OK" after selecting the values to commit them. The 
indicators on both variables should be green, as shown in 
:numref:`fig_database_filtering_green` Once a site is selected, an additional 
step is required to collect bathymetric data. 

.. _fig_database_filtering_green:
.. figure:: /images/database_filtering_green.png

   The "Database Filtering" variables, after being set

Select the Bathymetry
=====================

In order to choose how much bathymetric data to collect from the database, we 
must initiate the project boundaries interface. From the main toolbar click the 
"Initiate Bathymetry" button, as shown in 
:numref:`fig_initiate_bathymetry_action`. 

.. _fig_initiate_bathymetry_action:
.. figure:: /images/initiate_bathymetry_action.png

   Left-click the "Initiate Bathymetry" button

After passing the data check, the "Project Boundaries Interface" branch will 
now appear in the pipeline. This branch contain the variables used to define 
the desired lease area and cable corridor boundaries and the export cable 
landing point (see the :ref:`data_preparation` chapter for a full 
explanation of these terms). The initial boundaries cover the extent of all 
bathymetric data for the site, but we are going to use a smaller area for this 
tutorial. To visualise the default boundary positions, select the "Lease 
Boundary" variable from the "Project Boundaries Interface" branch of the 
pipeline, as shown in :numref:`fig_project_boundaries_interface`. Then switch 
the interface to the plots context, using the toolbar button, as shown in 
:numref:`fig_plots_context_2`. 

.. _fig_project_boundaries_interface:
.. figure:: /images/project_boundaries_interface.png

   Left-click the "Lease Boundary" variable

.. _fig_plots_context_2:
.. figure:: /images/plots_context.png

   The "plots context" is used for viewing plots

The default plot shows the lease area boundary polygon and the coordinates of 
its vertices. Further insight can be gained by examining all of the required 
boundaries together and we use a custom plot to achieve this. In the "Plot 
Manager" widget, above the main window, select "Design Boundaries" from the 
drop-down list of plots in the "Plot name:" field, as shown in 
:numref:`fig_plot_design_boundaries`. Now click the "Plot" button, as shown in 
:numref:`fig_plot_button`, to replace the default plot (the default plot can 
be restored by clicking the "Default" button). A digram similar to 
:numref:`fig_design_boundaries_plot` should be displayed. 

.. _fig_plot_design_boundaries:
.. figure:: /images/plot_design_boundaries.png

   Select the "Design Boundaries" plot in the "Plot Manager" widget

.. _fig_plot_button:
.. figure:: /images/plot_button.png

   Left-click the "Plot" button

.. _fig_design_boundaries_plot:
.. figure:: /images/design_boundaries_plot.png

   Plot of the design boundaries and export cable landing point

We are now going to reduce the extent of the lease area and modify the cable 
corridor to match. This is undertaken in the "Data" context, so switch back 
using the toolbar button, as shown in :numref:`fig_data_context_2`. The data 
table containing the :math:`(x,y)` coordinates of the lease area boundary 
polygon vertices should now be displayed. To edit the vertices, the table must 
first be placed into editing mode. This is achieved by clicking the "toggle 
editing mode" button in the main window, as shown in 
:numref:`fig_toggle_editing_mode`. 

.. _fig_data_context_2:
.. figure:: /images/data_context.png

   The "data context" is used for entering input data and viewing results

.. _fig_toggle_editing_mode:
.. figure:: /images/toggle_editing_mode.png

   Left-click the "toggle editing mode" button

.. _fig_edit_lease_area_coordinate:
.. figure:: /images/edit_lease_area_coordinate.png

   Use the table to modify the lease area coordinates

Once the editing mode has been enabled, you can double-click on the cells in 
the table to edit their data. Double-click on the "x" coordinates that have 
value "586500" and change the value to "588000", as shown in 
:numref:`fig_edit_lease_area_coordinate`. Click the "OK" button after the two 
coordinates have been changed to commit the new polygon and then repeat the 
process for the "Cable Corridor Boundary" boundary. The final coordinates for 
the lease and cable corridor boundaries are shown below. 

.. rubric:: Modified Lease Boundary Coordinates

.. table::

    +----------+-----------+
    |    x     |     y     |
    +==========+===========+
    | 588000.0 | 6651000.0 |
    +----------+-----------+
    | 588000.0 | 6653000.0 |
    +----------+-----------+
    | 588500.0 | 6653000.0 |
    +----------+-----------+
    | 588500.0 | 6651000.0 |
    +----------+-----------+
    
.. rubric:: Modified Cable Corridor Boundary Coordinates

.. table::

    +----------+-----------+
    |    x     |     y     |
    +==========+===========+
    | 588000.0 | 6651800.0 |
    +----------+-----------+
    | 588000.0 | 6652200.0 |
    +----------+-----------+
    | 590175.0 | 6652200.0 |
    +----------+-----------+
    | 590175.0 | 6651800.0 |
    +----------+-----------+

Now return to the plots context and open the "Design Boundaries" plot once 
more. The lease area and cable corridor should be reduced in size, as seen in 
:numref:`fig_design_boundaries_plot_updated` [#f1]_. 

.. _fig_design_boundaries_plot_updated:
.. figure:: /images/design_boundaries_plot_updated.png

   Plot of the updated design boundaries

Add Modules and Assessment 
==========================

The final stage before collecting the data from the database is to choose which
design modules and assessments we want for our simulation. In this example, 
we add the first three design modules (hydrodynamics, electrical sub-systems,
and mooring and foundations) and the economics assessment module. To add design
modules, click the "Add Modules" button in the main toolbar, as seen in
:numref:`fig_add_modules_action`.

.. _fig_add_modules_action:
.. figure:: /images/add_modules_action.png

   Left-click the "Add Modules" button

A shuttle dialogue will open which allows you to select which modules are 
required for the simulation. Select the desired module from the "Available:" 
list, and click the "Add" button, as seen in :numref:`fig_add_modules_shuttle`. 
The figure shows how the dialogue should look once the three modules are 
selected. If you accidentally add the wrong module, select it in the 
"Selected:" list and click the "Remove" button to deselect it. Click the "OK" 
button to accept your choice.

.. _fig_add_modules_shuttle:
.. figure:: /images/add_modules_shuttle.png

   Add Hydrodynamics", "Electrical Sub-Systems" and "Mooring and
   Foundations" to the list of selected modules

A similar process is used for adding assessments. Click the "Add Assessment" 
button, as shown in :numref:`fig_add_assessment_action` and use the shuttle to 
select the "Economics" assessment, as shown in 
:numref:`fig_add_assessment_shuttle`. Once again, click "OK" to accept the 
choice.

.. _fig_add_assessment_action:
.. figure:: /images/add_assessment_action.png

   Left-click the "Add Assessment" button

.. _fig_add_assessment_shuttle:
.. figure:: /images/add_assessment_shuttle.png

   Add "Economics" to the list of selected assessments

Initiate the Dataflow
=====================

The system is now ready to determine which variables are required to run the 
chosen modules and assessments and to collect available data from the database 
based on our selections. In DTOcean, this process is referred to as "initiating 
the dataflow", and the "Initiate Dataflow" button, in the main toolbar as seen 
in :numref:`fig_initiate_dataflow_action`, is used to start the process. 

.. _fig_initiate_dataflow_action:
.. figure:: /images/initiate_dataflow_action.png

   Left-click the "Initiate Dataflow" button

Once the process has completed the pipeline will populate with the variables 
required to run each module (and assessment) and indicate their status using 
icons with coloured shapes. A green square indicates that the variable contains 
data (satisfied), a blue diamond indicates that the variable contains no data 
but does not have to be satisfied (optional) and a red square indicates that 
the variable does not yet contain data but some must be added before the module 
can execute (required). The variables for the Hydrodynamics module should 
appear like :numref:`fig_required_project_variables`. 

.. _fig_required_project_variables:
.. figure:: /images/required_project_variables.png

   Variables required to run the "Hydrodynamics" module and their status
   indicators

Add Project Data
================

The DTOcean database does not contain variables that are specific only to the 
project being simulated and these must be added prior to execution of our 
simulation. :numref:`tab_tidal_example_inputs` provides a list of recommended 
values for all required and some optional variables. Note that satisfying 
optional variables may be required for the module to execute correctly for a 
particular simulation, as is the case here.

.. _tab_tidal_example_inputs:
.. table:: Recommended input values

    +-----------------------+----------------------------+---------+
    |        Branch         |          Variable          |  Value  |
    +=======================+============================+=========+
    |Hydrodynamics          |Array Rated Power           |      4.8|
    +-----------------------+----------------------------+---------+
    |Hydrodynamics          |Tidal Probability Bins      |       12|
    +-----------------------+----------------------------+---------+
    |Hydrodynamics          |Lease Area Boundary Padding |       25|
    +-----------------------+----------------------------+---------+
    |Hydrodynamics          |Minimum Q-Factor            |     0.98|
    +-----------------------+----------------------------+---------+
    |Hydrodynamics          |Power Histogram Bin Width   |     0.04|
    +-----------------------+----------------------------+---------+
    |Hydrodynamics          |User Option for Array Layout|Staggered|
    +-----------------------+----------------------------+---------+
    |Electrical Sub-Systems |Network Configuration       |   Radial|
    +-----------------------+----------------------------+---------+
    |Electrical Sub-Systems |Maximum Seabed Gradient     |       14|
    +-----------------------+----------------------------+---------+
    |Mooring and Foundations|Foundation Safety Factor    |        1|
    +-----------------------+----------------------------+---------+
    |Mooring and Foundations|Grout Strength Safety Factor|        1|
    +-----------------------+----------------------------+---------+
    |Mooring and Foundations|Concrete Cost per kg        |     0.05|
    +-----------------------+----------------------------+---------+
    |Mooring and Foundations|Grout Cost per kg           |     0.05|
    +-----------------------+----------------------------+---------+
    |Mooring and Foundations|Steel Cost per kg           |        5|
    +-----------------------+----------------------------+---------+

When entering the values, ensure that the :ref:`data_context` is active (the 
:ref:`menu_view` menu is used to change contexts). Also, using the variable 
:ref:`filter` will make finding the variables much easier. 

Execute the Simulation
======================

After the variables have been set, the process described from the 
:ref:`exectute_simulation` section of the :ref:`getting_started_1` chapter can 
be used to execute the simulation and inspect the results. The expected total 
CAPEX should be around 12 million Euro. 

This completes this tutorial. For information about preparing and adding new
data to the database please see the :ref:`data_preparation` chapter.

.. rubric:: Footnotes

.. [#f1] The lease area and the cable corridor should always have some 
         overlapping grid points.
