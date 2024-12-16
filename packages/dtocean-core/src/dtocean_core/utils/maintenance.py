# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2024 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Created on Wed Nov 30 12:02:41 2016

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import re
import logging
import calendar
import datetime as dt
from collections import Counter

import pandas as pd
from scipy.interpolate import RegularGridInterpolator

from .reliability import get_component_dict

# Set up logging
module_logger = logging.getLogger(__name__)


def get_input_tables(system_type,
                     array_layout,
                     bathymetry,
                     maintenance_start,
                     annual_maintenance_start,
                     annual_maintenance_end,
                     elec_network,
                     mandf_network,
                     mandf_bom,
                     electrical_components,
                     elec_database,
                     mandf_database,
                     operations_onsite_maintenance,
                     operations_replacements,
                     operations_inspections,
                     transportation_method,
                     subsystem_access,
                     subsystem_costs,
                     subsystem_failure_rates,
                     subsystem_inspections,
                     subsystem_maintenance,
                     subsystem_maintenance_parts,
                     subsystem_operation_weightings,
                     subsystem_replacement,
                     subsystem_replacement_parts,
                     control_subsystem_access,
                     control_subsystem_costs,
                     control_subsystem_failure_rates,
                     control_subsystem_inspections,
                     control_subsystem_maintenance,
                     control_subsystem_maintenance_parts,
                     control_subsystem_operation_weightings,
                     control_subsystem_replacement,
                     control_subsystem_replacement_parts,
                     umbilical_operations_weighting,
                     array_cables_operations_weighting,
                     substations_operations_weighting,
                     export_cable_operations_weighting,
                     foundations_operations_weighting,
                     moorings_operations_weighting,
                     calendar_maintenance_interval,
                     condition_maintenance_soh,
                     electrical_onsite_requirements,
                     moorings_onsite_requirements,
                     electrical_replacement_requirements,
                     moorings_replacement_requirements,
                     electrical_inspections_requirements,
                     moorings_inspections_requirements,
                     electrical_onsite_parts,
                     moorings_onsite_parts,
                     electrical_replacement_parts,
                     moorings_replacement_parts,
                     subsystem_monitering_costs,
                     spare_cost_multiplier=None,
                     transit_cost_multiplier=None,
                     loading_cost_multiplier=None
                     ):
    
    """Dynamically generate the Component, Failure_Mode, Repair_Action & 
    Inspection tables for the operations and maintenance module
    
    """
    
    # Set defaults
    if spare_cost_multiplier is None: spare_cost_multiplier = 1.
    if transit_cost_multiplier is None: transit_cost_multiplier = 0.
    if loading_cost_multiplier is None: loading_cost_multiplier = 0.
    
    # Define required subsystems

    # Device
    device_subsystems = ['Prime Mover',
                         'PTO',
                         'Support Structure']
        
    if control_subsystem_replacement_parts is not None:
        device_subsystems.append('Control')
        subsystem_access = subsystem_access.append(control_subsystem_access)
        subsystem_costs = subsystem_costs.append(control_subsystem_costs)
        subsystem_failure_rates = subsystem_failure_rates.append(
                                        control_subsystem_failure_rates)
        subsystem_inspections = subsystem_inspections.apppend(
                                        control_subsystem_inspections)
        subsystem_maintenance = subsystem_maintenance.append(
                                        control_subsystem_maintenance)
        subsystem_maintenance_parts = subsystem_maintenance_parts.append(
                                        control_subsystem_maintenance_parts)
        subsystem_operation_weightings = subsystem_operation_weightings.append(
                                        control_subsystem_operation_weightings)
        subsystem_replacement = subsystem_replacement.append(
                                        control_subsystem_replacement)
        subsystem_replacement_parts = subsystem_replacement_parts.append(
                                        control_subsystem_replacement_parts)
                         
    all_subsystems = device_subsystems[:]
    
    # Electrical
    subhubs = None
    elec_subsystems = []
    
    if elec_network is not None:
    
        elec_subsystems = ['Inter-Array Cables',
                           'Substations',
                           'Export Cable']
    
        if "floating" in system_type.lower():
            elec_subsystems.append('Umbilical Cable')
            
        all_subsystems.extend(elec_subsystems)
        
        # Check for subhubs
        n_subhubs = len(elec_network['nodes']) - len(array_layout) - 1

        if n_subhubs > 0:
            subhubs = ["subhub{:0>3}".format(x + 1) for x in xrange(n_subhubs)]

        electrical_subsystem_costs = get_electrical_system_cost(
                                                     electrical_components,
                                                     elec_subsystems,
                                                     elec_database)
        
    # Moorings and Foundations
    mandf_subsystems = []
    
    if mandf_network is not None:
    
        mandf_subsystems = ['Foundations']
                           
        if "floating" in system_type.lower():
            mandf_subsystems.append('Mooring Lines')
            
        mandf_subsystem_costs = get_mandf_system_cost(mandf_bom,
                                                      mandf_subsystems,
                                                      mandf_database)
            
        all_subsystems.extend(mandf_subsystems)
    
    standalone_subsystems = ['Prime Mover',
                             'PTO',
                             'Control',
                             'Support Structure',
                             'Substations',
                             'Export Cable']
                       
    subsystems_map = {'Prime Mover': 'Hydrodynamic',
                      'PTO': 'Pto',
                      'Control': 'Control',
                      'Support Structure': 'Support structure',
                      'Umbilical Cable': 'Umbilical',
                      'Inter-Array Cables': 'Elec sub-system',
                      'Substations': 'Substation',
                      'Export Cable': 'Export cable',
                      'Foundations': 'Foundation',
                      'Mooring Lines': 'Moorings lines'}
                      
    weightings_map = {
                'Prime Mover': 
                    subsystem_operation_weightings.loc['Prime Mover'],
                'PTO': subsystem_operation_weightings.loc['PTO'],
                'Support Structure':
                    subsystem_operation_weightings.loc['Support Structure'],
                'Umbilical Cable': umbilical_operations_weighting,
                'Inter-Array Cables': array_cables_operations_weighting,
                'Substations': substations_operations_weighting,
                'Export Cable': export_cable_operations_weighting,
                'Foundations': foundations_operations_weighting,
                'Mooring Lines': moorings_operations_weighting}
        
    if control_subsystem_replacement_parts is not None:
        weightings_map['Control'] = \
                      subsystem_operation_weightings.loc['Control']
                      
    repair_map = {
            'Maintenance Duration': 'duration_maintenance',
            'Access Duration': 'duration_accessibility',
            'Interruptible': 'interruptable',
            'Crew Preparation Delay': 'delay_crew',
            'Other Delay': 'delay_organisation',
            'Spare Parts Preparation Delay': 'delay_spare',
            'Technicians Required': 'number_technicians',
            'Specialists Required': 'number_specialists',
            'Max Wave Height for Access': 'wave_height_max_acc',
            'Max Wave Period for Access': 'wave_periode_max_acc',
            'Max Wind Speed for Access': 'wind_speed_max_acc',
            'Max Current Speed for Access': 'current_speed_max_acc',
            'Max Wave Height for Maintenance': 'wave_height_max_om',
            'Max Wave Period for Maintenance': 'wave_periode_max_om',
            'Max Wind Speed for Maintenance': 'wind_speed_max_om',
            'Max Current Speed for Maintenance': 'current_speed_max_om'}
            
    inspections_map = {
            'Inspection Duration': 'duration_inspection',
            'Access Duration': 'duration_accessibility',
            'Crew Preparation Delay': 'delay_crew',
            'Other Delay': 'delay_organisation',
            'Technicians Required': 'number_technicians',
            'Specialists Required': 'number_specialists',
            'Max Wave Height for Access': 'wave_height_max_acc',
            'Max Wave Period for Access': 'wave_periode_max_acc',
            'Max Wind Speed for Access': 'wind_speed_max_acc',
            'Max Current Speed for Access': 'current_speed_max_acc',
            'Max Wave Height for Inspections': 'wave_height_max_om',
            'Max Wave Period for Inspections': 'wave_periode_max_om',
            'Max Wind Speed for Inspections': 'wind_speed_max_om',
            'Max Current Speed for Inspections': 'current_speed_max_om'}
                      
    modes_map = {'Spare Parts Mass': 'spare_mass',
                 'Spare Parts Max Height': 'spare_height',
                 'Spare Parts Max Width': 'spare_width',
                 'Spare Parts Max Length': 'spare_length'}
                             
    # Start end dates
    months = list(calendar.month_name)
    
    start_month_int = None
    this_year = maintenance_start.year
    next_year = this_year + 1
    
    if annual_maintenance_start is not None:
        
        start_month_int = months.index(annual_maintenance_start)
        start_date = dt.datetime(this_year,
                                 start_month_int,
                                 1)
        
        if start_date < maintenance_start:
            start_date = start_date.replace(year=next_year)
            
    else:
        
        start_date = dt.datetime(next_year, 1, 1)
        
    if annual_maintenance_end is not None:
        
        end_month_int = months.index(annual_maintenance_end)
        
        if (start_month_int is not None and
            end_month_int < start_month_int):
                
            errStr = ("Annual maintenance end month may not be earlier than "
                      "start month")
            raise ValueError(errStr)
            
        last_day = calendar.monthrange(this_year,
                                       end_month_int)[1]

        end_date = dt.datetime(this_year,
                               end_month_int,
                               last_day,
                               23,
                               59,
                               59)
        
        if (end_date < maintenance_start or
            end_date < start_date):

            last_day = calendar.monthrange(next_year,
                                           end_month_int)[1]

            end_date = dt.datetime(next_year,
                                   end_month_int,
                                   last_day,
                                   23,
                                   59,
                                   59)
            
    else:
        
        end_date = dt.datetime(next_year,
                               12,
                               31,
                               23,
                               59,
                               59)
        
    logMsg = "Annual operations start on date {}".format(start_date)
    module_logger.info(logMsg)
    
    logMsg = "Annual operations end on date {}".format(end_date)
    module_logger.info(logMsg)
    
    # Final tables
    all_comp = pd.DataFrame()
    all_modes = pd.DataFrame()
    all_repair = pd.DataFrame()
    all_inspection = pd.DataFrame()
    
    # Error string helper
    shortErr = "{0} {1} data has not been provided for sub-system {2}"
    
    longErr = ("{0} {1} operations {2} data has not been provided, yet "
               "{1} operations are selected for sub-system {3}")
        
    for subsystem in all_subsystems:
        
        # Initiate temporary table data
        temp_comp = pd.Series()
        temp_modes = pd.Series()
        
        subsystem_root = subsystems_map[subsystem]

        # Collect the operations weightings in advance so that the failure
        # modes table can be completed per operation type
        operations_weightings = {"onsite": None,
                                 "replacement": None,
                                 "inspections": None}
        
        if (operations_onsite_maintenance is not None and
            operations_onsite_maintenance[subsystem]):
            
            weighting = weightings_map[subsystem]["On-Site Maintenance"]
            operations_weightings["onsite"] = weighting
            
        if (operations_replacements is not None and
            subsystem in operations_replacements and
            operations_replacements[subsystem]):
            
            weighting = weightings_map[subsystem]["Replacement"]
            operations_weightings["replacement"] = weighting

        if (operations_inspections is not None and
            operations_inspections[subsystem]):
            
            weighting = weightings_map[subsystem]["Inspections"]
            operations_weightings["inspections"] = weighting

        weighting_set = set(operations_weightings.values())

        # No work to do for this subsystem
        if len(weighting_set) == 1 and None in weighting_set: continue
    
        # Build temporary component table series
        temp_comp["Component_subtype"] = subsystem_root
        temp_comp["start_date_calendar_based_maintenance"] = start_date
        temp_comp["end_date_calendar_based_maintenance"] = end_date
        temp_comp["start_date_condition_based_maintenance"] = start_date
        temp_comp["end_date_condition_based_maintenance"] = end_date

        # Number of operation types active
        active_ops = [k for k, v in operations_weightings.items()
                                                             if v is not None]
        total_weight = sum([v for k, v in operations_weightings.items()
                                                             if v is not None])
                                                             
        temp_comp["number_failure_modes"] = len(active_ops)

        # Failure rates (convert to annual)
        if subsystem in device_subsystems:
            
            temp_comp["failure_rate"] = subsystem_failure_rates[subsystem] * \
                                                            24 * 365 / 1e6
    
        # Calendar maintenance interval
        temp_comp["interval_calendar_based_maintenance"] = \
                                    calendar_maintenance_interval[subsystem]

        # State of health
        temp_comp["soh_threshold"] = condition_maintenance_soh[subsystem]

        # Add subsytem to the Component table
        all_comp = update_comp_table(subsystem,
                                     subsystem_root,
                                     array_layout,
                                     temp_comp,
                                     all_comp,
                                     subhubs)

        # Base Costs
        if subsystem in device_subsystems:
            
            base_cost = subsystem_costs[subsystem]

        elif subsystem in elec_subsystems:
            
            base_cost = electrical_subsystem_costs[subsystem]

        elif subsystem in mandf_subsystems:
            
            base_cost = mandf_subsystem_costs[subsystem]

        # Conditioning monitering costs
        if subsystem_monitering_costs is None:
            monitering_cost = 0.
        else:
            monitering_cost = subsystem_monitering_costs[subsystem]

        # Costs can be divided per device
        if subsystem not in standalone_subsystems:
            
            n_devices = len(array_layout)
            base_cost /= n_devices

        # Add on-site operations
        if "onsite" in active_ops:
            
            # Initiate temporary table data
            onsite_modes = temp_modes.copy()
            
            # Build Repair Actions and Failure Mode series
            if subsystem in device_subsystems:
                
                access_map = {
                  'Operation Duration': 'duration_accessibility',
                  'Max Hs': 'wave_height_max_acc',
                  'Max Tp': 'wave_periode_max_acc',
                  'Max Wind Velocity': 'wind_speed_max_acc',
                  'Max Current Velocity': 'current_speed_max_acc'}
                
                device_repair_map = {
                  'Operation Duration': 'duration_maintenance',
                  'Interruptible': 'interruptable',
                  'Crew Preparation Delay': 'delay_crew',
                  'Other Delay': 'delay_organisation',
                  'Spare Parts Preparation Delay': 'delay_spare',
                  'Technicians Required': 'number_technicians',
                  'Specialists Required': 'number_specialists',
                  'Max Hs': 'wave_height_max_om',
                  'Max Tp': 'wave_periode_max_om',
                  'Max Wind Velocity': 'wind_speed_max_om',
                  'Max Current Velocity': 'current_speed_max_om'}
                
                temp_access = subsystem_access.loc[subsystem]
                temp_access = temp_access.rename(access_map)
                                
                onsite_modes = onsite_modes.append(
                                    subsystem_maintenance_parts.loc[subsystem])
                
                temp_repair = subsystem_maintenance.loc[subsystem]
                temp_repair = temp_repair.rename(device_repair_map)
                temp_repair = temp_repair.append(temp_access)

            elif subsystem in elec_subsystems:
                
                if electrical_onsite_requirements is None:
                    
                    errStr = longErr.format("Electrical Sub-Systems",
                                            "on-site",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)
                    
                if electrical_onsite_parts is None:
                    
                    errStr = longErr.format("Electrical Sub-Systems",
                                            "on-site",
                                            "parts",
                                            subsystem)
                    raise RuntimeError(errStr)
                
                temp_repair = electrical_onsite_requirements.loc[subsystem]
                onsite_modes = onsite_modes.append(
                                       electrical_onsite_parts.loc[subsystem])
                
                temp_repair = temp_repair.rename(repair_map)

            elif subsystem in mandf_subsystems:
                
                if moorings_onsite_requirements is None:
                    
                    errStr = longErr.format("Moorings and Foundations",
                                            "on-site",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)
                    
                if moorings_onsite_parts is None:
                    
                    errStr = longErr.format("Moorings and Foundations",
                                            "on-site",
                                            "parts",
                                            subsystem)
                    raise RuntimeError(errStr)
                
                temp_repair = moorings_onsite_requirements.loc[subsystem]
                onsite_modes = onsite_modes.append(
                                       moorings_onsite_parts.loc[subsystem])
                
                temp_repair = temp_repair.rename(repair_map)

            onsite_modes = onsite_modes.rename(modes_map)
            
            # Costs
            onsite_modes["cost_spare"] = base_cost * spare_cost_multiplier
            
            if transit_cost_multiplier is not None:
                onsite_modes["cost_spare_transit"] = \
                                        base_cost * transit_cost_multiplier
                                        
            if loading_cost_multiplier is not None:
                onsite_modes["cost_spare_loading"] = \
                                        base_cost * loading_cost_multiplier
                                        
            onsite_modes["CAPEX_condition_based_maintenance"] = monitering_cost
                                        
            # Probability
            onsite_modes["mode_probability"] = \
                        operations_weightings["onsite"] / total_weight * 100.

            # Add operation to Failure Mode and Repair Actions Tables
            (all_modes,
             all_repair) = update_onsite_tables(subsystem,
                                                subsystem_root,
                                                system_type,
                                                array_layout,
                                                bathymetry,
                                                onsite_modes,
                                                temp_repair,
                                                all_modes,
                                                all_repair,
                                                subhubs)
        
        # Add replacement operations
        if "replacement" in active_ops:
            
            replacement_modes = temp_modes.copy()
            
            # Build Repair Actions and Failure Mode series
            if subsystem in device_subsystems:
                
                access_map = {
                  'Operation Duration': 'duration_accessibility',
                  'Max Hs': 'wave_height_max_acc',
                  'Max Tp': 'wave_periode_max_acc',
                  'Max Wind Velocity': 'wind_speed_max_acc',
                  'Max Current Velocity': 'current_speed_max_acc'}
                
                device_repair_map = {
                  'Operation Duration': 'duration_maintenance',
                  'Interruptible': 'interruptable',
                  'Crew Preparation Delay': 'delay_crew',
                  'Other Delay': 'delay_organisation',
                  'Spare Parts Preparation Delay': 'delay_spare',
                  'Technicians Required': 'number_technicians',
                  'Specialists Required': 'number_specialists',
                  'Max Hs': 'wave_height_max_om',
                  'Max Tp': 'wave_periode_max_om',
                  'Max Wind Velocity': 'wind_speed_max_om',
                  'Max Current Velocity': 'current_speed_max_om'}
                
                temp_access = subsystem_access.loc[subsystem]
                temp_access = temp_access.rename(access_map)
                
                temp_repair = subsystem_replacement.loc[subsystem]
                temp_repair = temp_repair.rename(device_repair_map)
                temp_repair = temp_repair.append(temp_access)
                                
                replacement_modes = replacement_modes.append(
                                subsystem_replacement_parts.loc[subsystem])

            elif subsystem in elec_subsystems:
                
                if electrical_replacement_requirements is None:
                    
                    errStr = longErr.format("Electrical Sub-Systems",
                                            "replacement",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)
                    
                if electrical_replacement_parts is None:
                    
                    errStr = longErr.format("Electrical Sub-Systems",
                                            "on-site",
                                            "parts",
                                            subsystem)
                    raise RuntimeError(errStr)
                
                temp_repair = \
                            electrical_replacement_requirements.loc[subsystem]
                replacement_modes = replacement_modes.append(
                                   electrical_replacement_parts.loc[subsystem])
                
                temp_repair = temp_repair.rename(repair_map)

            elif subsystem in mandf_subsystems:
                
                if moorings_replacement_requirements is None:
                    
                    errStr = longErr.format("Moorings and Foundations",
                                            "replacement",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)
                    
                if moorings_replacement_parts is None:
                    
                    errStr = longErr.format("Moorings and Foundations",
                                            "on-site",
                                            "parts",
                                            subsystem)
                    raise RuntimeError(errStr)
                
                temp_repair = moorings_replacement_requirements.loc[subsystem]
                replacement_modes = replacement_modes.append(
                                   moorings_replacement_parts.loc[subsystem])
                
                temp_repair = temp_repair.rename(repair_map)

            replacement_modes = replacement_modes.rename(modes_map)
            
            # Costs
            replacement_modes["cost_spare"] = base_cost
            
            if transit_cost_multiplier is not None:
                replacement_modes["cost_spare_transit"] = \
                                        base_cost * transit_cost_multiplier
                                        
            if loading_cost_multiplier is not None:
                replacement_modes["cost_spare_loading"] = \
                                        base_cost * loading_cost_multiplier
                                        
            replacement_modes["CAPEX_condition_based_maintenance"] = \
                                                             monitering_cost
                                        
            # Probability
            replacement_modes["mode_probability"] = \
                    operations_weightings["replacement"] / total_weight * 100.

            # Add operation to Failure Mode and Repair Actions Tables
            (all_modes,
             all_repair) = update_replacement_tables(subsystem,
                                                     subsystem_root,
                                                     system_type,
                                                     transportation_method,
                                                     array_layout,
                                                     replacement_modes,
                                                     temp_repair,
                                                     all_modes,
                                                     all_repair)
        
        if "inspections" in active_ops:
            
            # Initiate temporary table data
            inspections_modes = temp_modes.copy()
            
            # Add some fake parts data
            inspections_modes['spare_mass'] = 0.1
            inspections_modes['spare_height'] = 0.1
            inspections_modes['spare_width'] = 0.1
            inspections_modes['spare_length'] = 0.1
            
            if subsystem in device_subsystems:
                
                access_map = {
                  'Operation Duration': 'duration_accessibility',
                  'Max Hs': 'wave_height_max_acc',
                  'Max Tp': 'wave_periode_max_acc',
                  'Max Wind Velocity': 'wind_speed_max_acc',
                  'Max Current Velocity': 'current_speed_max_acc'}
                
                temp_access = subsystem_access.loc[subsystem]
                temp_access = temp_access.rename(access_map)

                device_inspections_map = {
                  'Operation Duration': 'duration_inspection',
                  'Crew Preparation Delay': 'delay_crew',
                  'Other Delay': 'delay_organisation',
                  'Technicians Required': 'number_technicians',
                  'Specialists Required': 'number_specialists',
                  'Max Hs': 'wave_height_max_om',
                  'Max Tp': 'wave_periode_max_om',
                  'Max Wind Velocity': 'wind_speed_max_om',
                  'Max Current Velocity': 'current_speed_max_om'}
                
                temp_inspection = \
                            subsystem_inspections.loc[subsystem]
                            
                temp_inspection = temp_inspection.rename(
                                                        device_inspections_map)
                
                temp_inspection = temp_inspection.append(temp_access)

            elif subsystem in elec_subsystems:
                
                if electrical_inspections_requirements is None:
                    
                    errStr = longErr.format("Electrical Sub-Systems",
                                            "inspections",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)
                
                temp_inspection = \
                            electrical_inspections_requirements.loc[subsystem]
                            
                temp_inspection = temp_inspection.rename(inspections_map)

            elif subsystem in mandf_subsystems:
                
                if moorings_inspections_requirements is None:
                    
                    errStr = longErr.format("Moorings and Foundations",
                                            "inspections",
                                            "requirements",
                                            subsystem)
                    raise RuntimeError(errStr)

                temp_inspection = \
                            moorings_inspections_requirements.loc[subsystem]
                
                temp_inspection = temp_inspection.rename(inspections_map)

            # Costs
            inspections_modes["cost_spare"] = 0.
            inspections_modes["cost_spare_transit"] = 0.
            inspections_modes["cost_spare_loading"] = 0.
                                        
            inspections_modes["CAPEX_condition_based_maintenance"] = \
                                                            monitering_cost
                                        
            # Probability
            inspections_modes["mode_probability"] = \
                    operations_weightings["inspections"] / total_weight * 100.

            # Add operation to Failure Mode and Inspection Tables
            (all_modes,
             all_inspection) = update_inspections_tables(subsystem,
                                                         subsystem_root,
                                                         system_type,
                                                         array_layout,
                                                         bathymetry,
                                                         inspections_modes,
                                                         temp_inspection,
                                                         all_modes,
                                                         all_inspection,
                                                         subhubs)
            
    # Give empty data frames an index
    if all_comp.empty:
        
        index = [u'Component_ID',
                 u'Component_subtype',
                 u'Component_type',
                 u'end_date_calendar_based_maintenance',
                 u'end_date_condition_based_maintenance',
                 u'failure_rate',
                 u'interval_calendar_based_maintenance',
                 u'number_failure_modes',
                 u'soh_threshold',
                 u'start_date_calendar_based_maintenance',
                 u'start_date_condition_based_maintenance']
        
        all_comp = pd.DataFrame(index=index)
    
    if all_modes.empty:
                
        index = [u'CAPEX_condition_based_maintenance',
                 u'Component_ID',
                 u'FM_ID',
                 u'cost_spare',
                 u'cost_spare_loading',
                 u'cost_spare_transit',
                 u'mode_probability',
                 u'spare_height',
                 u'spare_length',
                 u'spare_mass',
                 u'spare_width']
        
        all_modes = pd.DataFrame(index=index)
        
    if all_repair.empty:
    
        index = [u'Component_ID',
                 u'FM_ID',
                 u'current_speed_max_acc',
                 u'current_speed_max_om',
                 u'delay_crew',
                 u'delay_organisation',
                 u'delay_spare',
                 u'duration_accessibility',
                 u'duration_maintenance',
                 u'interruptable',
                 u'number_specialists',
                 u'number_technicians',
                 u'wave_height_max_acc',
                 u'wave_height_max_om',
                 u'wave_periode_max_acc',
                 u'wave_periode_max_om',
                 u'wind_speed_max_acc',
                 u'wind_speed_max_om']
        
        all_repair = pd.DataFrame(index=index)
            
    if all_inspection.empty:
        
        index = [u'Component_ID',
                 u'FM_ID',
                 u'current_speed_max_acc',
                 u'current_speed_max_om',
                 u'delay_crew',
                 u'delay_organisation',
                 u'duration_accessibility',
                 u'duration_inspection',
                 u'number_specialists',
                 u'number_technicians',
                 u'wave_height_max_acc',
                 u'wave_height_max_om',
                 u'wave_periode_max_acc',
                 u'wave_periode_max_om',
                 u'wind_speed_max_acc',
                 u'wind_speed_max_om']
        
        all_inspection = pd.DataFrame(index=index)
    
    assert all_comp.shape[0] == 11
    assert all_modes.shape[0] == 11
    
    assert all_repair.shape[0] == 18
    assert all_inspection.shape[0] == 16
    
    assert all_modes.shape[1] == all_repair.shape[1] + \
                                                all_inspection.shape[1]
                
    return all_comp, all_modes, all_repair, all_inspection


