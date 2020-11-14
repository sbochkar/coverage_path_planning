"""Unit tests for decomposition object.

Note:
    Use caution when writing tests. Floating point precision error APPLIES!

Operations on Decomposition:
    init (Polygon) -> Decomposition. Intially has 1 cell.

stage_cut():
    Acts on existing decomposition. Applies specified cut on a decomposition.
    If cut is deemed valid, performs a cut and returns 2 resultant polygons. Does NOT modify
    existing decomposition.
    Conditions for valid cut:
        * Entirely within original polygon.
        * Touches exterior of polygon at only 2 points.
        * If decomposition contains existing cells, cannot cross cell boundaries.
cut() -> Modifies decomposition with a new cut producing 2 new cells within decomposition.
stage_undo_cut():
    Acts on existing decomposition. Removes a specified cut if it exists.
    If it exists, combines the two adjacent cuts returning combined cell and two original cells.
undo_cut() -> Undoes a cut in a decomposition and modifies it as needed.
"""
import pytest

from shapely.geometry import Polygon

from .decomposition import Decomposition
from .decomposition import cut, stage_cut, stage_undo_cut, undo_cut

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
@pytest.mark.parametrize('init_polygon, pre_test_cut, test_cut, orig_poly, res_p1, res_p2', [
    # Normal cut on a square polygon.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0., 0.), (1., 1.)],
     [(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.), (1., 1.)]),
    # Normal cut on a square polygon with a cut going opposite direction.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(1., 1.), (0., 0.)],
     [(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0., 0.), (1., 1.), (0., 1.)]),
    # Normal cut on a square polygon with cut with one vertex not on the vertecies of the polygon.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0.5, 1.), (0., 0.)],
     [(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.), (1., 1.), (0.5, 1.)],
     [(0., 0.), (0.5, 1.), (0., 1.)]),
    # Normal cut on a square polygon with cut that is not on the vertecies of the polygon.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0.5, 0.), (0.5, 1.)],
     [(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (0.5, 0.), (0.5, 1.), (0., 1.)],
     [(0.5, 0.), (1., 0.), (1., 1.), (0.5, 1.)]),
    # Normal cut but resulting polygon is tiny.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0., 10e-10), (1., 10e-10)],
     [(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 10e-10), (1., 10e-10), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.), (1., 10e-10), (0., 10e-10)]),
    # Cut originating from another cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [(0.5, 0.5), (1., 0.)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0.5, 0.5), (1., 0.), (1., 1.)],
     [(0.5, 0.5), (0., 0.), (1., 0.)]),
    # Cut originating from another cut vertex.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [(0., 0.), (1., 0.5)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0., 0.), (1., 0.5), (1., 1.)],
     [(0., 0.), (1., 0.), (1., 0.5)]),
    # Testing a cut not incident to another cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [(0.1, 0.), (1., 0.5)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0.1, 0.), (1., 0.5), (1., 1.), (0., 0.)],
     [(0.1, 0.), (1., 0.), (1., 0.5)]),
    # Testing precision.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [(1/3, 1/3), (1., 0.5)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(1/3, 1/3), (1., 0.5), (1., 1.)],
     [(1/3, 1/3), (0., 0.), (1., 0.), (1., 0.5)]),
    # Testing precision with really small values.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [((1/3)*10e-35, (1/3)*10e-35), (1., 0.5)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [((1/3)*10e-35, (1/3)*10e-35), (1., 0.5), (1., 1.)],
     [((1/3)*10e-35, (1/3)*10e-35), (0., 0.), (1., 0.), (1., 0.5)]),
    # TODO: Write tests for polygons with holes.
])
def test_stage(init_polygon, pre_test_cut, test_cut, orig_poly, res_p1, res_p2):
    """
    Verifies that function applies a cut to a decomposition and produces two new polygon without
    modifying existing decomposition. Only tests empty decomposition.

    Verify that a convention for returned polygon is followed:
        both polygons have ccw exterior rings.
        first polygon is aligned with the cut.
        second polygon is in the opposite direction of the cut.
    """
    decomp = Decomposition(init_polygon)

    if pre_test_cut:
        cut(decomp, *pre_test_cut)

    orig_cell, poly_1, poly_2 = stage_cut(decomp, *test_cut)

    assert poly_1.equals(Polygon(res_p1))
    assert poly_2.equals(Polygon(res_p2))

    assert len(decomp.cells) == (2 if pre_test_cut else 1)
    assert orig_cell.equals(Polygon(orig_poly))


