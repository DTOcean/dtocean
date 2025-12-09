.. _database_tables:

Database Tables
===============

All database tables used in the DTOcean database are listed here, alongside
additional useful information. A typical table is described as follows:

Table:
    The table name

Approximate dump path:
    When using the :ref:`database dump<load_dump>` function, a tree of files
    is generated. The path to the file representation of each table is given 
    here. As file types can vary, each path ends ``.*``. If the path contains a 
    ``#`` then the tables has been split across multiple directories, 
    sequentially numbered.

Linked to:
    If one of the columns in the given table references a column in another
    table, then the table name (or names) of the referenced tables are given
    here.

See
    If relevant information is available elsewhere in the chapter then a link
    will be provided here.

Details relating to each column are presented in a table. The headings of the
table have the following meanings:

.. table:: 
    :widths: 35, 65

    +---------------+-------------------------------------------+
    | Column        | The table column                          |
    +---------------+-------------------------------------------+
    | Variable Name | The DTOcean variable name                 |
    +---------------+-------------------------------------------+
    | Label         | The sub-section of the variable (if used) |
    +---------------+-------------------------------------------+
    | Unit          | The SI unit                               |
    +---------------+-------------------------------------------+


Project Schema
--------------

.. |project.bathymetry| replace:: ``project.bathymetry``
.. _project.bathymetry:

.. rubric:: Table: project.bathymetry

| Approximate dump path: ``site#\bathymetry.*``
| Linked to: |project.site|_
| See :ref:`bathymetry_sediments`

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+----------------+-----+----+
    |  Column   |Variable Name   |Label|Unit|
    +===========+================+=====+====+
    |id         |                |     |    |
    +-----------+----------------+-----+----+
    |utm_point  |Bathymetry      |     |    |
    +-----------+----------------+-----+----+
    |depth      |Bathymetry      |     |m   |
    +-----------+----------------+-----+----+
    |mannings_no|Manning's Number|     |    |
    +-----------+----------------+-----+----+


-------------------

.. |project.bathymetry_layer| replace:: ``project.bathymetry_layer``
.. _project.bathymetry_layer:

.. rubric:: Table: project.bathymetry_layer

| Approximate dump path: ``site#\bathymetry\bathymetry_layer.*``
| Linked to: |reference.soil_type|_; |project.bathymetry|_
| See :ref:`bathymetry_sediments`

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------+-------------+-----+----+
    |     Column     |Variable Name|Label|Unit|
    +================+=============+=====+====+
    |id              |             |     |    |
    +----------------+-------------+-----+----+
    |fk_bathymetry_id|             |     |    |
    +----------------+-------------+-----+----+
    |fk_soil_type_id |             |     |    |
    +----------------+-------------+-----+----+
    |layer_order     |Bathymetry   |     |    |
    +----------------+-------------+-----+----+
    |initial_depth   |Bathymetry   |     |m   |
    +----------------+-------------+-----+----+


-------------------

.. |project.cable_corridor_bathymetry| replace:: ``project.cable_corridor_bathymetry``
.. _project.cable_corridor_bathymetry:

.. rubric:: Table: project.cable_corridor_bathymetry

| Approximate dump path: ``site#\cable_corridor_bathymetry.*``
| Linked to: |project.site|_
| See :ref:`bathymetry_sediments`

.. table:: 
    :widths: 15, 50, 20, 15

    +---------+--------------------------+-----+----+
    | Column  |Variable Name             |Label|Unit|
    +=========+==========================+=====+====+
    |id       |                          |     |    |
    +---------+--------------------------+-----+----+
    |utm_point|Cable Corridor Bathymetry |     |    |
    +---------+--------------------------+-----+----+
    |depth    |Cable Corridor Bathymetry |     |m   |
    +---------+--------------------------+-----+----+


-------------------

.. |project.cable_corridor_bathymetry_layer| replace:: ``project.cable_corridor_bathymetry_layer``
.. _project.cable_corridor_bathymetry_layer:

.. rubric:: Table: project.cable_corridor_bathymetry_layer

| Approximate dump path: ``site#\cable_corridor_bathymetry\cable_corridor_bathymetry_layer.*``
| Linked to: |reference.soil_type|_; |project.cable_corridor_bathymetry|_
| See :ref:`bathymetry_sediments`

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------+--------------------------+-----+----+
    |     Column     |Variable Name             |Label|Unit|
    +================+==========================+=====+====+
    |id              |                          |     |    |
    +----------------+--------------------------+-----+----+
    |fk_bathymetry_id|                          |     |    |
    +----------------+--------------------------+-----+----+
    |fk_soil_type_id |                          |     |    |
    +----------------+--------------------------+-----+----+
    |layer_order     |Cable Corridor Bathymetry |     |    |
    +----------------+--------------------------+-----+----+
    |initial_depth   |Cable Corridor Bathymetry |     |m   |
    +----------------+--------------------------+-----+----+


-------------------

.. |project.cable_corridor_constraint| replace:: ``project.cable_corridor_constraint``
.. _project.cable_corridor_constraint:

.. rubric:: Table: project.cable_corridor_constraint

| Approximate dump path: ``site#\cable_corridor_constraint.*``
| Linked to: |project.site|_

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+-----------------------------+-----+----+
    |  Column   |        Variable Name        |Label|Unit|
    +===========+=============================+=====+====+
    |id         |                             |     |    |
    +-----------+-----------------------------+-----+----+
    |description|No Go Areas in Cable Corridor|     |    |
    +-----------+-----------------------------+-----+----+
    |boundary   |No Go Areas in Cable Corridor|     |    |
    +-----------+-----------------------------+-----+----+


-------------------

.. |project.constraint| replace:: ``project.constraint``
.. _project.constraint:

.. rubric:: Table: project.constraint

| Approximate dump path: ``site#\constraint.*``
| Linked to: |project.site|_

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+-----------------------------+-----+----+
    |  Column   |        Variable Name        |Label|Unit|
    +===========+=============================+=====+====+
    |id         |                             |     |    |
    +-----------+-----------------------------+-----+----+
    |description|Nogo Areas                   |     |    |
    +-----------+-----------------------------+-----+----+
    |boundary   |Nogo Areas                   |     |    |
    +-----------+-----------------------------+-----+----+


-------------------

.. |project.device| replace:: ``project.device``
.. _project.device:

.. rubric:: Table: project.device

| Approximate dump path: ``device.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+---------------------+-----------+----+
    |  Column   |    Variable Name    |   Label   |Unit|
    +===========+=====================+===========+====+
    |id         |All Available Devices|id         |    |
    +-----------+---------------------+-----------+----+
    |description|All Available Devices|description|    |
    +-----------+---------------------+-----------+----+
    |device_type|All Available Devices|device_type|    |
    +-----------+---------------------+-----------+----+
    |image      |                     |           |    |
    +-----------+---------------------+-----------+----+


-------------------

.. |project.device_floating| replace:: ``project.device_floating``
.. _project.device_floating:

.. rubric:: Table: project.device_floating

| Approximate dump path: ``device#\device_floating.*``
| Linked to: |project.device|_

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------+---------------------------------------+-----+----+
    |          Column          |             Variable Name             |Label|Unit|
    +==========================+=======================================+=====+====+
    |id                        |                                       |     |    |
    +--------------------------+---------------------------------------+-----+----+
    |draft                     |Floating Device Draft                  |     |m   |
    +--------------------------+---------------------------------------+-----+----+
    |maximum_displacement      |Maximum System Displacement            |     |m   |
    +--------------------------+---------------------------------------+-----+----+
    |depth_variation_permitted |Floating Device Submersible Option     |     |    |
    +--------------------------+---------------------------------------+-----+----+
    |fairlead_locations        |Fairlead Locations                     |     |m   |
    +--------------------------+---------------------------------------+-----+----+
    |umbilical_connection_point|Umbilical Cable Device Connection Point|     |m   |
    +--------------------------+---------------------------------------+-----+----+
    |prescribed_mooring_system |Mooring System Type                    |     |    |
    +--------------------------+---------------------------------------+-----+----+
    |prescribed_umbilical_type |Predefined Umbilical Cable Identifier  |     |    |
    +--------------------------+---------------------------------------+-----+----+


-------------------

.. |project.device_shared| replace:: ``project.device_shared``
.. _project.device_shared:

.. rubric:: Table: project.device_shared

| Approximate dump path: ``device#\device_shared.*``
| Linked to: |project.device|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------------------+-----------------------------------------------+------------+------+
    |           Column           |                 Variable Name                 |   Label    | Unit |
    +============================+===============================================+============+======+
    |id                          |                                               |            |      |
    +----------------------------+-----------------------------------------------+------------+------+
    |height                      |System Height                                  |            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |width                       |System Width                                   |            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |length                      |System Length                                  |            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |displaced_volume            |System Submerged Volume                        |            |m^{3} |
    +----------------------------+-----------------------------------------------+------------+------+
    |wet_frontal_area            |System Wet Frontal Area                        |            |m^{2} |
    +----------------------------+-----------------------------------------------+------------+------+
    |dry_frontal_area            |System Dry Frontal Area                        |            |m^{2} |
    +----------------------------+-----------------------------------------------+------------+------+
    |wet_beam_area               |System Wet Beam Area                           |            |m^{2} |
    +----------------------------+-----------------------------------------------+------------+------+
    |dry_beam_area               |System Dry Beam Area                           |            |m^{2} |
    +----------------------------+-----------------------------------------------+------------+------+
    |centre_of_gravity           |System Centre of Gravity                       |            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |mass                        |System Mass                                    |            |kg    |
    +----------------------------+-----------------------------------------------+------------+------+
    |profile                     |System Profile                                 |            |      |
    +----------------------------+-----------------------------------------------+------------+------+
    |surface_roughness           |System Surface Roughness                       |            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |yaw                         |Device Heading Angle Span                      |            |deg   |
    +----------------------------+-----------------------------------------------+------------+------+
    |prescribed_footprint_radius |Footprint Radius                               |            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |footprint_corner_coords     |Device Footprint Coordinates                   |            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |installation_depth_max      |Maximum Installation Water Depth               |            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |installation_depth_min      |Minimum Installation Water Depth               |            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |minimum_distance_x          |Minimum distance between devices in x direction|            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |minimum_distance_y          |Minimum distance between devices in y direction|            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |prescribed_foundation_system|Preferred Foundation Type                      |            |      |
    +----------------------------+-----------------------------------------------+------------+------+
    |foundation_locations        |Device Foundation Locations                    |            |m     |
    +----------------------------+-----------------------------------------------+------------+------+
    |rated_power                 |Device Rated Power                             |            |MW    |
    +----------------------------+-----------------------------------------------+------------+------+
    |rated_voltage_u0            |Device Rated Voltage (U0)                      |            |V     |
    +----------------------------+-----------------------------------------------+------------+------+
    |connector_type              |Connector type for device                      |            |      |
    +----------------------------+-----------------------------------------------+------------+------+
    |constant_power_factor       |Device Constant Power Factor                   |            |      |
    +----------------------------+-----------------------------------------------+------------+------+
    |variable_power_factor       |Device Variable Power Factor                   |            |      |
    +----------------------------+-----------------------------------------------+------------+------+
    |assembly_duration           |Device Assembly Duration                       |            |hours |
    +----------------------------+-----------------------------------------------+------------+------+
    |connect_duration            |Device Connect Duration                        |            |hours |
    +----------------------------+-----------------------------------------------+------------+------+
    |disconnect_duration         |Device Disconnect Duration                     |            |hours |
    +----------------------------+-----------------------------------------------+------------+------+
    |load_out_method             |Device Load Out Method                         |            |      |
    +----------------------------+-----------------------------------------------+------------+------+
    |transportation_method       |Device Transportation Method                   |            |      |
    +----------------------------+-----------------------------------------------+------------+------+
    |bollard_pull                |Device Towing Bollard Pull                     |            |tonnes|
    +----------------------------+-----------------------------------------------+------------+------+
    |two_stage_assembly          |Two Stage Assembly                             |            |      |
    +----------------------------+-----------------------------------------------+------------+------+
    |cost                        |Device Cost                                    |            |Euro  |
    +----------------------------+-----------------------------------------------+------------+------+


-------------------

.. |project.device_tidal| replace:: ``project.device_tidal``
.. _project.device_tidal:

.. rubric:: Table: project.device_tidal

| Approximate dump path: ``device#\device_tidal.*``
| Linked to: |project.device|_

.. table:: 
    :widths: 15, 50, 20, 15

    +---------------------+------------------------------+-----+----+
    |       Column        |        Variable Name         |Label|Unit|
    +=====================+==============================+=====+====+
    |id                   |                              |     |    |
    +---------------------+------------------------------+-----+----+
    |cut_in_velocity      |Tidal Turbine Cut-In Velocity |     |m/s |
    +---------------------+------------------------------+-----+----+
    |cut_out_velocity     |Tidal Turbine Cut-Out Velocity|     |m/s |
    +---------------------+------------------------------+-----+----+
    |hub_height           |Tidal Device Hub Height       |     |m   |
    +---------------------+------------------------------+-----+----+
    |turbine_diameter     |Turbine Rotor Diameter        |     |m   |
    +---------------------+------------------------------+-----+----+
    |two_ways_flow        |Bi-directional Turbine Boolean|     |    |
    +---------------------+------------------------------+-----+----+
    |turbine_interdistance|Interdistance Between Turbines|     |m   |
    +---------------------+------------------------------+-----+----+


-------------------

.. |project.device_tidal_power_performance| replace:: ``project.device_tidal_power_performance``
.. _project.device_tidal_power_performance:

.. rubric:: Table: project.device_tidal_power_performance

| Approximate dump path: ``device#\device_tidal_power_performance.*``
| Linked to: |project.device|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------+--------------------------+---------------------+----+
    |      Column      |      Variable Name       |        Label        |Unit|
    +==================+==========================+=====================+====+
    |id                |                          |                     |    |
    +------------------+--------------------------+---------------------+----+
    |velocity          |Turbine Performance Curves|Velocity             |m/s |
    +------------------+--------------------------+---------------------+----+
    |thrust_coefficient|Turbine Performance Curves|Coefficient of Thrust|    |
    +------------------+--------------------------+---------------------+----+
    |power_coefficient |Turbine Performance Curves|Coefficient of Power |    |
    +------------------+--------------------------+---------------------+----+


-------------------

.. |project.device_wave| replace:: ``project.device_wave``
.. _project.device_wave:

.. rubric:: Table: project.device_wave

| Approximate dump path: ``device#\device_wave.*``
| Linked to: |project.device|_

.. table:: 
    :widths: 15, 50, 20, 15

    +-------------------+-------------------+-----+----+
    |      Column       |   Variable Name   |Label|Unit|
    +===================+===================+=====+====+
    |id                 |                   |     |    |
    +-------------------+-------------------+-----+----+
    |wave_data_directory|Wave Data Directory|     |    |
    +-------------------+-------------------+-----+----+


-------------------

.. |project.lease_area| replace:: ``project.lease_area``
.. _project.lease_area:

.. rubric:: Table: project.lease_area

| Approximate dump path: ``site#\lease_area.*``
| Linked to: |project.site|_

.. table:: 
    :widths: 15, 50, 20, 15

    +---------------------------------+---------------------------------------------------+-----+-------+
    |             Column              |                   Variable Name                   |Label| Unit  |
    +=================================+===================================================+=====+=======+
    |id                               |                                                   |     |       |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |blockage_ratio                   |Site Blockage Ratio                                |     |       |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |tidal_occurrence_point           |Tidal Occurrence Extraction Point                  |     |       |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |wave_spectrum_type               |Wave Spectrum                                      |     |       |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |wave_spectrum_gamma              |Peak factor for Wave Spectrum                      |     |       |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |wave_spectrum_spreading_parameter|Spreading Parameter for Wave Spectrum              |     |       |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |surface_current_flow_velocity    |Maximum Tidal Stream Current Velocity in Lease Area|     |m/s    |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |current_flow_direction           |Maximum Surface Current Direction                  |     |degrees|
    +---------------------------------+---------------------------------------------------+-----+-------+
    |moor_found_current_profile       |Vertical Current Profile                           |     |       |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |significant_wave_height          |Maximum Significant Wave Height                    |     |m      |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |peak_wave_period                 |Maximum Peak Wave Period                           |     |s      |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |predominant_wave_direction       |Predominant Wave Direction                         |     |degrees|
    +---------------------------------+---------------------------------------------------+-----+-------+
    |jonswap_gamma                    |Maximum JONSWAP gamma                              |     |       |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |mean_wind_speed                  |Mean Wind Velocity                                 |     |m/s    |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |predominant_wind_direction       |Predominant Mean Wind Direction                    |     |degrees|
    +---------------------------------+---------------------------------------------------+-----+-------+
    |max_wind_gust_speed              |Maximum Gust Wind Velocity                         |     |m/s    |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |wind_gust_direction              |Predominant Direction of Max Gust                  |     |degrees|
    +---------------------------------+---------------------------------------------------+-----+-------+
    |water_level_max                  |Maximum Water Level                                |     |m      |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |water_level_min                  |Minimum Water Level                                |     |m      |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |soil_sensitivity                 |Soil Sensitivity                                   |     |       |
    +---------------------------------+---------------------------------------------------+-----+-------+
    |has_helipad                      |Array Helideck                                     |     |       |
    +---------------------------------+---------------------------------------------------+-----+-------+


-------------------

.. |project.site| replace:: ``project.site``
.. _project.site:

.. rubric:: Table: project.site

