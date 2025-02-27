# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Mathew Topper, Francesco Ferri, Rui Duarte
#    Copyright (C) 2017-2025 Mathew Topper
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

import argparse
import cmath
import math
import os
import warnings
from decimal import Decimal
from typing import Optional, Sequence

import numpy as np
import numpy.typing as npt
import pandas as pd
from scipy.integrate import simpson
from scipy.interpolate import interp1d

from .tidestats import make_tide_statistics as make_tide_statistics


def make_wave_statistics(
    wave_data: Sequence[tuple[float, float, float]],
    period_bin_size: float = 1.0,
    wave_height_bin_size: float = 0.5,
    direction_bin_size: float = 45,
):
    """Generate probability bins according to IEC DTS 62600-101"""

    dT = period_bin_size
    dH = wave_height_bin_size
    dD = direction_bin_size

    if dT > 1 or dH > 0.5 or dD > 45:
        warnStr = (
            "The given discretisation is larger then the"
            "suggested by the IEC standard"
        )
        warnings.warn(warnStr)

    # Calculate the number of bins in the direction space and fix bin size
    nDir = int(360.0 / dD)
    dD = 360.0 / nDir

    wave_array = np.array(wave_data)
    wave_array = wave_array[~np.isnan(wave_array).any(axis=1)]

    rad = 180.0 / np.pi
    direcs = (wave_array[:, 2]) / rad

    Hm0_max = max(wave_array[:, 0])
    Te_max = max(wave_array[:, 1])
    nT = int(Te_max / dT)
    nH = int(Hm0_max / dH)

    # nT and nH are increased by two in order to have a full coverage of the
    # space.
    Tbin = np.array(range(nT + 2), dtype=float) * dT
    Hbin = np.array(range(nH + 2), dtype=float) * dH

    # discretisation in the angular dimension in degrees
    Dbin = list(
        (np.array(range(nDir + 1), dtype=float) / nDir * 360.0 - (dD / 2.0))
        / rad
    )
    direcs[direcs > Dbin[-1]] -= 2 * np.pi
    thCut = pd.cut(direcs, Dbin, precision=6, include_lowest=True)

    wave_df = pd.DataFrame(wave_array, columns=["Hm0", "Te", "Dir"])
    wave_df["cuts"] = thCut[:]
    dataGr = wave_df.groupby("cuts", observed=False)

    scatter = np.zeros((nH + 1, nT + 1, nDir))
    binns = [Hbin, Tbin]

    for ind, data2d in enumerate(dataGr):
        if data2d[1].empty:
            counts = 0
        else:
            D2d = np.array(list(zip(data2d[1]["Hm0"], data2d[1]["Te"])))
            (counts, xedges, yedges) = np.histogram2d(  # type: ignore
                D2d[:, 0],
                D2d[:, 1],
                bins=binns,  # type: ignore
            )

        scatter[:, :, ind] = counts

    scatter_norm = scatter / len(wave_array)

    Hm0_centred = yedges[:-1] + dH / 2.0
    Te_centred = xedges[:-1] + dT / 2.0
    Dir_centred = np.array(Dbin[0:-1], dtype=float) * rad + (dD / 2.0)

    result = {
        "Dir": Dir_centred,
        "Hm0": Hm0_centred,
        "Te": Te_centred,
        "p": scatter_norm,
    }

    return result


def dump_wave_statistics(
    Hm0: Sequence[float],
    Te: Sequence[float],
    Dir: Sequence[float],
    p: npt.NDArray[np.float64],
    save_path: str = "performance_fit_scatter_diagram.csv",
    name: Optional[str] = None,
):
    if name is None:
        name = ""

    nH = len(Hm0)
    nDir = len(Dir)

    with open(save_path, "w") as fid:
        fid.write("Meteocean Condition\n")
        fid.write(name + "\n")
        fid.write("\n")

        fid.write("Te range [s]\n")
        fid.write(",".join([str(x) for x in Te]) + "\n")

        fid.write("Hm0 range [m]\n")
        fid.write(",".join([str(x) for x in Hm0]) + "\n")

        fid.write("Dir range [degrees]\n")
        fid.write(",".join([str(x) for x in Dir]) + "\n")

        fid.write(
            "Probability of occurrence [h/h_year], Te-columns and Hm0-rows\n"
        )
        for di_in in range(nDir):
            fid.write("Angle,{}\n".format(Dir[di_in]))
            for h_in in range(nH):
                fid.write(",".join([str(x) for x in p[h_in, :, di_in]]) + "\n")