def update_comp_table(subsystem,
                      subsystem_root,
                      array_layout,
                      temp_comp,
                      all_comp,
                      subhubs):
    
    array_subsystems = ['Substations',
                        'Export Cable']

    # Build final tables
    if subsystem in array_subsystems:
        
        subsystem_id = "{}001".format(subsystem_root)
        temp_comp["Component_ID"] = subsystem_id
        temp_comp["Component_type"] = "array"

        num_cols = all_comp.shape[1]
        temp_comp = temp_comp.rename(num_cols)
        all_comp = pd.concat([all_comp, temp_comp],
                             axis=1,
                             sort=False)
        
        if subsystem == 'Substations' and subhubs is not None:
            
            for subhub_id in subhubs:
                
                temp_comp["Component_ID"] = subhub_id
                temp_comp["Component_type"] = subhub_id
                temp_comp["Component_subtype"] = "subhub"
        
                num_cols = all_comp.shape[1]
                temp_comp = temp_comp.rename(num_cols)
                all_comp = pd.concat([all_comp, temp_comp],
                                     axis=1,
                                     sort=False)
        
    else:
        
        # Iterate through the devices
        for device_id in array_layout.keys():
            
            numstrs = re.findall('\d+', device_id)
            num = int(numstrs[0])
            
            subsystem_id = "{}{:0>3}".format(subsystem_root, num)
            temp_comp["Component_ID"] = subsystem_id
            temp_comp["Component_type"] = device_id

            num_cols = all_comp.shape[1]
            temp_comp = temp_comp.rename(num_cols)
            all_comp = pd.concat([all_comp, temp_comp],
                                 axis=1,
                                 sort=False)
                
    return all_comp

    
