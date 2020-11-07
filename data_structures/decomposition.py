"""Module containing definition of the Decomposition class."""
from functools import reduce
from typing import List, Tuple

from shapely.geometry import Polygon, LineString, MultiPoint, MultiLineString
from shapely.geometry.polygon import orient
from shapely.ops import shared_paths


class Decomposition:  # pylint: disable=too-few-public-methods # Container class
    """Class for Decomposition object."""
    __slots__ = (
        'cells',
        'exterior',
        'orig_polygon',
    )

    def __init__(self, polygon: List[Tuple[float, float]]):
        """Constructor for Decomposition object.

        Args:
            polygon (List): List of tuples representing points.
        """
        assert polygon and len(polygon) > 2, "Cannot create decomposition from invalid polygon."

        sh_polygon = Polygon(polygon)

        assert sh_polygon.is_valid, "Passed polygon is not valid."

        self.orig_polygon = sh_polygon
        self.exterior = self.orig_polygon.exterior
        self.cells: List[Polygon] = [sh_polygon]


def stage_cut(decomposition: Decomposition,
              point_1: Tuple[float], point_2: Tuple[float]) -> Tuple[Polygon, Polygon, Polygon]:
    """Stage a cut on a decomposition. Does not modify the decomposition.

    Split a polygon into two other polygons along split_line via the following steps:
        1. Find intersection between polygon exterior and cut for validation
        2. Split the exterior via difference with split line.
        3. If we get more than 2 lines, combine into 2.
        4. Form polygons from the resultant lines.
        5. Using above polygons as masks, find intersection of masks with original polygon.
        6. Orient resultant polygons.
        7. Order resultant polygons based on orientation w.r.t. cut.

    Args:
        decomposition (Decomposition): An instance of decomposition.
        point_1 (Tuple[float]): point_1
        point_2 (Tuple[float]): point_2

    Returns:
        res_p1 (Polygon): Resultant polygon aligned with the cut line.
        res_p2 (Polygon): Another resultant polygon aligned against the cut line.
        Return empty polygons if invalid conditions were encountered.
    """
    split_line = LineString([point_1, point_2])

    cell_contains = [cell.contains(split_line) for cell in decomposition.cells]
    if sum(cell_contains) != 1:
        return Polygon([]), Polygon([]), Polygon([])

    polygon = decomposition.cells[cell_contains.index(True)]
    ext_line = polygon.exterior

    # This calculates the points on the boundary where the split will happen.
    common_pts = ext_line.intersection(split_line)

    if (common_pts.is_empty or
            not common_pts.geom_type == 'MultiPoint' or # Intersection should be MultiPoint.
            len(common_pts) != 2 or # MultiPoint must ONLY have 2 points.
            not split_line.within(polygon) or # Split line should be inside polygon.
            any(split_line.intersects(hole) for hole in polygon.interiors)): # Cut touching holes?
        return Polygon([]), Polygon([]), Polygon([])

    split_boundary = ext_line.difference(split_line)

    if (not split_boundary.geom_type == 'MultiLineString' or # split must be MultiLineString
            len(split_boundary) > 3 or
            len(split_boundary) < 2): # Only 2 linestrings in the collection
        return Polygon([]), Polygon([]), Polygon([])

    # logger.debug("Split boundary: %s", split_boundary)

    # Even though we use LinearRing, there is no wrap around and diff produces
    # 3 strings. Need to union. Not sure if combining 1st and last strings
    # is guaranteed to be the right combo. For now, place a check.
    if len(split_boundary) == 3:
        if split_boundary[0].coords[0] != split_boundary[-1].coords[-1]:
            # logger.warning("The assumption that pts0[0] == pts2[-1] DOES not hold. Need"
            #                " to investigate.")
            return Polygon([]), Polygon([]), Polygon([])

        line1 = LineString(
            list(list(split_boundary[-1].coords)[:-1] + list(split_boundary[0].coords)))
    else:
        line1 = split_boundary[0]
    line2 = split_boundary[1]

    if len(line1.coords) < 3 or len(line2.coords) < 3:
        return Polygon([]), Polygon([]), Polygon([])

    mask1 = Polygon(line1)
    mask2 = Polygon(line2)

    if (not mask1.is_valid) or (not mask2.is_valid):
        return Polygon([]), Polygon([]), Polygon([])

    res_p1_pol = polygon.intersection(mask1)
    res_p2_pol = polygon.intersection(mask2)

    if (not res_p1_pol.geom_type == 'Polygon' or
            not res_p2_pol.geom_type == 'Polygon' or
            not res_p1_pol.is_valid or
            not res_p2_pol.is_valid):
        return Polygon([]), Polygon([]), Polygon([])

    # Correct the orientation of resultant polygons.
    res_p1_pol = orient(res_p1_pol)
    res_p2_pol = orient(res_p2_pol)

    # Enforce convention where first polygon is aligned with cut and second isn't.
    fwd, _ = shared_paths(res_p1_pol.exterior, split_line)
    if fwd.is_empty:
        res_p1_pol, res_p2_pol = res_p2_pol, res_p1_pol

    return polygon, res_p1_pol, res_p2_pol


def cut(decomposition: Decomposition,
        point_1: Tuple[float], point_2: Tuple[float]) -> Tuple[Polygon, Polygon]:
    """Perofrms a cut on a decomposition. Modifies the decomposition.

    Split a polygon into two other polygons along split_line.

    Args:
        decomposition (Decomposition): An instance of decomposition.
        point_1 (Tuple[float]): point_1
        point_2 (Tuple[float]): point_2

    Returns:
        res_p1 (Polygon): Resultant polygon aligned with the cut line.
        res_p2 (Polygon): Another resultant polygon aligned against the cut line.
        Return empty polygons if invalid conditions were encountered.
    """
    orig_cell, res_p1, res_p2 = stage_cut(decomposition, point_1, point_2)

    if res_p1.is_empty or res_p2.is_empty:
        return res_p1, res_p2

    decomposition.cells.remove(orig_cell)

    decomposition.cells.append(res_p1)
    decomposition.cells.append(res_p2)

    return res_p1, res_p2


def stage_undo_cut(decomposition: Decomposition,
                   point_1: Tuple[float],
                   point_2: Tuple[float]) -> Tuple[Polygon, Polygon, Polygon]:
    """Perofrms a cut on a decomposition. Modifies the decomposition.

    Split a polygon into two other polygons along split_line.

    Args:
        decomposition (Decomposition): An instance of decomposition.
        point_1 (Tuple[float]): point_1
        point_2 (Tuple[float]): point_2

    Returns:
        res_p1 (Polygon): Resultant polygon aligned with the cut line.
        res_p2 (Polygon): Another resultant polygon aligned against the cut line.
        Return empty polygons if invalid conditions were encountered.
    """
    split_line = LineString([point_1, point_2])

    res_p1_pol, res_p2_pol = None, None
    for cell in decomposition.cells:
        # Enforce convention where first polygon is aligned with cut and second isn't.
        res = shared_paths(cell.exterior, split_line)
        if not res.is_empty:
            fwd, bwd = res
            if not fwd.is_empty:
                res_p1_pol = cell
            if not bwd.is_empty:
                res_p2_pol = cell

    if not res_p1_pol or not res_p2_pol:
        return Polygon([]), Polygon([]), Polygon([])

    assert res_p2_pol, "Did not find a cell mis-aligned with the cut."

    union = res_p1_pol.union(res_p2_pol)
    return union, res_p1_pol, res_p2_pol
