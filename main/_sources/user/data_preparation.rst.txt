.. _data_preparation:

****************
Data Preparation
****************

Introduction
============

This chapter describes how to prepare data for storage within the 
DTOcean database. Data representing sites and devices are covered in 
extended detail. Storage of sites and devices in the persistent database 
allows reuse across multiple projects. For sites this also gives access 
to automatic computational domain resizing. 

A list of all database tables and their association to variables within DTOcean 
is given in the last section of the chapter. This includes the site and device 
tables, and the tables that store reference data to be used in all 
simulations. Data that is relevant only to a single project is not stored in 
the DTOcean database and is not discussed here. 

Site
====

Conventions
-----------

The following conventions are used for site data used within DTOcean: [#f1]_

 * Depths are **negative**
 * The datum for depths is **mean sea level**
 * Wave directions are described using **coming-from** convention. Wave 
   height and period conventions differ between variables.
 * Current directions are described using **going-to** convention
 * Wind speeds are measured at a reference height of 10m and the direction 
   uses **coming-from** convention

.. _boundaries:

Boundaries
----------

.. _fig_boundaries:

.. figure:: /images/boundaries.png

   Schematic of spatial site data

DTOcean uses two computational grids to store bathymetric, sedimentary and any 
environmental data that varies over the domain. The first grid covers the area 
where devices are to be deployed, known as the **lease area**, and the other 
covers the area where the export cable may be placed, known as the **cable 
corridor**. The lease area grid is normally of higher resolution than the cable 
corridor grid. The two areas must also overlap, as seen in 
:numref:`fig_boundaries`, and, more precisely, contain coincident points. As 
such, it is recommended that the low resolution grid spacing be a multiple of 
the high resolution grid. Details regarding defining these grids is provided in 
the :ref:`grids` section. 

The extents of the grids are demarcated by two polygons, the **lease boundary** 
and **cable corridor boundary**. These polygons allow the user to modify the 
size of the computational domain and reduce the amount of grid data collected 
from the DTOcean database. Note, an overlapping region must be maintained when 
modifying the lease and cable corridor boundaries. The **cable corridor landing 
point** is also shown in :numref:`fig_boundaries`, that marks the termination 
of the export cable at the shoreline. Although not a boundary, this should be 
included in the database so that the user can ensure it remains within the 
cable corridor following modifications. Within the lease area or cable 
corridor, additional polygons can be defined that excludes any grid points 
within them from computation. These areas are known as **no-go areas** and the 
user can define as many as required for a particular site. 

All features described thus far are given in (UTM-like) conformal projection 
coordinates (see :ref:`grids`). A final outer boundary, known as the 
**site boundary**, is defined using geodesic coordinates, to show the location 
of the site on a map. This is also why the polygon shown in 
:numref:`fig_boundaries` is slightly skewed.

Most of the features described above are stored in the **project.site** table 
of the DTOcean database (see the :ref:`database_tables` section). An example 
entry to the table (following being :ref:`dumped to a file<load_dump>`) is 
shown in :numref:`tab_site`. The geo-spatial objects are represented as WKT 
strings, but are stored as binary objects in the DTOcean database itself. No-go 
areas are stored in the **project.constraint** and 
**project.cable_corridor_constraint** tables. 

.. _tab_site:
.. table:: Example entry to 'site' table

    +-------------------------+-----------------------------------------------------------------------------------------------------+---------------------------------------------+
    | Column                  | Example Row                                                                                         | Notes                                       |
    +=========================+=====================================================================================================+=============================================+
    | id                      | 1                                                                                                   |                                             |
    +-------------------------+-----------------------------------------------------------------------------------------------------+---------------------------------------------+
    | site_name               | Eureka, CA                                                                                          |                                             |
    +-------------------------+-----------------------------------------------------------------------------------------------------+---------------------------------------------+
    | lease_area_proj4_string | +proj=utm +zone=10 +ellps=WGS84 +datum=WGS84 +units=m +no_defs                                      | See :ref:`grids`                            |
    +-------------------------+-----------------------------------------------------------------------------------------------------+---------------------------------------------+
    | site_boundary           | SRID=4326;POLYGON ((-124.15 40.75, -124.375 40.75, -124.375 40.925, -124.15 40.925, -124.15 40.75)) | WKT Polygon in WGS84 coordinates            |
    +-------------------------+-----------------------------------------------------------------------------------------------------+---------------------------------------------+
    | lease_boundary          | POLYGON ((391250 4517000, 386000 4520000, 391500 4529450, 396650 4526600, 391250 4517000))          | WKT Polygon in local projection coordinates |
    +-------------------------+-----------------------------------------------------------------------------------------------------+---------------------------------------------+
    | corridor_boundary       | POLYGON ((398600 4518300, 392800 4521500, 395900 4527000, 401600 4524000, 398600 4518300))          | WKT Polygon in local projection coordinates |
    +-------------------------+-----------------------------------------------------------------------------------------------------+---------------------------------------------+
    | cable_landing_location  | POINT (398575 4518325)                                                                              | WKT Point in local projection coordinates   |
    +-------------------------+-----------------------------------------------------------------------------------------------------+---------------------------------------------+


.. _grids:

Grids
-----

DTOcean requires two Cartesian grids for describing data that varies over the
lease area and cable corridor. These grids are drawn using a conformal
projection, with units of metres, similar, but not restricted to, Universal
Transverse Mercator (UTM) projections. When entering grid data into the DTOcean
database, the projection used for the grids must also be included. DTOcean
uses a `Proj4 <https://proj4.org/>`__ string to define projections. For 
instance, ::

    +proj=utm +zone=10 +ellps=WGS84 +datum=WGS84 +units=m +no_defs 

describes the `WGS 84 / UTM zone 10N 
<http://spatialreference.org/ref/epsg/wgs-84-utm-zone-10n/>`__ projection. Any 
conformal projection with units of metres is valid, but note that the 
validity of the projection is not checked by the software. The projection is
stored in the **project.site** table of the DTOcean database (see the 
:ref:`boundaries` section).

The data on the grid is stored in points at it's vertices, as seen in 
:numref:`fig_grid_plan`. The spacing of the grid must be uniform in the x and 
y directions but can differ between them. When entering points into the DTOcean 
database, those which lie outside of the boundary polygon do not need to be 
included. When reading the grid from the database, DTOcean will add points with 
NaN value to create a rectangular grid. When exporting and importing grids 
using file formats such as NetCDF, these NaN points are included. 

.. _fig_grid_plan:

.. figure:: /images/grid_plan.png

   Plan view of the computational grid

.. _bathymetry_sediments:

Bathymetry and Sediments
------------------------

Grids may also be defined with multiple layers. These layers can be used to 
define sedimentary layers, time series, etc. :numref:`fig_grid_layers` shows 
the schematic for the storage of sedimentary data in DTOcean. Two values for 
each layer of sediment are associated to every grid point -- the depth at which 
the sediment layer starts and the sediment type for that layer. The depth of 
the first layer represents the seabed bathymetry and the last defined layer 
is assumed to have infinite depth. A minimum of one sediment layer must be 
provided.

.. _fig_grid_layers:

.. figure:: /images/grid_layers.png

   Schematic of the data structure for describing sedimentary layers

The database definition of the sediment layers differs slightly from this 
definition, in that the distance of the start of each layer below the sea floor 
is used rather than the depth below sea level. An example of a single grid 
point definition, containing two sediment layers, defined in the 
**project.bathymetry** and **project.bathymetry_layer** tables, is show in 
:numref:`tab_bathymetry` and :numref:`tab_bathymetry_layer`. 

The **fk_bathymetry_id** column in the bathymetry_layer table references the 
**id** column of the associated point in the bathymetry table. A reference to 
an **id** in the **reference.soil_type** table (shown in 
:numref:`tab_soil_type`) is added to the **fk_soil_type_id** column of the 
bathymetry_layer table to select which sediment type belongs to the layer. 
Note, it is only necessary to include a value in the **mannings_no** column of 
the bathymetry table when the site will be used for tidal current energy 
extraction. 

.. _tab_bathymetry:
.. table:: Example entry to 'bathymetry' table
    
    +--------------+--------------------------+-----------------------------+
    |       Column |       Example Row        |           Notes             |
    +==============+==========================+=============================+
    |           id |       1                  |                             |
    +--------------+--------------------------+-----------------------------+
    |    utm_point |  POINT (391505 6651003)  | |utm_point_note|            |
    +--------------+--------------------------+-----------------------------+
    |        depth |     -50                  | (m -ve)                     |
    +--------------+--------------------------+-----------------------------+
    |  mannings_no |     0.3                  | Used only for tidal energy  |
    +--------------+--------------------------+-----------------------------+

.. |utm_point_note| replace:: WKT format (after :ref:`dump<load_dump>`)

.. _tab_bathymetry_layer:
.. table:: Example entries to 'bathymetry_layer' table
    
    +--------------------+-----------------------+-----------------------+-----------------------------------------------+
    |             Column |    Layer 1 Example    |    Layer 2 Example    | Notes                                         |
    +====================+=======================+=======================+===============================================+
    |                 id |         1             |         2             |                                               |
    +--------------------+-----------------------+-----------------------+-----------------------------------------------+
    |   fk_bathymetry_id |         1             |         1             | References id in :numref:`tab_bathymetry`     |
    +--------------------+-----------------------+-----------------------+-----------------------------------------------+
    |    fk_soil_type_id |         6             |        11             | References id in :numref:`tab_soil_type`      |
    +--------------------+-----------------------+-----------------------+-----------------------------------------------+
    |        layer_order |         1             |         2             | Indexed from 1                                |
    +--------------------+-----------------------+-----------------------+-----------------------------------------------+
    |      initial_depth |         0             |        10             | Measured from the sea floor (m +ve)           |
    +--------------------+-----------------------+-----------------------+-----------------------------------------------+

.. _tab_soil_type:
.. table:: Contents of 'soil_type' table
    
    +-----+-------------------+
    |  id | description       |
    +=====+===================+
    | 1   | loose sand        |
    +-----+-------------------+
    | 2   | medium sand       |
    +-----+-------------------+
    | 3   | dense sand        |
    +-----+-------------------+
    | 4   | very soft clay    |
    +-----+-------------------+
    | 5   | soft clay         |
    +-----+-------------------+
    | 6   | firm clay         |
    +-----+-------------------+
    | 7   | stiff clay        |
    +-----+-------------------+
    | 8   | hard glacial till |
    +-----+-------------------+
    | 9   | cemented          |
    +-----+-------------------+
    | 10  | soft rock coral   |
    +-----+-------------------+
    | 11  | hard rock         |
    +-----+-------------------+
    | 12  | gravel cobble     |
    +-----+-------------------+

.. _environmental_data:

Environmental Data
------------------

Tidal Current Energy
++++++++++++++++++++

When defining a site for tidal current energy extraction, layers of grid points 
are used to define the the currents throughout the domain. 
:numref:`tab_time_series_energy_tidal` shows an example of two hours of current 
data defined in the **project.time_series_energy_tidal** table for the example 
point shown in :numref:`tab_bathymetry`. :numref:`tab_bathymetry` should also 
have the Manning's number (**mannings_no** column) defined for each point in 
tidal current energy scenarios. 

Common practice, thus far, is to prepare two weeks of hourly tidal current data 
(between the flood and neap tides). Thus the 
**project.time_series_energy_tidal** table will contain 336 rows for every grid 
point defined. This table is easily the largest stored within the DTOcean 
database and the user must take care that it does not become computationally 
unmanageable. The recommended upper limit is approximately :math:`5 \times 
10^{6}` rows (per site), and the grid resolution of the site should be adapted 
accordingly. For each entry to the time_series_energy_tidal table, the velocity 
components in the x and y directions (columns **u** and **v** respectively), 
the turbulence intensity and the sea surface elevation w.r.t. mean sea level 
(column **ssh**) must be provided. 

.. _tab_time_series_energy_tidal:
.. table:: Example entries to 'time_series_energy_tidal' table

    +-----------------------+----------------+----------------+--------------------------------------------+
    |  Column               | Hour 1 Example | Hour 2 Example | Notes                                      |
    +=======================+================+================+============================================+
    | id                    | 1              | 2              |                                            |
    +-----------------------+----------------+----------------+--------------------------------------------+
    | fk_bathymetry_id      | 1              | 1              | References id in :numref:`tab_bathymetry`  |
    +-----------------------+----------------+----------------+--------------------------------------------+
    | measure_date          | 01/01/2016     | 01/01/2016     |                                            |
    +-----------------------+----------------+----------------+--------------------------------------------+
    | measure_time          | 00:00:00       | 01:00:00       |                                            |
    +-----------------------+----------------+----------------+--------------------------------------------+
    | u                     | 2.1            | 2              | (m/s)                                      |
    +-----------------------+----------------+----------------+--------------------------------------------+
    | v                     | 1.05           | 1.05           | (m/s)                                      |
    +-----------------------+----------------+----------------+--------------------------------------------+
    | turbulence_intensity  | 0.038586782    | 0.033037681    |                                            |
    +-----------------------+----------------+----------------+--------------------------------------------+
    | ssh                   | 0.35           | 0.35           | Sea surface elevation w.r.t. MSL (m)       |
    +-----------------------+----------------+----------------+--------------------------------------------+

Wave Energy
+++++++++++

For a site to be used for wave energy extraction, a time series at a single 
representative point (rather than the entire grid) is required; it 
is assumed that the wave conditions do not vary across the grid. Hourly 
values for the following quantities are required:

 * significant wave height (:math:`H_{s}`)
 * wave energy period (:math:`T_{e}`)
 * wave direction

The duration of all series must match and it is recommended that at least one 
year of data is provided, but a longer period will result in improved energy 
production predictions. The series are stored in the 
**project.time_series_energy_wave** table. See the :ref:`database_tables` 
section for further details. 

Logistics
+++++++++

Representative time series are also needed for logistics calculations. Hourly 
values for the following quantities are required for a single representative
point:

    * significant wave height
    * wave peak period (:math:`T_{p}`)
    * surface current magnitude
    * wind magnitude

The series must have matching durations and be at least one year in length, but 
longer periods are recommended. They are stored within the DTOcean database 
using the **project.time_series_om_wave**, **project.time_series_om_tidal** and 
**project.time_series_om_wind** tables. See the :ref:`database_tables` section 
for further details. 

Extremes
++++++++

The extreme conditions within the lease area must be known for balance of plant 
design. The following information should be provided (the recommended return 
period is shown in brackets): 

 * Long term sea surface current characteristics (10 year return period)
     
     * Maximum
     * Predominant direction
 
 * Long term wave characteristics (50 year return period)
     
     * Maximum :math:`H_{s}`
     * Maximum :math:`T_{p}`
     * Predominant direction
     * Representative gamma for a Jonswap spectrum
 
 * Long term wind characteristics (100 year return period)
     
     * Maximum speed
     * Predominant direction
     * Maximum gust speed
     * Predominant gust direction
 
 * Long term water level characteristics (50 year return period)
     
     * Maximum
     * Minimum

This data is stored in the **project.lease_area** table and further details
can be found in the :ref:`database_tables` section.

Device
======

Conventions and Dimensions
--------------------------

The following conventions are used when defining a device in DTOcean or its 
database: [#f1]_

 * Devices are categorised into one of four types: **Wave** or **Tidal** and
   **Fixed** or **Floating**
 * Devices can have either **Cylindrical** or **Rectangular** profile
 * Cylindrical devices are **always orientated vertically** (as in 
   :numref:`fig_floating_device`)
 * The *System Width* variable describes the diameter of a cylindrical device.
   The *System Length* variable is unused.
 * The local origin of a floating device **lies on the waterline** of the
   at-rest position of the device (see :numref:`fig_floating_device`)
 * The local origin of a fixed device **lies at the base of the device** (see 
   :numref:`fig_fixed_device`)
 * Height, width, length and draft are always given as **absolute values**
 * Other dimensions are **relative to the local origin**
 * For floating devices **each foundation defined must have a matching 
   fairlead** on the device
 * Floating devices must have an **umbilical cable connection point** defined
 * A **footprint** must be given for floating devices, to describe the area 
   swept by the device and its moorings. This can be given as a radius or a 
   polygon in the local coordinate system.
 * The vertical coordinate of foundation locations is unused
 * Minimum and maximum installation depths are directional, i.e. **the minimum
   depth is the deepest water** in which the device can be deployed
 * A **minimum distance between devices** in the x and y directions of the local
   coordinate system must be given
 * **Devices may yaw symmetrically** up to an angle of 180 degrees
 * **Tidal devices may have two rotors**, placed symmetrically perpendicular
   to the oncoming flow, in the horizontal plane

The name and type of a device is added to the **project.device** table (see the 
:ref:`database_tables` section). The **device_type** column has four (case
sensitive) values that can be used:

 * Tidal Fixed
 * Tidal Floating
 * Wave Fixed
 * Wave Floating

Examples of dimensions for floating and fixed devices (wave or tidal), having
cylindrical and rectangular profile, respectively, are shown in
:numref:`fig_floating_device`, :numref:`fig_floating_device_top` and 
:numref:`fig_fixed_device`. The related nomenclature is given in 
:numref:`tab_device_dimensions`.

.. _fig_floating_device:
.. figure:: /images/floating_device.png

   Floating, cylindrical device dimensions example (side view)

.. _fig_floating_device_top:
.. figure:: /images/floating_device_top.png

   Floating, cylindrical device dimensions example (top view)

.. _fig_fixed_device:
.. figure:: /images/fixed_device.png

   Fixed, rectangular device dimensions example

.. _tab_device_dimensions:
.. table:: Nomenclature for device dimensions examples

    +---------------+-----------------------------------------+-------+-----------------------------------------+
    | Symbol        | Variable Name                           | Units | Notes                                   |
    +===============+=========================================+=======+=========================================+
    | :math:`H`     | System Height                           | m     |                                         |
    +---------------+-----------------------------------------+-------+-----------------------------------------+
    | :math:`W`     | System Width                            | m     | Acts as diameter of cylindrical devices |
    +---------------+-----------------------------------------+-------+-----------------------------------------+
    | :math:`L`     | System Length                           | m     |                                         |
    +---------------+-----------------------------------------+-------+-----------------------------------------+
    | :math:`T`     | Floating Device Draft                   | m     | Always positive                         |
    +---------------+-----------------------------------------+-------+-----------------------------------------+
    | :math:`H_{R}` | Tidal Device Hub Height                 | m     | Tidal devices only                      |
    +---------------+-----------------------------------------+-------+-----------------------------------------+
    | :math:`G`     | System Centre of Gravity                | m     |                                         |
    +---------------+-----------------------------------------+-------+-----------------------------------------+
    | :math:`U`     | Umbilical Cable Device Connection Point | m     | Floating devices only                   |
    +---------------+-----------------------------------------+-------+-----------------------------------------+
    | :math:`F_{L}` | Fairlead Locations                      | m     | Floating devices only                   |
    +---------------+-----------------------------------------+-------+-----------------------------------------+
    | :math:`F_{A}` | Device Foundation Locations             | m     |                                         |
    +---------------+-----------------------------------------+-------+-----------------------------------------+
    | :math:`F_{R}` | Footprint Radius                        | m     | Floating devices only                   |
    +---------------+-----------------------------------------+-------+-----------------------------------------+

Technology agnostic dimensions are added to the **project.device_shared** table
of the DTOcean database. The **profile** column has only two (case sensitive) 
valid values which are:

 * Cylindrical
 * Rectangular

Floating device specific dimensions are added to the 
**project.device_floating** table. The **depth_variation_permitted** column of 
this table indicates if a vertical position of a floating device may vary. The 
valid values for this column are: 

 * yes
 * no

Note that this value is superseded if the **prescribed_mooring_system** column
is filled. The following (case sensitive) values can be used:

 * Catenary
 * Taut

Tidal device specific dimensions are stored in the **project.device_tidal** 
table. The rotor hub height and rotor diameter must be given in the 
**hub_height** and **turbine_diameter** columns, respectively. If the device 
has two rotors the **turbine_interdistance** column is used to describe the 
horizontal distance of the rotor hub from the device centre line (when 
orientated with the oncoming flow). 

Power Conversion and Transmission
---------------------------------

DTOcean requires the conversion performance of the simulated device to be 
known prior to simulation. For wave devices, the performance data must be
calculated using the **WEC Simulator** tool (see the ``:ref:`tools``` chapter).
This is necessary to allow calculation of the interactions between devices
within DTOcean. An output folder is produced by the tool, and the path to this
folder can be stored in the **project.device_wave** table of the DTOcean
database (see the :ref:`database_tables` section).

For tidal energy devices, traditional power and thrust curves are required. 
These are entered into the **project.device_tidal_power_performance** table of 
the DTOcean database and an example of this table is shown in 
:numref:`tab_tidal_curves`; a plot of this data is shown in 
:numref:`fig_tidal_curves`. Cut-in and cut-out velocities are entered into the 
**project.device_tidal** table. Negative velocities may not be used in the 
performance curves, but the given power curve can be used for negative 
velocities if the **two_ways_flow** column of the **project.device_tidal** 
table is set to **yes**. If this value is **no** then no power will be produced 
for reversed flow through the rotor(s). 

.. _tab_tidal_curves:
.. table:: Example device_tidal_power_performance table entries

    +----+----------+--------------------+-------------------+
    | id | velocity | thrust_coefficient | power_coefficient |
    +====+==========+====================+===================+
    | 1  | 0        | 0.91               | 0                 |
    +----+----------+--------------------+-------------------+
    | 2  | 0.5      | 0.87               | 0.04              |
    +----+----------+--------------------+-------------------+
    | 3  | 1        | 0.8                | 0.09              |
    +----+----------+--------------------+-------------------+
    | 4  | 1.5      | 0.68               | 0.14              |
    +----+----------+--------------------+-------------------+
    | 5  | 2        | 0.51               | 0.2               |
    +----+----------+--------------------+-------------------+
    | 6  | 2.5      | 0.4                | 0.25              |
    +----+----------+--------------------+-------------------+
    | 7  | 3        | 0.3                | 0.31              |
    +----+----------+--------------------+-------------------+
    | 8  | 3.5      | 0.25               | 0.38              |
    +----+----------+--------------------+-------------------+
    | 9  | 4        | 0.2                | 0.42              |
    +----+----------+--------------------+-------------------+
    | 10 | 4.5      | 0.15               | 0.44              |
    +----+----------+--------------------+-------------------+
    | 11 | 5        | 0.1                | 0.44              |
    +----+----------+--------------------+-------------------+
    | 12 | 5.5      | 0                  | 0                 |
    +----+----------+--------------------+-------------------+
    | 13 | 6        | 0                  | 0                 |
    +----+----------+--------------------+-------------------+

.. _fig_tidal_curves:
.. figure:: /images/tidal_curves.png

   Example tidal current device performance curves

Regardless of technology, the devices rated power and output voltage (U0) must 
be supplied. These values are added to the DTOcean database in the 
**project.device_shared** table. Note, any power generated above the device 
rating will be dumped. The type of connector used to couple the device to the 
electrical architecture must also be specified. The **connector_type** column 
has two valid (case sensitive) values: 

 * Wet-Mate
 * Dry-Mate

A constant or variable power factor should also be given in the 
**constant_power_factor** or **variable_power_factor** columns, respectively. 
The variable power factor is given as a list of tuples defined as {power in pu, 
power factor}. An example entry to the **variable_power_factor** column may 
be:: 

    {{1, 1}, {0.8, 0.9}, {0.5, 0.8}}

For floating devices the umbilical cable may be preselected using a value from
the **id** column of the **reference.component_cable**. Only cables with 
**fk_component_type_id** column value **2** are valid. The id can be added to
the **prescribed_umbilical_type** column of the **project.device_floating**
table. 

Sub-systems
-----------

For installation and life-time maintenance simulation, devices are divided into 
three or, optionally, four sub-systems. These sub-systems are: 

 * **Support Structure:** the main structural component of the device
 * **Prime Mover:** the device's source of motive power
 * **Power Take Off (PTO)**: the system responsible for conversion of motive
   power to electricity
 * **Control [optional]**: computational / mechanical equipment for device
   motion control

Examples of how these sub-systems may be allocated in a tidal current or 
wave energy device are shown in :numref:`fig_tidal_sub_systems` and
:numref:`fig_wave_sub_systems`.

.. _fig_tidal_sub_systems:
.. figure:: /images/tidal_sub_systems.png

   Example sub-systems in a tidal current device

.. _fig_wave_sub_systems:
.. figure:: /images/wave_sub_systems.png

   Example sub-systems in a wave device

Installation
------------

Installation of the device can be either as a single solid whole, or the 
support structure is installed first, followed by the remaining components. The 
choice is stored in the **two_stage_assembly** column of the 
**project.device_shared** table (see the :ref:`database_tables` section) and 
can have values: 

 * yes
 * no

How the device is transported to and from the deployment area is stored in the
**transportation_method** column. This can have one of two (case sensitive)
values:

  * Deck
  * Tow

If the device is to be towed then the **bollard_pull** column should also be
filled.

The **load_out_method** column indicates how the device is transported from 
shore onto the vessel or into the water. It has four (case sensitive) valid 
values: 

 * Skidded
 * Trailer
 * Float Away
 * Lift Away

Note that for the **Deck** transportation method, only the **Skidded** and
**Lift Away** load-out methods are valid.

The duration required to assemble, connect and disconnect the device is added
to the **assembly_duration**, **connect_duration** and **disconnect_duration** 
columns, respectively.

Installation information for the device sub-systems is stored in the 
**project.sub_systems_install** table, regardless of the choice in the 
**two_stage_assembly** column. This table dictates the allowable operational 
limit conditions (OLCs) when installing the device. An example entry to the 
table is shown in :numref:`tab_sub_systems_install`. Note that the 
**fk_sub_system_id** column should reference a value from the **id** column of 
the **project.sub_systems** table, which is shown in :numref:`tab_sub_systems`. 
Data for all device sub-systems to be simulated should be added. 



.. _tab_sub_systems_install:
.. table:: Example entries to 'sub_systems_install' table

    +------------------+---------------+-------------------------------------------+
    | Column           | Example Row   | Notes                                     |
    +==================+===============+===========================================+
    | id               | 1             |                                           |
    +------------------+---------------+-------------------------------------------+
    | fk_sub_system_id | 1             | References id in :numref:`tab_sub_systems`|
    +------------------+---------------+-------------------------------------------+
    | length           | 20            |                                           |
    +------------------+---------------+-------------------------------------------+
    | width            | 20            |                                           |
    +------------------+---------------+-------------------------------------------+
    | height           | 4             |                                           |
    +------------------+---------------+-------------------------------------------+
    | dry_mass         | 200000        |                                           |
    +------------------+---------------+-------------------------------------------+
    | max_hs           | 2             |                                           |
    +------------------+---------------+-------------------------------------------+
    | max_tp           | 99            |                                           |
    +------------------+---------------+-------------------------------------------+
    | max_ws           | 15            | Wind speed magnitude                      |
    +------------------+---------------+-------------------------------------------+
    | max_cs           | 1.5           | Surface current speed magnitude           |
    +------------------+---------------+-------------------------------------------+

.. _tab_sub_systems:
.. table:: Contents of 'sub_systems' table
    
    +----+-------------------+
    | id | sub_system        |
    +====+===================+
    | 1  | Prime Mover       |
    +----+-------------------+
    | 2  | PTO               |
    +----+-------------------+
    | 3  | Support Structure |
    +----+-------------------+
    | 4  | Control           |
    +----+-------------------+

Maintenance
-----------

Each sub-system defined within DTOcean can have three types of maintenance 
operation. These are "Inspection", "Maintenance" or "Replacement". The 
appropriate types for each device sub-system, and how likely they are with 
respect to each other must be chosen. This is partly controlled by the values 
given in the **project.sub_systems_operation_weightings** table. A set of 
example entries to this table is shown in 
:numref:`tab_sub_systems_operation_weightings`. An operation type can be 
excluded by using a value of zero for the required sub-system. Weightings can 
take any positive value; per sub-system, the likelihood of each operation will 
be calculated from the relative weights. 

.. _tab_sub_systems_operation_weightings:
.. table:: Contents of 'sub_systems_operation_weightings' table
    
    +----+------------------+-------------+-------------+------------+
    | id | fk_sub_system_id | maintenance | replacement | inspection |
    +====+==================+=============+=============+============+
    | 1  | 1                | 1           | 1           | 2          |
    +----+------------------+-------------+-------------+------------+
    | 2  | 2                | 1           | 0           | 2          |
    +----+------------------+-------------+-------------+------------+
    | 3  | 3                | 0           | 1           | 10         |
    +----+------------------+-------------+-------------+------------+

The **project.sub_systems_operation_weightings** table determines which types of
action are required when a sub-system failure is triggered, but the rate of
failure is determined by the value of the **failure_rate** column in the 
**project.sub_systems_economic** table. An example set of entries to this
table is shown in :numref:`tab_sub_systems_economic`. Failures rates are
supplied as the number of failures per :math:`1 \times 10^{6}` hours.

.. _tab_sub_systems_economic:
.. table:: Contents of 'sub_systems_economic' table
    
    +----+------------------+---------+--------------+
    | id | fk_sub_system_id | cost    | failure_rate |
    +====+==================+=========+==============+
    | 1  | 1                | 485000  | 4            |
    +----+------------------+---------+--------------+
    | 2  | 2                | 400000  | 20           |
    +----+------------------+---------+--------------+
    | 3  | 3                | 1200000 | 2            |
    +----+------------------+---------+--------------+

Detailed information for each required operation type for each device 
sub-system are entered into the **project.sub_systems_inspection**, 
**project.sub_systems_maintenance** and **project.sub_systems_replace** tables. 
An example row for the **project.sub_systems_maintenance** table is shown in 
:numref:`tab_sub_systems_maintenance`. The columns of the other two tables are 
a subset of the columns of this table. As the device must be accessed for all 
maintenance actions, the columns in **project.sub_systems_access** table must 
also be filled for any sub-systems that undergo any operation type. 

.. _tab_sub_systems_maintenance:
.. table:: Example entries to 'sub_systems_maintenance' table

    +--------------------+-------------+-----------------------------------------------------+
    | Column             | Example Row | Notes                                               |
    +--------------------+-------------+-----------------------------------------------------+
    | id                 | 1           |                                                     |
    +--------------------+-------------+-----------------------------------------------------+
    | fk_sub_system_id   | 1           | References id in :numref:`tab_sub_systems`          |
    +--------------------+-------------+-----------------------------------------------------+
    | operation_duration | 8           |                                                     |
    +--------------------+-------------+-----------------------------------------------------+
    | interruptible      | yes         | Can the operation be broken into parts? (yes or no) |
    +--------------------+-------------+-----------------------------------------------------+
    | parts_length       | 1           | Parts required for maintenance                      |
    +--------------------+-------------+-----------------------------------------------------+
    | parts_width        | 1           | |ditto|                                             |
    +--------------------+-------------+-----------------------------------------------------+
    | parts_height       | 1           | |ditto|                                             |
    +--------------------+-------------+-----------------------------------------------------+
    | parts_dry_mass     | 25          | |ditto|                                             |
    +--------------------+-------------+-----------------------------------------------------+
    | assembly_lead_time | 0           | Delays to commencement of operation in hours        |
    +--------------------+-------------+-----------------------------------------------------+
    | crew_lead_time     | 24          | |ditto|                                             |
    +--------------------+-------------+-----------------------------------------------------+
    | other_lead_time    | 0           | |ditto|                                             |
    +--------------------+-------------+-----------------------------------------------------+
    | n_specialists      | 1           | Two different wage levels are available             |
    +--------------------+-------------+-----------------------------------------------------+
    | n_technicians      | 4           | |ditto|                                             |
    +--------------------+-------------+-----------------------------------------------------+
    | max_hs             | 2           | OLCs specific to this operation on this subsystem   |
    +--------------------+-------------+-----------------------------------------------------+
    | max_tp             | 99          | |ditto|                                             |
    +--------------------+-------------+-----------------------------------------------------+
    | max_ws             | 15          | |ditto|                                             |
    +--------------------+-------------+-----------------------------------------------------+
    | max_cs             | 1.5         | |ditto|                                             |
    +--------------------+-------------+-----------------------------------------------------+

.. |ditto| unicode:: U+3003

Economics
---------

Storage of the cost of the whole device and each of its sub-systems within the 
DTOcean database is as follows:

 * The whole device cost is stored in the **cost** column of the
   **project.device_shared** table
 * The sub-systems costs are stored in the **cost** column of the 
   **project.sub_systems_economic** table

.. include:: database_tables.rst

.. rubric:: Footnotes

.. [#f1] Individual DTOcean modules may follow different conventions in their
         specific APIs.