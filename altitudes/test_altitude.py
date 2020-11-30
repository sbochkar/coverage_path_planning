"""Unit tests for altitude module.

Contains unit tests for functions that compute altitude of polygons.
"""
from math import isclose
import pytest

from shapely.geometry import Polygon

from altitude import get_altitude


UNIT_SQUARE = [[(0., 0.), (1., 0.), (1., 1.), (0., 1.)]]
UNIT_HOLE_SQUARE = [[(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
                    [[(0.1, 0.1), (0.1, 0.9), (0.9, 0.9), (0.9, 0.1)]]]
UNIT_HOLE_PLUR_SQUARE = [[(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
                         [[(0.1, 0.1), (0.1, 0.2), (0.1, 0.5), (0.1, 0.7),
                           (0.1, 0.9), (0.9, 0.9), (0.9, 0.1)]]]
UNIT_TRICK_HOLE_SQUARE = [[(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
                          [[(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.3),
                            (0.2, 0.4), (0.2, 0.8), (0.1, 0.8), (0.1, 0.9),
                            (0.9, 0.9), (0.9, 0.1)]]]
UNIT_DEAD_END_HOLE_SQUARE = [[(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
                             [[(0.1, 0.1), (0.5, 0.2), (0.1, 0.9), (0.9, 0.9), (0.9, 0.1)]]]
UNIT_DEAD_END_BOTH_SIDES_HOLE_SQUARE = [[(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
                                        [[(0.1, 0.1), (0.5, 0.2), (0.1, 0.9), (0.9, 0.9),
                                          (0.8, 0.5), (0.9, 0.1)]]]
BOOMERANG = [[(0., 1.), (2., 0.), (1., 1.), (2., 2.)]]


@pytest.mark.parametrize('test_polygon, test_theta, exp_alt', [
    (UNIT_SQUARE,
     0., 1.),
    (UNIT_SQUARE,
     90., 1.),
    (BOOMERANG,
     0., 3.),
    (UNIT_HOLE_SQUARE,
     0., 0.2 + 2 * 0.8),
    (UNIT_TRICK_HOLE_SQUARE,
     0., 0.1 + 0.3 + 2 * 0.7 + 0.1),
    # (UNIT_DEAD_END_HOLE_SQUARE,
    #  0., 0.1 + 0.3 + 2 * 0.7 + 0.1),
    # (UNIT_DEAD_END_BOTH_SIDES_HOLE_SQUARE,
    #  0., 0.1 + 0.3 + 2 * 0.6 + 0.3 + 0.1),
    # (UNIT_HOLE_PLUR_SQUARE,
    #  0., 0.2 + 2 * 0.8),
])
def test_get_altitude(test_polygon, test_theta, exp_alt):
    """Verifies that altitude of polygons is computed correctly."""
    result = get_altitude(Polygon(*test_polygon), test_theta)

    assert isclose(result, exp_alt)