| Approximate dump path: ``site.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------------------+-----------------------------+-----------------------+----+
    |        Column         |        Variable Name        |         Label         |Unit|
    +=======================+=============================+=======================+====+
    |id                     |All Available Sites          |id                     |    |
    +-----------------------+-----------------------------+-----------------------+----+
    |site_name              |All Available Sites          |site_name              |    |
    +-----------------------+-----------------------------+-----------------------+----+
    |                       |All Landing Points           |                       |    |
    +-----------------------+-----------------------------+-----------------------+----+
    |                       |All Lease Boundaries         |                       |    |
    +-----------------------+-----------------------------+-----------------------+----+
    |                       |All Site Boundaries          |                       |    |
    +-----------------------+-----------------------------+-----------------------+----+
    |                       |All Cable Corridor Boundaries|                       |    |
    +-----------------------+-----------------------------+-----------------------+----+
    |lease_area_proj4_string|All Available Sites          |lease_area_proj4_string|    |
    +-----------------------+-----------------------------+-----------------------+----+
    |site_boundary          |All Site Boundaries          |                       |    |
    +-----------------------+-----------------------------+-----------------------+----+
    |lease_boundary         |All Lease Boundaries         |                       |    |
    +-----------------------+-----------------------------+-----------------------+----+
    |corridor_boundary      |All Cable Corridor Boundaries|                       |    |
    +-----------------------+-----------------------------+-----------------------+----+
    |cable_landing_location |All Landing Points           |                       |    |
    +-----------------------+-----------------------------+-----------------------+----+


-------------------

.. |project.sub_systems| replace:: ``project.sub_systems``
.. _project.sub_systems:

.. rubric:: Table: project.sub_systems

| Approximate dump path: ``device#\sub_systems.*``
| Linked to: |project.device|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------+---------------------------------------------------+----------+-------------------------+
    |  Column  |                   Variable Name                   |  Label   |          Unit           |
    +==========+===================================================+==========+=========================+
    |id        |                                                   |          |                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |sub_system|Device Sub-System Costs                            |          |                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Device Access Requirements                         |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Control Sub-System On-Site Maintenance Requirements|Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Device On-Site Maintenance Requirements            |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Device Replacement Requirements                    |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Device On-Site Maintenance Parts Data              |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Control Sub-System Inspections Requirements        |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Device Sub-System Installation Specification       |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Device Control System Installation Specification   |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Control Sub-System Costs                           |          |                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Control Sub-System Replacement Requirements        |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Device Sub-System Failure Rates                    |          |                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Control Sub-System Access Requirements             |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Device Inspections Requirements                    |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Device Operation Weightings                        |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Control Sub-System Operation Weightings            |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Control Sub-System Failure Rates                   |          |                         |
    +----------+---------------------------------------------------+----------+-------------------------+
    |          |Control Sub-System On-Site Maintenance Parts Data  |Sub-System|                         |
    +----------+---------------------------------------------------+----------+-------------------------+


-------------------

.. |project.sub_systems_access| replace:: ``project.sub_systems_access``
.. _project.sub_systems_access:

.. rubric:: Table: project.sub_systems_access

| Approximate dump path: ``device#\sub_systems\sub_systems_access.*``
| Linked to: |project.sub_systems|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------+--------------------------------------+--------------------+-----+
    |      Column      |            Variable Name             |       Label        |Unit |
    +==================+======================================+====================+=====+
    |id                |                                      |                    |     |
    +------------------+--------------------------------------+--------------------+-----+
    |fk_sub_system_id  |                                      |                    |     |
    +------------------+--------------------------------------+--------------------+-----+
    |operation_duration|Device Access Requirements            |Operation Duration  |hours|
    +------------------+--------------------------------------+--------------------+-----+
    |                  |Control Sub-System Access Requirements|Operation Duration  |hours|
    +------------------+--------------------------------------+--------------------+-----+
    |max_hs            |Device Access Requirements            |Max Hs              |m    |
    +------------------+--------------------------------------+--------------------+-----+
    |                  |Control Sub-System Access Requirements|Max Hs              |m    |
    +------------------+--------------------------------------+--------------------+-----+
    |max_tp            |Device Access Requirements            |Max Tp              |s    |
    +------------------+--------------------------------------+--------------------+-----+
    |                  |Control Sub-System Access Requirements|Max Tp              |s    |
    +------------------+--------------------------------------+--------------------+-----+
    |max_ws            |Device Access Requirements            |Max Wind Velocity   |m/s  |
    +------------------+--------------------------------------+--------------------+-----+
    |                  |Control Sub-System Access Requirements|Max Wind Velocity   |m/s  |
    +------------------+--------------------------------------+--------------------+-----+
    |max_cs            |Device Access Requirements            |Max Current Velocity|m/s  |
    +------------------+--------------------------------------+--------------------+-----+
    |                  |Control Sub-System Access Requirements|Max Current Velocity|m/s  |
    +------------------+--------------------------------------+--------------------+-----+


-------------------

.. |project.sub_systems_economic| replace:: ``project.sub_systems_economic``
.. _project.sub_systems_economic:

.. rubric:: Table: project.sub_systems_economic

| Approximate dump path: ``device#\sub_systems\sub_systems_economic.*``
| Linked to: |project.sub_systems|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------+--------------------------------+-----+-------------------------+
    |     Column     |         Variable Name          |Label|          Unit           |
    +================+================================+=====+=========================+
    |id              |                                |     |                         |
    +----------------+--------------------------------+-----+-------------------------+
    |fk_sub_system_id|                                |     |                         |
    +----------------+--------------------------------+-----+-------------------------+
    |cost            |Device Sub-System Costs         |     |Euro                     |
    +----------------+--------------------------------+-----+-------------------------+
    |                |Control Sub-System Costs        |     |Euro                     |
    +----------------+--------------------------------+-----+-------------------------+
    |failure_rate    |Device Sub-System Failure Rates |     |Failures per 10^{6} hours|
    +----------------+--------------------------------+-----+-------------------------+
    |                |Control Sub-System Failure Rates|     |Failures per 10^{6} hours|
    +----------------+--------------------------------+-----+-------------------------+


-------------------

.. |project.sub_systems_inspection| replace:: ``project.sub_systems_inspection``
.. _project.sub_systems_inspection:

.. rubric:: Table: project.sub_systems_inspection

| Approximate dump path: ``device#\sub_systems\sub_systems_inspection.*``
| Linked to: |project.sub_systems|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------+-------------------------------------------+----------------------+-----+
    |      Column      |               Variable Name               |        Label         |Unit |
    +==================+===========================================+======================+=====+
    |id                |                                           |                      |     |
    +------------------+-------------------------------------------+----------------------+-----+
    |fk_sub_system_id  |                                           |                      |     |
    +------------------+-------------------------------------------+----------------------+-----+
    |operation_duration|Device Inspections Requirements            |Operation Duration    |hours|
    +------------------+-------------------------------------------+----------------------+-----+
    |                  |Control Sub-System Inspections Requirements|Operation Duration    |hours|
    +------------------+-------------------------------------------+----------------------+-----+
    |crew_lead_time    |Device Inspections Requirements            |Crew Preparation Delay|hours|
    +------------------+-------------------------------------------+----------------------+-----+
    |                  |Control Sub-System Inspections Requirements|Crew Preparation Delay|hours|
    +------------------+-------------------------------------------+----------------------+-----+
    |other_lead_time   |Device Inspections Requirements            |Other Delay           |hours|
    +------------------+-------------------------------------------+----------------------+-----+
    |                  |Control Sub-System Inspections Requirements|Other Delay           |hours|
    +------------------+-------------------------------------------+----------------------+-----+
    |n_specialists     |Device Inspections Requirements            |Specialists Required  |     |
    +------------------+-------------------------------------------+----------------------+-----+
    |                  |Control Sub-System Inspections Requirements|Specialists Required  |     |
    +------------------+-------------------------------------------+----------------------+-----+
    |n_technicians     |Device Inspections Requirements            |Technicians Required  |     |
    +------------------+-------------------------------------------+----------------------+-----+
    |                  |Control Sub-System Inspections Requirements|Technicians Required  |     |
    +------------------+-------------------------------------------+----------------------+-----+
    |max_hs            |Device Inspections Requirements            |Max Hs                |m    |
    +------------------+-------------------------------------------+----------------------+-----+
    |                  |Control Sub-System Inspections Requirements|Max Hs                |m    |
    +------------------+-------------------------------------------+----------------------+-----+
    |max_tp            |Device Inspections Requirements            |Max Tp                |s    |
    +------------------+-------------------------------------------+----------------------+-----+
    |                  |Control Sub-System Inspections Requirements|Max Tp                |s    |
    +------------------+-------------------------------------------+----------------------+-----+
    |max_ws            |Device Inspections Requirements            |Max Wind Velocity     |m/s  |
    +------------------+-------------------------------------------+----------------------+-----+
    |                  |Control Sub-System Inspections Requirements|Max Wind Velocity     |m/s  |
    +------------------+-------------------------------------------+----------------------+-----+
    |max_cs            |Device Inspections Requirements            |Max Current Velocity  |m/s  |
    +------------------+-------------------------------------------+----------------------+-----+
    |                  |Control Sub-System Inspections Requirements|Max Current Velocity  |m/s  |
    +------------------+-------------------------------------------+----------------------+-----+


-------------------

.. |project.sub_systems_install| replace:: ``project.sub_systems_install``
.. _project.sub_systems_install:

.. rubric:: Table: project.sub_systems_install

| Approximate dump path: ``device#\sub_systems\sub_systems_install.*``
| Linked to: |project.sub_systems|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------+------------------------------------------------+--------------------+----+
    |     Column     |                 Variable Name                  |       Label        |Unit|
    +================+================================================+====================+====+
    |id              |                                                |                    |    |
    +----------------+------------------------------------------------+--------------------+----+
    |fk_sub_system_id|                                                |                    |    |
    +----------------+------------------------------------------------+--------------------+----+
    |length          |Device Sub-System Installation Specification    |Length              |m   |
    +----------------+------------------------------------------------+--------------------+----+
    |                |Device Control System Installation Specification|Length              |m   |
    +----------------+------------------------------------------------+--------------------+----+
    |width           |Device Control System Installation Specification|Width               |m   |
    +----------------+------------------------------------------------+--------------------+----+
    |                |Device Sub-System Installation Specification    |Width               |m   |
    +----------------+------------------------------------------------+--------------------+----+
    |height          |Device Sub-System Installation Specification    |Height              |m   |
    +----------------+------------------------------------------------+--------------------+----+
    |                |Device Control System Installation Specification|Height              |m   |
    +----------------+------------------------------------------------+--------------------+----+
    |dry_mass        |Device Sub-System Installation Specification    |Dry Mass            |kg  |
    +----------------+------------------------------------------------+--------------------+----+
    |                |Device Control System Installation Specification|Dry Mass            |kg  |
    +----------------+------------------------------------------------+--------------------+----+
    |max_hs          |Device Sub-System Installation Specification    |Max Hs              |m   |
    +----------------+------------------------------------------------+--------------------+----+
    |                |Device Control System Installation Specification|Max Hs              |m   |
    +----------------+------------------------------------------------+--------------------+----+
    |max_tp          |Device Sub-System Installation Specification    |Max Tp              |s   |
    +----------------+------------------------------------------------+--------------------+----+
    |                |Device Control System Installation Specification|Max Tp              |s   |
    +----------------+------------------------------------------------+--------------------+----+
    |max_ws          |Device Sub-System Installation Specification    |Max Wind Velocity   |m/s |
    +----------------+------------------------------------------------+--------------------+----+
    |                |Device Control System Installation Specification|Max Wind Velocity   |m/s |
    +----------------+------------------------------------------------+--------------------+----+
    |max_cs          |Device Sub-System Installation Specification    |Max Current Velocity|m/s |
    +----------------+------------------------------------------------+--------------------+----+
    |                |Device Control System Installation Specification|Max Current Velocity|m/s |
    +----------------+------------------------------------------------+--------------------+----+


-------------------

.. |project.sub_systems_maintenance| replace:: ``project.sub_systems_maintenance``
.. _project.sub_systems_maintenance:

.. rubric:: Table: project.sub_systems_maintenance

| Approximate dump path: ``device#\sub_systems\sub_systems_maintenance.*``
| Linked to: |project.sub_systems|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------+---------------------------------------------------+-----------------------------+-----+
    |      Column      |                   Variable Name                   |            Label            |Unit |
    +==================+===================================================+=============================+=====+
    |id                |                                                   |                             |     |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |fk_sub_system_id  |                                                   |                             |     |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |operation_duration|Device On-Site Maintenance Requirements            |Operation Duration           |hours|
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Requirements|Operation Duration           |hours|
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |interruptible     |Device On-Site Maintenance Requirements            |Interruptable                |     |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Requirements|Interruptable                |     |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |parts_length      |Device On-Site Maintenance Parts Data              |Spare Parts Max Length       |m    |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Parts Data  |Spare Parts Max Length       |m    |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |parts_width       |Device On-Site Maintenance Parts Data              |Spare Parts Max Width        |m    |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Parts Data  |Spare Parts Max Width        |m    |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |parts_height      |Device On-Site Maintenance Parts Data              |Spare Parts Max Height       |m    |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Parts Data  |Spare Parts Max Height       |m    |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |parts_dry_mass    |Device On-Site Maintenance Parts Data              |Spare Parts Mass             |kg   |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Parts Data  |Spare Parts Mass             |kg   |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |assembly_lead_time|Device On-Site Maintenance Requirements            |Spare Parts Preparation Delay|hours|
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Requirements|Spare Parts Preparation Delay|hours|
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |crew_lead_time    |Device On-Site Maintenance Requirements            |Crew Preparation Delay       |hours|
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Requirements|Crew Preparation Delay       |hours|
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |other_lead_time   |Device On-Site Maintenance Requirements            |Other Delay                  |hours|
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Requirements|Other Delay                  |hours|
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |n_specialists     |Device On-Site Maintenance Requirements            |Specialists Required         |     |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Requirements|Specialists Required         |     |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |n_technicians     |Device On-Site Maintenance Requirements            |Technicians Required         |     |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System On-Site Maintenance Requirements|Technicians Required         |     |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |max_hs            |Control Sub-System On-Site Maintenance Requirements|Max Hs                       |m    |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Device On-Site Maintenance Requirements            |Max Hs                       |m    |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |max_tp            |Control Sub-System On-Site Maintenance Requirements|Max Tp                       |s    |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Device On-Site Maintenance Requirements            |Max Tp                       |s    |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |max_ws            |Control Sub-System On-Site Maintenance Requirements|Max Wind Velocity            |m/s  |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Device On-Site Maintenance Requirements            |Max Wind Velocity            |m/s  |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |max_cs            |Control Sub-System On-Site Maintenance Requirements|Max Current Velocity         |m/s  |
    +------------------+---------------------------------------------------+-----------------------------+-----+
    |                  |Device On-Site Maintenance Requirements            |Max Current Velocity         |m/s  |
    +------------------+---------------------------------------------------+-----------------------------+-----+


-------------------

.. |project.sub_systems_operation_weightings| replace:: ``project.sub_systems_operation_weightings``
.. _project.sub_systems_operation_weightings:

.. rubric:: Table: project.sub_systems_operation_weightings

| Approximate dump path: ``device#\sub_systems\sub_systems_operation_weightings.*``
| Linked to: |project.sub_systems|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------+---------------------------------------+-------------------+----+
    |     Column     |             Variable Name             |       Label       |Unit|
    +================+=======================================+===================+====+
    |id              |                                       |                   |    |
    +----------------+---------------------------------------+-------------------+----+
    |fk_sub_system_id|                                       |                   |    |
    +----------------+---------------------------------------+-------------------+----+
    |maintenance     |Device Operation Weightings            |On-Site Maintenance|    |
    +----------------+---------------------------------------+-------------------+----+
    |                |Control Sub-System Operation Weightings|On-Site Maintenance|    |
    +----------------+---------------------------------------+-------------------+----+
    |replacement     |Device Operation Weightings            |Replacement        |    |
    +----------------+---------------------------------------+-------------------+----+
    |                |Control Sub-System Operation Weightings|Replacement        |    |
    +----------------+---------------------------------------+-------------------+----+
    |inspection      |Device Operation Weightings            |Inspections        |    |
    +----------------+---------------------------------------+-------------------+----+
    |                |Control Sub-System Operation Weightings|Inspections        |    |
    +----------------+---------------------------------------+-------------------+----+


-------------------

.. |project.sub_systems_replace| replace:: ``project.sub_systems_replace``
.. _project.sub_systems_replace:

.. rubric:: Table: project.sub_systems_replace

| Approximate dump path: ``device#\sub_systems\sub_systems_replace.*``
| Linked to: |project.sub_systems|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------+-------------------------------------------+-----------------------------+-----+
    |      Column      |               Variable Name               |            Label            |Unit |
    +==================+===========================================+=============================+=====+
    |id                |                                           |                             |     |
    +------------------+-------------------------------------------+-----------------------------+-----+
    |fk_sub_system_id  |                                           |                             |     |
    +------------------+-------------------------------------------+-----------------------------+-----+
    |operation_duration|Device Replacement Requirements            |Operation Duration           |hours|
    +------------------+-------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System Replacement Requirements|Operation Duration           |hours|
    +------------------+-------------------------------------------+-----------------------------+-----+
    |interruptible     |Device Replacement Requirements            |Interruptable                |     |
    +------------------+-------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System Replacement Requirements|Interruptable                |     |
    +------------------+-------------------------------------------+-----------------------------+-----+
    |assembly_lead_time|Device Replacement Requirements            |Spare Parts Preparation Delay|hours|
    +------------------+-------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System Replacement Requirements|Spare Parts Preparation Delay|hours|
    +------------------+-------------------------------------------+-----------------------------+-----+
    |crew_lead_time    |Device Replacement Requirements            |Crew Preparation Delay       |hours|
    +------------------+-------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System Replacement Requirements|Crew Preparation Delay       |hours|
    +------------------+-------------------------------------------+-----------------------------+-----+
    |other_lead_time   |Device Replacement Requirements            |Other Delay                  |hours|
    +------------------+-------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System Replacement Requirements|Other Delay                  |hours|
    +------------------+-------------------------------------------+-----------------------------+-----+
    |n_specialists     |Device Replacement Requirements            |Specialists Required         |     |
    +------------------+-------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System Replacement Requirements|Specialists Required         |     |
    +------------------+-------------------------------------------+-----------------------------+-----+
    |n_technicians     |Device Replacement Requirements            |Technicians Required         |     |
    +------------------+-------------------------------------------+-----------------------------+-----+
    |                  |Control Sub-System Replacement Requirements|Technicians Required         |     |
    +------------------+-------------------------------------------+-----------------------------+-----+


