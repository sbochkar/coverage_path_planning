"""Computing directions of edges in a polygon."""
from math import atan2
from math import pi
from typing import List

from shapely.geometry import Polygon


def get_directions_set(polygon: Polygon) -> List[float]:
    """
    Generate a list of directions orthogonal to edges of polygon

    TODO: Get rid of repeating directions

    Augs:
            polygon: standard form polygon
    Returns:
            dirs: set of directions [rad]
    """
    dirs: List[float] = []
    for ((a_x, a_y), (b_x, b_y)) in zip(polygon.exterior.coords[:-2], polygon.exterior.coords[1:]):
        dirs.append(atan2(b_y - a_y, b_x - a_x) + pi / 2)

    for hole in polygon.interiors:
        for ((a_x, a_y), (b_x, b_y)) in zip(hole.coords[:-2], hole.coords[1:]):
            dirs.append(atan2(b_y - a_y, b_x - a_x) + pi / 2)

    return dirs
