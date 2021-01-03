"""Module for computing altitude of polygons."""
from math import atan2, pi
from itertools import tee
from typing import Tuple, List, Set
import sys

from shapely.geometry import Polygon, Point, LineString
from shapely.affinity import rotate, translate


def get_min_altitude(polygon: Polygon):
    """Computes minimum altitude for a given polygon.

    Function perofrm a series of call to get_altitude, to find the min altitude
    Things to look out for:
            min_alt init value might not be high ebough

    """
    min_alt = sys.float_info.max
    min_dir = 0.
    for theta in get_directions_set(polygon):
        test_alt = get_altitude(polygon, theta)
        if test_alt <= min_alt:
            min_alt = test_alt
            min_dir = theta

    return min_alt, min_dir


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


def get_altitude(polygon: Polygon, theta: float) -> float:
    """Compute theta altitude of polygon.

    Steps:
        1. Rotate the polygon to align sweep with the x-axis.
        2. Sort all vertices of the polygon by x-coordinate.
        3. Keep the counter of active corridors.
        4. Sum up the lengths between events scaled by the counter.

    Args:
        polygon (Polygon): Shapely object representing polygon.
        theta (float): Angle of measurement with respect to x-axis.

    Returns:
        altitude (float): A scalar value of the altitude.
    """
    # Align altitude direction with x axis, for convenience.
    polygon = rotate(polygon, -theta)

    prevs: List[Tuple[float, float]] = []
    currs: List[Tuple[float, float]] = []
    nexts: List[Tuple[float, float]] = []

    # Collapse vertecies with same x-coordinate to avoid ambigious behaviours.
    for chain in [polygon.exterior, *polygon.interiors]:
        # Forward pass
        cur, nxt = tee(chain.coords)
        next(nxt, None)
        for cur_vert, nxt_vert in zip(cur, nxt):
            if cur_vert[0] != nxt_vert[0]:
                currs.append(cur_vert)
                nexts.append(nxt_vert)

        # Backward pass
        cur, nxt = tee(chain.coords[::-1])
        next(nxt, None)
        prevs_: List[Tuple[float, float]] = []
        for cur_vert, nxt_vert in zip(cur, nxt):
            if cur_vert[0] != nxt_vert[0]:
                prevs_.append(nxt_vert)

        prevs_ = prevs_[1:] + [prevs_[0]]
        prevs_ = prevs_[::-1]
        prevs.extend(prevs_)

    event_map = list(zip(prevs, currs, nexts))
    sorted_by_x = sorted(event_map, key=lambda point: point[1][0])

    altitude, prev_x = 0., 0.
    active_event_counter = 0
    for (prv_x, _), (cur_x, _), (nxt_x, _) in sorted_by_x:

        if active_event_counter > 0:
            deltax = cur_x - prev_x
            altitude += active_event_counter * deltax

        if prv_x > cur_x < nxt_x:
            active_event_counter += 1
        elif prv_x < cur_x > nxt_x:
            active_event_counter -= 1

        prev_x = cur_x

    return altitude