-------------------

.. |project.time_series_energy_tidal| replace:: ``project.time_series_energy_tidal``
.. _project.time_series_energy_tidal:

.. rubric:: Table: project.time_series_energy_tidal

| Approximate dump path: ``site#\bathymetry\time_series_energy_tidal.*``
| Linked to: |project.bathymetry|_
| See :ref:`environmental_data`

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------+------------------+-----+----+
    |       Column       |Variable Name     |Label|Unit|
    +====================+==================+=====+====+
    |id                  |                  |     |    |
    +--------------------+------------------+-----+----+
    |fk_bathymetry_id    |                  |     |    |
    +--------------------+------------------+-----+----+
    |measure_date        |Tidal Time Series |     |    |
    +--------------------+------------------+-----+----+
    |measure_time        |Tidal Time Series |     |    |
    +--------------------+------------------+-----+----+
    |u                   |Tidal Time Series |     |m/s |
    +--------------------+------------------+-----+----+
    |v                   |Tidal Time Series |     |m/s |
    +--------------------+------------------+-----+----+
    |turbulence_intensity|Tidal Time Series |     |    |
    +--------------------+------------------+-----+----+
    |ssh                 |Tidal Time Series |     |m   |
    +--------------------+------------------+-----+----+


-------------------

.. |project.time_series_energy_wave| replace:: ``project.time_series_energy_wave``
.. _project.time_series_energy_wave:

.. rubric:: Table: project.time_series_energy_wave

| Approximate dump path: ``site#\time_series_energy_wave.*``
| Linked to: |project.site|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------+----------------+-----+----+
    |   Column   | Variable Name  |Label|Unit|
    +============+================+=====+====+
    |id          |                |     |    |
    +------------+----------------+-----+----+
    |measure_date|Wave Time Series|     |    |
    +------------+----------------+-----+----+
    |measure_time|Wave Time Series|     |    |
    +------------+----------------+-----+----+
    |height      |Wave Time Series|Hm0  |m   |
    +------------+----------------+-----+----+
    |te          |Wave Time Series|Te   |s   |
    +------------+----------------+-----+----+
    |direction   |Wave Time Series|Dir  |deg |
    +------------+----------------+-----+----+


-------------------

.. |project.time_series_om_tidal| replace:: ``project.time_series_om_tidal``
.. _project.time_series_om_tidal:

.. rubric:: Table: project.time_series_om_tidal

| Approximate dump path: ``site#\time_series_om_tidal.*``
| Linked to: |project.site|_

.. table:: 
    :widths: 15, 50, 20, 15

    +-------------+-------------------------+--------+----+
    |   Column    |      Variable Name      | Label  |Unit|
    +=============+=========================+========+====+
    |id           |                         |        |    |
    +-------------+-------------------------+--------+----+
    |measure_date |Tidal Current Time Series|        |    |
    +-------------+-------------------------+--------+----+
    |measure_time |Tidal Current Time Series|        |    |
    +-------------+-------------------------+--------+----+
    |current_speed|Tidal Current Time Series|Velocity|m/s |
    +-------------+-------------------------+--------+----+


-------------------

.. |project.time_series_om_wave| replace:: ``project.time_series_om_wave``
.. _project.time_series_om_wave:

.. rubric:: Table: project.time_series_om_wave

| Approximate dump path: ``site#\time_series_om_wave.*``
| Linked to: |project.site|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------+-------------------------------+-----+----+
    |   Column   |         Variable Name         |Label|Unit|
    +============+===============================+=====+====+
    |id          |                               |     |    |
    +------------+-------------------------------+-----+----+
    |measure_date|Wave Time Series (Installation)|     |    |
    +------------+-------------------------------+-----+----+
    |measure_time|Wave Time Series (Installation)|     |    |
    +------------+-------------------------------+-----+----+
    |period_tp   |Wave Time Series (Installation)|Tp   |s   |
    +------------+-------------------------------+-----+----+
    |height_hs   |Wave Time Series (Installation)|Hs   |m   |
    +------------+-------------------------------+-----+----+


-------------------

.. |project.time_series_om_wind| replace:: ``project.time_series_om_wind``
.. _project.time_series_om_wind:

.. rubric:: Table: project.time_series_om_wind

| Approximate dump path: ``site#\time_series_om_wind.*``
| Linked to: |project.site|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------+----------------------+--------+----+
    |   Column   |    Variable Name     | Label  |Unit|
    +============+======================+========+====+
    |id          |                      |        |    |
    +------------+----------------------+--------+----+
    |measure_date|Wind Speed Time Series|        |    |
    +------------+----------------------+--------+----+
    |measure_time|Wind Speed Time Series|        |    |
    +------------+----------------------+--------+----+
    |wind_speed  |Wind Speed Time Series|Velocity|m/s |
    +------------+----------------------+--------+----+


Reference Schema
----------------

.. |reference.component| replace:: ``reference.component``
.. _reference.component:

.. rubric:: Table: reference.component

| Approximate dump path: ``other\component.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+------------------------------------------------------+--------------+------+
    |  Column   |                    Variable Name                     |    Label     | Unit |
    +===========+======================================================+==============+======+
    |id         |Collection Point Data                                 |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Forerunner Assembly Critical Failure Rates    |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Swivel Non-Critical Failure Rates             |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Wet Mate Connector Non-Critical Failure Rates         |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Forerunner Assembly Data                      |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Foundation Drag Anchor Critical Failure Rates         |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Power Transformer Data                                |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Foundation Pile Critical Failure Rates                |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Static Cable Data                                     |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Forerunner Assembly Non-Critical Failure Rates|Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Foundation Pile Data                                  |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Chain Non-Critical Failure Rates              |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Wet Mate Connector Critical Failure Rates             |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Dry Mate Connector Non-Critical Failure Rates         |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Collection Points Foundation Locations                |              |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Shackle Data                                  |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Dynamic Cable Data                                    |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Collections Points Centre of Gravity                  |              |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Collection Points Non-Critical Failure Rates          |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Dry Mate Connector Data                               |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Foundation Drag Anchor Soft Coefficients              |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Rope Critical Failure Rates                   |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Wet Mate Connector Data                               |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Dynamic Cable Non-Critical Failure Rates              |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Foundation Drag Anchor Non-Critical Failure Rates     |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Foundation Drag Anchor Sand Coefficients              |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring shackle Non-Critical Failure Rates            |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Swivel Critical Failure Rates                 |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Chain Critical Failure Rates                  |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Rope Non-Critical Failure Rates               |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Rope Data                                     |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Swivel Data                                   |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Rope Axial Stiffness Data                     |              |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Static Cable Critical Failure Rates                   |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Dry Mate Connector Critical Failure Rates             |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Transformers Critical Failure Rates                   |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Transformers Non-Critical Failure Rates               |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Shackle Critical Failure Rates                |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Dynamic Cable Critical Failure Rates                  |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Collection Points Critical Failure Rates              |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Foundation Drag Anchor Data                           |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Chain Data                                    |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Foundation Pile Non-Critical Failure Rates            |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Static Cable Non-Critical Failure Rates               |Key Identifier|      |
    +-----------+------------------------------------------------------+--------------+------+
    |description|Collection Point Data                                 |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Forerunner Assembly Data                      |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Static Cable Data                                     |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Foundation Pile Data                                  |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Power Transformer Data                                |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Dynamic Cable Data                                    |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Shackle Data                                  |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Foundation Drag Anchor Data                           |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Dry Mate Connector Data                               |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Wet Mate Connector Data                               |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Rope Data                                     |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Swivel Data                                   |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+
    |           |Mooring Chain Data                                    |Name          |      |
    +-----------+------------------------------------------------------+--------------+------+


-------------------

.. |reference.component_anchor| replace:: ``reference.component_anchor``
.. _reference.component_anchor:

.. rubric:: Table: reference.component_anchor

| Approximate dump path: ``other\component\component_discrete\component_anchor.*``
| Linked to: |reference.component_discrete|_; |reference.component_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------+----------------------------------------+------------------------------+----+
    |         Column         |             Variable Name              |            Label             |Unit|
    +========================+========================================+==============================+====+
    |id                      |                                        |                              |    |
    +------------------------+----------------------------------------+------------------------------+----+
    |fk_component_discrete_id|                                        |                              |    |
    +------------------------+----------------------------------------+------------------------------+----+
    |fk_component_type_id    |                                        |                              |    |
    +------------------------+----------------------------------------+------------------------------+----+
    |connecting_size         |Foundation Drag Anchor Data             |Connecting Size               |m   |
    +------------------------+----------------------------------------+------------------------------+----+
    |minimum_breaking_load   |Foundation Drag Anchor Data             |Min Break Load                |N   |
    +------------------------+----------------------------------------+------------------------------+----+
    |axial_stiffness         |Foundation Drag Anchor Data             |Axial Stiffness               |N/m |
    +------------------------+----------------------------------------+------------------------------+----+
    |soft_holding_cap_coef_1 |Foundation Drag Anchor Soft Coefficients|Holding Capacity Coefficient 1|    |
    +------------------------+----------------------------------------+------------------------------+----+
    |soft_holding_cap_coef_2 |Foundation Drag Anchor Soft Coefficients|Holding Capacity Coefficient 2|    |
    +------------------------+----------------------------------------+------------------------------+----+
    |soft_penetration_coef_1 |Foundation Drag Anchor Soft Coefficients|Penetration Coefficient 1     |    |
    +------------------------+----------------------------------------+------------------------------+----+
    |soft_penetration_coef_2 |Foundation Drag Anchor Soft Coefficients|Penetration Coefficient 2     |    |
    +------------------------+----------------------------------------+------------------------------+----+
    |sand_holding_cap_coef_1 |Foundation Drag Anchor Sand Coefficients|Holding Capacity Coefficient 1|    |
    +------------------------+----------------------------------------+------------------------------+----+
    |sand_holding_cap_coef_2 |Foundation Drag Anchor Sand Coefficients|Holding Capacity Coefficient 2|    |
    +------------------------+----------------------------------------+------------------------------+----+
    |sand_penetration_coef_1 |Foundation Drag Anchor Sand Coefficients|Penetration Coefficient 1     |    |
    +------------------------+----------------------------------------+------------------------------+----+
    |sand_penetration_coef_2 |Foundation Drag Anchor Sand Coefficients|Penetration Coefficient 2     |    |
    +------------------------+----------------------------------------+------------------------------+----+


-------------------

.. |reference.component_cable| replace:: ``reference.component_cable``
.. _reference.component_cable:

.. rubric:: Table: reference.component_cable

| Approximate dump path: ``other\component\component_continuous\component_cable.*``
| Linked to: |reference.component_continuous|_; |reference.component_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------+------------------+------------------------------+------+
    |          Column          |  Variable Name   |            Label             | Unit |
    +==========================+==================+==============================+======+
    |id                        |                  |                              |      |
    +--------------------------+------------------+------------------------------+------+
    |fk_component_continuous_id|                  |                              |      |
    +--------------------------+------------------+------------------------------+------+
    |fk_component_type_id      |                  |                              |      |
    +--------------------------+------------------+------------------------------+------+
    |minimum_breaking_load     |Static Cable Data |Min Break Load                |N     |
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Min Break Load                |N     |
    +--------------------------+------------------+------------------------------+------+
    |minimum_bend_radius       |Static Cable Data |Min Bend Radius               |m     |
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Min Bend Radius               |m     |
    +--------------------------+------------------+------------------------------+------+
    |number_conductors         |Static Cable Data |Number of Conductors          |      |
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Number of Conductors          |      |
    +--------------------------+------------------+------------------------------+------+
    |number_fibre_channels     |Static Cable Data |Number of Fibre Optic Channels|      |
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Number of Fibre Optic Channels|      |
    +--------------------------+------------------+------------------------------+------+
    |resistance_dc_20          |Static Cable Data |DC Resistance                 |Ohm/km|
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|DC Resistance                 |Ohm/km|
    +--------------------------+------------------+------------------------------+------+
    |resistance_ac_90          |Static Cable Data |AC Resistance                 |Ohm/km|
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|AC Resistance                 |Ohm/km|
    +--------------------------+------------------+------------------------------+------+
    |inductive_reactance       |Static Cable Data |Inductive Reactance           |Ohm/km|
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Inductive Reactance           |Ohm/km|
    +--------------------------+------------------+------------------------------+------+
    |capacitance               |Static Cable Data |Capacitance                   |uF/km |
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Capacitance                   |uF/km |
    +--------------------------+------------------+------------------------------+------+
    |rated_current_air         |Static Cable Data |Rated Current in Air          |A     |
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Rated Current in Air          |A     |
    +--------------------------+------------------+------------------------------+------+
    |rated_current_buried      |Static Cable Data |Rated Current if Buried       |A     |
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Rated Current if Buried       |A     |
    +--------------------------+------------------+------------------------------+------+
    |rated_current_jtube       |Static Cable Data |Rated Current in J Tube       |A     |
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Rated Current in J Tube       |A     |
    +--------------------------+------------------+------------------------------+------+
    |rated_voltage_u0          |Static Cable Data |Rated Voltage (U0)            |V     |
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Rated Voltage (U0)            |V     |
    +--------------------------+------------------+------------------------------+------+
    |operational_temp_max      |Static Cable Data |Max Temperature               |C     |
    +--------------------------+------------------+------------------------------+------+
    |                          |Dynamic Cable Data|Max Temperature               |C     |
    +--------------------------+------------------+------------------------------+------+


-------------------

.. |reference.component_collection_point| replace:: ``reference.component_collection_point``
.. _reference.component_collection_point:

.. rubric:: Table: reference.component_collection_point

| Approximate dump path: ``other\component\component_discrete\component_collection_point.*``
| Linked to: |reference.component_type|_; |reference.component_discrete|_

.. table:: 
    :widths: 15, 50, 20, 15

    +-------------------------+--------------------------------------+------------------------------+-------+
    |         Column          |            Variable Name             |            Label             | Unit  |
    +=========================+======================================+==============================+=======+
    |id                       |                                      |                              |       |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |fk_component_discrete_id |                                      |                              |       |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |fk_component_type_id     |                                      |                              |       |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |wet_frontal_area         |Collection Point Data                 |Wet Frontal Area              |m^{2}  |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |dry_frontal_area         |Collection Point Data                 |Dry Frontal Area              |m^{2}  |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |wet_beam_area            |Collection Point Data                 |Wet Beam Area                 |m^{2}  |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |dry_beam_area            |Collection Point Data                 |Dry Beam Area                 |m^{2}  |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |maximum_water_depth      |Collection Point Data                 |Max Water Depth               |m      |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |orientation_angle        |Collection Point Data                 |Orientation Angle             |deg    |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |input_lines              |Collection Point Data                 |Input Lines                   |       |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |output_lines             |Collection Point Data                 |Output Lines                  |       |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |input_connector_type     |Collection Point Data                 |Input Connector Type          |       |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |output_connector_type    |Collection Point Data                 |Output Connector Type         |       |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |number_fibre_channels    |Collection Point Data                 |Number of Fibre Optic Channels|       |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |voltage_primary_winding  |Collection Point Data                 |Primary Winding Voltage       |V      |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |voltage_secondary_winding|Collection Point Data                 |Secondary Winding Voltage     |V      |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |rated_operating_current  |Collection Point Data                 |Rated Current                 |A      |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |operational_temp_min     |Collection Point Data                 |Min Temperature               |C      |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |operational_temp_max     |Collection Point Data                 |Max Temperature               |C      |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |foundation_locations     |Collection Points Foundation Locations|Key Identifier                |       |
    +-------------------------+--------------------------------------+------------------------------+-------+
    |centre_of_gravity        |Collections Points Centre of Gravity  |Key Identifier                |m, m, m|
    +-------------------------+--------------------------------------+------------------------------+-------+


-------------------

.. |reference.component_connector| replace:: ``reference.component_connector``
.. _reference.component_connector:

.. rubric:: Table: reference.component_connector

| Approximate dump path: ``other\component\component_discrete\component_connector.*``
| Linked to: |reference.component_type|_; |reference.component_discrete|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------+-----------------------+------------------------------+----+
    |         Column         |     Variable Name     |            Label             |Unit|
    +========================+=======================+==============================+====+
    |id                      |                       |                              |    |
    +------------------------+-----------------------+------------------------------+----+
    |fk_component_discrete_id|                       |                              |    |
    +------------------------+-----------------------+------------------------------+----+
    |fk_component_type_id    |                       |                              |    |
    +------------------------+-----------------------+------------------------------+----+
    |maximum_water_depth     |Wet Mate Connector Data|Max Water Depth               |m   |
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Max Water Depth               |m   |
    +------------------------+-----------------------+------------------------------+----+
    |number_contacts         |Wet Mate Connector Data|Number Of Contacts            |    |
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Number Of Contacts            |    |
    +------------------------+-----------------------+------------------------------+----+
    |number_fibre_channels   |Wet Mate Connector Data|Number of Fibre Optic Channels|    |
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Number of Fibre Optic Channels|    |
    +------------------------+-----------------------+------------------------------+----+
    |mating_force            |Wet Mate Connector Data|Mating Force                  |N   |
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Mating Force                  |N   |
    +------------------------+-----------------------+------------------------------+----+
    |demating_force          |Wet Mate Connector Data|Demating Force                |N   |
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Demating Force                |N   |
    +------------------------+-----------------------+------------------------------+----+
    |rated_voltage_u0        |Wet Mate Connector Data|Rated Voltage (U0)            |V   |
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Rated Voltage (U0)            |V   |
    +------------------------+-----------------------+------------------------------+----+
    |rated_current           |Wet Mate Connector Data|Rated Current                 |A   |
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Rated Current                 |A   |
    +------------------------+-----------------------+------------------------------+----+
    |cable_area_min          |Wet Mate Connector Data|Min Cable Area                |mm^2|
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Min Cable Area                |mm^2|
    +------------------------+-----------------------+------------------------------+----+
    |cable_area_max          |Wet Mate Connector Data|Max Cable Area                |mm^2|
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Max Cable Area                |mm^2|
    +------------------------+-----------------------+------------------------------+----+
    |operational_temp_min    |Wet Mate Connector Data|Min Temperature               |C   |
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Min Temperature               |C   |
    +------------------------+-----------------------+------------------------------+----+
    |operational_temp_max    |Wet Mate Connector Data|Max Temperature               |C   |
    +------------------------+-----------------------+------------------------------+----+
    |                        |Dry Mate Connector Data|Max Temperature               |C   |
    +------------------------+-----------------------+------------------------------+----+