def update_onsite_tables(subsystem,
                         subsystem_root,
                         system_type,
                         array_layout,
                         bathymetry,
                         temp_modes,
                         temp_repair,
                         all_modes,
                         all_repair,
                         subhubs):
    
    operation = 'onsite'
    
    array_subsystems = ['Substations',
                        'Export Cable']
                        
    operations_map = {'onsite' : "MoS",
                      "replacement": "RtP",
                      'inspections': "Insp"}

    array_dict = {'Substations': [1, 1],
                  'Export Cable': [7, 3]}

    array_df = pd.DataFrame(array_dict, index=['onsite', 'inspections'])

    iterables = [['Fixed', 'Floating'], ['Shallow', 'Deep']]
    op_index = pd.MultiIndex.from_product(iterables, names=['Type', 'Depth'])
    
    onsite_dict = {'Prime Mover': [3, 4, 1, 1],
                   'PTO': [3, 4, 1, 1],
                   'Control': [3, 4, 1, 1],
                   'Support Structure': [3, 4, 3, 4],
                   'Umbilical Cable': [-1, -1, 3, 4],
                   'Inter-Array Cables': [7, 7, 7, 7],
                   'Foundations': [6, 6, 6, 6],
                   'Mooring Lines': [5, 5, 5, 5]}

    onsite_df = pd.DataFrame(onsite_dict, index=op_index)

    # Build final tables
    if subsystem in array_subsystems:
        
        subsystem_id = "{}001".format(subsystem_root)
        
        # Get the operation type
        op_number = array_df[subsystem][operation]
        op_code = operations_map[operation]
        op_id = "{}{}".format(op_code, op_number)
        
        temp_repair["Component_ID"] = subsystem_id
        temp_repair["FM_ID"] = op_id

        num_cols = all_repair.shape[1]
        temp_repair = temp_repair.rename(num_cols)
        all_repair = pd.concat([all_repair, temp_repair],
                               axis=1,
                               sort=False)

        temp_modes["Component_ID"] = subsystem_id
        temp_modes["FM_ID"] = op_id

        num_cols = all_modes.shape[1]
        temp_modes = temp_modes.rename(num_cols)
        all_modes = pd.concat([all_modes, temp_modes],
                              axis=1,
                              sort=False)
        
        if subsystem == 'Substations' and subhubs is not None:
            
            for subhub_id in subhubs:
                
                temp_repair["Component_ID"] = subhub_id
        
                num_cols = all_repair.shape[1]
                temp_repair = temp_repair.rename(num_cols)
                all_repair = pd.concat([all_repair, temp_repair],
                                       axis=1,
                                       sort=False)
        
                temp_modes["Component_ID"] = subhub_id
        
                num_cols = all_modes.shape[1]
                temp_modes = temp_modes.rename(num_cols)
                all_modes = pd.concat([all_modes, temp_modes],
                                      axis=1,
                                      sort=False)
            
    else:
        
        # Iterate through the devices
        for device_id, position in array_layout.iteritems():
            
            numstrs = re.findall('\d+', device_id)
            num = int(numstrs[0])
            
            subsystem_id = "{}{:0>3}".format(subsystem_root, num)
            
            # Get device depth and position type
            depth = get_point_depth(bathymetry, position)
            
            if depth < -30.:
                depth_type = "Deep"
            else:
                depth_type = "Shallow"
                
            pos_type = system_type.split()[1]

            # Get the operation type
            op_number = onsite_df[subsystem][pos_type][depth_type]
            op_id = "MoS{}".format(op_number)
            
            temp_repair["Component_ID"] = subsystem_id
            temp_repair["FM_ID"] = op_id

            num_cols = all_repair.shape[1]
            temp_repair = temp_repair.rename(num_cols)
            all_repair = pd.concat([all_repair, temp_repair],
                                   axis=1,
                                   sort=False)

            temp_modes["Component_ID"] = subsystem_id
            temp_modes["FM_ID"] = op_id

            num_cols = all_modes.shape[1]
            temp_modes = temp_modes.rename(num_cols)
            all_modes = pd.concat([all_modes, temp_modes],
                                  axis=1,
                                  sort=False)       
            
    return all_modes, all_repair


