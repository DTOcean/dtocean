import warnings
from typing import Optional, Sequence

import numpy as np
import numpy.typing as npt
import pandas as pd


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
    wave_df["cuts"] = thCut[:]  # thCut.labels
    dataGr = wave_df.groupby("cuts")

    scatter = np.zeros((nH + 1, nT + 1, nDir))
    binns = [Hbin, Tbin]

    for ind, data2d in enumerate(dataGr):
        if data2d[1].empty:
            counts = 0
        else:
            D2d = np.array(zip(data2d[1]["Hm0"], data2d[1]["Te"]))
            (counts, xedges, yedges) = np.histogram2d(
                D2d[:, 0],
                D2d[:, 1],
                bins=binns,  # type: ignore
            )  # type: ignore

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


def dump_IEC(
    Te: Sequence[float],
    Hm0: Sequence[float],
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