-------------------

.. |reference.component_continuous| replace:: ``reference.component_continuous``
.. _reference.component_continuous:

.. rubric:: Table: reference.component_continuous

| Approximate dump path: ``other\component\component_continuous.*``
| Linked to: |reference.component|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------+--------------------------------+------------------------+------+
    |         Column         |         Variable Name          |         Label          | Unit |
    +========================+================================+========================+======+
    |id                      |                                |                        |      |
    +------------------------+--------------------------------+------------------------+------+
    |fk_component_id         |                                |                        |      |
    +------------------------+--------------------------------+------------------------+------+
    |diameter                |Static Cable Data               |Diameter                |m     |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Foundation Pile Data            |Diameter                |m     |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Dynamic Cable Data              |Diameter                |m     |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Forerunner Assembly Data|Diameter                |m     |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Chain Data              |Diameter                |m     |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Rope Data               |Diameter                |m     |
    +------------------------+--------------------------------+------------------------+------+
    |dry_mass_per_unit_length|Foundation Pile Data            |Dry Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Static Cable Data               |Dry Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Dynamic Cable Data              |Dry Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Forerunner Assembly Data|Dry Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Rope Data               |Dry Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Chain Data              |Dry Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |wet_mass_per_unit_length|Foundation Pile Data            |Wet Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Static Cable Data               |Wet Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Dynamic Cable Data              |Wet Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Forerunner Assembly Data|Wet Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Rope Data               |Wet Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Chain Data              |Wet Mass per Unit Length|kg/m  |
    +------------------------+--------------------------------+------------------------+------+
    |cost_per_unit_length    |Foundation Pile Data            |Cost per Unit Length    |Euro/m|
    +------------------------+--------------------------------+------------------------+------+
    |                        |Static Cable Data               |Cost per Unit Length    |Euro/m|
    +------------------------+--------------------------------+------------------------+------+
    |                        |Dynamic Cable Data              |Cost per Unit Length    |Euro/m|
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Forerunner Assembly Data|Cost per Unit Length    |Euro/m|
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Rope Data               |Cost per Unit Length    |Euro/m|
    +------------------------+--------------------------------+------------------------+------+
    |                        |Mooring Chain Data              |Cost per Unit Length    |Euro/m|
    +------------------------+--------------------------------+------------------------+------+


-------------------

.. |reference.component_discrete| replace:: ``reference.component_discrete``
.. _reference.component_discrete:

.. rubric:: Table: reference.component_discrete

| Approximate dump path: ``other\component\component_discrete.*``
| Linked to: |reference.component|_

.. table:: 
    :widths: 15, 50, 20, 15

    +---------------+---------------------------+-------------+----+
    |    Column     |       Variable Name       |    Label    |Unit|
    +===============+===========================+=============+====+
    |id             |                           |             |    |
    +---------------+---------------------------+-------------+----+
    |fk_component_id|                           |             |    |
    +---------------+---------------------------+-------------+----+
    |length         |Dry Mate Connector Data    |Depth        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Power Transformer Data     |Depth        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Mooring Swivel Data        |Depth        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Wet Mate Connector Data    |Depth        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Foundation Drag Anchor Data|Depth        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Mooring Shackle Data       |Depth        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Collection Point Data      |Depth        |m   |
    +---------------+---------------------------+-------------+----+
    |width          |Wet Mate Connector Data    |Width        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Dry Mate Connector Data    |Width        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Mooring Swivel Data        |Width        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Collection Point Data      |Width        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Power Transformer Data     |Width        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Mooring Shackle Data       |Width        |m   |
    +---------------+---------------------------+-------------+----+
    |               |Foundation Drag Anchor Data|Width        |m   |
    +---------------+---------------------------+-------------+----+
    |height         |Dry Mate Connector Data    |Height       |m   |
    +---------------+---------------------------+-------------+----+
    |               |Mooring Swivel Data        |Height       |m   |
    +---------------+---------------------------+-------------+----+
    |               |Collection Point Data      |Height       |m   |
    +---------------+---------------------------+-------------+----+
    |               |Wet Mate Connector Data    |Height       |m   |
    +---------------+---------------------------+-------------+----+
    |               |Power Transformer Data     |Height       |m   |
    +---------------+---------------------------+-------------+----+
    |               |Mooring Shackle Data       |Height       |m   |
    +---------------+---------------------------+-------------+----+
    |               |Foundation Drag Anchor Data|Height       |m   |
    +---------------+---------------------------+-------------+----+
    |dry_mass       |Dry Mate Connector Data    |Dry Mass     |kg  |
    +---------------+---------------------------+-------------+----+
    |               |Mooring Swivel Data        |Dry Unit Mass|kg  |
    +---------------+---------------------------+-------------+----+
    |               |Collection Point Data      |Dry Mass     |kg  |
    +---------------+---------------------------+-------------+----+
    |               |Wet Mate Connector Data    |Dry Mass     |kg  |
    +---------------+---------------------------+-------------+----+
    |               |Power Transformer Data     |Dry Mass     |kg  |
    +---------------+---------------------------+-------------+----+
    |               |Mooring Shackle Data       |Dry Unit Mass|kg  |
    +---------------+---------------------------+-------------+----+
    |               |Foundation Drag Anchor Data|Dry Unit Mass|kg  |
    +---------------+---------------------------+-------------+----+
    |wet_mass       |Wet Mate Connector Data    |Wet Mass     |kg  |
    +---------------+---------------------------+-------------+----+
    |               |Dry Mate Connector Data    |Wet Mass     |kg  |
    +---------------+---------------------------+-------------+----+
    |               |Power Transformer Data     |Wet Mass     |kg  |
    +---------------+---------------------------+-------------+----+
    |               |Mooring Swivel Data        |Wet Unit Mass|kg  |
    +---------------+---------------------------+-------------+----+
    |               |Collection Point Data      |Wet Mass     |kg  |
    +---------------+---------------------------+-------------+----+
    |               |Mooring Shackle Data       |Wet Unit Mass|kg  |
    +---------------+---------------------------+-------------+----+
    |               |Foundation Drag Anchor Data|Wet Unit Mass|kg  |
    +---------------+---------------------------+-------------+----+
    |cost           |Wet Mate Connector Data    |Cost         |Euro|
    +---------------+---------------------------+-------------+----+
    |               |Dry Mate Connector Data    |Cost         |Euro|
    +---------------+---------------------------+-------------+----+
    |               |Mooring Swivel Data        |Cost         |Euro|
    +---------------+---------------------------+-------------+----+
    |               |Collection Point Data      |Cost         |Euro|
    +---------------+---------------------------+-------------+----+
    |               |Power Transformer Data     |Cost         |Euro|
    +---------------+---------------------------+-------------+----+
    |               |Mooring Shackle Data       |Cost         |Euro|
    +---------------+---------------------------+-------------+----+
    |               |Foundation Drag Anchor Data|Cost         |Euro|
    +---------------+---------------------------+-------------+----+


-------------------

.. |reference.component_mooring_continuous| replace:: ``reference.component_mooring_continuous``
.. _reference.component_mooring_continuous:

.. rubric:: Table: reference.component_mooring_continuous

| Approximate dump path: ``other\component\component_continuous\component_mooring_continuous.*``
| Linked to: |reference.component_continuous|_; |reference.component_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------+--------------------------------+-----------------+----+
    |          Column          |         Variable Name          |      Label      |Unit|
    +==========================+================================+=================+====+
    |id                        |                                |                 |    |
    +--------------------------+--------------------------------+-----------------+----+
    |fk_component_continuous_id|                                |                 |    |
    +--------------------------+--------------------------------+-----------------+----+
    |fk_component_type_id      |                                |                 |    |
    +--------------------------+--------------------------------+-----------------+----+
    |connecting_length         |Mooring Forerunner Assembly Data|Connecting Length|m   |
    +--------------------------+--------------------------------+-----------------+----+
    |                          |Mooring Chain Data              |Connecting Length|m   |
    +--------------------------+--------------------------------+-----------------+----+
    |minimum_breaking_load     |Mooring Chain Data              |Min Break Load   |N   |
    +--------------------------+--------------------------------+-----------------+----+
    |                          |Mooring Forerunner Assembly Data|Min Break Load   |N   |
    +--------------------------+--------------------------------+-----------------+----+
    |axial_stiffness           |Mooring Forerunner Assembly Data|Axial Stiffness  |N/m |
    +--------------------------+--------------------------------+-----------------+----+
    |                          |Mooring Chain Data              |Axial Stiffness  |N/m |
    +--------------------------+--------------------------------+-----------------+----+


-------------------

.. |reference.component_mooring_discrete| replace:: ``reference.component_mooring_discrete``
.. _reference.component_mooring_discrete:

.. rubric:: Table: reference.component_mooring_discrete

| Approximate dump path: ``other\component\component_discrete\component_mooring_discrete.*``
| Linked to: |reference.component_discrete|_; |reference.component_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------+--------------------+-----------------+----+
    |         Column         |   Variable Name    |      Label      |Unit|
    +========================+====================+=================+====+
    |id                      |                    |                 |    |
    +------------------------+--------------------+-----------------+----+
    |fk_component_discrete_id|                    |                 |    |
    +------------------------+--------------------+-----------------+----+
    |fk_component_type_id    |                    |                 |    |
    +------------------------+--------------------+-----------------+----+
    |nominal_diameter        |Mooring Swivel Data |Nominal Diameter |m   |
    +------------------------+--------------------+-----------------+----+
    |                        |Mooring Shackle Data|Nominal Diameter |m   |
    +------------------------+--------------------+-----------------+----+
    |connecting_length       |Mooring Shackle Data|Connecting Length|m   |
    +------------------------+--------------------+-----------------+----+
    |                        |Mooring Swivel Data |Connecting Length|m   |
    +------------------------+--------------------+-----------------+----+
    |minimum_breaking_load   |Mooring Swivel Data |Min Break Load   |N   |
    +------------------------+--------------------+-----------------+----+
    |                        |Mooring Shackle Data|Min Break Load   |N   |
    +------------------------+--------------------+-----------------+----+
    |axial_stiffness         |Mooring Shackle Data|Axial Stiffness  |N/m |
    +------------------------+--------------------+-----------------+----+
    |                        |Mooring Swivel Data |Axial Stiffness  |N/m |
    +------------------------+--------------------+-----------------+----+


-------------------

.. |reference.component_pile| replace:: ``reference.component_pile``
.. _reference.component_pile:

.. rubric:: Table: reference.component_pile

| Approximate dump path: ``other\component\component_continuous\component_pile.*``
| Linked to: |reference.component_type|_; |reference.component_continuous|_

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------+--------------------+--------------+-------+
    |          Column          |   Variable Name    |    Label     | Unit  |
    +==========================+====================+==============+=======+
    |id                        |                    |              |       |
    +--------------------------+--------------------+--------------+-------+
    |fk_component_continuous_id|                    |              |       |
    +--------------------------+--------------------+--------------+-------+
    |fk_component_type_id      |                    |              |       |
    +--------------------------+--------------------+--------------+-------+
    |wall_thickness            |Foundation Pile Data|Wall Thickness|m      |
    +--------------------------+--------------------+--------------+-------+
    |yield_stress              |Foundation Pile Data|Yield Stress  |N/m^{2}|
    +--------------------------+--------------------+--------------+-------+
    |youngs_modulus            |Foundation Pile Data|Youngs Modulus|N/m^{2}|
    +--------------------------+--------------------+--------------+-------+


-------------------

.. |reference.component_rope| replace:: ``reference.component_rope``
.. _reference.component_rope:

.. rubric:: Table: reference.component_rope

| Approximate dump path: ``other\component\component_continuous\component_rope.*``
| Linked to: |reference.component_continuous|_; |reference.component_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------+---------------------------------+----------------------+------+
    |          Column          |          Variable Name          |        Label         | Unit |
    +==========================+=================================+======================+======+
    |id                        |                                 |                      |      |
    +--------------------------+---------------------------------+----------------------+------+
    |fk_component_continuous_id|                                 |                      |      |
    +--------------------------+---------------------------------+----------------------+------+
    |fk_component_type_id      |                                 |                      |      |
    +--------------------------+---------------------------------+----------------------+------+
    |material                  |Mooring Rope Data                |Material              |      |
    +--------------------------+---------------------------------+----------------------+------+
    |minimum_breaking_load     |Mooring Rope Data                |Min Break Load        |N     |
    +--------------------------+---------------------------------+----------------------+------+
    |rope_stiffness_curve      |Mooring Rope Axial Stiffness Data|% of Min Breaking Load|N, N/m|
    +--------------------------+---------------------------------+----------------------+------+


-------------------

.. |reference.component_shared| replace:: ``reference.component_shared``
.. _reference.component_shared:

.. rubric:: Table: reference.component_shared

| Approximate dump path: ``other\component\component_shared.*``
| Linked to: |reference.component|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |         Column         |                    Variable Name                     |       Label        |          Unit           |
    +========================+======================================================+====================+=========================+
    |id                      |                                                      |                    |                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |fk_component_id         |                                                      |                    |                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |preparation_person_hours|                                                      |                    |                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |inspection_person_hours |                                                      |                    |                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |maintenance_person_hours|                                                      |                    |                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |replacement_person_hours|                                                      |                    |                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |ncfr_lower_bound        |Collection Points Non-Critical Failure Rates          |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dynamic Cable Non-Critical Failure Rates              |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Forerunner Assembly Non-Critical Failure Rates|Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Drag Anchor Non-Critical Failure Rates     |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Swivel Non-Critical Failure Rates             |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring shackle Non-Critical Failure Rates            |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Chain Non-Critical Failure Rates              |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Static Cable Non-Critical Failure Rates               |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Wet Mate Connector Non-Critical Failure Rates         |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Transformers Non-Critical Failure Rates               |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Pile Non-Critical Failure Rates            |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Rope Non-Critical Failure Rates               |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dry Mate Connector Non-Critical Failure Rates         |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |ncfr_mean               |Collection Points Non-Critical Failure Rates          |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dynamic Cable Non-Critical Failure Rates              |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Forerunner Assembly Non-Critical Failure Rates|Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Drag Anchor Non-Critical Failure Rates     |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Swivel Non-Critical Failure Rates             |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring shackle Non-Critical Failure Rates            |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Chain Non-Critical Failure Rates              |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Static Cable Non-Critical Failure Rates               |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Wet Mate Connector Non-Critical Failure Rates         |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Transformers Non-Critical Failure Rates               |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Pile Non-Critical Failure Rates            |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Rope Non-Critical Failure Rates               |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dry Mate Connector Non-Critical Failure Rates         |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |ncfr_upper_bound        |Collection Points Non-Critical Failure Rates          |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dynamic Cable Non-Critical Failure Rates              |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Forerunner Assembly Non-Critical Failure Rates|Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Drag Anchor Non-Critical Failure Rates     |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Swivel Non-Critical Failure Rates             |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring shackle Non-Critical Failure Rates            |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Chain Non-Critical Failure Rates              |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Static Cable Non-Critical Failure Rates               |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Wet Mate Connector Non-Critical Failure Rates         |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Transformers Non-Critical Failure Rates               |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Pile Non-Critical Failure Rates            |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Rope Non-Critical Failure Rates               |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dry Mate Connector Non-Critical Failure Rates         |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |cfr_lower_bound         |Foundation Pile Critical Failure Rates                |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Static Cable Critical Failure Rates                   |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dry Mate Connector Critical Failure Rates             |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Rope Critical Failure Rates                   |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Forerunner Assembly Critical Failure Rates    |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Chain Critical Failure Rates                  |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Wet Mate Connector Critical Failure Rates             |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Collection Points Critical Failure Rates              |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Transformers Critical Failure Rates                   |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Swivel Critical Failure Rates                 |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dynamic Cable Critical Failure Rates                  |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Drag Anchor Critical Failure Rates         |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Shackle Critical Failure Rates                |Lower Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |cfr_mean                |Foundation Pile Critical Failure Rates                |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Static Cable Critical Failure Rates                   |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dry Mate Connector Critical Failure Rates             |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Rope Critical Failure Rates                   |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Forerunner Assembly Critical Failure Rates    |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Chain Critical Failure Rates                  |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Wet Mate Connector Critical Failure Rates             |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Collection Points Critical Failure Rates              |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Transformers Critical Failure Rates                   |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Swivel Critical Failure Rates                 |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dynamic Cable Critical Failure Rates                  |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Drag Anchor Critical Failure Rates         |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Shackle Critical Failure Rates                |Mean                |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |cfr_upper_bound         |Foundation Pile Critical Failure Rates                |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Static Cable Critical Failure Rates                   |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dry Mate Connector Critical Failure Rates             |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Rope Critical Failure Rates                   |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Forerunner Assembly Critical Failure Rates    |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Chain Critical Failure Rates                  |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Wet Mate Connector Critical Failure Rates             |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Collection Points Critical Failure Rates              |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Transformers Critical Failure Rates                   |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Swivel Critical Failure Rates                 |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dynamic Cable Critical Failure Rates                  |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Drag Anchor Critical Failure Rates         |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Shackle Critical Failure Rates                |Upper Bound         |Failures per 10^{6} hours|
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |environmental_impact    |Wet Mate Connector Data                               |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dry Mate Connector Data                               |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Static Cable Data                                     |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Chain Data                                    |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Swivel Data                                   |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Collection Point Data                                 |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Pile Data                                  |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Power Transformer Data                                |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Dynamic Cable Data                                    |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Foundation Drag Anchor Data                           |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Forerunner Assembly Data                      |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Shackle Data                                  |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+
    |                        |Mooring Rope Data                                     |Environmental Impact|                         |
    +------------------------+------------------------------------------------------+--------------------+-------------------------+