def update_replacement_tables(subsystem,
                              subsystem_root,
                              system_type,
                              transportation_method,
                              array_layout,
                              temp_modes,
                              temp_repair,
                              all_modes,
                              all_repair):
    
    array_subsystems = ['Substations',
                        'Export Cable']
    
    if transportation_method == "Tow":
        dev_actions = [4, 3]
    elif transportation_method == "Deck":
        dev_actions = [2, 1]
    else:
        errMsg = "Holy Astringent Plum-like Fruit, Batman!"
        raise RuntimeError(errMsg)
        
    replacement_dict = {'Prime Mover': dev_actions,
                        'PTO': dev_actions,
                        'Control': dev_actions,
                        'Support Structure': dev_actions,
                        'Umbilical Cable': [6, 6],
                        'Mooring Lines': [5, 5]}
    
    replacement_df = pd.DataFrame(replacement_dict,
                                  index=['Fixed', 'Floating'])

    # Build final tables
    if subsystem not in array_subsystems:

        # Iterate through the devices
        for device_id, position in array_layout.iteritems():
            
            numstrs = re.findall('\d+', device_id)
            num = int(numstrs[0])
            
            subsystem_id = "{}{:0>3}".format(subsystem_root, num)
            pos_type = system_type.split()[1]
                
            # Get the operation type
            op_number = replacement_df[subsystem][pos_type]
            op_id = "RtP{}".format(op_number)
            
            temp_repair["Component_ID"] = subsystem_id
            temp_repair["FM_ID"] = op_id

            num_cols = all_repair.shape[1]
            temp_repair = temp_repair.rename(num_cols)
            all_repair = pd.concat([all_repair, temp_repair],
                                   axis=1,
                                   sort=False)

            temp_modes["Component_ID"] = subsystem_id
            temp_modes["FM_ID"] = op_id

            num_cols = all_modes.shape[1]
            temp_modes = temp_modes.rename(num_cols)
            all_modes = pd.concat([all_modes, temp_modes],
                                  axis=1,
                                  sort=False)
                
    return all_modes, all_repair


