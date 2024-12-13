
import pytest

import datetime as dt

import pandas as pd
from pandas.api.types import is_datetime64_dtype

from dtocean_core.utils.maintenance import (update_comp_table,
                                            update_onsite_tables,
                                            update_replacement_tables,
                                            update_inspections_tables,
                                            get_events_table,
                                            get_electrical_system_cost,
                                            get_mandf_system_cost,
                                            _get_elec_db_cost)


@pytest.fixture(scope="module")
def corrective_events_table():
    
    events_dict = \
        {'ComponentID [-]': {0: 'Array elec sub-system003',
                             1: 'Export Cable001',
                             2: 'Array elec sub-system004',
                             3: 'Array elec sub-system002',
                             4: 'Array elec sub-system004',
                             5: 'Pto003',
                             6: 'Array elec sub-system001',
                             7: 'Array elec sub-system002',
                             8: 'Array elec sub-system004',
                             9: 'Array elec sub-system003',
                             10: 'Array elec sub-system001',
                             11: 'Pto003',
                             12: 'Array elec sub-system004',
                             13: 'Array elec sub-system001',
                             14: 'Array elec sub-system003',
                             15: 'Pto001',
                             16: 'Pto004',
                             17: 'Hydrodynamic001',
                             18: 'Array elec sub-system004',
                             19: 'Array elec sub-system003',
                             20: 'Array elec sub-system002',
                             21: 'Array elec sub-system003',
                             22: 'Array elec sub-system004',
                             23: 'Array elec sub-system001',
                             24: 'Array elec sub-system001',
                             25: 'Array elec sub-system002',
                             26: 'Array elec sub-system001',
                             27: 'Array elec sub-system004',
                             28: 'Array elec sub-system002',
                             29: 'Array elec sub-system002',
                             30: 'Array elec sub-system001'},
         'ComponentSubType [-]': {0: 'Array elec sub-system',
                                  1: 'Export Cable',
                                  2: 'Array elec sub-system',
                                  3: 'Array elec sub-system',
                                  4: 'Array elec sub-system',
                                  5: 'Pto',
                                  6: 'Array elec sub-system',
                                  7: 'Array elec sub-system',
                                  8: 'Array elec sub-system',
                                  9: 'Array elec sub-system',
                                  10: 'Array elec sub-system',
                                  11: 'Pto',
                                  12: 'Array elec sub-system',
                                  13: 'Array elec sub-system',
                                  14: 'Array elec sub-system',
                                  15: 'Pto',
                                  16: 'Pto',
                                  17: 'Hydrodynamic',
                                  18: 'Array elec sub-system',
                                  19: 'Array elec sub-system',
                                  20: 'Array elec sub-system',
                                  21: 'Array elec sub-system',
                                  22: 'Array elec sub-system',
                                  23: 'Array elec sub-system',
                                  24: 'Array elec sub-system',
                                  25: 'Array elec sub-system',
                                  26: 'Array elec sub-system',
                                  27: 'Array elec sub-system',
                                  28: 'Array elec sub-system',
                                  29: 'Array elec sub-system',
                                  30: 'Array elec sub-system'},
         'ComponentType [-]': {0: 'device003',
                               1: 'Export Cable001',
                               2: 'device004',
                               3: 'device002',
                               4: 'device004',
                               5: 'device003',
                               6: 'device001',
                               7: 'device002',
                               8: 'device004',
                               9: 'device003',
                               10: 'device001',
                               11: 'device003',
                               12: 'device004',
                               13: 'device001',
                               14: 'device003',
                               15: 'device001',
                               16: 'device004',
                               17: 'device001',
                               18: 'device004',
                               19: 'device003',
                               20: 'device002',
                               21: 'device003',
                               22: 'device004',
                               23: 'device001',
                               24: 'device001',
                               25: 'device002',
                               26: 'device001',
                               27: 'device004',
                               28: 'device002',
                               29: 'device002',
                               30: 'device001'},
         'FM_ID [-]': {0: 'MoS7',
                       1: 'MoS7',
                       2: 'MoS7',
                       3: 'MoS7',
                       4: 'MoS7',
                       5: 'RtP2',
                       6: 'MoS7',
                       7: 'MoS7',
                       8: 'MoS7',
                       9: 'MoS7',
                       10: 'MoS7',
                       11: 'MoS4',
                       12: 'MoS7',
                       13: 'MoS7',
                       14: 'MoS7',
                       15: 'RtP2',
                       16: 'RtP2',
                       17: 'RtP2',
                       18: 'MoS7',
                       19: 'MoS7',
                       20: 'MoS7',
                       21: 'MoS7',
                       22: 'MoS7',
                       23: 'MoS7',
                       24: 'MoS7',
                       25: 'MoS7',
                       26: 'MoS7',
                       27: 'MoS7',
                       28: 'MoS7',
                       29: 'MoS7',
                       30: 'MoS7'},
         'RA_ID [-]': {0: 'LpM5',
                       1: 'LpM5',
                       2: 'LpM5',
                       3: 'LpM5',
                       4: 'LpM5',
                       5: 'LpM6',
                       6: 'LpM5',
                       7: 'LpM5',
                       8: 'LpM5',
                       9: 'LpM5',
                       10: 'LpM5',
                       11: 'LpM3',
                       12: 'LpM5',
                       13: 'LpM5',
                       14: 'LpM5',
                       15: 'LpM6',
                       16: 'LpM6',
                       17: 'LpM6',
                       18: 'LpM5',
                       19: 'LpM5',
                       20: 'LpM5',
                       21: 'LpM5',
                       22: 'LpM5',
                       23: 'LpM5',
                       24: 'LpM5',
                       25: 'LpM5',
                       26: 'LpM5',
                       27: 'LpM5',
                       28: 'LpM5',
                       29: 'LpM5',
                       30: 'LpM5'},
         'costLogistic [Euro]': {0: 472056,
                                 1: 472081L,
                                 2: 472011L,
                                 3: 472134L,
                                 4: 472011L,
                                 5: 1001388L,
                                 6: 472118L,
                                 7: 472134L,
                                 8: 472011L,
                                 9: 472056L,
                                 10: 472118L,
                                 11: 53420L,
                                 12: 472011L,
                                 13: 472118L,
                                 14: 472056L,
                                 15: 1002111L,
                                 16: 1001794L,
                                 17: 1121760L,
                                 18: 472011L,
                                 19: 472056L,
                                 20: 472134L,
                                 21: 472056L,
                                 22: 472011L,
                                 23: 472118L,
                                 24: 472118L,
                                 25: 472134L,
                                 26: 472118L,
                                 27: 472011L,
                                 28: 472134L,
                                 29: 472134L,
                                 30: 472118L},
         'costOM_Labor [Euro]': {0: 21175,
                                 1: 21178L,
                                 2: 21170L,
                                 3: 21184L,
                                 4: 21170L,
                                 5: 37474L,
                                 6: 21182L,
                                 7: 21184L,
                                 8: 21170L,
                                 9: 21175L,
                                 10: 21182L,
                                 11: 13280L,
                                 12: 21170L,
                                 13: 21182L,
                                 14: 21175L,
                                 15: 37527L,
                                 16: 37504L,
                                 17: 43127L,
                                 18: 21170L,
                                 19: 21175L,
                                 20: 21184L,
                                 21: 21175L,
                                 22: 21170L,
                                 23: 21182L,
                                 24: 21182L,
                                 25: 21184L,
                                 26: 21182L,
                                 27: 21170L,
                                 28: 21184L,
                                 29: 21184L,
                                 30: 21182L},
         'costOM_Spare [Euro]': {0: 14685,
                                 1: 247435L,
                                 2: 14685L,
                                 3: 14685L,
                                 4: 14685L,
                                 5: 125000L,
                                 6: 14685L,
                                 7: 14685L,
                                 8: 14685L,
                                 9: 14685L,
                                 10: 14685L,
                                 11: 125000L,
                                 12: 14685L,
                                 13: 14685L,
                                 14: 14685L,
                                 15: 125000L,
                                 16: 125000L,
                                 17: 125000L,
                                 18: 14685L,
                                 19: 14685L,
                                 20: 14685L,
                                 21: 14685L,
                                 22: 14685L,
                                 23: 14685L,
                                 24: 14685L,
                                 25: 14685L,
                                 26: 14685L,
                                 27: 14685L,
                                 28: 14685L,
                                 29: 14685L,
                                 30: 14685L},
         'currentAlarmDate [-]': {0: dt.datetime(2000, 10, 23, 7, 50),
                                  1: dt.datetime(2001, 11, 12, 12, 38),
                                  2: dt.datetime(2002, 12, 13, 12, 38),
                                  3: dt.datetime(2003, 7, 17, 12, 38),
                                  4: dt.datetime(2003, 10, 19, 10, 56),
                                  5: dt.datetime(2004, 3, 28, 5, 26),
                                  6: dt.datetime(2004, 3, 30, 0, 38),
                                  7: dt.datetime(2005, 3, 18, 3, 44),
                                  8: dt.datetime(2006, 4, 15, 22, 56),
                                  9: dt.datetime(2006, 4, 21, 15, 44),
                                  10: dt.datetime(2006, 11, 2, 18, 8),
                                  11: dt.datetime(2006, 12, 28, 12, 38),
                                  12: dt.datetime(2008, 2, 23, 18, 8),
                                  13: dt.datetime(2008, 8, 29, 10, 56),
                                  14: dt.datetime(2009, 2, 5, 3, 44),
                                  15: dt.datetime(2011, 3, 12, 22, 14),
                                  16: dt.datetime(2011, 11, 2, 19, 50),
                                  17: dt.datetime(2011, 12, 1, 15, 2),
                                  18: dt.datetime(2012, 8, 13, 10, 56),
                                  19: dt.datetime(2012, 10, 25, 22, 56),
                                  20: dt.datetime(2013, 12, 13, 15, 44),
                                  21: dt.datetime(2014, 1, 27, 8, 32),
                                  22: dt.datetime(2014, 11, 16, 6, 8),
                                  23: dt.datetime(2015, 1, 24, 18, 8),
                                  24: dt.datetime(2016, 1, 27, 8, 32),
                                  25: dt.datetime(2016, 8, 15, 10, 56),
                                  26: dt.datetime(2017, 3, 28, 13, 20),
                                  27: dt.datetime(2017, 7, 21, 6, 8),
                                  28: dt.datetime(2017, 9, 14, 8, 32),
                                  29: dt.datetime(2019, 7, 5, 15, 44),
                                  30: dt.datetime(2019, 8, 26, 8, 32)},
         'downtimeDeviceList [-]': {0: ['device003', 'device004'],
                                    1: ['device003',
                                        'device002',
                                        'device004',
                                        'device001'],
                                    2: ['device004'],
                                    3: ['device002', 'device001'],
                                    4: ['device004'],
                                    5: ['device003'],
                                    6: ['device001'],
                                    7: ['device002', 'device001'],
                                    8: ['device004'],
                                    9: ['device003', 'device004'],
                                    10: ['device001'],
                                    11: ['device003'],
                                    12: ['device004'],
                                    13: ['device001'],
                                    14: ['device003', 'device004'],
                                    15: ['device001'],
                                    16: ['device004'],
                                    17: ['device001'],
                                    18: ['device004'],
                                    19: ['device003', 'device004'],
                                    20: ['device002', 'device001'],
                                    21: ['device003', 'device004'],
                                    22: ['device004'],
                                    23: ['device001'],
                                    24: ['device001'],
                                    25: ['device002', 'device001'],
                                    26: ['device001'],
                                    27: ['device004'],
                                    28: ['device002', 'device001'],
                                    29: ['device002', 'device001'],
                                    30: ['device001']},
         'downtimeDuration [Hour]': {0: 7015,
                                     1: 5503L,
                                     2: 3703L,
                                     3: 0L,
                                     4: 7159L,
                                     5: 7714L,
                                     6: 0L,
                                     7: 2191L,
                                     8: 1423L,
                                     9: 0L,
                                     10: 4831L,
                                     11: 0L,
                                     12: 2791L,
                                     13: 7543L,
                                     14: 2311L,
                                     15: 1306L,
                                     16: 3826L,
                                     17: 2628L,
                                     18: 0L,
                                     19: 4063L,
                                     20: 0L,
                                     21: 4495L,
                                     22: 4471L,
                                     23: 0L,
                                     24: 4495L,
                                     25: 6943L,
                                     26: 2887L,
                                     27: 0L,
                                     28: 8095L,
                                     29: 247L,
                                     30: 6655L},
         'failureRate [1/year]': {0: 0.26298,
                                  1: 0.26298,
                                  2: 0.39446999999999993,
                                  3: 0.26298,
                                  4: 0.39446999999999993,
                                  5: 0.0210384,
                                  6: 0.39446999999999993,
                                  7: 0.26298,
                                  8: 0.39446999999999993,
                                  9: 0.26298,
                                  10: 0.39446999999999993,
                                  11: 0.0420768,
                                  12: 0.39446999999999993,
                                  13: 0.39446999999999993,
                                  14: 0.26298,
                                  15: 0.0210384,
                                  16: 0.0210384,
                                  17: 0.0210384,
                                  18: 0.39446999999999993,
                                  19: 0.26298,
                                  20: 0.26298,
                                  21: 0.26298,
                                  22: 0.39446999999999993,
                                  23: 0.39446999999999993,
                                  24: 0.39446999999999993,
                                  25: 0.26298,
                                  26: 0.39446999999999993,
                                  27: 0.39446999999999993,
                                  28: 0.26298,
                                  29: 0.26298,
                                  30: 0.39446999999999993},
         'indexFM [-]': {0: 1L,
                         1: 1L,
                         2: 1L,
                         3: 1L,
                         4: 1L,
                         5: 2L,
                         6: 1L,
                         7: 1L,
                         8: 1L,
                         9: 1L,
                         10: 1L,
                         11: 1L,
                         12: 1L,
                         13: 1L,
                         14: 1L,
                         15: 2L,
                         16: 2L,
                         17: 2L,
                         18: 1L,
                         19: 1L,
                         20: 1L,
                         21: 1L,
                         22: 1L,
                         23: 1L,
                         24: 1L,
                         25: 1L,
                         26: 1L,
                         27: 1L,
                         28: 1L,
                         29: 1L,
                         30: 1L},
         'repairActionDate [-]': {0: '2001-08-15 13:00:00',
                                  1: '2002-08-15 13:00:00',
                                  2: '2003-08-15 13:00:00',
                                  3: '2003-08-15 13:00:00',
                                  4: '2004-08-14 13:00:00',
                                  5: '2004-07-08 16:00:00',
                                  6: '2004-08-15 13:00:00',
                                  7: '2005-08-15 13:00:00',
                                  8: '2006-08-15 13:00:00',
                                  9: '2006-08-15 13:00:00',
                                  10: '2007-08-15 13:00:00',
                                  11: '2007-06-07 15:00:00',
                                  12: '2008-08-14 13:00:00',
                                  13: '2009-08-15 13:00:00',
                                  14: '2009-08-15 13:00:00',
                                  15: '2011-07-08 16:00:00',
                                  16: '2012-07-07 16:00:00',
                                  17: '2012-06-19 14:00:00',
                                  18: '2012-08-15 13:00:00',
                                  19: '2013-08-15 13:00:00',
                                  20: '2014-08-15 13:00:00',
                                  21: '2014-08-15 13:00:00',
                                  22: '2015-08-15 13:00:00',
                                  23: '2015-08-15 13:00:00',
                                  24: '2016-08-14 13:00:00',
                                  25: '2017-08-15 13:00:00',
                                  26: '2017-08-15 13:00:00',
                                  27: '2017-08-15 13:00:00',
                                  28: '2018-08-15 13:00:00',
                                  29: '2019-08-15 13:00:00',
                                  30: '2020-08-14 13:00:00'},
         'repairActionRequestDate [-]': {0: dt.datetime(2000, 10, 23, 7, 50),
                                         1: dt.datetime(2001, 11, 12, 12, 38),
                                         2: dt.datetime(2002, 12, 13, 12, 35),
                                         3: dt.datetime(2003, 7, 17, 12, 38),
                                         4: dt.datetime(2003, 10, 19, 10, 56),
                                         5: dt.datetime(2004, 3, 28, 5, 26),
                                         6: dt.datetime(2004, 3, 30, 0, 38),
                                         7: dt.datetime(2005, 3, 18, 3, 44),
                                         8: dt.datetime(2006, 4, 15, 22, 56),
                                         9: dt.datetime(2006, 4, 21, 15, 44),
                                         10: dt.datetime(2006, 11, 2, 18, 8),
                                         11: dt.datetime(2006, 12, 28, 12, 38),
                                         12: dt.datetime(2008, 2, 23, 18, 8),
                                         13: dt.datetime(2008, 8, 29, 10, 56),
                                         14: dt.datetime(2009, 2, 5, 3, 44),
                                         15: dt.datetime(2011, 3, 12, 22, 14),
                                         16: dt.datetime(2011, 11, 2, 19, 50),
                                         17: dt.datetime(2011, 12, 1, 15, 2),
                                         18: dt.datetime(2012, 8, 13, 10, 56),
                                         19: dt.datetime(2012, 10, 25, 22, 56),
                                         20: dt.datetime(2013, 12, 13, 15, 44),
                                         21: dt.datetime(2014, 1, 27, 8, 32),
                                         22: dt.datetime(2014, 11, 16, 6, 8),
                                         23: dt.datetime(2015, 1, 24, 18, 8),
                                         24: dt.datetime(2016, 1, 27, 8, 32),
                                         25: dt.datetime(2016, 8, 15, 10, 56),
                                         26: dt.datetime(2017, 3, 28, 13, 20),
                                         27: dt.datetime(2017, 7, 21, 6, 8),
                                         28: dt.datetime(2017, 9, 14, 8, 32),
                                         29: dt.datetime(2019, 7, 5, 15, 44),
                                         30: dt.datetime(2019, 8, 26, 8, 32)},
        'nameOfvessel [-]': {0: 'Bob',
                             1: 'Bob',
                             2: 'Bob',
                             3: 'Bob',
                             4: 'Bob',
                             5: 'Bob',
                             6: 'Bob',
                             7: 'Bob',
                             8: 'Bob',
                             9: 'Bob',
                             10: 'Bob',
                             11: 'Bob',
                             12: 'Bob',
                             13: 'Bob',
                             14: 'Bob',
                             15: 'Bob',
                             16: 'Bob',
                             17: 'Bob',
                             18: 'Bob',
                             19: 'Bob',
                             20: 'Bob',
                             21: 'Bob',
                             22: 'Bob',
                             23: 'Bob',
                             24: 'Bob',
                             25: 'Bob',
                             26: 'Bob',
                             27: 'Bob',
                             28: 'Bob',
                             29: 'Bob',
                             30: 'Bob'}}

    events_df = pd.DataFrame(events_dict)
    
    return events_df