-------------------

.. |reference.component_transformer| replace:: ``reference.component_transformer``
.. _reference.component_transformer:

.. rubric:: Table: reference.component_transformer

| Approximate dump path: ``other\component\component_discrete\component_transformer.*``
| Linked to: |reference.component_type|_; |reference.component_discrete|_

.. table:: 
    :widths: 15, 50, 20, 15

    +-------------------------+----------------------+-------------------------+----+
    |         Column          |    Variable Name     |          Label          |Unit|
    +=========================+======================+=========================+====+
    |id                       |                      |                         |    |
    +-------------------------+----------------------+-------------------------+----+
    |fk_component_discrete_id |                      |                         |    |
    +-------------------------+----------------------+-------------------------+----+
    |fk_component_type_id     |                      |                         |    |
    +-------------------------+----------------------+-------------------------+----+
    |maximum_water_depth      |Power Transformer Data|Max Water Depth          |m   |
    +-------------------------+----------------------+-------------------------+----+
    |power_rating             |Power Transformer Data|Power Rating             |VA  |
    +-------------------------+----------------------+-------------------------+----+
    |impedance                |Power Transformer Data|Impedance                |pc  |
    +-------------------------+----------------------+-------------------------+----+
    |windings                 |Power Transformer Data|Number of Windings       |    |
    +-------------------------+----------------------+-------------------------+----+
    |voltage_primary_winding  |Power Transformer Data|Primary Winding Voltage  |V   |
    +-------------------------+----------------------+-------------------------+----+
    |voltage_secondary_winding|Power Transformer Data|Secondary Winding Voltage|V   |
    +-------------------------+----------------------+-------------------------+----+
    |voltage_tertiary_winding |Power Transformer Data|Tertiary Winding Voltage |V   |
    +-------------------------+----------------------+-------------------------+----+
    |operational_temp_min     |Power Transformer Data|Min Temperature          |C   |
    +-------------------------+----------------------+-------------------------+----+
    |operational_temp_max     |Power Transformer Data|Max Temperature          |C   |
    +-------------------------+----------------------+-------------------------+----+


-------------------

.. |reference.component_type| replace:: ``reference.component_type``
.. _reference.component_type:

.. rubric:: Table: reference.component_type

| Approximate dump path: ``component_type.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+-------------+-----+----+
    |  Column   |Variable Name|Label|Unit|
    +===========+=============+=====+====+
    |id         |             |     |    |
    +-----------+-------------+-----+----+
    |description|             |     |    |
    +-----------+-------------+-----+----+


-------------------

.. |reference.constants| replace:: ``reference.constants``
.. _reference.constants:

.. rubric:: Table: reference.constants

| Approximate dump path: ``other\constants.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------------+--------------------------+-----+--------+
    |     Column      |      Variable Name       |Label|  Unit  |
    +=================+==========================+=====+========+
    |lock             |                          |     |        |
    +-----------------+--------------------------+-----+--------+
    |gravity          |Gravitational Acceleration|     |m/s^{2} |
    +-----------------+--------------------------+-----+--------+
    |sea_water_density|Sea Water Density         |     |kg/m^{3}|
    +-----------------+--------------------------+-----+--------+
    |air_density      |Air Density               |     |kg/m^{3}|
    +-----------------+--------------------------+-----+--------+
    |steel_density    |Steel Density             |     |kg/m^{3}|
    +-----------------+--------------------------+-----+--------+
    |concrete_density |Concrete Density          |     |kg/m^{3}|
    +-----------------+--------------------------+-----+--------+
    |grout_density    |Grout Density             |     |kg/m^{3}|
    +-----------------+--------------------------+-----+--------+
    |grout_strength   |Grout Compressive Strength|     |psi     |
    +-----------------+--------------------------+-----+--------+


-------------------

.. |reference.equipment_cable_burial| replace:: ``reference.equipment_cable_burial``
.. _reference.equipment_cable_burial:

.. rubric:: Table: reference.equipment_cable_burial

| Approximate dump path: ``other\equipment\equipment_cable_burial.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------------+-----------------------------------------+------------------------------+--------+
    |            Column            |              Variable Name              |            Label             |  Unit  |
    +==============================+=========================================+==============================+========+
    |id                            |                                         |                              |        |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |description                   |Installation Equipment: Cable Burial Data|Name                          |        |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |width                         |Installation Equipment: Cable Burial Data|Width                         |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |length                        |Installation Equipment: Cable Burial Data|Length                        |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |height                        |Installation Equipment: Cable Burial Data|Height                        |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |dry_mass                      |Installation Equipment: Cable Burial Data|Dry Mass                      |tonnes  |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |max_operating_depth           |Installation Equipment: Cable Burial Data|Max Operating Depth           |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |tow_force_required            |Installation Equipment: Cable Burial Data|Tow Force Required            |tonnes  |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |jetting_capability            |Installation Equipment: Cable Burial Data|Jetting Capability            |        |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |ploughing_capability          |Installation Equipment: Cable Burial Data|Ploughing Capability          |        |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |cutting_capability            |Installation Equipment: Cable Burial Data|Cutting Capability            |        |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |jetting_trench_depth          |Installation Equipment: Cable Burial Data|Jetting Trench Depth          |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |ploughing_trench_depth        |Installation Equipment: Cable Burial Data|Ploughing Trench Depth        |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |cutting_trench_depth          |Installation Equipment: Cable Burial Data|Cutting Trench Depth          |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |max_cable_diameter            |Installation Equipment: Cable Burial Data|Max Cable Diameter            |mm      |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |min_cable_bend_radius         |Installation Equipment: Cable Burial Data|Min Cable Bending Radius      |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |additional_equipment_footprint|Installation Equipment: Cable Burial Data|Additional Equipment Footprint|m^{2}   |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |additional_equipment_mass     |Installation Equipment: Cable Burial Data|Additional Equipment Mass     |tonnes  |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |equipment_day_rate            |Installation Equipment: Cable Burial Data|Equipment Day Rate            |Euro/day|
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |personnel_day_rate            |Installation Equipment: Cable Burial Data|Personnel Day Rate            |Euro/day|
    +------------------------------+-----------------------------------------+------------------------------+--------+


-------------------

.. |reference.equipment_divers| replace:: ``reference.equipment_divers``
.. _reference.equipment_divers:

.. rubric:: Table: reference.equipment_divers

| Approximate dump path: ``other\equipment\equipment_divers.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------------------+------------------------------------+------------------------------+--------+
    |        Column         |           Variable Name            |            Label             |  Unit  |
    +=======================+====================================+==============================+========+
    |id                     |                                    |                              |        |
    +-----------------------+------------------------------------+------------------------------+--------+
    |description            |Installation Equipment: Divers  Data|Name                          |        |
    +-----------------------+------------------------------------+------------------------------+--------+
    |max_operating_depth    |Installation Equipment: Divers  Data|Max Operating Depth           |m       |
    +-----------------------+------------------------------------+------------------------------+--------+
    |deployment_eq_footprint|Installation Equipment: Divers  Data|Deployment Equipment Footprint|m^{2}   |
    +-----------------------+------------------------------------+------------------------------+--------+
    |deployment_eq_mass     |Installation Equipment: Divers  Data|Deployment Equipment Mass     |tonnes  |
    +-----------------------+------------------------------------+------------------------------+--------+
    |total_day_rate         |Installation Equipment: Divers  Data|Total Day Rate                |Euro/day|
    +-----------------------+------------------------------------+------------------------------+--------+


-------------------

.. |reference.equipment_drilling_rigs| replace:: ``reference.equipment_drilling_rigs``
.. _reference.equipment_drilling_rigs:

.. rubric:: Table: reference.equipment_drilling_rigs

| Approximate dump path: ``other\equipment\equipment_drilling_rigs.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------------+------------------------------------------+------------------------------+--------+
    |            Column            |              Variable Name               |            Label             |  Unit  |
    +==============================+==========================================+==============================+========+
    |id                            |                                          |                              |        |
    +------------------------------+------------------------------------------+------------------------------+--------+
    |description                   |Installation Equipment: Drilling Rigs Data|Name                          |        |
    +------------------------------+------------------------------------------+------------------------------+--------+
    |diameter                      |Installation Equipment: Drilling Rigs Data|Diameter                      |m       |
    +------------------------------+------------------------------------------+------------------------------+--------+
    |length                        |Installation Equipment: Drilling Rigs Data|Length                        |m       |
    +------------------------------+------------------------------------------+------------------------------+--------+
    |dry_mass                      |Installation Equipment: Drilling Rigs Data|Dry Mass                      |tonnes  |
    +------------------------------+------------------------------------------+------------------------------+--------+
    |max_water_depth               |Installation Equipment: Drilling Rigs Data|Max Water Depth               |m       |
    +------------------------------+------------------------------------------+------------------------------+--------+
    |max_drilling_depth            |Installation Equipment: Drilling Rigs Data|Max Drilling Depth            |m       |
    +------------------------------+------------------------------------------+------------------------------+--------+
    |drilling_diameter_range       |Installation Equipment: Drilling Rigs Data|Drilling Diameter Range       |m       |
    +------------------------------+------------------------------------------+------------------------------+--------+
    |additional_equipment_footprint|Installation Equipment: Drilling Rigs Data|Additional Equipment Footprint|m^{2}   |
    +------------------------------+------------------------------------------+------------------------------+--------+
    |additional_equipment_mass     |Installation Equipment: Drilling Rigs Data|Additional Equipment Mass     |tonnes  |
    +------------------------------+------------------------------------------+------------------------------+--------+
    |equipment_day_rate            |Installation Equipment: Drilling Rigs Data|Equipment Day Rate            |Euro/day|
    +------------------------------+------------------------------------------+------------------------------+--------+
    |personnel_day_rate            |Installation Equipment: Drilling Rigs Data|Personnel Day Rate            |Euro/day|
    +------------------------------+------------------------------------------+------------------------------+--------+


-------------------

.. |reference.equipment_excavating| replace:: ``reference.equipment_excavating``
.. _reference.equipment_excavating:

.. rubric:: Table: reference.equipment_excavating

| Approximate dump path: ``other\equipment\equipment_excavating.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------+---------------------------------------+------------------+--------+
    |      Column      |             Variable Name             |      Label       |  Unit  |
    +==================+=======================================+==================+========+
    |id                |                                       |                  |        |
    +------------------+---------------------------------------+------------------+--------+
    |description       |Installation Equipment: Excavating Data|Name              |        |
    +------------------+---------------------------------------+------------------+--------+
    |width             |Installation Equipment: Excavating Data|Width             |m       |
    +------------------+---------------------------------------+------------------+--------+
    |height            |Installation Equipment: Excavating Data|Height            |m       |
    +------------------+---------------------------------------+------------------+--------+
    |dry_mass          |Installation Equipment: Excavating Data|Dry Mass          |tonnes  |
    +------------------+---------------------------------------+------------------+--------+
    |depth_rating      |Installation Equipment: Excavating Data|Depth Rating      |m       |
    +------------------+---------------------------------------+------------------+--------+
    |equipment_day_rate|Installation Equipment: Excavating Data|Equipment Day Rate|Euro/day|
    +------------------+---------------------------------------+------------------+--------+
    |personnel_day_rate|Installation Equipment: Excavating Data|Personnel Day Rate|Euro/day|
    +------------------+---------------------------------------+------------------+--------+


-------------------

.. |reference.equipment_hammer| replace:: ``reference.equipment_hammer``
.. _reference.equipment_hammer:

.. rubric:: Table: reference.equipment_hammer

| Approximate dump path: ``other\equipment\equipment_hammer.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------------+-----------------------------------+------------------------------+--------+
    |            Column            |           Variable Name           |            Label             |  Unit  |
    +==============================+===================================+==============================+========+
    |id                            |                                   |                              |        |
    +------------------------------+-----------------------------------+------------------------------+--------+
    |description                   |Installation Equipment: Hammer Data|Name                          |        |
    +------------------------------+-----------------------------------+------------------------------+--------+
    |length                        |Installation Equipment: Hammer Data|Length                        |m       |
    +------------------------------+-----------------------------------+------------------------------+--------+
    |dry_mass                      |Installation Equipment: Hammer Data|Dry Mass                      |tonnes  |
    +------------------------------+-----------------------------------+------------------------------+--------+
    |depth_rating                  |Installation Equipment: Hammer Data|Depth Rating                  |m       |
    +------------------------------+-----------------------------------+------------------------------+--------+
    |min_pile_diameter             |Installation Equipment: Hammer Data|Min Pile Diameter             |mm      |
    +------------------------------+-----------------------------------+------------------------------+--------+
    |max_pile_diameter             |Installation Equipment: Hammer Data|Max Pile Diameter             |mm      |
    +------------------------------+-----------------------------------+------------------------------+--------+
    |additional_equipment_footprint|Installation Equipment: Hammer Data|Additional Equipment Footprint|m^{2}   |
    +------------------------------+-----------------------------------+------------------------------+--------+
    |additional_equipment_mass     |Installation Equipment: Hammer Data|Additional Equipment Mass     |tonnes  |
    +------------------------------+-----------------------------------+------------------------------+--------+
    |equipment_day_rate            |Installation Equipment: Hammer Data|Equipment Day Rate            |Euro/day|
    +------------------------------+-----------------------------------+------------------------------+--------+
    |personnel_day_rate            |Installation Equipment: Hammer Data|Personnel Day Rate            |Euro/day|
    +------------------------------+-----------------------------------+------------------------------+--------+


-------------------

.. |reference.equipment_mattress| replace:: ``reference.equipment_mattress``
.. _reference.equipment_mattress:

.. rubric:: Table: reference.equipment_mattress

| Approximate dump path: ``other\equipment\equipment_mattress.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+----------------------------------------------+---------+------+
    |  Column   |                Variable Name                 |  Label  | Unit |
    +===========+==============================================+=========+======+
    |id         |                                              |         |      |
    +-----------+----------------------------------------------+---------+------+
    |description|Installation Equipment: Concrete Mattress Data|Name     |      |
    +-----------+----------------------------------------------+---------+------+
    |width      |Installation Equipment: Concrete Mattress Data|Width    |m     |
    +-----------+----------------------------------------------+---------+------+
    |length     |Installation Equipment: Concrete Mattress Data|Length   |m     |
    +-----------+----------------------------------------------+---------+------+
    |thickness  |Installation Equipment: Concrete Mattress Data|Thickness|m     |
    +-----------+----------------------------------------------+---------+------+
    |dry_mass   |Installation Equipment: Concrete Mattress Data|Dry Mass |tonnes|
    +-----------+----------------------------------------------+---------+------+
    |cost       |Installation Equipment: Concrete Mattress Data|Cost     |Euro  |
    +-----------+----------------------------------------------+---------+------+


-------------------

.. |reference.equipment_rock_filter_bags| replace:: ``reference.equipment_rock_filter_bags``
.. _reference.equipment_rock_filter_bags:

.. rubric:: Table: reference.equipment_rock_filter_bags

| Approximate dump path: ``other\equipment\equipment_rock_filter_bags.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+--------------------------------------+--------+------+
    |  Column   |            Variable Name             | Label  | Unit |
    +===========+======================================+========+======+
    |id         |                                      |        |      |
    +-----------+--------------------------------------+--------+------+
    |description|Installation Equipment: Rock Bags Data|Name    |      |
    +-----------+--------------------------------------+--------+------+
    |diameter   |Installation Equipment: Rock Bags Data|Diameter|m     |
    +-----------+--------------------------------------+--------+------+
    |height     |Installation Equipment: Rock Bags Data|Height  |m     |
    +-----------+--------------------------------------+--------+------+
    |dry_mass   |Installation Equipment: Rock Bags Data|Dry Mass|tonnes|
    +-----------+--------------------------------------+--------+------+
    |cost       |Installation Equipment: Rock Bags Data|Cost    |Euro  |
    +-----------+--------------------------------------+--------+------+


-------------------

.. |reference.equipment_rov| replace:: ``reference.equipment_rov``
.. _reference.equipment_rov:

.. rubric:: Table: reference.equipment_rov