@pytest.mark.parametrize('init_polygon, pre_test_cut, test_cut', [
    # Invalid: non-decomposing cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0., 0.), (0.5, 0.5)],
    ),
    # Invalid: non-decomposing cut completely on the inside the polygon.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0.2, 0.2), (0.5, 0.5)],
    ),
    # Invalid: non-decomposing cut extending beyond exterior.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0., 0.), (1.5, 1.5)],
    ),
    # Invalid: invalid cut of length 0.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0., 0.), (0., 0.)],
    ),
    # Invalid: non-decomposing cut on the boundary of exterior.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0., 0.), (1., 0.)],
    ),
    # Invalid: incomplete cut partially outside of the polygon.
    ([(0., 0.), (1., 1.), (2., 0.), (2., 2.), (0., 2.)],
     [],
     [(0., 0.), (1., 0.)],
    ),
    # Invalid: incomplete cut completely outside of the polygon.
    ([(0., 0.), (1., 1.), (2., 0.), (2., 2.), (0., 2.)],
     [],
     [(-1., -1.), (-2., -2.)],
    ),
    # Invalid: complete cut outside of the polygon.
    ([(0., 0.), (1., 1.), (2., 0.), (2., 2.), (0., 2.)],
     [],
     [(0., 0.), (2., 0.)],
    ),
    # Invalid: cut incident on 3 points on the exterior.
    ([(0., 0.), (1., 1.), (2., 0.), (2., 2.), (0., 2.)],
     [],
     [(0., 1.), (2., 1.)],
    ),
    # Invalid: cut partially aligned with one of the edges of the polygon.
    ([(0., 0.), (1., 1.), (2., 0.), (2., 2.), (0., 2.)],
     [],
     [(0., 0.), (2., 2.)],
    ),
    # Invalid: cut already exists.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [(0., 0.), (1., 1.)],
    ),
    # Invalid: cut crosses boundary of 2 polygons.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [(1., 0.), (0., 1.)],
    ),
])
def test_stage_invalid(init_polygon, pre_test_cut, test_cut):
    """
    Verifies that stage_cut handles invalid cuts accordingly.
    """
    decomp = Decomposition(init_polygon)

    if pre_test_cut:
        cut(decomp, *pre_test_cut)

    results = stage_cut(decomp, *test_cut)

    assert all(poly.equals(Polygon([])) for poly in results)
    assert len(decomp.cells) == 1 + bool(pre_test_cut)


@pytest.mark.parametrize('init_polygon, pre_test_cut, test_cut, res_p1, res_p2', [
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0., 0.), (1., 1.)],
     [(0., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.), (1., 1.)],
     ),
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(1., 1.), (0., 0.)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0., 0.), (1., 1.), (0., 1.)],
     ),
])
def test_cut(init_polygon, pre_test_cut, test_cut, res_p1, res_p2):
    """
    Verifies that function applies a cut to a decomposition and produces two new polygon.
    Modifies existing decomposition in process.

    Verify that a convention for returned polygon is followed:
        both polygons have ccw exterior rings.
        first polygon is aligned with the cut.
        second polygon is in the opposite direction of the cut.
    """
    decomp = Decomposition(init_polygon)
    if pre_test_cut:
        cut(decomp, *pre_test_cut)

    poly_1, poly_2 = cut(decomp, *test_cut)

    assert poly_1.equals(Polygon(res_p1))
    assert poly_2.equals(Polygon(res_p2))

    assert len(decomp.cells) == 2 + bool(pre_test_cut)

    assert any([poly.equals(Polygon(res_p1)) for poly in decomp.cells])
    assert any([poly.equals(Polygon(res_p2)) for poly in decomp.cells])


@pytest.mark.parametrize('init_polygon, pre_test_cut, test_cut', [
    # Invalid: non-decomposing cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [],
     [(0., 0.), (0.5, 0.5)],
    ),
    # Invalid: cut already exists.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [(0., 0.), (1., 1.)],
    ),
])
def test_cut_invalid(init_polygon, pre_test_cut, test_cut):
    """
    Verifies that cut function handles incorrect cuts accordingly.
    """
    decomp = Decomposition(init_polygon)
    if pre_test_cut:
        cut(decomp, *pre_test_cut)

    results = cut(decomp, *test_cut)

    assert all(poly.equals(Polygon([])) for poly in results)
    assert len(decomp.cells) == 1 + bool(pre_test_cut)


# Note:
#   Not sure about false negatives here. It's possible for a test to fail because of floating
#   point precession errors rather than the scenario that was tested.
@pytest.mark.parametrize('invalid_cut', [
    ([(0.9, 0.), (0.9, 1.)]),  # Invalid: non-existent cut not touching existing cut.
    ([(1., 0.), (0., 1.)]),  # Invalid: non-existent cut touching existing cut.
    ([(1., 0.), (0.5, 0.5)]),  # Invalid: non-existent cut ending on existing cut.
    ([(0., 0.), (0.5, 0.5)]),  # Invalid: specified cut is subset of existing cut.
    ([(0., 0.), (0., 0.)]),  # Invalid: Degenerate cut.
    ([(0., 0.), (-1., -1.)]),  # Invalid: Partially outside of polygon except one point.
    ([(0.5, 0.5), (-1., -1.)]),  # Invalid: Partially outside of polygon except half the cut.
    ([(-2., 0.5), (-2., -1.)]),  # Invalid: Cut completely outside of polygon.
    ([(-2., -2.), (2., 2.)]),  # Invalid: Cut superset of existing cut.
    ([(0., 0.), (1., 0.)]),  # Invalid: Cut is an edge of polygon.
    ([(0., 0.), (1., 1.)]),  # Invalid: Cut exists but undoing it will break the polygon.
    ([(0., 0.), (0.5, 0.5)]),  # Invalid: A subset of a shared edge is merged.
    ([(1., 1.), (0.9, 0.9)]),  # Invalid: Same as above just in case.
])
def test_stage_undo_cut_invalid(invalid_cut):
    """Verifies that we cannot undo a cut on empty decomposition."""
    decomp = Decomposition([(0., 0.), (1., 0.), (1., 1.), (0., 1.)])
    cut(decomp, (0., 0.), (1., 1.))
    cut(decomp, (0.1, 0.1), (0.1, 0.))

    results = stage_undo_cut(decomp, *invalid_cut)

    assert all(poly.equals(Polygon([])) for poly in results)


