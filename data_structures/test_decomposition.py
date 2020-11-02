"""Unit tests for decomposition object.

Operations on Decomposition:
    init (Polygon) -> Decomposition. Intially has 1 cell.

stage_undo_cut (Cut) -> New combined polygon.
get_cells () -> A list of polygons in a decomposition.
undo_cut() -> Modifies current decomposition with combined polygon.
stage_cut():
    Acts on existing decomposition. Applies specified cut on a decomposition.
    If cut is deemed valid, performs a cut and returns 2 resultant polygons. Does NOT modify
    existing decomposition.
    Conditions for valid cut:
        * Entirely within original polygon.
        * Touches exterior of polygon at only 2 points.
        * If decomposition contains existing cells, cannot cross cell boundaries.
cut() -> Modifies decomposition with a new cut producing 2 new cells within decomposition.
"""
import pytest

from shapely.geometry import Polygon

from .decomposition import Decomposition
from .decomposition import cut, stage_cut

# ------------------------------ Decomposition initialization ------------------------------------ #
@pytest.mark.parametrize('test_polygon', [
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)])
])
def test_decomposition_init(test_polygon):
    """Verify that decomposition can be initialized with some valid intial polygon."""
    decomp = Decomposition(test_polygon)
    assert decomp.orig_polygon == Polygon(test_polygon)


@pytest.mark.parametrize('test_polygon', [
    ([]),
    ([(0., 0.), (1., 0.)]),
    ([(0., 0.), (1., 0.), (0., 1.), (1., 1.)])
])
def test_decomposition_init_error(test_polygon):
    """Verify that decomposition handles error cases with invalid initial polygon."""
    with pytest.raises(AssertionError):
        Decomposition(test_polygon)


# ------------------------------ Decomposition cuts ---------------------------------------------- #
@pytest.mark.parametrize('init_polygon, test_cut, res_p1, res_p2', [
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [(0., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.), (1., 1.)]),
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(1., 1.), (0., 0.)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0., 0.), (1., 1.), (0., 1.)]),
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0.5, 1.), (0., 0.)],
     [(0., 0.), (1., 0.), (1., 1.), (0.5, 1.)],
     [(0., 0.), (0.5, 1.), (0., 1.)]),
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0.5, 0.), (0.5, 1.)],
     [(0., 0.), (0.5, 0.), (0.5, 1.), (0., 1.)],
     [(0.5, 0.), (1., 0.), (1., 1.), (0.5, 1.)]),
    # Invalid: non-decomposing cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (0.5, 0.5)],
     [],
     []),
    # Invalid: non-decomposing cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1.5, 1.5)],
     [],
     []),
    # Invalid: invalid cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (0., 0.)],
     [],
     []),
    # Invalid: non-decomposing cut on the boundary of exterior.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.)],
     [],
     []),
])
def test_stage_cut_on_empty_decomposition(init_polygon, test_cut, res_p1, res_p2):
    """
    Verifies that function applies a cut to a decomposition and produces two new polygon without
    modifying existing decomposition. Only tests empty decomposition.

    Verify that a convention for returned polygon is followed:
        both polygons have ccw exterior rings.
        first polygon is aligned with the cut.
        second polygon is in the opposite direction of the cut.
    """
    decomp = Decomposition(init_polygon)

    orig_cell, poly_1, poly_2 = stage_cut(decomp, *test_cut)

    assert poly_1.equals(Polygon(res_p1))
    assert poly_2.equals(Polygon(res_p2))

    assert len(decomp.cells) == 1
    if res_p1:
        assert orig_cell.equals(Polygon(init_polygon))
    else:
        assert orig_cell.equals(Polygon([]))


@pytest.mark.parametrize('init_polygon, test_cut, orig_cell, res_p1, res_p2', [
    # Invalid: cut already exists
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [],
     [],
     []),
    # Invalid: cut crosses boundary of 2 polygons.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(1., 0.), (0., 1.)],
     [],
     [],
     []),
    # Cut originating from another cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0.5, 0.5), (1., 0.)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0.5, 0.5), (1., 0.), (1., 1.)],
     [(0.5, 0.5), (0., 0.), (1., 0.)]),
    # Cut originating from another's cut vertex.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.5)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0., 0.), (1., 0.5), (1., 1.)],
     [(0., 0.), (1., 0.), (1., 0.5)]),
])
def test_stage_cut_on_non_empty_decomposition(init_polygon, test_cut, orig_cell,
                                              res_p1, res_p2):
    """
    Verifies that function applies a cut to a decomposition with existing cells. Verify that
    existing decompostion does NOT modify the decomposition.
    """
    decomp = Decomposition(init_polygon)
    cut(decomp, (0., 0.), (1., 1.))

    orig_cell, poly_1, poly_2 = stage_cut(decomp, *test_cut)

    assert poly_1.equals(Polygon(res_p1))
    assert poly_2.equals(Polygon(res_p2))

    assert len(decomp.cells) == 2
    assert orig_cell.equals(Polygon(orig_cell))


@pytest.mark.parametrize('init_polygon, test_cut, res_p1, res_p2, is_invalid', [
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [(0., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.), (1., 1.)],
     False),
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(1., 1.), (0., 0.)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0., 0.), (1., 1.), (0., 1.)],
     False),
    # Invalid: non-decomposing cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (0.5, 0.5)],
     [],
     [],
     True),
])
def test_cut_on_empty_decomposition(init_polygon, test_cut, res_p1, res_p2, is_invalid):
    """
    Verifies that function applies a cut to a decomposition and produces two new polygon.
    Modifies existing decomposition in process. Only tests empty decomposition.

    Verify that a convention for returned polygon is followed:
        both polygons have ccw exterior rings.
        first polygon is aligned with the cut.
        second polygon is in the opposite direction of the cut.
    """
    decomp = Decomposition(init_polygon)

    poly_1, poly_2 = cut(decomp, *test_cut)

    assert poly_1.equals(Polygon(res_p1))
    assert poly_2.equals(Polygon(res_p2))

    if is_invalid:
        assert len(decomp.cells) == 1
        assert decomp.cells[0].equals(Polygon(init_polygon))
    else:
        assert len(decomp.cells) == 2
        assert decomp.cells[0].equals(Polygon(res_p1))
        assert decomp.cells[1].equals(Polygon(res_p2))


# def test_cuts():
#     init_polygon = ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)])
#     decomp = Decomposition(init_polygon)
#     poly_1, poly_2 = cut(decomp, (0., 0.), (1., 1.))


# def test_other():
#     """Verify decomposition's cuts."""
#     polygon = [(0., 0.), (1., 0.), (2., 1.), (3., 0.), (4., 0.), (4., 4.),
#                (3., 4.), (2., 3.), (1., 4.), (0., 4.)]
#     decomp = Decomposition(polygon)

#     point_1 = (1., 1.)
#     point_2 = (3., 3.)

#     # What should this object be able to do?
#     # We need to be able to add a cut this decomposition.
#     # And the method should return the two polygons that result from this cut.
#     pol_1, pol_2 = decomp.cut(point_1, point_2)




# def test_decomp_polygon_lookup():
#     # You should be able to access the 2 polygons that are produced by a cut
#     cuts = decomp.cuts()
#     poly_3, pol_4 = decomp[cuts[0]]


# def test_remove_cut():
#     # Should be able to remove a cut from decomposition.
#     cuts = decomp.cuts()
#     decomp.unite(cuts[0])