| Approximate dump path: ``other\equipment\equipment_rov.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------------+--------------------------------+------------------------------+--------+
    |             Column             |         Variable Name          |            Label             |  Unit  |
    +================================+================================+==============================+========+
    |id                              |                                |                              |        |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |description                     |Installation Equipment: ROV Data|Name                          |        |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |rov_class                       |Installation Equipment: ROV Data|Class                         |        |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |width                           |Installation Equipment: ROV Data|Width                         |m       |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |length                          |Installation Equipment: ROV Data|Length                        |m       |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |height                          |Installation Equipment: ROV Data|Height                        |m       |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |dry_mass                        |Installation Equipment: ROV Data|Dry Mass                      |tonnes  |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |depth_rating                    |Installation Equipment: ROV Data|Depth Rating                  |m       |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |payload                         |Installation Equipment: ROV Data|Payload                       |tonnes  |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |manipulator_grip_force          |Installation Equipment: ROV Data|Manipulator Grip Force        |N       |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |additional_equipment_footprint  |Installation Equipment: ROV Data|Additional Equipment Footprint|m^{2}   |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |additional_equipment_mass       |Installation Equipment: ROV Data|Additional Equipment Mass     |tonnes  |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |additional_equipment_supervisors|Installation Equipment: ROV Data|Number of Supervisors         |        |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |additional_equipment_technicians|Installation Equipment: ROV Data|Number of Technicians         |        |
    +--------------------------------+--------------------------------+------------------------------+--------+
    |equipment_day_rate              |Installation Equipment: ROV Data|Equipment Day Rate            |Euro/day|
    +--------------------------------+--------------------------------+------------------------------+--------+
    |supervisor_day_rate             |Installation Equipment: ROV Data|Supervisor Day Rate           |Euro/day|
    +--------------------------------+--------------------------------+------------------------------+--------+
    |technician_day_rate             |Installation Equipment: ROV Data|Technician Day Rate           |Euro/day|
    +--------------------------------+--------------------------------+------------------------------+--------+


-------------------

.. |reference.equipment_soil_lay_rates| replace:: ``reference.equipment_soil_lay_rates``
.. _reference.equipment_soil_lay_rates:

.. rubric:: Table: reference.equipment_soil_lay_rates

| Approximate dump path: ``other\equipment\equipment_soil_lay_rates.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------+-----------------------------------------+-----------------+----+
    |    Column    |              Variable Name              |      Label      |Unit|
    +==============+=========================================+=================+====+
    |equipment_type|Installation Technique Soil Compatibility|Technique        |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_ls       |Installation Technique Soil Compatibility|Loose Sand       |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_ms       |Installation Technique Soil Compatibility|Medium Sand      |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_ds       |Installation Technique Soil Compatibility|Dense Sand       |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_vsc      |Installation Technique Soil Compatibility|Very Soft Clay   |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_sc       |Installation Technique Soil Compatibility|Soft Clay        |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_fc       |Installation Technique Soil Compatibility|Firm Clay        |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_stc      |Installation Technique Soil Compatibility|Stiff Clay       |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_hgt      |Installation Technique Soil Compatibility|Hard Glacial Till|    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_cm       |Installation Technique Soil Compatibility|Cemented         |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_src      |Installation Technique Soil Compatibility|Soft Rock Coral  |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_hr       |Installation Technique Soil Compatibility|Hard Rock        |    |
    +--------------+-----------------------------------------+-----------------+----+
    |soil_gc       |Installation Technique Soil Compatibility|Gravel Cobble    |    |
    +--------------+-----------------------------------------+-----------------+----+


-------------------

.. |reference.equipment_soil_penet_rates| replace:: ``reference.equipment_soil_penet_rates``
.. _reference.equipment_soil_penet_rates:

.. rubric:: Table: reference.equipment_soil_penet_rates

| Approximate dump path: ``other\equipment\equipment_soil_penet_rates.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------+-----------------------------------------+-----------------+------+
    |    Column    |              Variable Name              |      Label      | Unit |
    +==============+=========================================+=================+======+
    |equipment_type|Installation Equipment: Penetration Rates|Technique        |      |
    +--------------+-----------------------------------------+-----------------+------+
    |soil_ls       |Installation Equipment: Penetration Rates|Loose Sand       |m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_ms       |Installation Equipment: Penetration Rates|Medium Sand      |m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_ds       |Installation Equipment: Penetration Rates|Dense Sand       |m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_vsc      |Installation Equipment: Penetration Rates|Very Soft Clay   |m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_sc       |Installation Equipment: Penetration Rates|Soft Clay        |m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_fc       |Installation Equipment: Penetration Rates|Firm Clay        |m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_stc      |Installation Equipment: Penetration Rates|Stiff Clay       |m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_hgt      |Installation Equipment: Penetration Rates|Hard Glacial Till|m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_cm       |Installation Equipment: Penetration Rates|Cemented         |m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_src      |Installation Equipment: Penetration Rates|Soft Rock Coral  |m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_hr       |Installation Equipment: Penetration Rates|Hard Rock        |m/hour|
    +--------------+-----------------------------------------+-----------------+------+
    |soil_gc       |Installation Equipment: Penetration Rates|Gravel Cobble    |m/hour|
    +--------------+-----------------------------------------+-----------------+------+


-------------------

.. |reference.equipment_split_pipe| replace:: ``reference.equipment_split_pipe``
.. _reference.equipment_split_pipe:

.. rubric:: Table: reference.equipment_split_pipe

| Approximate dump path: ``other\equipment\equipment_split_pipe.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+----------------------------------------+------+----+
    |  Column   |             Variable Name              |Label |Unit|
    +===========+========================================+======+====+
    |id         |                                        |      |    |
    +-----------+----------------------------------------+------+----+
    |description|Installation Equipment: Split Pipes Data|Name  |    |
    +-----------+----------------------------------------+------+----+
    |length     |Installation Equipment: Split Pipes Data|Length|mm  |
    +-----------+----------------------------------------+------+----+
    |cost       |Installation Equipment: Split Pipes Data|Cost  |Euro|
    +-----------+----------------------------------------+------+----+


-------------------

.. |reference.equipment_vibro_driver| replace:: ``reference.equipment_vibro_driver``
.. _reference.equipment_vibro_driver:

.. rubric:: Table: reference.equipment_vibro_driver

| Approximate dump path: ``other\equipment\equipment_vibro_driver.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------------+-----------------------------------------+------------------------------+--------+
    |            Column            |              Variable Name              |            Label             |  Unit  |
    +==============================+=========================================+==============================+========+
    |id                            |                                         |                              |        |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |description                   |Installation Equipment: Vibro Driver Data|Name                          |        |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |width                         |Installation Equipment: Vibro Driver Data|Width                         |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |length                        |Installation Equipment: Vibro Driver Data|Length                        |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |height                        |Installation Equipment: Vibro Driver Data|Height                        |m       |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |vibro_driver_mass             |Installation Equipment: Vibro Driver Data|Vibro Driver Mass             |tonnes  |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |clamp_mass                    |Installation Equipment: Vibro Driver Data|Clamp Mass                    |tonnes  |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |min_pile_diameter             |Installation Equipment: Vibro Driver Data|Min Pile Diameter             |mm      |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |max_pile_diameter             |Installation Equipment: Vibro Driver Data|Max Pile Diameter             |mm      |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |max_pile_mass                 |Installation Equipment: Vibro Driver Data|Max Pile Mass                 |tonnes  |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |additional_equipment_footprint|Installation Equipment: Vibro Driver Data|Additional Equipment Footprint|m^{2}   |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |additional_equipment_mass     |Installation Equipment: Vibro Driver Data|Additional Equipment Mass     |tonnes  |
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |equipment_day_rate            |Installation Equipment: Vibro Driver Data|Equipment Day Rate            |Euro/day|
    +------------------------------+-----------------------------------------+------------------------------+--------+
    |personnel_day_rate            |Installation Equipment: Vibro Driver Data|Personnel Day Rate            |Euro/day|
    +------------------------------+-----------------------------------------+------------------------------+--------+


-------------------

.. |reference.operations_limit_cs| replace:: ``reference.operations_limit_cs``
.. _reference.operations_limit_cs:

.. rubric:: Table: reference.operations_limit_cs

| Approximate dump path: ``other\operations\operations_limit_cs.*``
| Linked to: |reference.operations_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------+--------------------------------+----------------------+----+
    |     Column     |         Variable Name          |        Label         |Unit|
    +================+================================+======================+====+
    |id              |                                |                      |    |
    +----------------+--------------------------------+----------------------+----+
    |fk_operations_id|                                |                      |    |
    +----------------+--------------------------------+----------------------+----+
    |cs_limit        |Current Speed Operational Limits|Current Velocity Limit|m/s |
    +----------------+--------------------------------+----------------------+----+


-------------------

.. |reference.operations_limit_hs| replace:: ``reference.operations_limit_hs``
.. _reference.operations_limit_hs:

.. rubric:: Table: reference.operations_limit_hs

| Approximate dump path: ``other\operations\operations_limit_hs.*``
| Linked to: |reference.operations_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------+------------------------------+--------+----+
    |     Column     |        Variable Name         | Label  |Unit|
    +================+==============================+========+====+
    |id              |                              |        |    |
    +----------------+------------------------------+--------+----+
    |fk_operations_id|                              |        |    |
    +----------------+------------------------------+--------+----+
    |hs_limit        |Wave Height Operational Limits|Hs Limit|m   |
    +----------------+------------------------------+--------+----+


-------------------

.. |reference.operations_limit_tp| replace:: ``reference.operations_limit_tp``
.. _reference.operations_limit_tp:

.. rubric:: Table: reference.operations_limit_tp

| Approximate dump path: ``other\operations\operations_limit_tp.*``
| Linked to: |reference.operations_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------+------------------------------+--------+----+
    |     Column     |        Variable Name         | Label  |Unit|
    +================+==============================+========+====+
    |id              |                              |        |    |
    +----------------+------------------------------+--------+----+
    |fk_operations_id|                              |        |    |
    +----------------+------------------------------+--------+----+
    |tp_limit        |Wave Period Operational Limits|Tp Limit|s   |
    +----------------+------------------------------+--------+----+


-------------------

.. |reference.operations_limit_ws| replace:: ``reference.operations_limit_ws``
.. _reference.operations_limit_ws:

.. rubric:: Table: reference.operations_limit_ws

| Approximate dump path: ``other\operations\operations_limit_ws.*``
| Linked to: |reference.operations_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------+-----------------------------+-------------------+----+
    |     Column     |        Variable Name        |       Label       |Unit|
    +================+=============================+===================+====+
    |id              |                             |                   |    |
    +----------------+-----------------------------+-------------------+----+
    |fk_operations_id|                             |                   |    |
    +----------------+-----------------------------+-------------------+----+
    |ws_limit        |Wind Speed Operational Limits|Wind Velocity Limit|m/s |
    +----------------+-----------------------------+-------------------+----+


-------------------

.. |reference.operations_type| replace:: ``reference.operations_type``
.. _reference.operations_type:

.. rubric:: Table: reference.operations_type

| Approximate dump path: ``operations_type.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+--------------------------------+-----+----+
    |  Column   |         Variable Name          |Label|Unit|
    +===========+================================+=====+====+
    |id         |                                |     |    |
    +-----------+--------------------------------+-----+----+
    |description|Wave Height Operational Limits  |Name |    |
    +-----------+--------------------------------+-----+----+
    |           |Wind Speed Operational Limits   |Name |    |
    +-----------+--------------------------------+-----+----+
    |           |Current Speed Operational Limits|Name |    |
    +-----------+--------------------------------+-----+----+
    |           |Wave Period Operational Limits  |Name |    |
    +-----------+--------------------------------+-----+----+


-------------------

.. |reference.ports| replace:: ``reference.ports``
.. _reference.ports:

.. rubric:: Table: reference.ports

| Approximate dump path: ``other\ports.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------------+--------------+------------------------------+------------+
    |            Column            |Variable Name |            Label             |    Unit    |
    +==============================+==============+==============================+============+
    |id                            |              |                              |            |
    +------------------------------+--------------+------------------------------+------------+
    |name                          |Ports Data    |Name                          |            |
    +------------------------------+--------------+------------------------------+------------+
    |                              |Port Locations|                              |            |
    +------------------------------+--------------+------------------------------+------------+
    |country                       |Ports Data    |Country                       |            |
    +------------------------------+--------------+------------------------------+------------+
    |type_of_terminal              |Ports Data    |Type of Terminal              |            |
    +------------------------------+--------------+------------------------------+------------+
    |entrance_width                |Ports Data    |Entrance Width                |m           |
    +------------------------------+--------------+------------------------------+------------+
    |terminal_length               |Ports Data    |Terminal Length               |m           |
    +------------------------------+--------------+------------------------------+------------+
    |terminal_load_bearing         |Ports Data    |Terminal Load Bearing         |tonnes/m^{2}|
    +------------------------------+--------------+------------------------------+------------+
    |terminal_draught              |Ports Data    |Terminal Draught              |m           |
    +------------------------------+--------------+------------------------------+------------+
    |terminal_area                 |Ports Data    |Terminal Area                 |m^{2}       |
    +------------------------------+--------------+------------------------------+------------+
    |max_gantry_crane_lift_capacity|Ports Data    |Max Gantry Crane Lift Capacity|tonnes      |
    +------------------------------+--------------+------------------------------+------------+
    |max_tower_crane_lift_capacity |Ports Data    |Max Tower Crane Lift Capacity |tonnes      |
    +------------------------------+--------------+------------------------------+------------+
    |jacking_capability            |Ports Data    |Jacking Capability            |            |
    +------------------------------+--------------+------------------------------+------------+
    |point_location                |Port Locations|                              |degrees     |
    +------------------------------+--------------+------------------------------+------------+


-------------------

.. |reference.ref_current_drag_coef_rect| replace:: ``reference.ref_current_drag_coef_rect``
.. _reference.ref_current_drag_coef_rect:

.. rubric:: Table: reference.ref_current_drag_coef_rect

| Approximate dump path: ``other\constants\ref_current_drag_coef_rect.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +---------------+---------------------------------------------+---------------------+----+
    |    Column     |                Variable Name                |        Label        |Unit|
    +===============+=============================================+=====================+====+
    |width_length   |Rectangular Section Current Drag Coefficients|Width / Length       |    |
    +---------------+---------------------------------------------+---------------------+----+
    |thickness_width|Rectangular Section Current Drag Coefficients|Thickness / Width = 0|    |
    +---------------+---------------------------------------------+---------------------+----+


-------------------

.. |reference.ref_drag_coef_cyl| replace:: ``reference.ref_drag_coef_cyl``
.. _reference.ref_drag_coef_cyl:

.. rubric:: Table: reference.ref_drag_coef_cyl

| Approximate dump path: ``other\constants\ref_drag_coef_cyl.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +---------------+--------------------------+----------------------------+----+
    |    Column     |      Variable Name       |           Label            |Unit|
    +===============+==========================+============================+====+
    |reynolds_number|Cylinder Drag Coefficients|Reynolds Number             |    |
    +---------------+--------------------------+----------------------------+----+
    |smooth         |Cylinder Drag Coefficients|Smooth Coefficient          |    |
    +---------------+--------------------------+----------------------------+----+
    |roughness_1e_5 |Cylinder Drag Coefficients|Roughness = 1e-5 Coefficient|    |
    +---------------+--------------------------+----------------------------+----+
    |roughness_1e_2 |Cylinder Drag Coefficients|Roughness = 1e-2 Coefficient|    |
    +---------------+--------------------------+----------------------------+----+


-------------------

.. |reference.ref_drift_coef_float_rect| replace:: ``reference.ref_drift_coef_float_rect``
.. _reference.ref_drift_coef_float_rect:

.. rubric:: Table: reference.ref_drift_coef_float_rect

| Approximate dump path: ``other\constants\ref_drift_coef_float_rect.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------------+--------------------------------------+----------------------+----+
    |        Column        |            Variable Name             |        Label         |Unit|
    +======================+======================================+======================+====+
    |wavenumber_draft      |Rectangular Section Drift Coefficients|Wavenumber * Draft    |    |
    +----------------------+--------------------------------------+----------------------+----+
    |reflection_coefficient|Rectangular Section Drift Coefficients|Reflection Coefficient|    |
    +----------------------+--------------------------------------+----------------------+----+


-------------------

.. |reference.ref_holding_capacity_factors_plate_anchors| replace:: ``reference.ref_holding_capacity_factors_plate_anchors``
.. _reference.ref_holding_capacity_factors_plate_anchors:

.. rubric:: Table: reference.ref_holding_capacity_factors_plate_anchors

| Approximate dump path: ``other\constants\ref_holding_capacity_factors_plate_anchors.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------------------+------------------------------------+-----------------------------------+----+
    |           Column           |           Variable Name            |               Label               |Unit|
    +============================+====================================+===================================+====+
    |relative_embedment_depth    |Drained Soil Holding Capacity Factor|Relative Embedment Depth           |    |
    +----------------------------+------------------------------------+-----------------------------------+----+
    |drained_friction_angle_20deg|Drained Soil Holding Capacity Factor|Drained Friction Angle = 20 degrees|    |
    +----------------------------+------------------------------------+-----------------------------------+----+
    |drained_friction_angle_25deg|Drained Soil Holding Capacity Factor|Drained Friction Angle = 25 degrees|    |
    +----------------------------+------------------------------------+-----------------------------------+----+
    |drained_friction_angle_30deg|Drained Soil Holding Capacity Factor|Drained Friction Angle = 30 degrees|    |
    +----------------------------+------------------------------------+-----------------------------------+----+
    |drained_friction_angle_35deg|Drained Soil Holding Capacity Factor|Drained Friction Angle = 35 degrees|    |
    +----------------------------+------------------------------------+-----------------------------------+----+
    |drained_friction_angle_40deg|Drained Soil Holding Capacity Factor|Drained Friction Angle = 40 degrees|    |
    +----------------------------+------------------------------------+-----------------------------------+----+


-------------------

.. |reference.ref_line_bcf| replace:: ``reference.ref_line_bcf``
.. _reference.ref_line_bcf:

.. rubric:: Table: reference.ref_line_bcf

| Approximate dump path: ``other\constants\ref_line_bcf.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------------------+-------------------------------------------+-----------------------+-------+
    |        Column         |               Variable Name               |         Label         | Unit  |
    +=======================+===========================================+=======================+=======+
    |soil_friction_angle    |Buried Mooring Line Bearing Capacity Factor|Soil Friction Angle    |degrees|
    +-----------------------+-------------------------------------------+-----------------------+-------+
    |bearing_capacity_factor|Buried Mooring Line Bearing Capacity Factor|Bearing Capacity Factor|       |
    +-----------------------+-------------------------------------------+-----------------------+-------+