def update_inspections_tables(subsystem,
                              subsystem_root,
                              system_type,
                              array_layout,
                              bathymetry,
                              temp_modes,
                              temp_inspection,
                              all_modes,
                              all_inspection,
                              subhubs):
    
    operation = "inspections"
    
    array_subsystems = ['Substations',
                        'Export Cable']
                        
    operations_map = {'onsite' : "MoS",
                      "replacement": "RtP",
                      'inspections': "Insp"}

    array_dict = {'Substations': [1, 1],
                  'Export Cable': [7, 3]}

    array_df = pd.DataFrame(array_dict, index=['onsite', 'inspections'])

    iterables = [['Fixed', 'Floating'], ['Shallow', 'Deep']]
    op_index = pd.MultiIndex.from_product(iterables, names=['Type', 'Depth'])
    
    inspections_dict = {'Prime Mover': [3, 4, 1, 1],
                        'PTO': [3, 4, 1, 1],
                        'Control': [3, 4, 1, 1],
                        'Support Structure': [3, 4, 3, 4],
                        'Umbilical Cable': [-1, -1, 3, 4],
                        'Inter-Array Cables': [3, 4, 3, 4],
                        'Foundations': [3, 4, 3, 4],
                        'Mooring Lines': [3, 4, 3, 4]}

    inspections_df = pd.DataFrame(inspections_dict, index=op_index)

    # Build final tables
    if subsystem in array_subsystems:
        
        subsystem_id = "{}001".format(subsystem_root)
        
        # Get the operation type
        op_number = array_df[subsystem][operation]
        op_code = operations_map[operation]
        op_id = "{}{}".format(op_code, op_number)
                    
        temp_inspection["Component_ID"] = subsystem_id
        temp_inspection["FM_ID"] = op_id

        num_cols = all_inspection.shape[1]
        temp_inspection = temp_inspection.rename(num_cols)
        all_inspection = pd.concat([all_inspection, temp_inspection],
                                   axis=1,
                                   sort=False)

        temp_modes["Component_ID"] = subsystem_id
        temp_modes["FM_ID"] = op_id

        num_cols = all_modes.shape[1]
        temp_modes = temp_modes.rename(num_cols)
        all_modes = pd.concat([all_modes, temp_modes],
                              axis=1,
                              sort=False)
        
        if subsystem == 'Substations' and subhubs is not None:
            
            for subhub_id in subhubs:
                
                temp_inspection["Component_ID"] = subhub_id
        
                num_cols = all_inspection.shape[1]
                temp_inspection = temp_inspection.rename(num_cols)
                all_inspection = pd.concat([all_inspection, temp_inspection],
                                           axis=1,
                                           sort=False)
        
                temp_modes["Component_ID"] = subhub_id
        
                num_cols = all_modes.shape[1]
                temp_modes = temp_modes.rename(num_cols)
                all_modes = pd.concat([all_modes, temp_modes],
                                      axis=1,
                                      sort=False)
            
    else:
        
        # Iterate through the devices
        for device_id, position in array_layout.iteritems():
            
            numstrs = re.findall('\d+', device_id)
            num = int(numstrs[0])
            
            subsystem_id = "{}{:0>3}".format(subsystem_root, num)
            
            # Get device depth and position type
            depth = get_point_depth(bathymetry, position)
            
            if depth < -30.:
                depth_type = "Deep"
            else:
                depth_type = "Shallow"
                
            pos_type = system_type.split()[1]
                                
            # Get the operation type
            op_number = inspections_df[subsystem][pos_type][depth_type]
            op_id = "Insp{}".format(op_number)

            temp_inspection["Component_ID"] = subsystem_id
            temp_inspection["FM_ID"] = op_id

            num_cols = all_inspection.shape[1]
            temp_inspection = temp_inspection.rename(num_cols)
            all_inspection = pd.concat([all_inspection, temp_inspection],
                                       axis=1,
                                       sort=False)

            temp_modes["Component_ID"] = subsystem_id
            temp_modes["FM_ID"] = op_id

            num_cols = all_modes.shape[1]
            temp_modes = temp_modes.rename(num_cols)
            all_modes = pd.concat([all_modes, temp_modes],
                                  axis=1,
                                  sort=False)
                
    return all_modes, all_inspection