def Tp_to_Te(
    wave_data: Sequence[tuple[float, float]],
    gamma: float = 3.3,
    drop_nan: bool = True,
):
    wave_array = np.array(wave_data)

    if drop_nan:
        wave_array = wave_array[~np.isnan(wave_array).any(axis=1)]

    t_Te = []

    for row in wave_data:
        t_S, t_w = make_JONSWAP(*row, gamma)
        new_spectrum = make_spectra_analysis(t_S, t_w)
        t_Te.append(new_spectrum["Tm_10"])

    wave_array[:, 1] = t_Te

    if drop_nan:
        wave_array = wave_array[~np.isnan(wave_array).any(axis=1)]

    return wave_array


def make_JONSWAP(
    Hm0: float,
    Tp: float,
    gamma: float = 3.3,
    w: Optional[npt.ArrayLike] = None,
    wc: Optional[float] = None,
):
    if wc is None:
        wc = 33.0 / Tp

    if w is None:
        w = np.linspace(0, wc, 257)
        assert isinstance(w, np.ndarray)
    else:
        w = np.array(w)

    g = 9.8063
    sa = 0.07
    sb = 0.09
    wp = 2.0 * np.pi / Tp

    # if sa and sb are different from 0.07 and 0.09 the scaling factor A
    # needs to be evaluated as:
    # >>A=(Hm0/g)**2/16/simpson(S,w)
    A = 5.061 * Hm0**2 / Tp**4 * (1 - 0.287 * np.log(gamma))

    s = sb * np.ones(len(w))
    s[w < wp] = sa

    S = (
        A
        * g**2
        / w**5
        * np.exp(-5.0 / 4.0 * (wp / w) ** 4)
        * gamma ** np.exp(-0.5 * ((w / wp - 1.0) / s) ** 2)
    )
    S[0] = 0

    return S, w


def make_spectra_analysis(S, w):
    g = 9.8063
    f = w / 2.0 / np.pi

    m0 = simpson(S * (f) ** 0, w)
    m1 = simpson(S * (f) ** 1, w)
    m2 = simpson(S * (f) ** 2, w)
    m3 = simpson(S * (f) ** 3, w)
    m4 = simpson(S * (f) ** 4, w)

    m_1 = simpson(S[f > 0] / f[f > 0], w[f > 0])  # = m_1

    Hm0 = 4.0 * np.sqrt(m0)
    Tm01 = m0 / m1
    Tm02 = np.sqrt(m0 / m2)
    Tm24 = np.sqrt(m2 / m4)
    Tm_10 = m_1 / m0

    Tm12 = m1 / m2

    Tp = 1.0 / f[S.argmax()]  # peak period /length
    Ss = 2.0 * np.pi * Hm0 / g / Tm02**2  # Significant wave steepness
    Sp = 2.0 * np.pi * Hm0 / g / Tp**2  # Average wave steepness
    Ka = abs(simpson(S * np.exp(1j * w * Tm02), w)) / m0  # groupiness factor

    # Quality control parameter
    # critical value is approximately 0.02 for surface displacement records
    # If Rs>0.02 then there are something wrong with the lower frequency part
    # of S.
    smooth = interp1d(f, S)

    Rs = (
        sum(
            smooth(
                [
                    0.0146 * 2.0 * np.pi,
                    0.0195 * 2.0 * np.pi,
                    0.0244 * 2.0 * np.pi,
                ]
            )
        )
        / 3.0
        / max(S)
    )

    # Second estimation of Tp
    Tp2 = 2.0 * np.pi * simpson(S**4, w) / simpson(w * S**4, w)

    alpha1 = Tm24 / Tm02  # m(3)/sqrt(m(1)*m(5))
    eps2 = np.sqrt(Tm01 / Tm12 - 1)  # sqrt(m(1)*m(3)/m(2)^2-1)
    eps4 = np.sqrt(1 - alpha1**2)  # sqrt(1-m(3)^2/m(1)/m(5))
    Qp = 2.0 / m0**2 * simpson(w * S**2, w)

    dic = {
        "m0": m0,
        "m1": m1,
        "m2": m2,
        "m3": m3,
        "m4": m4,
        "m_1": m_1,
        "Hm0": Hm0,
        "Tm01": Tm01,
        "Tm02": Tm02,
        "Tm24": Tm24,
        "Tm_10": Tm_10,
        "Tm12": Tm12,
        "Tp": Tp,
        "Ss": Ss,
        "Sp": Sp,
        "Ka": Ka,
        "Rs": Rs,
        "Tp2": Tp2,
        "alpha1": alpha1,
        "eps2": eps2,
        "eps4": eps4,
        "Qp": Qp,
    }

    return dic


