# -*- coding: utf-8 -*-

#    Copyright (c) 2014 Inria
#    Copyright (C) 2021-2024 Mathew Topper
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

#  Author: Nikolaus Hansen, 2008-
#  Author: Petr Baudis, 2014
#  Author: Youhei Akimoto, 2016-

# pylint: disable=line-too-long

from collections import deque

import numpy as np
from cma.utilities.math import Mh


class MovingAverage:
    def __init__(self, window_length, init=None):
        if init is None:
            init = []

        self._length = window_length
        self._data = deque(init, window_length)
        self._predict = None

        return

    def add(self, new_data=None):
        if new_data is not None:
            self._data.append(new_data)

        if len(self._data) < self._length:
            result = None
        else:
            result = sum(self._data) / float(self._length)

        self._predict = result

        return

    def __call__(self):
        return self._predict


class NoiseHandler:
    """Noise handling according to [Hansen et al 2009, A Method for
    Handling Uncertainty in Evolutionary Optimization...]
    The interface of this class is yet versatile and subject to changes.
    The noise handling follows closely [Hansen et al 2009] in the
    measurement part, but the implemented treatment is slightly
    different: for ``noiseS > 0``, ``evaluations`` (time) and sigma are
    increased by ``alpha``. For ``noiseS < 0``, ``evaluations`` (time)
    is decreased by ``alpha**(1/4)``.
    The (second) parameter ``evaluations`` defines the maximal number
    of evaluations for a single fitness computation. If it is a list,
    the smallest element defines the minimal number and if the list has
    three elements, the median value is the start value for
    ``evaluations``.
    `NoiseHandler` serves to control the noise via steps-size
    increase and number of re-evaluations, for example via `fmin` or
    with `ask_and_eval`.
    Examples
    --------
    Minimal example together with `fmin` on a non-noisy function:
    >>> import cma
    >>> res = cma.fmin(cma.ff.elli, 7 * [1], 1, noise_handler=cma.NoiseHandler(7))  #doctest: +ELLIPSIS
    (4_w,9)-aCMA-ES (mu_w=2.8,...
    >>> assert res[1] < 1e-8
    >>> res = cma.fmin(cma.ff.elli, 6 * [1], 1, {'AdaptSigma':cma.sigma_adaptation.CMAAdaptSigmaTPA},
    ...          noise_handler=cma.NoiseHandler(6))  #doctest: +ELLIPSIS
    (4_w,...
    >>> assert res[1] < 1e-8
    in dimension 7 (which needs to be given tice). More verbose example
    in the optimization loop with a noisy function defined in ``func``:
    >>> import cma, numpy as np
    >>> func = lambda x: cma.ff.sphere(x) * (1 + 4 * np.random.randn() / len(x))  # cma.ff.noisysphere
    >>> es = cma.CMAEvolutionStrategy(np.ones(10), 1)  #doctest: +ELLIPSIS
    (5_w,10)-aCMA-ES (mu_w=3.2,...
    >>> nh = cma.NoiseHandler(es.N, maxevals=[1, 1, 30])
    >>> while not es.stop():
    ...     X, fit_vals = es.ask_and_eval(func, evaluations=nh.evaluations)
    ...     es.tell(X, fit_vals)  # prepare for next iteration
    ...     es.sigma *= nh(X, fit_vals, func, es.ask)  # see method __call__
    ...     es.countevals += nh.evaluations_just_done  # this is a hack, not important though
    ...     es.logger.add(more_data = [nh.evaluations, nh.noiseS])  # add a data point
    ...     es.disp()
    ...     # nh.maxevals = ...  it might be useful to start with smaller values and then increase
    ...                # doctest: +ELLIPSIS
    Iterat...
    >>> print(es.stop())
    ...                # doctest: +ELLIPSIS
    {...
    >>> print(es.result[-2])  # take mean value, the best solution is totally off
    ...                # doctest: +ELLIPSIS
    [...
    >>> assert sum(es.result[-2]**2) < 1e-9
    >>> print(X[np.argmin(fit_vals)])  # not bad, but probably worse than the mean
    ...                # doctest: +ELLIPSIS
    [...
    >>> # es.logger.plot()
    The command ``logger.plot()`` will plot the logged data.
    The noise options of fmin` control a `NoiseHandler` instance
    similar to this example. The command ``cma.CMAOptions('noise')``
    lists in effect the parameters of `__init__` apart from
    ``aggregate``.
    Details
    -------
    The parameters reevals, theta, c_s, and alpha_t are set differently
    than in the original publication, see method `__init__`. For a
    very small population size, say popsize <= 5, the measurement
    technique based on rank changes is likely to fail.
    Missing Features
    ----------------
    In case no noise is found, ``self.lam_reeval`` should be adaptive
    and get at least as low as 1 (however the possible savings from this
    are rather limited). Another option might be to decide during the
    first call by a quantitative analysis of fitness values whether
    ``lam_reeval`` is set to zero. More generally, an automatic noise
    mode detection might also set the covariance matrix learning rates
    to smaller values.
    :See also: `fmin`, `CMAEvolutionStrategy.ask_and_eval`
    """

    # TODO: for const additive noise a better version might be with alphasigma
    # also used for sigma-increment, while all other variance changing sources
    # are removed (because they are intrinsically biased). Then using kappa to
    # get convergence (with unit sphere samples): noiseS=0 leads to a certain
    # kappa increasing rate?
    def __init__(self, N, maxevals=None, reevals=None, epsilon=1e-7):
        """Parameters are:
        ``N``
            dimension, (only) necessary to adjust the internal
            "alpha"-parameters
        ``maxevals``
            maximal value for ``self.evaluations``, where
            ``self.evaluations`` function calls are aggregated for
            noise treatment. With ``maxevals == 0`` the noise
            handler is (temporarily) "switched off". If `maxevals`
            is a list, min value and (for >2 elements) median are
            used to define minimal and initial value of
            ``self.evaluations``. Choosing ``maxevals > 1`` is only
            reasonable, if also the original ``fit`` values (that
            are passed to `__call__`) are computed by aggregation of
            ``self.evaluations`` values (otherwise the values are
            not comparable), as it is done within `fmin`.
        ``reevals``
            number of solutions to be reevaluated for noise
            measurement, can be a float, by default set to ``2 +
            popsize/20``, where ``popsize = len(fit)`` in
            ``__call__``. zero switches noise handling off.
        ``epsilon``
            multiplier for perturbation of the reevaluated solutions
        :See also: `fmin`, `CMAOptions`, `CMAEvolutionStrategy.ask_and_eval`
        """

        if maxevals is None:
            maxevals = [1, 1, 1]

        self.lam_reeval = reevals  # 2 + popsize/20, see method indices(), originally 2 + popsize/10
        self.epsilon = epsilon
        ## meta_parameters.noise_theta == 0.5
        self.theta = 0.5  # 0.5  # originally 0.2
        self.cum = 0.3  # originally 1, 0.3 allows one disagreement of current point with resulting noiseS
        ## meta_parameters.noise_alphasigma == 2.0
        self.alphasigma = 1 + 1.0 / (
            N + 10
        )  # 2, unit sphere sampling: 1 + 1 / (N + 10)
        ## meta_parameters.noise_alphaevals == 2.0
        self.alphaevals = 1 + 2.0 / (N + 10)  # 2, originally 1.5
        ## meta_parameters.noise_alphaevalsdown_exponent == -0.25
        self.alphaevalsdown = self.alphaevals**-0.25  # originally 1/1.5
        # zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
        if 11 < 3 and maxevals[2] > 1e18:  # for testing purpose
            self.alphaevals = 1.5
            self.alphaevalsdown = self.alphaevals**-0.999  # originally 1/1.5

        self.evaluations = 1
        """number of f-evaluations to get a single measurement by aggregation"""
        self.minevals = 1
        self.maxevals = int(np.max(maxevals))
        if hasattr(maxevals, "__contains__"):  # i.e. can deal with ``in``
            if len(maxevals) > 1:
                self.minevals = min(maxevals)
                self.evaluations = self.minevals
            if len(maxevals) > 2:
                self.evaluations = np.median(maxevals)
        self.n_evals = max(int(self.evaluations), 1)
        self.last_n_evals = None
        ## meta_parameters.noise_aggregate == None
        self.evaluations_just_done = (
            0  # actually conducted evals, only for documentation
        )
        self.noiseS = 0
        self.idx = None
        self.popsize = None
        self.fit = None
        self.fitre = None
        self._X = None
        self._sols = None
        self._sigma_fac = 1.0
        self._noise_predict = MovingAverage(3)

        return

    @property
    def sigma_fac(self):
        return self._sigma_fac

    def get_predicted_noise(self):
        result = self._noise_predict()
        if result is None:
            result = 0.0

        return result

    def prepare(self, X, fit):
        """Prepare noise measurement.
        Parameters
        ----------
        ``X``
            a list/sequence/vector of solutions
        ``fit``
            the respective list of function values
        Details
        -------
        Calls the methods `reeval`, `update_measure` and ``treat` in
        this order. ``self.evaluations`` is adapted within the method
        `treat`.
        """

        self.last_n_evals = self.n_evals
        self.n_evals = int(self.evaluations)
        self.evaluations_just_done = 0
        self._sols = None

        if not self.maxevals or self.lam_reeval == 0:
            return

        self.idx = self._indices(list(fit))
        self.popsize = len(self.idx)

        if self.idx.size == 0:
            return

        self.fit = list(fit)
        self.fitre = list(fit)
        self._X = X

        return

    def ask(self, ask=None):
        """Give solutions for noise measurement.
        Parameters
        ----------
        ``ask``
            a method to generate a new, slightly disturbed solution. The
            argument is (only) mandatory if ``epsilon`` is not zero, see
            `__init__`.
        """

        if self._X is None or self.idx is None:
            raise RuntimeError("Call prepare first")

        if self.epsilon:
            if ask is None:
                raise ValueError("ask must be defined if epsilon is not zero")
            sols = [ask(1, self._X[i], self.epsilon)[0] for i in self.idx]
        else:
            sols = [self._X[i] for i in self.idx]

        # Store a copy of the solutions for checking in tell
        self._sols = sols[:]

        return sols

    def tell(self, sols, function_values):
        """Get function values for noise measurement, set anew attributes ``evaluations``
        (proposed number of evaluations to "treat" noise) and ``evaluations_just_done``
        and return a factor for increasing sigma.
        """

        if self.idx is None or self.fitre is None:
            raise RuntimeError("Call prepare first")

        def get_sol_match(i, test_sol):
            if self._sols is None:
                raise RuntimeError("Call ask first")

            for j, sol in enumerate(self._sols):
                if np.isclose(test_sol, sol).all():
                    return j, function_values[i]

            test_sol_strs = [str(x) for x in test_sol]
            test_sol_str = ", ".join(test_sol_strs)
            err_msg = "Solution {} was not asked for".format(test_sol_str)
            raise RuntimeError(err_msg)

        # Case where prepare has not been called
        if None in [self.fit, self.fitre]:
            return

        # Case where ask has not been called
        if self._sols is None:
            return

        # No return values given (probably due to constraint violation)
        if not sols or not function_values:
            self.fit = None
            self.fitre = None
            self._sigma_fac = 1.0

            return

        # Check the given solutions and sort the function values
        n_sols = len(self._sols)

        if len(sols) != n_sols or len(function_values) != n_sols:
            err_msg = (
                "Exactly {} solutions and function values must be " "provided"
            ).format(n_sols)
            raise ValueError(err_msg)

        f_sorted = np.zeros(n_sols)

        for i, test_sol in enumerate(sols):
            j, f = get_sol_match(i, test_sol)
            f_sorted[j] = f

        real_evals = 0

        for j, i in enumerate(self.idx):
            if np.isnan(f_sorted[j]):
                continue
            self.fitre[i] = f_sorted[j]
            real_evals += 1

        self._update_measure()
        self.evaluations_just_done = real_evals
        self._sigma_fac = self._treat()
        self._sols = None

        return

    def _indices(self, fit):
        """return the set of indices to be reevaluated for noise
        measurement.
        Given the first values are the earliest, this is a useful policy
        also with a time changing objective.
        """
        ## meta_parameters.noise_reeval_multiplier == 1.0
        lam_reev = 1.0 * (
            self.lam_reeval if self.lam_reeval else 2 + len(fit) / 20.0
        )
        lam_reev = int(lam_reev) + ((lam_reev % 1) > np.random.rand())
        ## meta_parameters.noise_choose_reeval == 1
        choice = 1
        if choice == 1:
            # take n_first first and reev - n_first best of the remaining
            n_first = lam_reev - lam_reev // 2
            sort_idx = np.argsort(np.array(fit, copy=False)[n_first:]) + n_first
            return np.array(
                list(range(0, n_first))
                + list(sort_idx[0 : lam_reev - n_first]),
                copy=False,
            )
        elif choice == 2:
            idx_sorted = np.argsort(np.array(fit, copy=False))
            # take lam_reev equally spaced, starting with best
            linsp = np.linspace(0, len(fit) - len(fit) / lam_reev, lam_reev)
            return idx_sorted[[int(i) for i in linsp]]
        # take the ``lam_reeval`` best from the first ``2 * lam_reeval + 2`` values.
        elif choice == 3:
            return np.argsort(np.array(fit, copy=False)[: 2 * (lam_reev + 1)])[
                :lam_reev
            ]
        else:
            raise ValueError(
                "unrecognized choice value %d for noise reev" % choice
            )

    def _update_measure(self):
        """updated noise level measure using two fitness lists ``self.fit`` and
        ``self.fitre``, return ``self.noiseS, all_individual_measures``.
        Assumes that ``self.idx`` contains the indices where the fitness
        lists differ.
        """

        if self.fit is None or self.fitre is None or self.idx is None:
            raise RuntimeError("Call prepare first")

        lam = len(self.fit)
        idx = np.argsort(self.fit + self.fitre)
        ranks = np.argsort(idx).reshape((2, lam))
        rankDelta = ranks[0] - ranks[1] - np.sign(ranks[0] - ranks[1])

        # compute rank change limits using both ranks[0] and ranks[1]
        r = np.arange(1, 2 * lam)  # 2 * lam - 2 elements

        limits = []

        for i in self.idx:
            first = Mh.prctile(
                np.abs(r - (ranks[0, i] + 1 - (ranks[0, i] > ranks[1, i]))),
                self.theta * 50,
            )
            second = Mh.prctile(
                np.abs(r - (ranks[1, i] + 1 - (ranks[1, i] > ranks[0, i]))),
                self.theta * 50,
            )
            assert isinstance(first, float)
            assert isinstance(second, float)

            limit = 0.5 * (first + second)
            limits.append(limit)

        # compute measurement
        # max: 1 rankchange in 2*lambda is always fine
        s = np.abs(rankDelta[self.idx]) - Mh.amax(
            limits, 1
        )  # lives roughly in 0..2*lambda
        self.noiseS += self.cum * (np.mean(s) - self.noiseS)
        self._noise_predict.add(self.noiseS)

        self.fit = None
        self.fitre = None

        return self.noiseS, s

    def _treat(self):
        """adapt self.evaluations depending on the current measurement
        value and return ``sigma_fac in (1.0, self.alphasigma)``
        """

        # Use noise prediction
        predicted_noise = self._noise_predict()

        if predicted_noise is None:
            return 1.0

        if predicted_noise > 0:
            self.evaluations = min(
                (self.evaluations * self.alphaevals, self.maxevals)
            )

            if self.evaluations == self.maxevals:
                sigma_fac = 1.0
            else:
                sigma_fac = self.alphasigma

        else:
            self.evaluations = max(
                (self.evaluations * self.alphaevalsdown, self.minevals)
            )
            sigma_fac = 1.0

        return sigma_fac
