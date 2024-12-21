# -*- coding: utf-8 -*-

import numpy as np
import pytest
from scipy.stats import norm

from dtocean_core.utils.stats import (
    BiVariateKDE,
    UniVariateKDE,
    get_standard_error,
    pdf_confidence_densities,
    pdf_contour_coords,
)

SLACK = 85


@pytest.fixture(scope="module")
def gaussian():
    """Build an estimate of a gaussian distribution. Object is shared"""

    data = np.random.normal(size=10000)
    distribution = UniVariateKDE(data)

    return distribution


@pytest.fixture
def gaussian_fresh():
    """Build an estimate of a gaussian distribution. Object is recreated"""

    data = np.random.normal(size=10000)
    distribution = UniVariateKDE(data)

    return distribution


@pytest.fixture(scope="module")
def bigaussian():
    """Build an estimate of a bivariate gaussian distribution.
    Object is shared"""

    mean = [0, 0]
    cov = [[1, 0], [0, 1]]  # diagonal covariance

    x, y = np.random.multivariate_normal(mean, cov, int(1e6)).T
    distribution = BiVariateKDE(x, y)

    return distribution


@pytest.fixture(scope="module")
def bigaussian_pdf(bigaussian):
    xx, yy, pdf = bigaussian.pdf(npoints=10)

    result = {"xx": xx, "yy": yy, "pdf": pdf}

    return result


def test_UniVariateKDE_pdf(gaussian):
    values = np.linspace(-5, 5, 200)
    estimated = gaussian.pdf(values)
    ideal = norm.pdf(values)

    assert np.isclose(estimated, ideal, rtol=0, atol=5e-02).all()


def test_UniVariateKDE_cdf(gaussian):
    values = np.linspace(-5, 5, 200)
    estimated = gaussian.cdf(values)
    ideal = norm.cdf(values)

    assert np.isclose(estimated, ideal, rtol=0, atol=5e-02).all()


def test_UniVariateKDE_ppf(gaussian):
    probs = np.linspace(0.01, 0.99, 200)
    estimated = gaussian.ppf(probs)
    ideal = norm.ppf(probs)

    assert np.isclose(estimated, ideal, rtol=0, atol=2e-1).all()


def test_UniVariateKDE_ppf_nan(mocker, gaussian):
    mocker.patch(
        "dtocean_core.utils.stats.optimize.fsolve",
        return_value=[0, 0, 0],
        autospec=True,
    )

    probs = np.linspace(0.01, 0.99, 200)
    estimated = gaussian.ppf(probs)

    assert estimated is None


def test_UniVariateKDE_mean():
    """Trival function calculates mean of initial dataset not distribution"""

    def get_vals():
        results = []
        for _ in range(30):
            data = np.random.normal(size=50)
            distribution = UniVariateKDE(data)
            results.append(distribution.mean())
        return results

    expected = 0
    confidence = 3.291  # 99.9% interval

    n_tests = 20
    tests = []

    for _ in range(n_tests):
        values = get_vals()
        std_error = get_standard_error(values)
        assert std_error is not None

        # Check that the expected value is within interval
        actual = np.array(values).mean()
        test = (actual - confidence * std_error < expected) and (
            expected < actual + confidence * std_error
        )
        tests.append(int(test))

    tpct = sum(tests) * 100.0 / n_tests

    # Add some slack!
    assert tpct >= SLACK


def test_UniVariateKDE_median():
    """Trival function calculates median of initial dataset not distribution"""

    def get_vals():
        results = []
        for _ in range(30):
            data = np.random.normal(size=50)
            distribution = UniVariateKDE(data)
            results.append(distribution.median())
        return results

    expected = 0
    confidence = 3.291  # 99.9% interval

    n_tests = 20
    tests = []

    for _ in range(n_tests):
        values = get_vals()
        std_error = get_standard_error(values)
        assert std_error is not None

        # Check that the expected value is within interval
        actual = np.median(values)
        test = (actual - confidence * std_error < expected) and (
            expected < actual + confidence * std_error
        )
        tests.append(int(test))

    tpct = sum(tests) * 100.0 / n_tests

    # Add some slack!
    assert tpct >= SLACK


def test_UniVariateKDE_mode():
    def get_vals():
        results = []
        for _ in range(30):
            data = np.random.normal(size=50)
            distribution = UniVariateKDE(data)
            results.append(distribution.mode())
        return results

    expected = 0
    confidence = 3.291  # 99.9% interval

    n_tests = 20
    tests = []

    for _ in range(n_tests):
        values = get_vals()
        std_error = get_standard_error(values)
        assert std_error is not None

        # Check that the expected value is within interval
        actual = np.array(values).mean()
        test = (actual - confidence * std_error < expected) and (
            expected < actual + confidence * std_error
        )
        tests.append(int(test))

    tpct = sum(tests) * 100.0 / n_tests

    # Add some slack!
    assert tpct >= SLACK


def test_UniVariateKDE_interval(gaussian):
    estimated = gaussian.confidence_interval(90)
    ideal = norm.interval(0.9)

    assert np.isclose(estimated, ideal, rtol=0, atol=2e-1).all()


