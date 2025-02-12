# -*- coding: utf-8 -*-
"""
Example wave case with optimised device layout
"""

from pathlib import Path

import numpy as np

from dtocean_hydro import start_logging
from dtocean_hydro.input import WP2_MachineData, WP2_SiteData, WP2input
from dtocean_hydro.main import WP2

THIS_DIR = Path(__file__).parent

# Start the logging system
start_logging()


def get_inputs():
    # Lease Area
    leaseAreaVertexUTM = np.array(
        [[0, 0], [200.0, 0], [200.0, 200.0], [0, 200.0]], dtype=float
    )
    Nogoareas_wave = []

    # Statistical analysis generation
    B = np.array([180], "f") / 180 * np.pi
    H = np.linspace(1, 9, 9, endpoint=True)
    T = np.linspace(1, 14, 14, endpoint=True)
    p = 1 / len(B) / len(H) / len(T) * np.ones((len(T), len(H), len(B)))

    SSH = 0.0
    specType = ("Jonswap", 3.3, 0)

    Meteocean_wave = {
        "Te": T,
        "Hs": H,
        "B": B,
        "p": p,
        "specType": specType,
        "SSH": SSH,
    }
    MainDirection = None

    x = np.linspace(0.0, 200.0, 50, endpoint=True)
    y = np.linspace(0.0, 200.0, 50, endpoint=True)

    X, Y = np.meshgrid(x, y)
    Z = -X * 0 - 70.0
    xyz = np.vstack((X.ravel(), Y.ravel(), Z.ravel())).T
    Bathymetry = xyz

    BR = np.empty(0)
    electrical_connection_point = (-1000.0, -4000.0)

    Site = WP2_SiteData(
        leaseAreaVertexUTM,
        Nogoareas_wave,
        Meteocean_wave,
        None,
        None,
        MainDirection,
        Bathymetry,
        BR,
        electrical_connection_point,
        boundary_padding=10.0,
    )

    # Machine data
    Type = "Wave"
    lCS = np.array([0, 0.0, 0.0])
    Clen = (1,)
    YawAngle = 0.0 / 180 * np.pi

    Float_flag = True
    InstalDepth = [-np.inf, 0]
    MinDist = (60,)
    OpThreshold = 0.8

    # The input folder defined the place were the software will search for
    # the wave device solution file
    wave_data_path = THIS_DIR / "inputs_wave"

    UserArray = {"Option": 1, "Value": "staggered"}
    RatedPowerDevice = 5 * 1e5
    RatedPowerArray = 10 * RatedPowerDevice

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
        wave_data_folder=str(wave_data_path),
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