-------------------

.. |reference.ref_pile_deflection_coefficients| replace:: ``reference.ref_pile_deflection_coefficients``
.. _reference.ref_pile_deflection_coefficients:

.. rubric:: Table: reference.ref_pile_deflection_coefficients

| Approximate dump path: ``other\constants\ref_pile_deflection_coefficients.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------------+----------------------------+-----------------+----+
    |     Column      |       Variable Name        |      Label      |Unit|
    +=================+============================+=================+====+
    |depth_coefficient|Pile Deflection Coefficients|Depth Coefficient|    |
    +-----------------+----------------------------+-----------------+----+
    |coefficient_ay   |Pile Deflection Coefficients|Ay               |    |
    +-----------------+----------------------------+-----------------+----+
    |coefficient_by   |Pile Deflection Coefficients|By               |    |
    +-----------------+----------------------------+-----------------+----+


-------------------

.. |reference.ref_pile_limiting_values_noncalcareous| replace:: ``reference.ref_pile_limiting_values_noncalcareous``
.. _reference.ref_pile_limiting_values_noncalcareous:

.. rubric:: Table: reference.ref_pile_limiting_values_noncalcareous

| Approximate dump path: ``other\constants\ref_pile_limiting_values_noncalcareous.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------------+-------------------------------------------+---------------------------+-------+
    |         Column         |               Variable Name               |           Label           | Unit  |
    +========================+===========================================+===========================+=======+
    |soil_friction_angle     |Pile Skin Friction and End Bearing Capacity|Soil Friction Angle        |degrees|
    +------------------------+-------------------------------------------+---------------------------+-------+
    |friction_angle_sand_pile|Pile Skin Friction and End Bearing Capacity|Friction Angle Sand-Pile   |degrees|
    +------------------------+-------------------------------------------+---------------------------+-------+
    |bearing_capacity_factor |Pile Skin Friction and End Bearing Capacity|Max Bearing Capacity Factor|       |
    +------------------------+-------------------------------------------+---------------------------+-------+
    |max_unit_skin_friction  |Pile Skin Friction and End Bearing Capacity|Max Unit Skin Friction     |N/m^{2}|
    +------------------------+-------------------------------------------+---------------------------+-------+
    |max_end_bearing_capacity|Pile Skin Friction and End Bearing Capacity|Max End Bearing Capacity   |N/m^{2}|
    +------------------------+-------------------------------------------+---------------------------+-------+


-------------------

.. |reference.ref_pile_moment_coefficient_sam| replace:: ``reference.ref_pile_moment_coefficient_sam``
.. _reference.ref_pile_moment_coefficient_sam:

.. rubric:: Table: reference.ref_pile_moment_coefficient_sam

| Approximate dump path: ``other\constants\ref_pile_moment_coefficient_sam.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |                  Column                   |      Variable Name       |                     Label                     |Unit|
    +===========================================+==========================+===============================================+====+
    |depth_coefficient                          |Am Pile Moment Coefficient|Depth Coefficient                              |    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |pile_length_relative_soil_pile_stiffness_10|Am Pile Moment Coefficient|Pile Length / Relative Soil-Pile Stiffness = 10|    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |pile_length_relative_soil_pile_stiffness_5 |Am Pile Moment Coefficient|Pile Length / Relative Soil-Pile Stiffness = 5 |    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |pile_length_relative_soil_pile_stiffness_4 |Am Pile Moment Coefficient|Pile Length / Relative Soil-Pile Stiffness = 4 |    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |pile_length_relative_soil_pile_stiffness_3 |Am Pile Moment Coefficient|Pile Length / Relative Soil-Pile Stiffness = 3 |    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |pile_length_relative_soil_pile_stiffness_2 |Am Pile Moment Coefficient|Pile Length / Relative Soil-Pile Stiffness = 2 |    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+


-------------------

.. |reference.ref_pile_moment_coefficient_sbm| replace:: ``reference.ref_pile_moment_coefficient_sbm``
.. _reference.ref_pile_moment_coefficient_sbm:

.. rubric:: Table: reference.ref_pile_moment_coefficient_sbm

| Approximate dump path: ``other\constants\ref_pile_moment_coefficient_sbm.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |                  Column                   |      Variable Name       |                     Label                     |Unit|
    +===========================================+==========================+===============================================+====+
    |depth_coefficient                          |Bm Pile Moment Coefficient|Depth Coefficient                              |    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |pile_length_relative_soil_pile_stiffness_10|Bm Pile Moment Coefficient|Pile Length / Relative Soil-Pile Stiffness = 10|    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |pile_length_relative_soil_pile_stiffness_5 |Bm Pile Moment Coefficient|Pile Length / Relative Soil-Pile Stiffness = 5 |    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |pile_length_relative_soil_pile_stiffness_4 |Bm Pile Moment Coefficient|Pile Length / Relative Soil-Pile Stiffness = 4 |    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |pile_length_relative_soil_pile_stiffness_3 |Bm Pile Moment Coefficient|Pile Length / Relative Soil-Pile Stiffness = 3 |    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+
    |pile_length_relative_soil_pile_stiffness_2 |Bm Pile Moment Coefficient|Pile Length / Relative Soil-Pile Stiffness = 2 |    |
    +-------------------------------------------+--------------------------+-----------------------------------------------+----+


-------------------

.. |reference.ref_rectangular_wave_inertia| replace:: ``reference.ref_rectangular_wave_inertia``
.. _reference.ref_rectangular_wave_inertia:

.. rubric:: Table: reference.ref_rectangular_wave_inertia

| Approximate dump path: ``other\constants\ref_rectangular_wave_inertia.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------+---------------------------------------------+--------------------+----+
    |       Column       |                Variable Name                |       Label        |Unit|
    +====================+=============================================+====================+====+
    |width/length        |Rectangular Section Wave Inertia Coefficients|Width / Length      |    |
    +--------------------+---------------------------------------------+--------------------+----+
    |inertia_coefficients|Rectangular Section Wave Inertia Coefficients|Inertia Coefficients|    |
    +--------------------+---------------------------------------------+--------------------+----+


-------------------

.. |reference.ref_subgrade_reaction_coefficient_cohesionless| replace:: ``reference.ref_subgrade_reaction_coefficient_cohesionless``
.. _reference.ref_subgrade_reaction_coefficient_cohesionless:

.. rubric:: Table: reference.ref_subgrade_reaction_coefficient_cohesionless

| Approximate dump path: ``other\constants\ref_subgrade_reaction_coefficient_cohesionless.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------------------------+--------------------------------------------------+--------------------------------+----+
    |           Column            |                  Variable Name                   |             Label              |Unit|
    +=============================+==================================================+================================+====+
    |allowable_deflection_diameter|Cohesionless Soil Coefficient of Subgrade Reaction|Allowable Deflection / Diameter |    |
    +-----------------------------+--------------------------------------------------+--------------------------------+----+
    |relative_density_35          |Cohesionless Soil Coefficient of Subgrade Reaction|35% Relative Density Coefficient|    |
    +-----------------------------+--------------------------------------------------+--------------------------------+----+
    |relative_density_50          |Cohesionless Soil Coefficient of Subgrade Reaction|50% Relative Density Coefficient|    |
    +-----------------------------+--------------------------------------------------+--------------------------------+----+
    |relative_density_65          |Cohesionless Soil Coefficient of Subgrade Reaction|65% Relative Density Coefficient|    |
    +-----------------------------+--------------------------------------------------+--------------------------------+----+
    |relative_density_85          |Cohesionless Soil Coefficient of Subgrade Reaction|85% Relative Density Coefficient|    |
    +-----------------------------+--------------------------------------------------+--------------------------------+----+


-------------------

.. |reference.ref_subgrade_reaction_coefficient_k1_cohesive| replace:: ``reference.ref_subgrade_reaction_coefficient_k1_cohesive``
.. _reference.ref_subgrade_reaction_coefficient_k1_cohesive:

.. rubric:: Table: reference.ref_subgrade_reaction_coefficient_k1_cohesive

| Approximate dump path: ``other\constants\ref_subgrade_reaction_coefficient_k1_cohesive.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------------------------+----------------------------------------------+-------------------------------+----+
    |           Column            |                Variable Name                 |             Label             |Unit|
    +=============================+==============================================+===============================+====+
    |allowable_deflection_diameter|Cohesive Soil Coefficient of Subgrade Reaction|Allowable Deflection / Diameter|    |
    +-----------------------------+----------------------------------------------+-------------------------------+----+
    |softclay                     |Cohesive Soil Coefficient of Subgrade Reaction|Soft Clay Coefficient          |    |
    +-----------------------------+----------------------------------------------+-------------------------------+----+
    |stiffclay                    |Cohesive Soil Coefficient of Subgrade Reaction|Stiff Clay Coefficient         |    |
    +-----------------------------+----------------------------------------------+-------------------------------+----+


-------------------

.. |reference.ref_superline_nylon| replace:: ``reference.ref_superline_nylon``
.. _reference.ref_superline_nylon:

.. rubric:: Table: reference.ref_superline_nylon

| Approximate dump path: ``other\constants\ref_superline_nylon.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +---------+-------------+-----+----+
    | Column  |Variable Name|Label|Unit|
    +=========+=============+=====+====+
    |extension|             |     |    |
    +---------+-------------+-----+----+
    |load_mbl |             |     |    |
    +---------+-------------+-----+----+


-------------------

.. |reference.ref_superline_polyester| replace:: ``reference.ref_superline_polyester``
.. _reference.ref_superline_polyester:

.. rubric:: Table: reference.ref_superline_polyester

| Approximate dump path: ``other\constants\ref_superline_polyester.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +---------+-------------+-----+----+
    | Column  |Variable Name|Label|Unit|
    +=========+=============+=====+====+
    |extension|             |     |    |
    +---------+-------------+-----+----+
    |load_mbl |             |     |    |
    +---------+-------------+-----+----+


-------------------

.. |reference.ref_superline_steelite| replace:: ``reference.ref_superline_steelite``
.. _reference.ref_superline_steelite:

.. rubric:: Table: reference.ref_superline_steelite

| Approximate dump path: ``other\constants\ref_superline_steelite.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +---------+-------------+-----+----+
    | Column  |Variable Name|Label|Unit|
    +=========+=============+=====+====+
    |extension|             |     |    |
    +---------+-------------+-----+----+
    |load_mbl |             |     |    |
    +---------+-------------+-----+----+


-------------------

.. |reference.ref_wake_amplification_factor_cyl| replace:: ``reference.ref_wake_amplification_factor_cyl``
.. _reference.ref_wake_amplification_factor_cyl:

.. rubric:: Table: reference.ref_wake_amplification_factor_cyl

| Approximate dump path: ``other\constants\ref_wake_amplification_factor_cyl.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------------------------------------+-----------------------------------+------------------------------------+----+
    |                 Column                  |           Variable Name           |               Label                |Unit|
    +=========================================+===================================+====================================+====+
    |kc_steady_drag_coefficient               |Cylinder Wake Amplification Factors|kc/steady Drag Coefficient          |    |
    +-----------------------------------------+-----------------------------------+------------------------------------+----+
    |amplification_factor_for_smooth_cylinders|Cylinder Wake Amplification Factors|Smooth Cylinder Amplification Factor|    |
    +-----------------------------------------+-----------------------------------+------------------------------------+----+
    |amplification_factor_for_rough_cylinders |Cylinder Wake Amplification Factors|Rough Cylinder Amplification Factor |    |
    +-----------------------------------------+-----------------------------------+------------------------------------+----+


-------------------

.. |reference.ref_wind_drag_coef_rect| replace:: ``reference.ref_wind_drag_coef_rect``
.. _reference.ref_wind_drag_coef_rect:

.. rubric:: Table: reference.ref_wind_drag_coef_rect

| Approximate dump path: ``other\constants\ref_wind_drag_coef_rect.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------+------------------------------------------+------------------------+----+
    |          Column          |              Variable Name               |         Label          |Unit|
    +==========================+==========================================+========================+====+
    |width_length              |Rectangular Section Wind Drag Coefficients|Width / Length          |    |
    +--------------------------+------------------------------------------+------------------------+----+
    |height_breadth_between_0_1|Rectangular Section Wind Drag Coefficients|0 < Height / Breadth < 1|    |
    +--------------------------+------------------------------------------+------------------------+----+
    |height_breadth_less_1     |Rectangular Section Wind Drag Coefficients|Height / Breadth = 1    |    |
    +--------------------------+------------------------------------------+------------------------+----+
    |height_breadth_less_2     |Rectangular Section Wind Drag Coefficients|Height / Breadth = 2    |    |
    +--------------------------+------------------------------------------+------------------------+----+
    |height_breadth_less_4     |Rectangular Section Wind Drag Coefficients|Height / Breadth = 4    |    |
    +--------------------------+------------------------------------------+------------------------+----+
    |height_breadth_less_6     |Rectangular Section Wind Drag Coefficients|Height / Breadth = 6    |    |
    +--------------------------+------------------------------------------+------------------------+----+
    |height_breadth_less_10    |Rectangular Section Wind Drag Coefficients|Height / Breadth = 10   |    |
    +--------------------------+------------------------------------------+------------------------+----+
    |height_breadth_less_20    |Rectangular Section Wind Drag Coefficients|Height / Breadth = 20   |    |
    +--------------------------+------------------------------------------+------------------------+----+


-------------------

.. |reference.soil_type| replace:: ``reference.soil_type``
.. _reference.soil_type:

.. rubric:: Table: reference.soil_type

| Approximate dump path: ``soil_type.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+---------------------+---------+----+
    |  Column   |    Variable Name    |  Label  |Unit|
    +===========+=====================+=========+====+
    |id         |                     |         |    |
    +-----------+---------------------+---------+----+
    |description|Soil Properties Table|Soil Type|    |
    +-----------+---------------------+---------+----+


-------------------

.. |reference.soil_type_geotechnical_properties| replace:: ``reference.soil_type_geotechnical_properties``
.. _reference.soil_type_geotechnical_properties:

.. rubric:: Table: reference.soil_type_geotechnical_properties

| Approximate dump path: ``other\constants\soil_type_geotechnical_properties.*``
| Linked to: |reference.soil_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------------------------------+---------------------+--------------------------------------+-------+
    |                      Column                      |    Variable Name    |                Label                 | Unit  |
    +==================================================+=====================+======================================+=======+
    |fk_soil_type_id                                   |                     |                                      |       |
    +--------------------------------------------------+---------------------+--------------------------------------+-------+
    |drained_soil_friction_angle                       |Soil Properties Table|Drained Soil Friction Angle           |degrees|
    +--------------------------------------------------+---------------------+--------------------------------------+-------+
    |relative_soil_density                             |Soil Properties Table|Relative Soil Density                 |%      |
    +--------------------------------------------------+---------------------+--------------------------------------+-------+
    |buoyant_unit_weight_of_soil                       |Soil Properties Table|Buoyant Unit Weight of Soil           |N/m^3  |
    +--------------------------------------------------+---------------------+--------------------------------------+-------+
    |effective_drained_cohesion                        |Soil Properties Table|Effective Drained Cohesion            |N/m^2  |
    +--------------------------------------------------+---------------------+--------------------------------------+-------+
    |seafloor_friction_coefficient                     |Soil Properties Table|Seafloor Friction Coefficient         |       |
    +--------------------------------------------------+---------------------+--------------------------------------+-------+
    |soil_sensitivity                                  |Soil Properties Table|Soil Sensitivity                      |       |
    +--------------------------------------------------+---------------------+--------------------------------------+-------+
    |rock_compressive_strength                         |Soil Properties Table|Rock Compressive Strength             |N/m^2  |
    +--------------------------------------------------+---------------------+--------------------------------------+-------+
    |undrained_soil_shear_strength_constant_term       |Soil Properties Table|Undrained Soil / Rock Shear Strength 1|N/m^2  |
    +--------------------------------------------------+---------------------+--------------------------------------+-------+
    |undrained_soil_shear_strength_depth_dependent_term|Soil Properties Table|Undrained Soil / Rock Shear Strength 2|N/m^2  |
    +--------------------------------------------------+---------------------+--------------------------------------+-------+


-------------------

.. |reference.vehicle| replace:: ``reference.vehicle``
.. _reference.vehicle:

.. rubric:: Table: reference.vehicle

| Approximate dump path: ``other\vehicle.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+-----------------------------------------------+-----+----+
    |  Column   |                 Variable Name                 |Label|Unit|
    +===========+===============================================+=====+====+
    |id         |                                               |     |    |
    +-----------+-----------------------------------------------+-----+----+
    |description|Vessels: Cable Laying Vessel Data              |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Cable Laying Barge Data               |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Anchor Handling Tug Supply Vessel Data|Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Helicopter Data                       |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Jackup Vessel Data                    |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Crane Vessel Data                     |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Construction Support Vessel Data      |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Multicat Data                         |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Crane Barge Data                      |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Barge Data                            |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Crew Transfer Vessel Data             |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Jackup Barge Data                     |Name |    |
    +-----------+-----------------------------------------------+-----+----+
    |           |Vessels: Tugboat Data                          |Name |    |
    +-----------+-----------------------------------------------+-----+----+


-------------------

.. |reference.vehicle_helicopter| replace:: ``reference.vehicle_helicopter``
.. _reference.vehicle_helicopter:

.. rubric:: Table: reference.vehicle_helicopter