@pytest.mark.parametrize('init_polygon, pre_test_cuts, test_cut, new_polygon, res_p1, res_p2', [
    # Normal case with diagonal cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [[(0., 0.), (1., 1.)]],
     [(0., 0.), (1., 1.)],
     [(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.), (1., 1.)]),
    # Normal case with flat cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [[(0.1, 0.), (0.1, 1.)]],
     [(0.1, 0.), (0.1, 1.)],
     [(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (0.1, 0.), (0.1, 1.), (0., 1.)],
     [(0.1, 0.), (1., 0.), (1., 1.), (0.1, 1.)]),
    # Normal case with 2 independent cuts.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [[(0.1, 0.), (0.1, 1.)], [(0.9, 0.), (0.9, 1.)]],
     [(0.1, 0.), (0.1, 1.)],
     [(0., 0.), (0.9, 0.), (0.9, 1.), (0., 1.)],
     [(0., 0.), (0.1, 0.), (0.1, 1.), (0., 1.)],
     [(0.1, 0.), (0.9, 0.), (0.9, 1.), (0.1, 1.)]),
    # Normal case with 2 cuts, one adjacent on anothers' vertex.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [[(0., 0.), (1., 1.)], [(1., 1.), (0.9, 0.)]],
     [(0.9, 0.), (1., 1.)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0., 0.), (0.9, 0.), (1., 1.)],
     [(1., 0.), (1., 1.), (0.9, 0.)]),
    # Normal case with 2 cuts, one incident to the middle of another. Undo the one that won't break.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [[(0., 0.), (1., 1.)], [(0.5, 0.5), (1., 0.)]],
     [(0.5, 0.5), (1., 0.)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0.5, 0.5), (1., 0.), (1., 1.)],
     [(0.5, 0.5), (0., 0.), (1., 0.)]),
    # Normal case with 2 cuts, one incident to the middle of another. Undo half the first one.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [[(0., 0.), (1., 1.)], [(0.5, 0.5), (1., 0.)]],
     [(0.5, 0.5), (0., 0.)],
     [(0., 0.), (1., 0.), (0.5, 0.5), (1., 1.), (0., 1.)],
     [(0.5, 0.5), (0., 0.), (1., 0.)],
     [(0., 0.), (1., 1.), (0., 1.)]),
])
def test_stage_undo(init_polygon, pre_test_cuts, test_cut, new_polygon, res_p1, res_p2):
    """Verifies that we undo one cut."""
    decomp = Decomposition(init_polygon)

    for pre_test_cut in pre_test_cuts:
        cut(decomp, *pre_test_cut)

    new_cell, old_cell_1, old_cell_2 = stage_undo_cut(decomp, *test_cut)

    assert new_cell.equals(Polygon(new_polygon))
    assert old_cell_1.equals(Polygon(res_p1))
    assert old_cell_2.equals(Polygon(res_p2))


@pytest.mark.parametrize('init_polygon, pre_test_cuts, test_cut, res_p', [
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [[(0., 0.), (1., 1.)]],
     [(0., 0.), (1., 1.)],
     [(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     ),
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [[(1., 1.), (0., 0.)], [(0.5, 0.5), (1., 0.)]],
     [(0.5, 0.5), (1., 0.0)],
     [(0., 0.), (1., 0.), (1., 1.)],
     ),
])
def test_undo_cut(init_polygon, pre_test_cuts, test_cut, res_p):
    """
    Verifies that function applies a cut to a decomposition and produces two new polygon.
    Modifies existing decomposition in process.

    Verify that a convention for returned polygon is followed:
        both polygons have ccw exterior rings.
        first polygon is aligned with the cut.
        second polygon is in the opposite direction of the cut.
    """
    decomp = Decomposition(init_polygon)
    for cut_ in pre_test_cuts:
        cut(decomp, *cut_)

    new_polygon = undo_cut(decomp, *test_cut)

    assert new_polygon.equals(Polygon(res_p))
    assert len(decomp.cells) == 1 + len(pre_test_cuts) - 1
    assert any([poly.equals(Polygon(new_polygon)) for poly in decomp.cells])