def get_user_network(subsytem_comps, array_layout):
    
    """Manufacture the user network for the device subsytems"""
    
    subsystem_names = ['Hydrodynamic',
                       'Pto',
                       'Support structure']
    
    if len(subsytem_comps) == 4:
        subsystem_names.insert(2, 'Control')
    
    user_hierarchy = {}
    user_bom = {}

    device_subsytem_hierarchy = {k: [v] for k, v in zip(subsystem_names,
                                                        subsytem_comps)}
                                 
    device_subsytem_bom = {k: {'quantity': Counter({v: 1})}
                            for k, v in zip(subsystem_names, subsytem_comps)}

    for device_id in array_layout.keys():
        
        user_hierarchy[device_id] = device_subsytem_hierarchy
        user_bom[device_id] = device_subsytem_bom

    return user_hierarchy, user_bom


def get_user_compdict(subsytem_comps,
                      subsystem_failure_rates):
    
    subsystem_names = ['Prime Mover',
                       'PTO',
                       'Support Structure']
    
    if len(subsytem_comps) == 4:
        subsystem_names.insert(2, 'Control')
    
    all_rates = [subsystem_failure_rates[x] for x in subsystem_names]
    rates_dict = {'Key Identifier': subsytem_comps,
                  "Lower Bound": all_rates,
                  "Mean": all_rates,
                  "Upper Bound": all_rates}
    
    rates_df = pd.DataFrame(rates_dict)
    
    comp_db = get_component_dict('user-defined',
                                 rates_df,
                                 rates_df)
    
    return comp_db