def test_update_comp_table_subhubs():
    
    subsystem = 'Substations'
    subsystem_root = "test"
    array_layout = {}
    temp_comp = pd.Series()
    all_comp = pd.DataFrame()
    subhubs = ["subhub1", "subhub2"]

    result = update_comp_table(subsystem,
                               subsystem_root,
                               array_layout,
                               temp_comp,
                               all_comp,
                               subhubs)
        
    assert set(result.index.values) == set(["Component_ID",
                                            "Component_type",
                                            "Component_subtype"])
    assert len(result.columns) == 3
    
    
def test_update_comp_table_devices():
    
    subsystem = 'PTO'
    subsystem_root = "test"
    array_layout = {"dev1": 0, "dev2": 0}
    temp_comp = pd.Series()
    all_comp = pd.DataFrame()
    subhubs = None

    result = update_comp_table(subsystem,
                               subsystem_root,
                               array_layout,
                               temp_comp,
                               all_comp,
                               subhubs)
    
    assert set(result.index.values) == set(["Component_ID",
                                            "Component_type"])
    assert len(result.columns) == 2
    
    
def test_update_onsite_tables_subhubs(mocker):
    
    subsystem = 'Substations'
    subsystem_root = "test"
    system_type = 'Wave Floating'
    array_layout = {}
    bathymetry = None
    temp_modes = pd.Series()
    temp_repair = pd.Series()
    all_modes = pd.DataFrame()
    all_repair = pd.DataFrame()
    subhubs = ["subhub1", "subhub2"]
    
    mocker.patch("dtocean_core.utils.maintenance.get_point_depth",
                 return_value=1,
                 autospec=True)
    
    all_modes, all_repair = update_onsite_tables(subsystem,
                                                 subsystem_root,
                                                 system_type,
                                                 array_layout,
                                                 bathymetry,
                                                 temp_modes,
                                                 temp_repair,
                                                 all_modes,
                                                 all_repair,
                                                 subhubs)

    assert set(all_modes.index.values) == set(["Component_ID",
                                               "FM_ID"])
    assert set(all_repair.index.values) == set(["Component_ID",
                                                "FM_ID"])
    assert len(all_modes.columns) == 3
    assert len(all_repair.columns) == 3
    
    
