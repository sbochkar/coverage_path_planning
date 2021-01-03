"""Unit tests for altitude module.

Contains unit tests for functions that compute altitude of polygons.
"""
from math import isclose
import pytest

from shapely.geometry import Polygon

from altitude import get_altitude, get_min_altitude


UNIT_SQUARE = [[(0., 0.), (1., 0.), (1., 1.), (0., 1.)]]
RECTANGLE = [[(0., 0.), (8., 0.), (8., 1.), (0., 1.)]]
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
                             [[(0.1, 0.1), (0.2, 0.2), (0.1, 0.9), (0.9, 0.9), (0.9, 0.1)]]]
UNIT_DEAD_END_BOTH_SIDES_HOLE_SQUARE = [[(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
                                        [[(0.1, 0.1), (0.2, 0.2), (0.1, 0.9), (0.9, 0.9),
                                          (0.8, 0.5), (0.9, 0.1)]]]
BOOMERANG = [[(0., 1.), (2., 0.), (1., 1.), (2., 2.)]]
CLAMP = [[(0., 0.), (0., 10.), (4., 10.), (4., 0.), (3., 0.), (3., 9.), (1., 9.), (1., 0.)]]


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
    (UNIT_DEAD_END_HOLE_SQUARE,
     0., 0.1 + 0.3 + 2 * 0.7 + 0.1),
    (UNIT_DEAD_END_BOTH_SIDES_HOLE_SQUARE,
     0., 0.1 + 0.3 + 2 * 0.6 + 0.3 + 0.1),
    (UNIT_HOLE_PLUR_SQUARE,
     0., 0.2 + 2 * 0.8),
    ([[(0.0, 0.0), (0.1, 0.0), (0.2, 0.0), (0.3, 0.0), (1.0, 0.0), (1.0, 1.0), (0., 1.0)]],
     0, 1.),
    ([[(0.0, 0.0), (1.0, 0.0), (1.0, 0.1), (1.0, 0.1), (1.0, 0.1), (1.0, 0.1), (1.0, 1.0),
       (0., 1.0)]],
     0, 1.),
    ([[(0.0, 0.0), (1.0, 0.0), (1.0, 0.1), (1.0, 0.2), (1.0, 0.3), (1.0, 0.4), (1.0, 1.0),
       (0., 1.0)]],
     0, 1.),
    ([[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0., 1.0), (0., 0.9), (0., 0.8), (0., 0.7), (0., 0.6)]],
     0, 1.),
    ([[(0.0, 0.2), (0.0, 0.1), (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0., 1.0), (0., 0.9), (0., 0.8),
       (0., 0.7), (0., 0.6), (0., 1.0)]],
     0, 1.),
    ([[(0., 0.), (6., 0.), (6., 5.), (4., 5.), (4., 3.), (5., 3.), (5., 2.), (3., 2.), (3., 6.),
       (7., 6.), (7., 0.), (10., 0.), (10., 10.), (0., 10.)],
      [[(4., 7.), (3.5, 8.), (4.5, 9.), (6., 8.)]]],
     0, 16.5),
])
def test_get_altitude(test_polygon, test_theta, exp_alt):
    """Verifies that altitude of polygons is computed correctly."""
    result = get_altitude(Polygon(*test_polygon), test_theta)

    assert isclose(result, exp_alt)


@pytest.mark.parametrize('test_polygon, exp_alt, exp_dir', [
    (RECTANGLE, 1., 90.),
    (CLAMP, 4., 0.),

])
def test_get_min_altitude(test_polygon, exp_alt, exp_dir):
    """Verifies that minimum altitude is found."""
    min_alt, min_dir = get_min_altitude(Polygon(*test_polygon))

    assert (min_alt, min_dir) == (exp_alt, exp_dir)
