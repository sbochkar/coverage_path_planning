"""Module for locating reflex vertices in a polygon."""
from itertools import chain
from typing import Tuple

from pkg.poly_operations.others.adjacency_edges import get_edge_adjacency_as_dict


def find_reflex_vertices(polygon):
    """Return a list of reflex vertices in polygon.

    TODO: Revisit the simiplified algorithm.

    Function will iterate over all vertices in polygon and return a list of reflex
    vertices

    Args:
        polygon (ext, [int]): tuple of list of (x,y) vertices ext is a ccw list of vertices
                              for boundary, int is cw list of vertices for holes.
    Returns:
        List of reflex verecies.
    """
    # TODO: When we switch to new data structure for decompositions. Switch to this method.
    # ext, holes = polygon

    # vert_iter: Tuple[Tuple[float, float]] = []
    # for boundary in [ext, *holes]:
    #     prev_verts = [boundary[-1], *boundary[:-1]]
    #     curr_verts = boundary
    #     next_verts = [*boundary[1:], boundary[0]]

    #     vert_iter.extend(list(zip(prev_verts, curr_verts, next_verts)))

    # reflex_verts2 = []
    # for prev_vert, curr_vert, next_vert in chain(vert_iter):
    #     dx_1 = float(curr_vert[0]) - float(next_vert[0])
    #     dy_1 = float(curr_vert[1]) - float(next_vert[1])
    #     dx_2 = float(prev_vert[0]) - float(curr_vert[0])
    #     dy_2 = float(prev_vert[1]) - float(curr_vert[1])
    #     if dx_1 * dy_2 - dy_1 * dx_2 > 0.0:
    #         reflex_verts2.append(curr_vert)

    reflex_verts = []
    adj_dict = get_edge_adjacency_as_dict(polygon)

    for mid_vert, adj_verts in adj_dict.items():
        prev_vert, next_vert = adj_verts

        dx_1 = float(mid_vert[1][0]) - float(next_vert[1][0])
        dy_1 = float(mid_vert[1][1]) - float(next_vert[1][1])
        dx_2 = float(prev_vert[1][0]) - float(mid_vert[1][0])
        dy_2 = float(prev_vert[1][1]) - float(mid_vert[1][1])

        if dx_1 * dy_2 - dy_1 * dx_2 < 0.0:
            reflex_verts.append(mid_vert)

    return reflex_verts