def test_update_onsite_tables_devices(mocker):
    
    subsystem = 'PTO'
    subsystem_root = "test"
    system_type = 'Wave Floating'
    array_layout = {"dev1": 0, "dev2": 0}
    bathymetry = None
    temp_modes = pd.Series()
    temp_repair = pd.Series()
    all_modes = pd.DataFrame()
    all_repair = pd.DataFrame()
    subhubs = None
    
    mocker.patch("dtocean_core.utils.maintenance.get_point_depth",
                 return_value=-1,
                 autospec=True)
    
    all_modes, all_repair = update_onsite_tables(subsystem,
                                                 subsystem_root,
                                                 system_type,
                                                 array_layout,
                                                 bathymetry,
                                                 temp_modes,
                                                 temp_repair,
                                                 all_modes,
                                                 all_repair,
                                                 subhubs)

    assert set(all_modes.index.values) == set(["Component_ID",
                                               "FM_ID"])
    assert set(all_repair.index.values) == set(["Component_ID",
                                                "FM_ID"])
    assert len(all_modes.columns) == 2
    assert len(all_repair.columns) == 2


def test_update_onsite_tables_devices_deep(mocker):
    
    subsystem = 'PTO'
    subsystem_root = "test"
    system_type = 'Wave Floating'
    array_layout = {"dev1": 0, "dev2": 0}
    bathymetry = None
    temp_modes = pd.Series()
    temp_repair = pd.Series()
    all_modes = pd.DataFrame()
    all_repair = pd.DataFrame()
    subhubs = None
    
    mocker.patch("dtocean_core.utils.maintenance.get_point_depth",
                 return_value=-50,
                 autospec=True)
    
    all_modes, all_repair = update_onsite_tables(subsystem,
                                                 subsystem_root,
                                                 system_type,
                                                 array_layout,
                                                 bathymetry,
                                                 temp_modes,
                                                 temp_repair,
                                                 all_modes,
                                                 all_repair,
                                                 subhubs)

    assert set(all_modes.index.values) == set(["Component_ID",
                                               "FM_ID"])
    assert set(all_repair.index.values) == set(["Component_ID",
                                                "FM_ID"])
    assert len(all_modes.columns) == 2
    assert len(all_repair.columns) == 2


