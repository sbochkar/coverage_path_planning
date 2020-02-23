"""Module for locating reflex vertices in a polygon."""
from typing import List, Tuple

from shapely.geometry import Polygon, Point


def is_reflex(prev_vert: Tuple[float], mid_vert: Tuple[float], next_vert: Tuple[float]) -> bool:
    """Method for checking if three verts are reflex or not.

    Args:
        prev_vert (Tuple[float]): First vertex in a sequence.
        mid_vert (Tuple[float]): Second vertex in a sequence.
        next_vert (Tuple[float]): Third vertex in a sequence.

    Returns:
        True if the sequence is reflex.
    """
    dx_1 = float(mid_vert[0]) - float(next_vert[0])
    dy_1 = float(mid_vert[1]) - float(next_vert[1])
    dx_2 = float(prev_vert[0]) - float(mid_vert[0])
    dy_2 = float(prev_vert[1]) - float(mid_vert[1])
    if dx_1 * dy_2 - dy_1 * dx_2 > 0.0:
        return True
    return False


def find_reflex_vertices(polygon: Polygon) -> List[Point]:
    """Return a list of reflex vertices in polygon.

    Function will iterate over all vertices in polygon and return a list of reflex
    vertices

    Note:
        Shapely's boundaries are implmeneted as rings so last coords equals first coord.

    Args:
        polygon (Polygon): Polygon as a Shapely object.

    Returns:
        List of reflex vertecies in the form of Shapely's Point object.
    """
    vert_iter: List[Tuple[Tuple[float, float]]] = []
    for boundary in [polygon.exterior, *polygon.interiors]:
        prev_verts = [boundary.coords[-2], *boundary.coords[:-2]]
        curr_verts = boundary.coords[:-1]
        next_verts = boundary.coords[1:]

        vert_iter.extend(zip(prev_verts, curr_verts, next_verts))

    return [Point(mid) for prev, mid, next_ in vert_iter if is_reflex(prev, mid, next_)]
