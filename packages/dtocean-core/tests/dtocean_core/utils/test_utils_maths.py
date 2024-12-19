import math

import numpy as np
import pytest

from dtocean_core.utils.maths import bearing_to_radians, radians_to_bearing


@pytest.mark.parametrize(
    "bearing, radians",
    [
        (0.0, math.pi / 2.0),
        (45.0, math.pi / 4.0),
        (90.0, 0.0),
        (135.0, 7 * math.pi / 4.0),
        (180.0, 3 * math.pi / 2.0),
        (225.0, 5 * math.pi / 4.0),
        (270.0, math.pi),
        (315.0, 3 * math.pi / 4.0),
    ],
)
def test_bearing_to_radians(bearing, radians):
    test_radians = bearing_to_radians(bearing)

    assert np.isclose(test_radians, radians)


@pytest.mark.parametrize(
    "bearing, radians",
    [
        (0.0, math.pi / 2.0),
        (45.0, math.pi / 4.0),
        (90.0, 0.0),
        (135.0, 7 * math.pi / 4.0),
        (180.0, 3 * math.pi / 2.0),
        (225.0, 5 * math.pi / 4.0),
        (270.0, math.pi),
        (315.0, 3 * math.pi / 4.0),
    ],
)
def test_radians_to_bearing(bearing, radians):
    test_bearing = radians_to_bearing(radians)

    assert np.isclose(test_bearing, bearing)