def check_bin_widths(rated_power, bin_width):
    if bin_width is None:
        bin_width = 0.1

    # Check whether the bin width divides the RP perfectly
    if Decimal(str(rated_power)) % Decimal(str(bin_width)) != 0:
        errStr = (
            "Power histogram bin width '{}' does not divide the rated "
            "power perfectly"
        ).format(bin_width)
        raise ValueError(errStr)

    return


def make_power_histograms(
    device_power_pmfs: dict[str, npt.NDArray],
    rated_power: float,
    bin_width: Optional[float] = None,
):
    """This function converts the hydrodynamics output into the array power
    output histogram required for Electrical analysis.

    """

    if bin_width is None:
        bin_width = 0.1

    # Check whether the bin width devides the RP perfectly
    check_bin_widths(rated_power, bin_width)

    # Set the power bins to include the maximum power
    power_bins = np.arange(0, rated_power + bin_width, bin_width)

    # Adjust values that exceed the bin values
    device_hists = {}

    for dev_id, dev_power_pmf in device_power_pmfs.items():
        # Change outlying values to the rated power
        outlier_indices = dev_power_pmf[:, 0] > rated_power
        dev_power_pmf[outlier_indices, 0] = rated_power

        hist, final_bins = np.histogram(dev_power_pmf[:, 0], bins=power_bins)

        sort_pow_idx = dev_power_pmf[:, 0].argsort()
        output_occurrence = sum_bins(hist, dev_power_pmf[sort_pow_idx, 1])
        bin_widths = [j - i for i, j in zip(power_bins[:-1], power_bins[1:])]
        device_hists[dev_id] = (
            output_occurrence / np.array(bin_widths),
            final_bins,
        )

    return device_hists


def sum_bins(bins, data):
    """

    args:
        bins (array): number of items in each bin.
        data (array): data to be counted.


    returns:
        bin_sums

    """

    start = 0
    bin_sums = []
    for items in bins:
        end = start + items
        bin_sums.append(data[start:end].sum())
        start = end

    return np.array(bin_sums)


def bearing_to_radians(bearing):
    angle = 90.0 - bearing
    if angle <= -180.0:
        angle += 360.0

    angle = math.radians(angle)

    if angle < 0:
        angle += 2 * math.pi

    return angle


def bearing_to_vector(bearing, distance=1.0):
    angle = bearing_to_radians(bearing)

    start = complex(0.0, 0.0)
    movement = cmath.rect(distance, angle)
    end = start + movement

    endx = round(end.real, 10)
    endy = round(end.imag, 10)

    return endx, endy


def radians_to_bearing(x):
    initial_bearing = 90 - math.degrees(x)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def vector_to_bearing(x, y):
    initial_bearing = math.atan2(y, x)
    compass_bearing = radians_to_bearing(initial_bearing)

    return compass_bearing


def add_Te_interface():
    """Command line interface for add_Te.

    Example:

        To get help::

            $ add-Te -h

    """

    desStr = "Add Te time series to wave data containing Hm0 and Tp."
    parser = argparse.ArgumentParser(description=desStr)

    parser.add_argument(
        "path",
        help=(
            "path to file containing wave height and peak "
            "period time series (excel or csv)"
        ),
        type=str,
    )

    parser.add_argument(
        "-g",
        "--gamma",
        help=("JONSWAP spectrum gamma parameter"),
        type=float,
        default=3.3,
    )

    args = parser.parse_args()

    file_path = args.path
    gamma = args.gamma

    # Build a data frame from the given file
    _, ext = os.path.splitext(file_path)

    if ext == ".csv":
        wave_df = pd.read_csv(file_path)

    elif ".xls" in ext:
        wave_df = pd.read_excel(file_path)

    else:
        errStr = "File must be either CSV or MS Excel format"
        raise ValueError(errStr)

    with_Te = Tp_to_Te(wave_df["Hm0", "Tp"].to_list(), gamma)
    wave_df["Te"] = with_Te[:, 1]

    if ext == ".csv":
        wave_df.to_csv(file_path, index=False)

    elif ".xls" in ext:
        wave_df.to_excel(file_path, index=False)

    return
