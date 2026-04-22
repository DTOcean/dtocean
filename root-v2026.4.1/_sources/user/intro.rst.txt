.. raw:: latex

    \part{User Guide}

.. _introduction:

************
Introduction
************

An Overview of DTOcean
======================

DTOcean automates the design of an array of ocean energy converters (OECs) for
a relevant geographical location and technology type. The design process is
modularised into the following stages:

* Hydrodynamics:
        Design the layout of converters in a chosen region and calculate their
        power output.
* Electrical Sub-Systems:
        Design an electrical layout for the given converter locations and
        calculate the losses from exporting the energy to shore.
* Moorings and Foundations:
        Design the foundations and moorings required to secure the converters 
        at their given locations.
* Installation:
        Design the installation plan for the converters, electrical
        sub-systems, moorings and foundations designs.
* Operations and Maintenance:
        Calculate the required maintenance actions and power losses resulting
        from the operation of the converters over the lifetime of the array.

The software can also evaluate each stage of the design, and the design as a 
whole, using three thematic assessments. These are:

* Economics:
        Produce economic indicators for the design, in particular the Levelised
        Cost of Energy (LCOE).
* Reliability:
        Assess the reliability of sub-systems resulting from the components
        chosen in the design stages.
* Environmental:
        Assess the environmental impact of each stage of the design.


.. _key_terminology:

Key Terminology
===============

This section summarises the key terminology used when describing DTOcean.

 * Project:
        A project is the overarching container for a design session
        using the DTOcean software. Projects contain one or many Simulations and
        can be saved and reloaded.
 * Simulation: 
        A simulation refers to a set of modules, assessments and variable
        values. Multiple simulations can be stored in a single project, using
        different variable values, and compared.
 * Module:
        Design modules are the main functional engines of the DTOcean software, 
        manipulating existing and creating new data for a particular purpose 
        (such as solving the layout and power output of the array of OECs). 
 * Assessment:
        Assessments are used to provide key metrics to compare the results of 
        simulations, such as the LCOE.
 * Variable:
        Variables refers to the data that is required as inputs to the modules
        and assessments, and the results obtained from them.
 * Strategy:
        Strategies are used to automate the execution of modules. Strategies
        have various complexity from simply running the modules in order, to 
        searching for optimum input variable values. 
 * Pipeline:
        The pipeline provides a structure for visualising and preparing 
        the variables required for a simulation, visualising the order of
        execution of modules and examining results.
 * Level:
        A "level" refers to the state of the data after execution of a
        particular module. The software can recall any level in any
        simulation and compare between them.
 * Database:
        The database is a persistent store of data that can be used
        to support the needs of the design process. It stores OEC designs,
        site characteristics and long-standing reference data for components,
        vessels, equipment, etc.
 * Tool:
        Tools are functions additional to the design process that can be used
        to inspect, manipulate, or create new data.


DTOcean License
===============

    Copyright |copy| 2016-|year| The DTOcean Developers

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


.. |copy|   unicode:: U+000A9 .. COPYRIGHT SIGN
.. |year| date:: %Y