@pytest.mark.parametrize("transport", 
                         ["Tow", "Deck"])
def test_update_replacement_tables(transport):

    subsystem = 'PTO'
    subsystem_root = "test"
    system_type = 'Wave Floating'
    transportation_method = transport
    array_layout = {"dev1": 0, "dev2": 0}
    temp_modes = pd.Series()
    temp_repair = pd.Series()
    all_modes = pd.DataFrame()
    all_repair = pd.DataFrame()

    all_modes, all_repair = update_replacement_tables(subsystem,
                                                      subsystem_root,
                                                      system_type,
                                                      transportation_method,
                                                      array_layout,
                                                      temp_modes,
                                                      temp_repair,
                                                      all_modes,
                                                      all_repair)
    
    assert set(all_modes.index.values) == set(["Component_ID",
                                               "FM_ID"])
    assert set(all_repair.index.values) == set(["Component_ID",
                                                "FM_ID"])
    assert len(all_modes.columns) == 2
    assert len(all_repair.columns) == 2


def test_update_replacement_tables_bad_transport():

    subsystem = 'PTO'
    subsystem_root = "test"
    system_type = 'Wave Floating'
    transportation_method = "Bad"
    array_layout = {"dev1": 0, "dev2": 0}
    temp_modes = pd.Series()
    temp_repair = pd.Series()
    all_modes = pd.DataFrame()
    all_repair = pd.DataFrame()

    with pytest.raises(RuntimeError):
        update_replacement_tables(subsystem,
                                  subsystem_root,
                                  system_type,
                                  transportation_method,
                                  array_layout,
                                  temp_modes,
                                  temp_repair,
                                  all_modes,
                                  all_repair)


