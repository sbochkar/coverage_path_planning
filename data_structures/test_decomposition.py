"""Unit tests for decomposition object.

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
undo_cut() ->
"""
import pytest

from shapely.geometry import Polygon

from .decomposition import Decomposition
from .decomposition import cut, stage_cut, stage_undo_cut

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
    assert orig_cell.equals(Polygon(init_polygon if res_p1 else []))


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
    # TODO: Implement a test case that encounters an issue with floating point representation.
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


@pytest.mark.parametrize('init_polygon, test_cut, orig_cell, res_p1, res_p2', [
    # Invalid: cut already exists
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
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
    # Testing a cut not incident to another cut.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0.1, 0.), (1., 0.5)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(0.1, 0.), (1., 0.5), (1., 1.), (0., 0.)],
     [(0.1, 0.), (1., 0.), (1., 0.5)]),
    # Testing precision.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(1/3, 1/3), (1., 0.5)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [(1/3, 1/3), (1., 0.5), (1., 1.)],
     [(1/3, 1/3), (0., 0.), (1., 0.), (1., 0.5)]),
    # Testing precision with really small vertecies.
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [((1/3)*10e-35, (1/3)*10e-35), (1., 0.5)],
     [(0., 0.), (1., 0.), (1., 1.)],
     [((1/3)*10e-35, (1/3)*10e-35), (1., 0.5), (1., 1.)],
     [((1/3)*10e-35, (1/3)*10e-35), (0., 0.), (1., 0.), (1., 0.5)]),
])
def test_cut_on_non_empty_decomposition(init_polygon, test_cut, orig_cell,
                                        res_p1, res_p2):
    """
    Verifies that function applies a cut to a decomposition with existing cells. Verify that
    existing decompostion gets modified accordingly.
    """
    decomp = Decomposition(init_polygon)
    cut(decomp, (0., 0.), (1., 1.))

    poly_1, poly_2 = cut(decomp, *test_cut)

    assert poly_1.equals(Polygon(res_p1))
    assert poly_2.equals(Polygon(res_p2))

    assert len(decomp.cells) == (2 if not orig_cell else 3)
    assert not any([poly.equals(Polygon(init_polygon)) for poly in decomp.cells])
    if res_p1:
        assert any([poly.equals(Polygon(res_p1)) for poly in decomp.cells])
    if res_p2:
        assert any([poly.equals(Polygon(res_p2)) for poly in decomp.cells])


@pytest.mark.parametrize('init_polygon', [
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)]),
])
def test_cut_on_non_empty_decomposition_sweep(init_polygon):
    """
    Verifies that function applies a cut to a decomposition with existing cells. Verify that
    existing decompostion gets modified accordingly.
    """
    decomp = Decomposition(init_polygon)
    cut(decomp, (0., 0.), (1., 0.1))

    import numpy as np
    from shapely.geometry import LineString

    orig_cut = LineString([(0., 0.,), (1., 0.1)])
    for distance in np.linspace(0, 0.99, num=10):
        p_1 = orig_cut.interpolate(distance, normalized=True)

        new_cut = [(p_1.x, p_1.y), (1., 0.05)]
        orig, poly_1, poly_2 = stage_cut(decomp, *new_cut)

        
        expected_p1 = [(p_1.x, p_1.y), (1., 0.05), (1., 0.1)]
        expected_p2 = [(p_1.x, p_1.y), (0., 0.), (1., 0.), (1., 0.05)]
        print(poly_1)
        assert poly_1.equals(Polygon(expected_p1))
        assert poly_2.equals(Polygon(expected_p2))
        assert orig.equals(poly_1.union(poly_2))



        


    # poly_1, poly_2 = cut(decomp, *test_cut)

    # assert poly_1.equals(Polygon(res_p1))
    # assert poly_2.equals(Polygon(res_p2))

    # assert len(decomp.cells) == (2 if not orig_cell else 3)
    # assert not any([poly.equals(Polygon(init_polygon)) for poly in decomp.cells])
    # if res_p1:
    #     assert any([poly.equals(Polygon(res_p1)) for poly in decomp.cells])
    # if res_p2:
    #     assert any([poly.equals(Polygon(res_p2)) for poly in decomp.cells])


def test_stage_undo_cut_invalid():
    """Verifies that we cannot undo a cut on empty decomposition."""
    decomp = Decomposition([(0., 0.), (1., 0.), (1., 1.), (0., 1.)])
    cut(decomp, (0., 0.), (1., 1.))

    results = stage_undo_cut(decomp, (1., 0.), (0., 1.))

    assert all(poly.equals(Polygon([])) for poly in results)


@pytest.mark.parametrize('init_polygon, test_cut, res_p1, res_p2', [
    ([(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 1.)],
     [(0., 0.), (1., 1.), (0., 1.)],
     [(0., 0.), (1., 0.), (1., 1.)]),
])
def test_stage_undo_cut_with_one_existing_cut(init_polygon, test_cut, res_p1, res_p2):
    """Verifies that we undo one cut."""
    decomp = Decomposition(init_polygon)
    cut(decomp, *test_cut)

    new_cell, old_cell_1, old_cell_2 = stage_undo_cut(decomp, *test_cut)

    assert new_cell.equals(Polygon(init_polygon))
    assert old_cell_1.equals(Polygon(res_p1))
    assert old_cell_2.equals(Polygon(res_p2))
