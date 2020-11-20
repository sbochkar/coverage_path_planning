"""Module containing definition of the Decomposition class."""
from typing import List, Tuple

from shapely.geometry import Polygon, Point, LineString, MultiPoint, MultiLineString
from shapely.geometry.polygon import orient
from shapely.ops import shared_paths, split


class Decomposition:  # pylint: disable=too-few-public-methods # Container class
    """Class for Decomposition object."""
    __slots__ = (
        'cells',
        'exterior',
        'orig_polygon',
    )

    def __init__(self, polygon: Polygon):
        """Constructor for Decomposition object.

        Args:
            polygon (List): List of tuples representing points.
        """
        assert not polygon.is_empty, "Cannot create decomposition from empty polygon."
        assert polygon.is_valid, "Cannot create decomposition from invalid polygon."

        self.orig_polygon = polygon
        self.exterior = self.orig_polygon.exterior
        self.cells: List[Polygon] = [polygon]


def stage_cut(decomposition: Decomposition,
              point_1: Tuple[float], point_2: Tuple[float]) -> Tuple[Polygon, Polygon, Polygon]:
    """Stage a cut on a decomposition. Does not modify the decomposition.

    Split a polygon into two other polygons along split_line via the following steps:
        1. Find intersection between polygon exterior and cut for validation
        2. Split the polygon via split line.
        3. Orient resultant polygons.
        4. Order resultant polygons based on orientation w.r.t. cut.

    Returns empty polygons if an error condition is encountered.

    Args:
        decomposition (Decomposition): An instance of decomposition.
        point_1 (Tuple[float]): point_1. Must be within exterior of some cell.
        point_2 (Tuple[float]): point_2. Must be within exterior of some cell.

    Returns:
        res_p1 (Polygon): Resultant polygon aligned with the cut line.
        res_p2 (Polygon): Another resultant polygon aligned against the cut line.
        Return empty polygons if invalid conditions were encountered.
    """
    split_line = LineString([point_1, point_2])

    for cell in decomposition.cells:
        # Intersection of cell boundary with the proposed split line.
        common_pts = cell.exterior.intersection(split_line)

        if not (common_pts.is_empty or
                not common_pts.geom_type == 'MultiPoint' or # Intersection should be MultiPoint.
                len(common_pts) != 2 or # MultiPoint must ONLY have 2 points.
                not split_line.within(cell) or # Split line should be inside cell.
                any(split_line.intersects(hole) for hole in cell.interiors)): # Cut touching holes?
            break
    else:
        return Polygon([]), Polygon([]), Polygon([])

    split_result = split(cell, split_line)
    # Sanity check that the split was successful.
    if len(split_result) != 2:
        return Polygon([]), Polygon([]), Polygon([])
    if not all(poly.geom_type == 'Polygon' and poly.is_valid for poly in split_result):
        return Polygon([]), Polygon([]), Polygon([])

    # Correct the orientation of resultant polygons.
    res_p1_pol, res_p2_pol = orient(split_result[0]), orient(split_result[1])

    # Enforce convention where first cell is aligned with cut and second isn't.
    fwd, _ = shared_paths(res_p1_pol.exterior, split_line)
    if fwd.is_empty:
        res_p1_pol, res_p2_pol = res_p2_pol, res_p1_pol

    return cell, res_p1_pol, res_p2_pol


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
    """Undoes a cut in a decomposition. Does not modify the decomposition.

    Performs union of the two adjacent cells that share the split line. Given it's valid.

    Args:
        decomposition (Decomposition): An instance of decomposition.
        point_1 (Tuple[float]): point_1
        point_2 (Tuple[float]): point_2

    Returns:
        union (Polygon): Resultant polygon from the union.
        res_p1 (Polygon): Original polygon adjacent to the split line. Aligned with the cut.
        res_p2 (Polygon): Original polygon adjacent to the split line. Not aligned with the cut.
        Return empty polygons if invalid conditions were encountered.
    """
    split_line = LineString([point_1, point_2])

    def is_compat_with_cell(cell):
        """Perform validity checks of the given cell w.r.t the split_line."""
        intersection = cell.exterior.intersection(split_line)

        if (intersection.is_empty or  # Does not intersect.
                not intersection.geom_type == 'LineString' or  # Intersects but not just a line.
                not intersection.equals(split_line)):  # Intersection is a subset of an edge.
            return False
        return True

    valid_cells = list(map(is_compat_with_cell, decomposition.cells))

    # Only 2 cells can be compatible with undo at a time.
    if sum(valid_cells) != 2:
        return Polygon([]), Polygon([]), Polygon([])

    res_p1, res_p2 = [decomposition.cells[i] for i, is_valid in enumerate(valid_cells) if is_valid]

    # Enforce convention where first cell is aligned with cut and second isn't.
    fwd, _ = shared_paths(res_p1.exterior, split_line)
    if fwd.is_empty:
        res_p1, res_p2 = res_p2, res_p1

    union = res_p1.union(res_p2)

    # Perform sanity checks after the union: valid union and if merged cut is equal specified line.
    if not union.is_valid or \
            not res_p1.exterior.difference(union.exterior).equals(split_line):
        return Polygon([]), Polygon([]), Polygon([])

    return union, res_p1, res_p2


def undo_cut(decomposition: Decomposition, point_1: Tuple[float],
             point_2: Tuple[float]) -> Polygon:
    """Undoes a cut in a decomposition. Modifies the decomposition.

    Performs union of the two adjacent cells that share the split line. Given it's valid.

    Args:
        decomposition (Decomposition): An instance of decomposition.
        point_1 (Tuple[float]): point_1
        point_2 (Tuple[float]): point_2

    Returns:
        union (Polygon): Resultant polygon from the union.
        Return empty polygons if invalid conditions were encountered.
    """
    new_cell, res_p1, res_p2 = stage_undo_cut(decomposition, point_1, point_2)

    if new_cell.is_empty:
        return new_cell

    decomposition.cells.remove(res_p1)
    decomposition.cells.remove(res_p2)

    decomposition.cells.append(new_cell)

    return new_cell
