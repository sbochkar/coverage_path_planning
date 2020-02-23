"""Logic for computing cone of bisection."""
from math import atan2, cos, pi, sin
from typing import Any, Optional

import numpy as np

from shapely.geometry import LineString, Polygon, Point
from shapely.affinity import rotate, scale

from pkg.poly_operations.others.adjacency_edges import get_neighbor_map
from log_utils import get_logger


# pylint: disable=invalid-name
logger = get_logger("cone_of_bisection")
# pylint: enable=invalid-name


def get_cone_of_bisection(polygon: Polygon, vert: Point) -> Optional[Any]:
    """Compute cone of bisection given a reflex vertex and polygon.

    Args:
        polygon (Polygon): Shapely object representing the polygon.
        vert (Point): Shapelyt object representing reflex vertex.
    """
    diameter = polygon.length

    # TODO: Can probably avoid calling this function.
    vert_prev, vert_next = get_neighbor_map(polygon).get((vert.x, vert.y), (None, None))

    if vert_prev is None or vert_next is None:
        logger.debug("Error looking up adjacent vertices of reflex vertex.")
        return None

    edge_prev = LineString([vert_prev, (vert.x, vert.y)])
    edge_next = LineString([(vert.x, vert.y), vert_next])

    # Rotate and scale to form edges of a cone.
    edge_prev_new = rotate(edge_prev, 180, origin=vert)
    edge_prev_new = scale(edge_prev_new, origin=vert,
                          xfact=diameter / edge_prev.length, yfact=diameter / edge_prev.length)
    edge_next_new = rotate(edge_next, 180, origin=vert)
    edge_next_new = scale(edge_next_new, origin=vert,
                          xfact=diameter / edge_next.length, yfact=diameter / edge_next.length)

    import code; code.interact(local=locals())



    ## TODO: Replace logic below with just using edge and affine transformations to form cone.

    ## Find the angle of adjacent edges w.r.t x-axis.
    #theta_next = atan2(abs(vert_next[1] - vert.y), abs(vert_next[0] - vert.x))
    #theta_prev = atan2(abs(vert_prev[1] - vert.y), abs(vert_prev[0] - vert.x))

    ## Consider several cases which will determine the measurement for the cone of bisection
    #if theta_next < 0 > theta_prev:
    #    angle = abs(theta_next - theta_prev)
    #    orientation = pi + theta_next + angle / 2
    #elif theta_next <= 0 <= theta_prev:
    #    angle = theta_prev - theta_next
    #    orientation = pi + theta_next + angle / 2
    #elif theta_next > 0 <= theta_prev:
    #    angle = abs(theta_prev - theta_next)
    #    orientation = pi + theta_next + angle / 2
    #elif theta_next > 0 > theta_prev:
    #    angle = 2 * pi - (theta_next - theta_prev)
    #    orientation = pi + theta_next + angle / 2
    #else:
    #    # TODO: Improve this
    #    print("ERROR: CONE OF BISECTION<: IF DID NTO CAPTURE")

    #p = []

    #p.append(vert)
    #for i in np.arange(orientation - angle / 2, orientation + angle / 2, 0.1):
    #    x = diameter * cos(i)geom, angle, origin='center', use_radians=False)¶
    #    y = diameter * sin(i)

    #    new_x = vert[0] + x
    #    new_y = vert[1] + y

    #    p.append((new_x, new_y))

    #x = diameter * cos(orientation + angle / 2)
    #y = diameter * sin(orientation + angle / 2)

    #new_x = vert[0] + x
    #new_y = vert[1] + y

    #p.append((new_x, new_y))

    #return p
