# -*- coding: utf-8 -*-
"""
Example tidal case with optimised device layout
"""

import numpy as np
from scipy.stats import multivariate_normal, norm

from dtocean_hydro import start_logging
from dtocean_hydro.input import WP2_MachineData, WP2_SiteData, WP2input
from dtocean_hydro.main import WP2

# Start the logging system
start_logging()


def get_inputs():
    # Lease Area
    leaseAreaVertexUTM = np.array(
        [[0, 0], [900.0, 0], [900.0, 230.0], [0, 230.0]], dtype=float
    )

    Nogoareas_wave = [
        np.array([[0, 0], [250.0, 0], [250.0, 50.0], [0, 50.0]], dtype=float),
        np.array(
            [[0, 0], [250.0, 20], [550.0, 450.0], [100, 600], [0, 50.0]],
            dtype=float,
        ),
    ]

    # Tidal time series
    time_points = 1
    time_pdf = norm.pdf(np.linspace(-2, 2, time_points))
    time_scaled = time_pdf * (1.0 / np.amax(time_pdf))

    # Statistical analysis generation
    x = np.linspace(-50.0, 1000.0, 75)
    y = np.linspace(-50, 300.0, 11)

    nx = len(x)
    ny = len(y)

    xgrid, ygrid = np.meshgrid(x, y)
    pos = np.dstack((xgrid, ygrid))

    rv = multivariate_normal(
        [x.mean(), y.mean()],
        [[max(x) * 5.0, max(y) * 2.0], [max(y) * 2.0, max(x) * 5.0]],  # type: ignore
    )

    # u_max = 10.
    u_max = 5.0
    v_max = 1.0
    ssh_max = 1.0

    grid_pdf = rv.pdf(pos)

    u_scaled = grid_pdf * (u_max / np.amax(grid_pdf))
    v_scaled = np.ones((ny, nx)) * v_max
    ssh_scaled = grid_pdf * (ssh_max / np.amax(grid_pdf))

    u_arrays = []
    v_arrays = []
    ssh_arrays = []

    for multiplier in time_scaled:
        u_arrays.append(u_scaled * multiplier)
        v_arrays.append(v_scaled * multiplier)
        ssh_arrays.append(ssh_scaled * multiplier)

    U = np.dstack(u_arrays)
    V = np.dstack(v_arrays)
    SSH = np.dstack(ssh_arrays)
    TI = np.array([0.1])
    p = np.ones(U.shape[-1])

    # END of Statistical analysis generation
    # ---------------------------------------
    Meteocean = {"V": V, "U": U, "p": p, "TI": TI, "x": x, "y": y, "SSH": SSH}
    MainDirection = None
    Bathymetry = np.array([-60.0])
    BR = 1.0
    electrical_connection_point = (-1000.0, -4000.0)

    Site = WP2_SiteData(
        leaseAreaVertexUTM,
        Nogoareas_wave,
        Meteocean,
        None,
        None,
        MainDirection,
        Bathymetry,
        BR,
        electrical_connection_point,
        boundary_padding=0,
    )

    # Machine data
    X = np.array(
        [
            0.0,
            0.1010101,
            0.2020202,
            0.3030303,
            0.4040404,
            0.50505051,
            0.60606061,
            0.70707071,
            0.80808081,
            0.90909091,
            1.01010101,
            1.11111111,
            1.21212121,
            1.31313131,
            1.41414141,
            1.51515152,
            1.61616162,
            1.71717172,
            1.81818182,
            1.91919192,
            2.02020202,
            2.12121212,
            2.22222222,
            2.32323232,
            2.42424242,
            2.52525253,
            2.62626263,
            2.72727273,
            2.82828283,
            2.92929293,
            3.03030303,
            3.13131313,
            3.23232323,
            3.33333333,
            3.43434343,
            3.53535354,
            3.63636364,
            3.73737374,
            3.83838384,
            3.93939394,
            4.04040404,
            4.14141414,
            4.24242424,
            4.34343434,
            4.44444444,
            4.54545455,
            4.64646465,
            4.74747475,
            4.84848485,
            4.94949495,
            5.05050505,
        ]
    )

    Cp = np.array(
        [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.00248182,
            0.0273,
            0.05211818,
            0.07693636,
            0.10175455,
            0.12657273,
            0.15139091,
            0.17620909,
            0.20102727,
            0.22584545,
            0.25066364,
            0.27548182,
            0.3003,
            0.32511818,
            0.34993636,
            0.37475455,
            0.39957273,
            0.42439091,
            0.44920909,
            0.47402727,
            0.49884545,
            0.52366364,
            0.54848182,
            0.5733,
            0.59811818,
            0.62293636,
            0.64775455,
            0.67257273,
            0.69739091,
            0.72220909,
            0.74702727,
            0.77184545,
            0.79666364,
            0.82148182,
            0.8463,
            0.86,
            0.86,
            0.86,
            0.86,
            0.86,
            0.86,
        ]
    )

    Ct = 0.4 * np.ones((len(X)))
    Bidirection = False
    C_IO = np.array([1.0, 4.0])

    Type = "Tidal"
    lCS = np.array([0, 0, 30])
    Clen = (10,)
    YawAngle = 0.0 / 180 * np.pi  # Need to be clarified
    Float_flag = False
    InstalDepth = [-np.inf, 0]
    MinDist = (10,)
    OpThreshold = 0
    UserArray = {"Option": 1, "Value": "staggered"}
    RatedPowerDevice = 1 * 1e6
    RatedPowerArray = 20 * RatedPowerDevice

    Machine = WP2_MachineData(
        Type,
        lCS,
        Clen,
        YawAngle,
        Float_flag,
        InstalDepth,
        MinDist,
        OpThreshold,
        UserArray,
        RatedPowerArray,
        RatedPowerDevice,
        tidal_power_curve=Cp,
        tidal_thrust_curve=Ct,
        tidal_bidirectional=Bidirection,
        tidal_cutinout=C_IO,
        tidal_velocity_curve=X,
    )

    iWP2input = WP2input(Machine, Site)

    return iWP2input


def main(iWP2input, debug=False):
    WPobj = WP2(iWP2input, debug=debug)
    Out = WPobj.optimisationLoop()

    if not Out == -1:
        Out.printRes()
    else:
        raise RuntimeError("Error code -1")


if __name__ == "__main__":
    iWP2input = get_inputs()
    main(iWP2input)