def get_point_depth(bathyset, position):
    
    x = bathyset["x"].values
    y = bathyset["y"].values

    zv = bathyset["depth"].max(dim=["layer"]).values

    bathy_interp_function = RegularGridInterpolator((x, y), zv)
    
    depth = bathy_interp_function(position.coords[0][0:2])
    
    return depth


def get_events_table(raw_df,
                     prepend_special_raw=None,
                     prepend_special_name=None):
    
    raw_df = raw_df.dropna()
    
    # Get required columns from raw_df
    if prepend_special_raw is not None:
        cols_toget = [prepend_special_raw]
    else:
        cols_toget = []
    
    # Add standard columns
    cols_toget.extend([u'repairActionRequestDate [-]',
                       u'repairActionDate [-]',
                       u'downtimeDuration [Hour]',
                       u'ComponentSubType [-]',
                       u'FM_ID [-]',
                       u'costLogistic [Euro]',
                       u'costOM_Labor [Euro]',
                       u'costOM_Spare [Euro]',
                       u'nameOfvessel [-]'])
    
    data_df = raw_df.loc[:, cols_toget]
    
    if prepend_special_raw is not None:
        data_df[prepend_special_raw] = pd.to_datetime(
                                            data_df[prepend_special_raw])

    data_df.loc[:, "repairActionDate [-]"] = pd.to_datetime(
                            data_df["repairActionDate [-]"])
    data_df.loc[:, "repairActionRequestDate [-]"] = pd.to_datetime(
                            data_df["repairActionRequestDate [-]"])
    data_df = data_df.sort_values(by="repairActionDate [-]")
    data_df = data_df.reset_index(drop=True)
        
    def mode_match(x):
        
        if "Insp" in x:
            return "Inspection"
        
        if "MoS" in x:
            return "On-Site Maintenance"
        
        if "RtP" in x:
            return "Replacement"
    
    data_df["FM_ID [-]"] = data_df["FM_ID [-]"].apply(mode_match)        
    
    name_map = {
            "repairActionRequestDate [-]": "Operation Request Date",
            "repairActionDate [-]": "Operation Action Date",
            "downtimeDuration [Hour]": "Downtime",
            "ComponentSubType [-]": "Sub-System",
            "FM_ID [-]": "Operation Type",
            "costLogistic [Euro]": "Logistics Cost",
            "costOM_Labor [Euro]": "Labour Cost",
            "costOM_Spare [Euro]": "Parts Cost",
            'nameOfvessel [-]': "Vessel Name"}
    
    if prepend_special_name is not None:
        name_map[prepend_special_raw] = prepend_special_name

    data_df = data_df.rename(columns=name_map)
    
    subsytem_map = {'Elec sub-system': 'Inter-Array Cables',
                    'Control': 'Control',
                    'Umbilical': 'Umbilical Cable',
                    'Export cable': 'Export Cable',
                    'Foundation': 'Foundations',
                    'Hydrodynamic': 'Prime Mover',
                    'Moorings lines': 'Mooring Lines',
                    'Pto': 'PTO',
                    'Substation': 'Substations',
                    'Support structure': 'Support Structure'}
    
    data_df["Sub-System"] = data_df["Sub-System"].replace(subsytem_map)
    
    return data_df