def test_update_inspections_tables_subhubs(mocker):

    subsystem = 'Substations'
    subsystem_root = "test"
    system_type = 'Wave Floating'
    array_layout = {}
    bathymetry = None
    temp_modes = pd.Series()
    temp_inspection = pd.Series()
    all_modes = pd.DataFrame()
    all_inspection = pd.DataFrame()
    subhubs = ["subhub1", "subhub2"]

    (all_modes,
     all_inspection) = update_inspections_tables(subsystem,
                                                 subsystem_root,
                                                 system_type,
                                                 array_layout,
                                                 bathymetry,
                                                 temp_modes,
                                                 temp_inspection,
                                                 all_modes,
                                                 all_inspection,
                                                 subhubs)
    
    assert set(all_modes.index.values) == set(["Component_ID",
                                               "FM_ID"])
    assert set(all_inspection.index.values) == set(["Component_ID",
                                                "FM_ID"])
    assert len(all_modes.columns) == 3
    assert len(all_inspection.columns) == 3


def test_update_inspections_tables_devices(mocker):

    subsystem = 'PTO'
    subsystem_root = "test"
    system_type = 'Wave Floating'
    array_layout = {"dev1": 0, "dev2": 0}
    bathymetry = None
    temp_modes = pd.Series()
    temp_inspection = pd.Series()
    all_modes = pd.DataFrame()
    all_inspection = pd.DataFrame()
    subhubs = None
    
    mocker.patch("dtocean_core.utils.maintenance.get_point_depth",
                 return_value=-1,
                 autospec=True)

    (all_modes,
     all_inspection) = update_inspections_tables(subsystem,
                                                 subsystem_root,
                                                 system_type,
                                                 array_layout,
                                                 bathymetry,
                                                 temp_modes,
                                                 temp_inspection,
                                                 all_modes,
                                                 all_inspection,
                                                 subhubs)
    
    assert set(all_modes.index.values) == set(["Component_ID",
                                               "FM_ID"])
    assert set(all_inspection.index.values) == set(["Component_ID",
                                                "FM_ID"])
    assert len(all_modes.columns) == 2
    assert len(all_inspection.columns) == 2


