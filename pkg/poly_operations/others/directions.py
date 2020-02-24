"""Computing directions of edges in a polygon."""
from math import atan2, pi
from typing import Set

from shapely.geometry import LineString, Polygon, Point
from shapely.affinity import rotate, translate


def get_directions_set(polygon: Polygon) -> Set[float]:
    """Generate a list of directions orthogonal to edges of polygon

    Args:
        polygon (Polygon): Polygon as a shapely object.
    Returns:
        dirs (Set): Set of directions in degrees.
    """
    dirs: Set[float] = set()
    for chain in [polygon.exterior, *polygon.interiors]:
        for idx, coord in enumerate(chain.coords[:-1]):
            edge = LineString([coord, chain.coords[idx + 1]])
            edge = rotate(edge, 90, origin=Point(coord))  # Perpendicular to the edge.
            edge = translate(edge, xoff=-coord[0], yoff=-coord[1])  # Direction vector.
            deg = atan2(edge.coords[1][1], edge.coords[1][0]) % pi
            dirs.add(180 * deg / pi)

    return dirs