def test_UniVariateKDE_ppf_x0(gaussian):
    probs = np.linspace(0.01, 0.99, 200)
    estimated = gaussian.ppf(probs)

    assert estimated.all()


def test_UniVariateKDE_interval_x0(gaussian):
    estimated = gaussian.confidence_interval(90)

    assert estimated.all()


def test_UniVariateKDE_ppf_fresh(gaussian_fresh):
    probs = np.linspace(0.01, 0.99, 200)
    estimated = gaussian_fresh.ppf(probs)
    ideal = norm.ppf(probs)

    assert np.isclose(estimated, ideal, rtol=0, atol=2e-1).all()


def test_UniVariateKDE_interval_fresh(gaussian_fresh):
    estimated = gaussian_fresh.confidence_interval(90)
    ideal = norm.interval(0.9)

    assert np.isclose(estimated, ideal, rtol=0, atol=2e-1).all()


def test_BiVariateKDE_mean():
    def get_vals():
        results = []
        mean = [0, 0]
        cov = [[1, 0], [0, 1]]
        for _ in range(30):
            x, y = np.random.multivariate_normal(mean, cov, int(1e4)).T
            distribution = BiVariateKDE(x, y)
            results.append(sum(distribution.mean()))
        return results

    expected = 0
    confidence = 3.291  # 99.9% interval

    n_tests = 20
    tests = []

    for _ in range(n_tests):
        values = get_vals()
        std_error = get_standard_error(values)
        assert std_error is not None

        # Check that the expected value is within interval
        actual = np.array(values).mean()
        test = (actual - confidence * std_error < expected) and (
            expected < actual + confidence * std_error
        )
        tests.append(int(test))

    tpct = sum(tests) * 100.0 / n_tests

    # Add some slack!
    assert tpct >= SLACK


def test_BiVariateKDE_mode():
    def get_vals():
        results = []
        mean = [0, 0]
        cov = [[1, 0], [0, 1]]
        for _ in range(30):
            x, y = np.random.multivariate_normal(mean, cov, int(1e4)).T
            distribution = BiVariateKDE(x, y)
            results.append(sum(distribution.mode()))
        return results

    expected = 0
    confidence = 3.291  # 99.9% interval

    n_tests = 20
    tests = []

    for _ in range(n_tests):
        values = get_vals()
        std_error = get_standard_error(values)
        assert std_error is not None

        # Check that the expected value is within interval
        actual = np.array(values).mean()
        test = (actual - confidence * std_error < expected) and (
            expected < actual + confidence * std_error
        )
        tests.append(int(test))

    tpct = sum(tests) * 100.0 / n_tests

    # Add some slack!
    assert tpct >= SLACK


def test_BiVariateKDE_pdf(bigaussian_pdf):
    xx = bigaussian_pdf["xx"]
    yy = bigaussian_pdf["yy"]
    pdf = bigaussian_pdf["pdf"]

    assert pdf.shape == (len(xx), len(yy))


def test_pdf_confidence_densities(bigaussian_pdf):
    pdf = bigaussian_pdf["pdf"]
    result = pdf_confidence_densities(pdf)
    is_positive = [x > 0 for x in result]

    assert all(is_positive)


def test_pdf_confidence_densities_levels(bigaussian_pdf):
    pdf = bigaussian_pdf["pdf"]
    result = pdf_confidence_densities(pdf, [50, 95])
    is_positive = [x > 0 for x in result]

    assert all(is_positive)


def test_pdf_contour_coords(bigaussian_pdf):
    xx = bigaussian_pdf["xx"]
    yy = bigaussian_pdf["yy"]
    pdf = bigaussian_pdf["pdf"]

    levels = pdf_confidence_densities(pdf)

    if not levels:
        pytest.skip("No levels generated for testing")

    cx, cy = pdf_contour_coords(xx, yy, pdf, levels[0])

    assert len(cx) > 0
    assert len(cy) > 0


def test_get_standard_error():
    def get_vals():
        results = []
        for _ in range(30):
            result = np.mean(np.random.standard_normal(size=10) + 1)
            results.append(result)
        return results

    expected = 1
    confidence = 3.291  # 99.9% interval

    n_tests = 100
    tests = []

    for _ in range(n_tests):
        values = get_vals()
        std_error = get_standard_error(values)
        assert std_error is not None

        # Check that the expected value is within interval
        actual = np.array(values).mean()
        test = (actual - confidence * std_error < expected) and (
            expected < actual + confidence * std_error
        )
        tests.append(int(test))

    tpct = sum(tests) * 100.0 / n_tests

    # Add some slack!
    assert tpct >= SLACK


def test_get_standard_error_large():
    values = np.random.normal(size=1000)
    result = get_standard_error(values)

    assert result is not None
    assert result > 0


@pytest.mark.parametrize("length", [0, 1])
def test_get_standard_error_one_value(length):
    values = [1] * length
    assert get_standard_error(values) is None