def test_update_inspections_tables_devices_deep(mocker):

    subsystem = 'PTO'
    subsystem_root = "test"
    system_type = 'Wave Floating'
    array_layout = {"dev1": 0, "dev2": 0}
    bathymetry = None
    temp_modes = pd.Series()
    temp_inspection = pd.Series()
    all_modes = pd.DataFrame()
    all_inspection = pd.DataFrame()
    subhubs = None
    
    mocker.patch("dtocean_core.utils.maintenance.get_point_depth",
                 return_value=-50,
                 autospec=True)

    (all_modes,
     all_inspection) = update_inspections_tables(subsystem,
                                                 subsystem_root,
                                                 system_type,
                                                 array_layout,
                                                 bathymetry,
                                                 temp_modes,
                                                 temp_inspection,
                                                 all_modes,
                                                 all_inspection,
                                                 subhubs)
    
    assert set(all_modes.index.values) == set(["Component_ID",
                                               "FM_ID"])
    assert set(all_inspection.index.values) == set(["Component_ID",
                                                "FM_ID"])
    assert len(all_modes.columns) == 2
    assert len(all_inspection.columns) == 2


def test_get_events_table(corrective_events_table):
    
    events_df = corrective_events_table.copy()
    result = get_events_table(events_df)
    
    valid_columns = ["Operation Request Date",
                     "Operation Action Date",
                     "Downtime",
                     "Sub-System",
                     "Operation Type",
                     "Logistics Cost",
                     "Labour Cost",
                     "Parts Cost",
                     "Vessel Name"]
        
    assert len(result) == len(corrective_events_table)
    assert is_datetime64_dtype(result["Operation Request Date"])
    assert is_datetime64_dtype(result["Operation Action Date"])
    assert set(result.columns) == set(valid_columns)
    assert (result["Downtime"] >= 0).all()
    
    
