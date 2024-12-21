# -*- coding: utf-8 -*-

#    Copyright (C) 2020 National Technology & Engineering Solutions of Sandia
#    Copyright (C) 2017-2024 Mathew Topper
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
Created on Mon Sep 11 08:49:07 2017

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import logging
from typing import TypeAlias, cast

import numpy as np
import numpy.typing as npt
from contourpy import LineType, contour_generator
from scipy import optimize, stats
from scipy.special import gamma

PointArray: TypeAlias = npt.NDArray[np.float64]

# Set up logging
module_logger = logging.getLogger(__name__)


class UniVariateKDE:
    def __init__(self, data, bandwidth=0.3):
        self._kde = stats.gaussian_kde(data, bw_method=bandwidth)
        self._cdf = None
        self._ppf = None
        self._x0 = 0.0

    def pdf(self, values):
        return self._kde(values)

    def cdf(self, values):
        if self._cdf is None:
            self._cdf = self._calc_cdf()

        return self._cdf(values)

    def ppf(self, probabilities, x0=None):
        if self._ppf is None or self._x0 != x0:
            self._ppf = self._calc_ppf(x0)
            self._x0 = x0

        result = self._ppf(probabilities)

        if np.isnan(result).any():
            result = None

        return result

    def mean(self):
        return self._kde.dataset.mean()

    def median(self):
        return np.median(self._kde.dataset)

    def mode(self, samples=1000):
        """Numerically search for the mode"""

        x = np.linspace(
            self._kde.dataset.min(), self._kde.dataset.max(), samples
        )
        most_likely = x[np.argsort(self._kde(x))[-1]]

        return most_likely

    def confidence_interval(self, percent, x0=None):
        if self._ppf is None:
            self._ppf = self._calc_ppf(x0)

        x = percent / 100.0
        bottom = (1 - x) / 2
        top = (1 + x) / 2

        result = self._ppf([bottom, top])

        if np.isnan(result).any():
            result = None

        return result

    def _calc_cdf(self):
        def _kde_cdf(x):
            return self._kde.integrate_box_1d(-np.inf, x)

        kde_cdf = np.vectorize(_kde_cdf)

        return kde_cdf

    def _calc_ppf(self, x0=None):
        if self._cdf is None:
            self._cdf = self._calc_cdf()

        def _kde_ppf(q):
            def f(x, q):
                assert self._cdf is not None
                return self._cdf(x) - q

            x0_list = [
                self.mean(),
                0.0,
                self._kde.dataset.min(),
                self._kde.dataset.max(),
            ]

            if x0 is not None:
                x0_list = [x0] + x0_list

            for x0_local in x0_list:
                result = optimize.fsolve(
                    f,
                    x0_local,
                    args=(q,),
                    full_output=True,
                )

                if result[2] == 1:
                    return result[0][0]

            return np.nan

        kde_ppf = np.vectorize(_kde_ppf)

        return kde_ppf


class BiVariateKDE:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kernel = self._set_kernel()

    def _set_kernel(self):
        values = np.vstack([self.x, self.y])
        return stats.gaussian_kde(values)

    def mean(self):
        return self.x.mean(), self.y.mean()

    def median(self):
        return np.median(self.kernel.dataset, 1)

    def mode(self, xtol=0.0001, ftol=0.0001, disp=False):
        """Determine the ordinate of the most likely value of the given KDE"""

        median = self.median()
        modal_coords = optimize.fmin(
            lambda x: -1 * self.kernel(x),
            median,
            xtol=xtol,
            ftol=ftol,
            disp=disp,
        )

        return modal_coords

    def pdf(self, x_range=None, y_range=None, npoints=1000):
        # Wide estimate on the ranges if not given
        if x_range is None:
            dx = self.x.max() - self.x.min()
            x_range = (self.x.min() - dx, self.x.max() + dx)

        if y_range is None:
            dy = self.y.max() - self.y.min()
            y_range = (self.y.min() - dy, self.y.max() + dy)

        X, Y = np.mgrid[
            x_range[0] : x_range[1] : (npoints * 1j),
            y_range[0] : y_range[1] : (npoints * 1j),
        ]
        positions = np.vstack([X.ravel(), Y.ravel()])

        xx = X[:, 0]
        yy = Y[0, :]
        pdf = np.reshape(self.kernel(positions).T, X.shape)

        return xx, yy, pdf


def pdf_confidence_densities(pdf, levels=None):
    """Determine the required density values to satisfy a list of confidence
    levels in the given pdf"""

    def diff_frac(density, pdf, target_frac, pdf_sum):
        density_frac = pdf[pdf >= density].sum() / pdf_sum
        return density_frac - target_frac

    if levels is None:
        levels = np.array([95.0])
    else:
        levels = np.array(levels)

    fracs = levels / 100.0
    pdf_sum = pdf.sum()
    densities = []

    for frac in fracs:
        local_pdf = np.copy(pdf)

        try:
            density = optimize.brentq(
                diff_frac, pdf.min(), pdf.max(), args=(local_pdf, frac, pdf_sum)
            )

            densities.append(density)
        except ValueError as e:
            module_logger.debug(e, exc_info=True)

    return densities


def pdf_contour_coords(xx, yy, pdf, level):
    cont_gen = contour_generator(xx, yy, pdf.T, line_type=LineType.Separate)
    lines = cast(list[PointArray], cont_gen.lines(level))

    cx = []
    cy = []

    for v in lines:
        cx.extend(v[:, 0])
        cy.extend(v[:, 1])

    return cx, cy


def get_standard_error(values):
    """
    Calculates the standard error of the mean of a given function.

    This function can either be used to reduce the standard error to
    a certain level or calculate the standard error given a fixed number
    of samples.

    Args:
      values

    Returns: the standard error metric vector
    """

    def get_c4(n):
        # Correction for unbiased estimate of the standard deviation.
        # https://en.wikipedia.org/wiki/Unbiased_estimation_of_standard_deviation
        b_bottom = gamma((n - 1) / 2.0)

        if np.isinf(b_bottom):
            return np.inf

        a = np.sqrt(2.0 / (n - 1))
        b_top = gamma(n / 2.0)
        return a * b_top / b_bottom

    n = len(values)

    if n < 2:
        return None

    c4 = get_c4(n)

    if not np.isfinite(c4):
        c4 = 1

    result_error = c4 * np.std(values) / np.sqrt(n)

    return result_error
