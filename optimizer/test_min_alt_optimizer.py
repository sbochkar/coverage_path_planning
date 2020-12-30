import pytest

from shapely.geometry import LineString, Polygon

from decomposition.decomposition import Decomposition
from altitudes.altitude import get_min_altitude
from min_alt_optimizer import compute_vertex_sampler, get_cut_origins, min_alt_optimize


UNIT_SQUARE = [[(0., 0.), (1., 0.), (1., 1.), (0., 1.)]]
UNIT_SQUARE_HOLE = [[(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
                    [[(0.2, 0.2), (0.2, 0.8), (0.8, 0.8), (0.8, 0.2)]]]
ONE_REFLEX = [[(0., 0.), (1., 0.), (2., 1.), (3., 0.), (4., 0.), (4., 2.), (0., 2.)]]
ONE_REFLEX_HOLE = [[(0., 0.), (1., 0.), (2., 1.), (3., 0.), (4., 0.), (4., 2.), (0., 2.)]]
TWO_REFLEX = [[(0., 0.), (1., 0.), (2., 1.), (3., 0.), (4., 0.), (4., 3.), (3., 3.), (2., 2.),
               (1., 3.), (0., 3.)]]
TWO_REFLEX_ELONG = [[(0., 0.), (1., 0.), (1.5, 1.), (3., 0.), (8., 0.), (8., 3.), (3., 3.),
                     (1.5, 2.), (1., 3.), (0., 3.)]]


@pytest.mark.parametrize("test_polygon, exp_origins", [
    (ONE_REFLEX, [(2., 1.)]),
])
def test_get_cut_origins(test_polygon, exp_origins):
    """Verify that cut origins is computed correctly."""
    decomp = Decomposition(Polygon(*test_polygon))

    origins = get_cut_origins(decomp)

    assert origins == exp_origins


@pytest.mark.parametrize("test_polygon, expected_sample_space", [
    (ONE_REFLEX, [((2., 1.), (0., 0.)),
                  ((2., 1.), (4., 0.)),
                  ((2., 1.), (4., 2.)),
                  ((2., 1.), (0., 2.)),
                 ]),
    (TWO_REFLEX, [((2., 1.), (0., 0.)),
                  ((2., 1.), (4., 0.)),
                  ((2., 1.), (4., 3.)),
                  ((2., 1.), (3., 3.)),
                  ((2., 1.), (2., 2.)),
                  ((2., 1.), (1., 3.)),
                  ((2., 1.), (0., 3.)),
                  ((2., 2.), (0., 0.)),
                  ((2., 2.), (1., 0.)),
                  ((2., 2.), (2., 1.)),
                  ((2., 2.), (3., 0.)),
                  ((2., 2.), (4., 0.)),
                  ((2., 2.), (4., 3.)),
                  ((2., 2.), (0., 3.)),
                 ]),
    (UNIT_SQUARE_HOLE, [((0.2, 0.2), (0., 0.)),
                        ((0.2, 0.2), (0., 1.)),
                        ((0.2, 0.2), (1., 0.)),
                        ((0.2, 0.8), (0., 0.)),
                        ((0.2, 0.8), (0., 1.)),
                        ((0.2, 0.8), (1., 1.)),
                        ((0.8, 0.8), (0., 1.)),
                        ((0.8, 0.8), (1., 1.)),
                        ((0.8, 0.8), (1., 0.)),
                        ((0.8, 0.2), (1., 1.)),
                        ((0.8, 0.2), (1., 0.)),
                        ((0.8, 0.2), (0., 0.)),
                       ]),
])
def test_vertex_sampler(test_polygon, expected_sample_space):
    """
    Unit tests for simple sampler. Simple sampler's objectie is given a polygon, propose a list
    of cuts which originate from reflex verticies and end on some vertex of the polygon.
    These cuts will then be used by the optimizer to find the most optimal one.
    """
    decomp = Decomposition(Polygon(*test_polygon))

    sample_space = compute_vertex_sampler(decomp)

    ls_expected = [LineString(a) for a in expected_sample_space]
    for result in sample_space:
        assert any(result.equals(a) for a in ls_expected)


@pytest.mark.parametrize("test_polygon, test_sample_space", [
    (TWO_REFLEX_ELONG, [((1.5, 1.), (1.5, 2.)),
                       ]),
])
def test_min_alt_optimize(test_polygon, test_sample_space):
    """Verify that the optimizer attempts to choose the best cut from the supplied cuts."""
    decomp = Decomposition(Polygon(*test_polygon))
    test_samples = [LineString(a) for a in test_sample_space]

    min_alt_optimize(decomp, test_samples)

    assert False