def test_get_events_table_prepend(corrective_events_table):
    
    events_df = corrective_events_table.copy()
    result = get_events_table(events_df,
                              "indexFM [-]",
                              "Test")
    
    valid_columns = ["Operation Request Date",
                     "Operation Action Date",
                     "Downtime",
                     "Sub-System",
                     "Operation Type",
                     "Logistics Cost",
                     "Labour Cost",
                     "Parts Cost",
                     "Vessel Name",
                     "Test"]
    
    assert len(result) == len(corrective_events_table)
    assert is_datetime64_dtype(result["Operation Request Date"])
    assert is_datetime64_dtype(result["Operation Action Date"])
    assert set(result.columns) == set(valid_columns)
    assert (result["Downtime"] >= 0).all()
    
    
def test_get_electrical_system_cost_bad_install_type():
    
    component_data_dict = \
                            {'Installation Type': {0: 'motherboard'},
                             'Key Identifier': {0: 18},
                             'Marker': {0: 1},
                             'Quantity': {0: 1.0},
                             'UTM X': {0: 491940.0},
                             'UTM Y': {0: 6502050.0}}
                             
    component_data = pd.DataFrame(component_data_dict)
    system_names = ['Inter-Array Cables', 'Substations', 'Export Cable']
    
    with pytest.raises(ValueError):
        get_electrical_system_cost(component_data,
                                   system_names,
                                   None)
    
    
