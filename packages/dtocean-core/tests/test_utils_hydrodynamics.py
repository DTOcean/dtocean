
import os
import math

import pytest
import numpy as np
import pandas as pd

from dtocean_core.utils.hydrodynamics import (make_wave_statistics,
                                              bearing_to_radians,
                                              bearing_to_vector,
                                              radians_to_bearing,
                                              vector_to_bearing,
                                              make_power_histograms)


def test_make_wave_statistics_propability():
    
    sample_size = 1000
        
    Hm0 = 9. * np.random.random_sample(sample_size)
    Te = 15. * np.random.random_sample(sample_size)    
    dir_rmean = 360. * np.random.random_sample(sample_size)
#    H_max = 16. * np.random.random_sample(sample_size)
#    Tp = 16. * np.random.random_sample(sample_size)
#    T02 = 12. * np.random.random_sample(sample_size)
#    dir_peak = 360. * np.random.random_sample(sample_size)
#    P = 600. * np.random.random_sample(sample_size)
#    Wind_speed = 30. * np.random.random_sample(sample_size)
#    Wind_dir = 360. * np.random.random_sample(sample_size)
    
    wave_dict = {"Hm0"          : Hm0,
                 "Te"           : Te,
                 "Dir"          : dir_rmean
#                 "H_max"        : H_max,
#                 "Tp"           : Tp,
#                 "T02"          : T02,
#                 "dir_peak"     : dir_peak,
#                 "P"            : P,
#                 "wind_speed"   : Wind_speed,
#                 "wind_dir"     : Wind_dir
                 }
                
    wave_df = pd.DataFrame(wave_dict)

    test = make_wave_statistics(wave_df)

    assert len(test["Te"]) == test["p"].shape[0]    
    assert len(test["Hs"]) == test["p"].shape[1]    
    assert len(test["B"]) == test["p"].shape[2]
    assert np.allclose(np.sum(test["p"]), 1)
    
    
def test_make_wave_statistics_save(tmpdir):
    
    save_path = os.path.join(str(tmpdir), "test")
    
    sample_size = 1000
        
    Hm0 = 9. * np.random.random_sample(sample_size)
    Te = 15. * np.random.random_sample(sample_size)    
    dir_rmean = 360. * np.random.random_sample(sample_size)
#    H_max = 16. * np.random.random_sample(sample_size)
#    Tp = 16. * np.random.random_sample(sample_size)
#    T02 = 12. * np.random.random_sample(sample_size)
#    dir_peak = 360. * np.random.random_sample(sample_size)
#    P = 600. * np.random.random_sample(sample_size)
#    Wind_speed = 30. * np.random.random_sample(sample_size)
#    Wind_dir = 360. * np.random.random_sample(sample_size)
    
    wave_dict = {"Hm0"          : Hm0,
                 "Te"           : Te,
                 "Dir"          : dir_rmean
#                 "H_max"        : H_max,
#                 "Tp"           : Tp,
#                 "T02"          : T02,
#                 "dir_peak"     : dir_peak,
#                 "P"            : P,
#                 "wind_speed"   : Wind_speed,
#                 "wind_dir"     : Wind_dir
                 }
                
    wave_df = pd.DataFrame(wave_dict)

    make_wave_statistics(wave_df,
                         save_flag=True,
                         filepath=save_path)

    assert len(os.listdir(str(tmpdir))) == 1