def get_electrical_system_cost(component_data, system_names, db):
    
    '''Get cost of each electrical subsystem in system_names.

    Args:
        component_data (pd.DataFrame) [-]: Table of components used in
            the electrical network.
        system_names (list) [-]: List of subsystems in the given network.
        db (Object) [-]: Component database object.

    Attributes:
        cost_dict (dict) [E]: Cost of each subsystem;
            key = subsystem, val = total cost.

    Returns:
        cost_dict

    '''
    
    subsytem_map = {'array': 'Inter-Array Cables',
                    'dry-mate': 'Inter-Array Cables',
                    'wet-mate': 'Inter-Array Cables',
                    'export': 'Export Cable',
                    'passive hub': 'Substations',
                    'substation': 'Substations',
                    'umbilical': 'Umbilical Cable'}
    
    cost_dict = {key: 0 for key in system_names}

    for _, component in component_data.iterrows():
                        
        install_type = component['Installation Type']

        if install_type not in subsytem_map.keys():
            
            errStr = ("Installation type '{}' is not "
                      "recognised").format(install_type)
            raise ValueError(errStr)
    
        subsytem_type = subsytem_map[install_type]
        
        if subsytem_type not in system_names:
            
            errStr = "Where's the bloody air force?"
            raise RuntimeError(errStr)
        
        component_id = component['Key Identifier']
        
        cost_dict[subsytem_type] += _get_elec_db_cost(component_id,
                                                      component.Quantity,
                                                      db,
                                                      install_type)
    
    return cost_dict


def get_mandf_system_cost(mandf_bom, system_names, db):
    
    '''Get cost of each moorings or foundations subsystem in system_names.
    
    Args:
        mandf_bom (pd.DataFrame) [-]: Table of costs used in the moorings
            and foundations networks.
        system_names (list) [-]: List of subsystems in the given network.
        db (Object) [-]: Component database object.
    
    Attributes:
        cost_dict (dict) [E]: Cost of each subsystem;
            key = subsystem, val = total cost.
    
    Returns:
        cost_dict
    
    '''
    
    subsytem_map = {'drag anchor': 'Foundations',
                    'pile': 'Foundations',
                    'suctioncaisson': 'Foundations',
                    "cable": 'Mooring Lines',
                    "chain": 'Mooring Lines',
                    "forerunner assembly": 'Mooring Lines',
                    "rope": 'Mooring Lines',
                    "shackle": 'Mooring Lines',
                    "swivel": 'Mooring Lines'}
    
    cost_dict = {key: 0 for key in system_names}
    
    for _, component in mandf_bom.iterrows():
        
        component_key = component['Key Identifier']
        
        # Catch 'n/a'
        if component_key == "n/a":
            
            subsytem_type = "Foundations"
            cost = component['Cost']
        
        else:
            
            # Get the component dictionary
            component_dict = db[component_key]
            
            # Pick up the component type
            component_type = component_dict['item2']
            
            if component_type not in subsytem_map.keys():
                
                errStr = ("Component type '{}' is not "
                          "recognised").format(component_type)
                raise ValueError(errStr)
            
            subsytem_type = subsytem_map[component_type]
            cost = component_dict['item11'] * component['Quantity']
        
        if subsytem_type not in system_names:
            
            errStr = "I would like to have seen Montana..."
            raise RuntimeError(errStr)
        
        cost_dict[subsytem_type] += cost
    
    return cost_dict


def _get_elec_db_cost(component_key, quantity, db, type_):
        
    '''Use component key and quantity to calculate total cost.

    Args:
        component_key (int) [-]: Database key.
        quantity (float) [-]: Quantity of component used.
        db (Object) [-]: Electrical component database object.

    Returns:
        float: total cost of quantity components

    '''
    
    convert_map = {'export': 'export_cable',
                   'array': 'array_cable',
                   'umbilical': 'dynamic_cable',
                   'passive hub': 'collection_points',
                   'substation': 'collection_points',
                   'subhub': 'collection_points',
                   'dry-mate': 'dry_mate_connectors',
                   'wet-mate': 'wet_mate_connectors'}
    
    if type_ not in convert_map:
        
        errMsg = ("Electrical system type '{}' is not "
                  "recognised").format(type_)
        raise ValueError(errMsg)
    
    converted_type = convert_map[type_]
    component_db = getattr(db, converted_type)
    
    cost = component_db[component_db.id == component_key].cost.values[0]
    val = quantity * cost
    
    return val