def test_get_electrical_system_cost_bad_system_names():
    
    component_data_dict = \
                            {'Installation Type': {0: 'wet-mate'},
                             'Key Identifier': {0: 18},
                             'Marker': {0: 1},
                             'Quantity': {0: 1.0},
                             'UTM X': {0: 491940.0},
                             'UTM Y': {0: 6502050.0}}
                             
    component_data = pd.DataFrame(component_data_dict)
    system_names = ['Sub-Array Cables', 'Substations', 'Export Cable']
    
    with pytest.raises(RuntimeError):
        get_electrical_system_cost(component_data,
                                   system_names,
                                   None)


def test_get_mandf_system_cost_bad_install_type():
    
    mandf_bom_dict = \
                    {'Cost': {0: 5375.346446283334,
                              12: 10200.532323116358},
                     'Key Identifier': {0: 'n/a',
                                        12: 336L},
                     'Quantity': {0: 1.0,
                                  12: 1.0},
                     'Year': {0: 0,
                              12: 0L}}

    mandf_bom = pd.DataFrame(mandf_bom_dict)
    system_names = ['Foundations']
    db = {336L: {'item2': "hook"}}
     
    with pytest.raises(ValueError):
        get_mandf_system_cost(mandf_bom,
                              system_names,
                              db)


def test_get_mandf_system_cost_bad_system_names():
    
    mandf_bom_dict = \
                    {'Cost': {0: 5375.346446283334,
                              12: 10200.532323116358},
                     'Key Identifier': {0: 'n/a',
                                        12: 336L},
                     'Quantity': {0: 1.0,
                                  12: 1.0},
                     'Year': {0: 0,
                              12: 0L}}

    mandf_bom = pd.DataFrame(mandf_bom_dict)
    system_names = ['Pins']
    db = {336L: {'item2': 'pile'}}
     
    with pytest.raises(RuntimeError):
        get_mandf_system_cost(mandf_bom,
                              system_names,
                              db)
        
        
def test_get_elec_db_cost_bad_type():
    
    with pytest.raises(ValueError):
        _get_elec_db_cost(None, None, None, "bob")