#@pytest.mark.parametrize("ext, gamma", 
#                         [(".csv", 3.0),
#                          (".csv", 3.3),
#                          (".xlsx", 3.3),
#                          (".xlsx", 3.6)
#                          ])
#def test_add_Te_interface(tmpdir, ext, gamma):
#    
#    test_path_local = tmpdir.join("wave_data" + ext)
#    test_path = str(test_path_local)
#    
#    sample_size = 50
#        
#    Hm0 = 9. * np.random.random_sample(sample_size)
#    Tp = 16. * np.random.random_sample(sample_size)
#
#    wave_dict = {"Hm0"  : Hm0,
#                 "Tp"   : Tp
#                 }
#                
#    wave_df = pd.DataFrame(wave_dict)
#    
#    if ext == ".csv":
#        
#        wave_df.to_csv(test_path, index=False)
#        
#    elif ext == ".xlsx":
#        
#        wave_df.to_excel(test_path, index=False)
#        
#    else:
#        
#        raise ValueError("Someone call Superman")
#        
#    gamma_str = "-g {}".format(gamma)
#    
#    call(["add-Te", gamma_str, test_path])
#    
#    if ext == ".csv":
#        
#        wave_df = pd.read_csv(test_path)
#        
#    else:
#    
#        wave_df = pd.read_excel(test_path)
#    
#    assert "Te" in wave_df.columns
#    assert pd.notnull(wave_df["Te"]).all()
#    assert wave_df["Te"].min() >= 0.
#    assert wave_df["Te"].max() <= 16.


@pytest.mark.parametrize("bearing, radians", 
                         [(0.,   math.pi / 2.),
                          (45., math.pi / 4.),
                          (90.,  0.),
                          (135., 7 * math.pi / 4.),
                          (180., 3 * math.pi / 2.),
                          (225., 5 * math.pi / 4.),
                          (270., math.pi),
                          (315., 3 * math.pi / 4.)])
def test_bearing_to_radians(bearing, radians):
    
    test_radians = bearing_to_radians(bearing)
    
    assert np.isclose(test_radians, radians)


@pytest.mark.parametrize("bearing, vector", 
                         [(0.,   [0.,  1.]),
                          (45.,  [1 / math.sqrt(2),   1 / math.sqrt(2)]),
                          (90.,  [1.,  0.]),
                          (135., [1 / math.sqrt(2),  -1 / math.sqrt(2)]),
                          (180., [0., -1.]),
                          (225., [-1 / math.sqrt(2), -1 / math.sqrt(2)]),
                          (270., [-1., 0.]),
                          (315., [-1 / math.sqrt(2),  1 / math.sqrt(2)])])
def test_bearing_to_vector(bearing, vector):
    
    test_vector = bearing_to_vector(bearing)
    
    assert np.isclose(test_vector, vector).all()


@pytest.mark.parametrize("bearing, radians", 
                         [(0.,   math.pi / 2.),
                          (45.,  math.pi / 4.),
                          (90.,  0.),
                          (135., 7 * math.pi / 4.),
                          (180., 3 * math.pi / 2.),
                          (225., 5 * math.pi / 4.),
                          (270., math.pi),
                          (315., 3 * math.pi / 4.)])
def test_radians_to_bearing(bearing, radians):
    
    test_bearing = radians_to_bearing(radians)
    
    assert np.isclose(test_bearing, bearing)
    
    
@pytest.mark.parametrize("bearing, vector", 
                         [(0.,   [0.,   1.]),
                          (45.,  [1.,   1.]),
                          (90.,  [1.,   0.]),
                          (135., [1.,  -1.]),
                          (180., [0.,  -1.]),
                          (225., [-1., -1.]),
                          (270., [-1.,  0.]),
                          (315., [-1.,  1.])])
def test_vector_to_bearing(bearing, vector):
    
    test_bearing = vector_to_bearing(*vector)
    
    assert np.isclose(test_bearing, bearing)


def test_make_power_histograms():
    
    device_power_pmfs = {"device001": np.array([[0.2, 0.4],
                                                [0.8, 0.5],
                                                [1.2, 0.1]])}
    rated_power = 1.0
    
    result = make_power_histograms(device_power_pmfs,
                                   rated_power)
    
    assert len(result['device001'][0]) == 10
    assert len(result['device001'][1]) == 11
    assert np.isclose(result['device001'][0][9], 1)


def test_make_power_histograms_width_error():
    
    device_power_pmfs = {"device001": np.array([[0.2, 0.4],
                                                [0.8, 0.5],
                                                [1.2, 0.1]])}
    rated_power = 1.0
    
    with pytest.raises(ValueError):
        make_power_histograms(device_power_pmfs,
                              rated_power,
                              bin_width=0.3)
