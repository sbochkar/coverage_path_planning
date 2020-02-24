"""Module for computing altitude of polygons."""
from typing import Dict, Tuple
import sys

from shapely.geometry import Polygon
from shapely.affinity import rotate

from pkg.poly_operations.others.adjacency_edges import get_neighbor_map
from pkg.poly_operations.others.directions import get_directions_set


def get_min_altitude(polygon: Polygon):
    """Computes minimum altitude for a given polygon.

    Function perofrm a series of call to get_altitude, to find the min altitude
    Things to look out for:
            min_alt init value might not be high ebough

    """
    min_alt = sys.float_info.max
    min_dir = 0
    for theta in get_directions_set(polygon):
        test_alt = get_altitude(polygon, theta)
        if test_alt <= min_alt:
            min_alt = test_alt
            min_dir = theta

    return min_alt, min_dir


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
    polygon = rotate(polygon, -theta)
    neighbors_map = get_neighbor_map(polygon)

    sorted_by_x = sorted(neighbors_map.keys(), key=lambda point: point[0])

    altitude = 0.
    active_event_counter = 0
    prev_x = -sys.float_info.max
    checked_verts = []
    for i, vert in enumerate(sorted_by_x):

        if vert in checked_verts:
            continue

        v_x, _ = vert
        (adj_x_1, _), (adj_x_2, _) = neighbors_map[vert]

        if i > 0:
            deltax = v_x - prev_x
            altitude += active_event_counter * deltax
        prev_x = v_x

        if (adj_x_1 > v_x) and (adj_x_2 > v_x):
            active_event_counter += 1
        elif (adj_x_1 < v_x) and (adj_x_2 < v_x):
            active_event_counter -= 1

        if (adj_x_1 > v_x) and (adj_x_2 == v_x):
            if resolve_local_equality(neighbors_map, neighbors_map[vert][1], vert) == 1:
                active_event_counter += 1
                checked_verts.append(neighbors_map[vert][1])
        if (adj_x_2 > v_x) and (adj_x_1 == v_x):
            if resolve_local_equality(neighbors_map, neighbors_map[vert][0], vert) == 1:
                active_event_counter += 1
                checked_verts.append(neighbors_map[vert][0])
        if (adj_x_1 < v_x) and (adj_x_2 == v_x):
            if resolve_local_equality(neighbors_map, neighbors_map[vert][1], vert) == -1:
                active_event_counter -= 1
                checked_verts.append(neighbors_map[vert][1])
        if (adj_x_2 < v_x) and (adj_x_1 == v_x):
            if resolve_local_equality(neighbors_map, neighbors_map[vert][0], vert) == -1:
                active_event_counter -= 1
                checked_verts.append(neighbors_map[vert][0])

        # TODO: Implement the case where both x coords are equal to curr x.

    return altitude


def resolve_local_equality(neighbors_map: Dict[Tuple[float, float], Tuple[Tuple[float, float]]],
                           curr_vert: Tuple[float, float], prev_vert: Tuple[float, float]):
    """Recursivly determine the action in the case where adjacent edges are collinear."""
    adjacent_verts = list(neighbors_map[curr_vert])
    if prev_vert in adjacent_verts:
        adjacent_verts.remove(prev_vert)

    x_curr, _ = curr_vert
    x_next, _ = adjacent_verts[0]

    if x_next > x_curr:
        return 1
    if x_next < x_curr:
        return -1
    return resolve_local_equality(neighbors_map, adjacent_verts[0], curr_vert)