| Approximate dump path: ``other\vehicle\vehicle_helicopter.*``
| Linked to: |reference.vehicle|_; |reference.vehicle_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------------+------------------------+-------------------+------------+
    |        Column        |     Variable Name      |       Label       |    Unit    |
    +======================+========================+===================+============+
    |id                    |                        |                   |            |
    +----------------------+------------------------+-------------------+------------+
    |fk_vehicle_id         |                        |                   |            |
    +----------------------+------------------------+-------------------+------------+
    |fk_vehicle_type_id    |                        |                   |            |
    +----------------------+------------------------+-------------------+------------+
    |deck_space            |Vessels: Helicopter Data|Deck Space         |m^{2}       |
    +----------------------+------------------------+-------------------+------------+
    |max_deck_load_pressure|Vessels: Helicopter Data|Max Deck Pressure  |tonnes/m^{2}|
    +----------------------+------------------------+-------------------+------------+
    |max_cargo_mass        |Vessels: Helicopter Data|Max Cargo Mass     |tonnes      |
    +----------------------+------------------------+-------------------+------------+
    |crane_max_load_mass   |Vessels: Helicopter Data|Max Crane Load Mass|tonnes      |
    +----------------------+------------------------+-------------------+------------+
    |external_personel     |Vessels: Helicopter Data|External  Personnel|            |
    +----------------------+------------------------+-------------------+------------+


-------------------

.. |reference.vehicle_shared| replace:: ``reference.vehicle_shared``
.. _reference.vehicle_shared:

.. rubric:: Table: reference.vehicle_shared

| Approximate dump path: ``other\vehicle\vehicle_shared.*``
| Linked to: |reference.vehicle|_

.. table:: 
    :widths: 15, 50, 20, 15

    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |           Column           |                 Variable Name                 |           Label            |  Unit  |
    +============================+===============================================+============================+========+
    |id                          |                                               |                            |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |fk_vehicle_id               |                                               |                            |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |gross_tonnage               |Vessels: Cable Laying Vessel Data              |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Gross Tonnage               |        |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |length                      |Vessels: Cable Laying Vessel Data              |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Length                      |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |consumption                 |Vessels: Cable Laying Vessel Data              |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Consumption                 |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Consumption                 |l/hour  |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |transit_speed               |Vessels: Cable Laying Vessel Data              |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Transit Speed               |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |transit_max_hs              |Vessels: Cable Laying Vessel Data              |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Max Transit Hs              |m       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |transit_max_tp              |Vessels: Cable Laying Vessel Data              |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Max Transit Tp              |s       |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |transit_max_cs              |Vessels: Cable Laying Vessel Data              |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Max Transit Current Velocity|m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |transit_max_ws              |Vessels: Cable Laying Vessel Data              |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Max Transit Wind Velocity   |m/s     |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |mobilisation_time           |Vessels: Cable Laying Vessel Data              |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Mobilisation Time           |hours   |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |mobilisation_percentage_cost|Vessels: Cable Laying Vessel Data              |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Mobilisation Percentage Cost|pc      |
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |min_day_rate                |Vessels: Cable Laying Vessel Data              |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Min Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |max_day_rate                |Vessels: Cable Laying Vessel Data              |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Vessel Data                    |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Multicat Data                         |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Barge Data                      |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crane Vessel Data                     |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Barge Data                            |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Crew Transfer Vessel Data             |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Cable Laying Barge Data               |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Anchor Handling Tug Supply Vessel Data|Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Helicopter Data                       |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Construction Support Vessel Data      |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Jackup Barge Data                     |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+
    |                            |Vessels: Tugboat Data                          |Max Day Rate                |Euro/day|
    +----------------------------+-----------------------------------------------+----------------------------+--------+


-------------------

.. |reference.vehicle_type| replace:: ``reference.vehicle_type``
.. _reference.vehicle_type:

.. rubric:: Table: reference.vehicle_type

| Approximate dump path: ``vehicle_type.*``

.. table:: 
    :widths: 15, 50, 20, 15

    +-----------+-------------+-----+----+
    |  Column   |Variable Name|Label|Unit|
    +===========+=============+=====+====+
    |id         |             |     |    |
    +-----------+-------------+-----+----+
    |description|             |     |    |
    +-----------+-------------+-----+----+


-------------------

.. |reference.vehicle_vessel_anchor_handling| replace:: ``reference.vehicle_vessel_anchor_handling``
.. _reference.vehicle_vessel_anchor_handling:

.. rubric:: Table: reference.vehicle_vessel_anchor_handling

| Approximate dump path: ``other\vehicle\vehicle_vessel_anchor_handling.*``
| Linked to: |reference.vehicle_type|_; |reference.vehicle|_

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------------+----------------------+--------------------------------+------------+
    |             Column             |    Variable Name     |             Label              |    Unit    |
    +================================+======================+================================+============+
    |id                              |                      |                                |            |
    +--------------------------------+----------------------+--------------------------------+------------+
    |fk_vehicle_id                   |                      |                                |            |
    +--------------------------------+----------------------+--------------------------------+------------+
    |fk_vehicle_type_id              |                      |                                |            |
    +--------------------------------+----------------------+--------------------------------+------------+
    |beam                            |Vessels: Multicat Data|Beam                            |m           |
    +--------------------------------+----------------------+--------------------------------+------------+
    |max_draft                       |Vessels: Multicat Data|Max Draft                       |m           |
    +--------------------------------+----------------------+--------------------------------+------------+
    |consumption_towing              |Vessels: Multicat Data|Towing Consumption              |l/hour      |
    +--------------------------------+----------------------+--------------------------------+------------+
    |deck_space                      |Vessels: Multicat Data|Deck Space                      |m^{2}       |
    +--------------------------------+----------------------+--------------------------------+------------+
    |max_deck_load_pressure          |Vessels: Multicat Data|Max Deck Pressure               |tonnes/m^{2}|
    +--------------------------------+----------------------+--------------------------------+------------+
    |max_cargo_mass                  |Vessels: Multicat Data|Max Cargo Mass                  |tonnes      |
    +--------------------------------+----------------------+--------------------------------+------------+
    |crane_max_load_mass             |Vessels: Multicat Data|Max Crane Load Mass             |tonnes      |
    +--------------------------------+----------------------+--------------------------------+------------+
    |bollard_pull                    |Vessels: Multicat Data|Bollard Pull                    |tonnes      |
    +--------------------------------+----------------------+--------------------------------+------------+
    |anchor_handling_drum_capacity   |Vessels: Multicat Data|Anchor Handling Drum Capacity   |m           |
    +--------------------------------+----------------------+--------------------------------+------------+
    |anchor_handling_winch_rated_pull|Vessels: Multicat Data|Anchor Handling Winch Rated Pull|tonnes      |
    +--------------------------------+----------------------+--------------------------------+------------+
    |external_personel               |Vessels: Multicat Data|External  Personnel             |            |
    +--------------------------------+----------------------+--------------------------------+------------+
    |towing_max_hs                   |Vessels: Multicat Data|Max Towing Hs                   |m           |
    +--------------------------------+----------------------+--------------------------------+------------+


-------------------

.. |reference.vehicle_vessel_cable_laying| replace:: ``reference.vehicle_vessel_cable_laying``
.. _reference.vehicle_vessel_cable_laying:

.. rubric:: Table: reference.vehicle_vessel_cable_laying

| Approximate dump path: ``other\vehicle\vehicle_vessel_cable_laying.*``
| Linked to: |reference.vehicle_type|_; |reference.vehicle|_

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------------+---------------------------------+--------------------------------+------------+
    |             Column             |          Variable Name          |             Label              |    Unit    |
    +================================+=================================+================================+============+
    |id                              |                                 |                                |            |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |fk_vehicle_id                   |                                 |                                |            |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |fk_vehicle_type_id              |                                 |                                |            |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |beam                            |Vessels: Cable Laying Vessel Data|Beam                            |m           |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Beam                            |m           |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |max_draft                       |Vessels: Cable Laying Vessel Data|Max Draft                       |m           |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Max Draft                       |m           |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |deck_space                      |Vessels: Cable Laying Vessel Data|Deck Space                      |m^{2}       |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Deck Space                      |m^{2}       |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |max_deck_load_pressure          |Vessels: Cable Laying Vessel Data|Max Deck Pressure               |tonnes/m^{2}|
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Max Deck Pressure               |tonnes/m^{2}|
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |max_cargo_mass                  |Vessels: Cable Laying Vessel Data|Max Cargo Mass                  |tonnes      |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Max Cargo Mass                  |tonnes      |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |crane_max_load_mass             |Vessels: Cable Laying Vessel Data|Max Crane Load Mass             |tonnes      |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Max Crane Load Mass             |tonnes      |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |bollard_pull                    |Vessels: Cable Laying Vessel Data|Bollard Pull                    |tonnes      |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |number_turntables               |Vessels: Cable Laying Vessel Data|Number of Turntables            |            |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Number of Turntables            |            |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |turntable_max_load_mass         |Vessels: Cable Laying Vessel Data|Max Turntable Load Mass         |tonnes      |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Max Turntable Load Mass         |tonnes      |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |turntable_inner_diameter        |Vessels: Cable Laying Vessel Data|Turntable Inner Diameter        |m           |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Turntable Inner Diameter        |m           |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |cable_splice_capabilities       |Vessels: Cable Laying Vessel Data|Cable Splice Capabilities       |            |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Cable Splice Capabilities       |            |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |dynamic_positioning_capabilities|Vessels: Cable Laying Vessel Data|Dynamic Positioning Capabilities|            |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |Dynamic Positioning Capabilities|            |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |external_personel               |Vessels: Cable Laying Vessel Data|External  Personnel             |            |
    +--------------------------------+---------------------------------+--------------------------------+------------+
    |                                |Vessels: Cable Laying Barge Data |External  Personnel             |            |
    +--------------------------------+---------------------------------+--------------------------------+------------+


-------------------

.. |reference.vehicle_vessel_cargo| replace:: ``reference.vehicle_vessel_cargo``
.. _reference.vehicle_vessel_cargo:

.. rubric:: Table: reference.vehicle_vessel_cargo

| Approximate dump path: ``other\vehicle\vehicle_vessel_cargo.*``
| Linked to: |reference.vehicle|_; |reference.vehicle_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |             Column             |              Variable Name              |             Label              |    Unit    |
    +================================+=========================================+================================+============+
    |id                              |                                         |                                |            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |fk_vehicle_id                   |                                         |                                |            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |fk_vehicle_type_id              |                                         |                                |            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |beam                            |Vessels: Crane Barge Data                |Beam                            |m           |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crane Vessel Data               |Beam                            |m           |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Barge Data                      |Beam                            |m           |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crew Transfer Vessel Data       |Beam                            |m           |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Construction Support Vessel Data|Beam                            |m           |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |max_draft                       |Vessels: Crane Barge Data                |Max Draft                       |m           |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crane Vessel Data               |Max Draft                       |m           |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Barge Data                      |Max Draft                       |m           |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crew Transfer Vessel Data       |Max Draft                       |m           |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Construction Support Vessel Data|Max Draft                       |m           |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |deck_space                      |Vessels: Crane Barge Data                |Deck Space                      |m^{2}       |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crane Vessel Data               |Deck Space                      |m^{2}       |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Barge Data                      |Deck Space                      |m^{2}       |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crew Transfer Vessel Data       |Deck Space                      |m^{2}       |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Construction Support Vessel Data|Deck Space                      |m^{2}       |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |max_deck_load_pressure          |Vessels: Crane Barge Data                |Max Deck Pressure               |tonnes/m^{2}|
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crane Vessel Data               |Max Deck Pressure               |tonnes/m^{2}|
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Barge Data                      |Max Deck Pressure               |tonnes/m^{2}|
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crew Transfer Vessel Data       |Max Deck Pressure               |tonnes/m^{2}|
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Construction Support Vessel Data|Max Deck Pressure               |tonnes/m^{2}|
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |max_cargo_mass                  |Vessels: Crane Barge Data                |Max Cargo Mass                  |tonnes      |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crane Vessel Data               |Max Cargo Mass                  |tonnes      |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Barge Data                      |Max Cargo Mass                  |tonnes      |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crew Transfer Vessel Data       |Max Cargo Mass                  |tonnes      |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Construction Support Vessel Data|Max Cargo Mass                  |tonnes      |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |crane_max_load_mass             |Vessels: Crane Barge Data                |Max Crane Load Mass             |tonnes      |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crane Vessel Data               |Max Crane Load Mass             |tonnes      |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Barge Data                      |Max Crane Load Mass             |tonnes      |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crew Transfer Vessel Data       |Max Crane Load Mass             |tonnes      |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Construction Support Vessel Data|Max Crane Load Mass             |tonnes      |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |dynamic_positioning_capabilities|Vessels: Crane Barge Data                |Dynamic Positioning Capabilities|            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crane Vessel Data               |Dynamic Positioning Capabilities|            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Barge Data                      |Dynamic Positioning Capabilities|            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crew Transfer Vessel Data       |Dynamic Positioning Capabilities|            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Construction Support Vessel Data|Dynamic Positioning Capabilities|            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |external_personel               |Vessels: Crane Barge Data                |External  Personnel             |            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crane Vessel Data               |External  Personnel             |            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Barge Data                      |External  Personnel             |            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Crew Transfer Vessel Data       |External  Personnel             |            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+
    |                                |Vessels: Construction Support Vessel Data|External  Personnel             |            |
    +--------------------------------+-----------------------------------------+--------------------------------+------------+


-------------------

.. |reference.vehicle_vessel_jackup| replace:: ``reference.vehicle_vessel_jackup``
.. _reference.vehicle_vessel_jackup:

.. rubric:: Table: reference.vehicle_vessel_jackup

| Approximate dump path: ``other\vehicle\vehicle_vessel_jackup.*``
| Linked to: |reference.vehicle_type|_; |reference.vehicle|_

.. table:: 
    :widths: 15, 50, 20, 15

    +--------------------------------+---------------------------+--------------------------------+------------+
    |             Column             |       Variable Name       |             Label              |    Unit    |
    +================================+===========================+================================+============+
    |id                              |                           |                                |            |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |fk_vehicle_id                   |                           |                                |            |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |fk_vehicle_type_id              |                           |                                |            |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |beam                            |Vessels: Jackup Vessel Data|Beam                            |m           |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Beam                            |m           |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |max_draft                       |Vessels: Jackup Vessel Data|Max Draft                       |m           |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Max Draft                       |m           |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |deck_space                      |Vessels: Jackup Vessel Data|Deck Space                      |m^{2}       |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Deck Space                      |m^{2}       |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |max_deck_load_pressure          |Vessels: Jackup Vessel Data|Max Deck Pressure               |tonnes/m^{2}|
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Max Deck Pressure               |tonnes/m^{2}|
    +--------------------------------+---------------------------+--------------------------------+------------+
    |max_cargo_mass                  |Vessels: Jackup Vessel Data|Max Cargo Mass                  |tonnes      |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Max Cargo Mass                  |tonnes      |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |crane_max_load_mass             |Vessels: Jackup Vessel Data|Max Crane Load Mass             |tonnes      |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Max Crane Load Mass             |tonnes      |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |dynamic_positioning_capabilities|Vessels: Jackup Vessel Data|Dynamic Positioning Capabilities|            |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Dynamic Positioning Capabilities|            |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |jackup_max_water_depth          |Vessels: Jackup Vessel Data|Max Jack-Up Water Depth         |m           |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Max Jack-Up Water Depth         |m           |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |jackup_speed_down               |Vessels: Jackup Vessel Data|Jack-Up Lowering Velocity       |m/min       |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Jack-Up Lowering Velocity       |m/min       |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |jackup_max_payload_mass         |Vessels: Jackup Vessel Data|Max Jack-Up Payload             |tonnes      |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Max Jack-Up Payload             |tonnes      |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |external_personel               |Vessels: Jackup Vessel Data|External  Personnel             |            |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |External  Personnel             |            |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |jacking_max_hs                  |Vessels: Jackup Vessel Data|Max Jacking Hs                  |m           |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Max Jacking Hs                  |m           |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |jacking_max_tp                  |Vessels: Jackup Vessel Data|Max Jacking Tp                  |s           |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Max Jacking Tp                  |s           |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |jacking_max_cs                  |Vessels: Jackup Vessel Data|Max Jacking Current Velocity    |m/s         |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Max Jacking Current Velocity    |m/s         |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |jacking_max_ws                  |Vessels: Jackup Vessel Data|Max Jacking Wind Velocity       |m/s         |
    +--------------------------------+---------------------------+--------------------------------+------------+
    |                                |Vessels: Jackup Barge Data |Max Jacking Wind Velocity       |m/s         |
    +--------------------------------+---------------------------+--------------------------------+------------+


-------------------

.. |reference.vehicle_vessel_tugboat| replace:: ``reference.vehicle_vessel_tugboat``
.. _reference.vehicle_vessel_tugboat:

.. rubric:: Table: reference.vehicle_vessel_tugboat

| Approximate dump path: ``other\vehicle\vehicle_vessel_tugboat.*``
| Linked to: |reference.vehicle|_; |reference.vehicle_type|_

.. table:: 
    :widths: 15, 50, 20, 15

    +------------------+---------------------+------------------+------+
    |      Column      |    Variable Name    |      Label       | Unit |
    +==================+=====================+==================+======+
    |id                |                     |                  |      |
    +------------------+---------------------+------------------+------+
    |fk_vehicle_id     |                     |                  |      |
    +------------------+---------------------+------------------+------+
    |fk_vehicle_type_id|                     |                  |      |
    +------------------+---------------------+------------------+------+
    |beam              |Vessels: Tugboat Data|Beam              |m     |
    +------------------+---------------------+------------------+------+
    |max_draft         |Vessels: Tugboat Data|Max Draft         |m     |
    +------------------+---------------------+------------------+------+
    |consumption_towing|Vessels: Tugboat Data|Towing Consumption|l/hour|
    +------------------+---------------------+------------------+------+
    |bollard_pull      |Vessels: Tugboat Data|Bollard Pull      |tonnes|
    +------------------+---------------------+------------------+------+
