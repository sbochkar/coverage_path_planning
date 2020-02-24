from  itertools import combinations_with_replacement
from typing import List, Tuple, Optional

from shapely.affinity import rotate
from shapely.geometry import Polygon, Point, LinearRing, LineString, CAP_STYLE
from shapely.geometry.polygon import orient
from shapely.ops import snap

from pkg.aux.altitudes.altitude import get_min_altitude
from pkg.poly_operations.others.directions import get_directions_set
from pkg.poly_operations.others.adjacency_edges import get_neighbor_map_shp
from .visib_polyg import compute_vis_polygon
from log_utils import get_logger


# pylint: disable=invalid-name
logger = get_logger("cuts")
# pylint: enable=invalid-name


LINE_LENGTH_THRESHOLD = 0.001
BUFFER_RADIUS = 0.0001


def find_optimal_cut(polygon: Polygon, vertex: Point) -> LineString:
    """Given a polygon and a reflex vertex, finds and returns an optimal decomposing cut.

    TODO: Does not support cuts for polygons with holes.
    TODO: Can narrow down the search space by only exploring some directions.

    Args:
        polygon (List[List[Any]]): Polygon in cannonical form.
        vertex (Tuple[float]): Vertex from which to search an optimal cut.

    Returns:
        cut (LineString): LineString object representing optimal cut.
    """
    min_altitude, _ = get_min_altitude(polygon)
    min_altitude_solution = None
    for edge in find_cut_space(polygon, vertex):
        for point in edge.coords:
            p_l, p_r = perform_cut(polygon, [vertex, Point(point)])
            a_l, theta_l = get_min_altitude(Polygon(p_l))
            a_r, theta_r = get_min_altitude(Polygon(p_r))

            if round(a_l + a_r, 5) < round(min_altitude, 5):
                min_altitude = a_l + a_r
                min_altitude_solution = Point(point), theta_l, theta_r

            # # TODO: Add this later when the rest of optimization engine is stabilized.
            # for dir_1, dir_2 in combinations_with_replacement(get_directions_set(polygon), 2):
            #     # transition_point = find_best_transition_point(edge, vertex, dir_1, dir_2)

            #     p_l, p_r = perform_cut(polygon, [vertex, transition_point])
            #     a_l = alt.get_altitude(Polygon(p_l), dir_1)
            #     a_r = alt.get_altitude(Polygon(p_r), dir_2)

            #     if round(a_l + a_r, 5) < round(min_altitude, 5):
            #         min_altitude = a_l + a_r
            #         min_altitude_solution = transition_point, dir_1, dir_2

    print(min_altitude_solution)
    return min_altitude_solution


def find_cut_space(polygon: Polygon, vertex: Point) -> List[LineString]:
    """Generate the cut space at vertex using Visilibity library.

    Args:
        polygon (Polygon): Shapely object representing the polygon.
        vertex (Point): Shapele object representing the point.

    Returns:
        cut_space (List): List of LineStrings representing cut space.
    """
    vert_prev, vert_next = get_neighbor_map_shp(polygon).get((vertex.x, vertex.y), (None, None))

    # TODO: Don't know how expensive this operation is.
    vis_poly_cur = compute_vis_polygon(polygon, vertex)
    vis_poly_prev = compute_vis_polygon(polygon, vert_prev)
    vis_poly_next = compute_vis_polygon(polygon, vert_next)

    cone_of_bisection = vis_poly_cur.intersection(vis_poly_prev).intersection(vis_poly_next)
    cone_of_bisection = cone_of_bisection.intersection(polygon)
    cone_of_bisection = orient(cone_of_bisection)
    cone_of_bisection = snap(cone_of_bisection, polygon, tolerance=0.0001)

    buffered_cone_lines: List[Polygon] = []
    for idx, coord in enumerate(cone_of_bisection.exterior.coords[:-1]):
        edge = LineString([coord, cone_of_bisection.exterior.coords[idx + 1]])
        buffered_cone_lines.append(edge.buffer(BUFFER_RADIUS, cap_style=CAP_STYLE.flat))

    cut_space: List[LineString] = []
    for idx, coord in enumerate(polygon.exterior.coords[:-1]):
        edge = LineString([coord, polygon.exterior.coords[idx + 1]])

        for cone_line in buffered_cone_lines:
            result = cone_line.intersection(edge)
            if result.geom_type != "LineString":
                continue
            if result.length <= LINE_LENGTH_THRESHOLD:
                continue

            cut_space.append(result)
    return cut_space


def find_transition_point(cone_line: LineString, theta: float, cut_origin: Point) -> Point:
    """
    Returns transition for a polygon, a cut space segment, and a direction of
            altitude

    Function will perform a series of geometric functions to return a transition
            point.

    Args:
        cone_line (LineString): Line segment from the cone.
        theta (float): direction w.r.t. x-axis
        cut_origin (Point): Point representing the origin of the cut.
    Returns:
        trans_point (Point): a transition point.
    """
    rotated_cone_line = rotate(cone_line, -theta, origin=Point(0, 0))
    rotated_cut_origin = rotate(cut_origin, -theta, origin=Point(0, 0))

    y_s_min_idx, y_s_min = min(enumerate(rotated_cone_line.coords[:-1]), key=lambda x: x[1])
    y_s_max_idx, y_s_max = max(enumerate(rotated_cone_line.coords[:-1]), key=lambda x: x[1])

    x_s_min_idx, x_s_min = min(enumerate(rotated_cone_line.coords[:-1]), key=lambda x: x[0])
    x_s_max_idx, x_s_max = max(enumerate(rotated_cone_line.coords[:-1]), key=lambda x: x[0])

    # Check the easy cases first
    if x_s_min[0] >= rotated_cut_origin.x:
        return Point(cone_line.coords[x_s_min_idx])

    if x_s_max[0] <= rotated_cut_origin.x:
        return Point(cone_line.coords[x_s_max_idx])
#	if y_s_min[1] >= rotated_cut_origin[1]:
#		return cone_line[y_s_min_idx]
#	elif y_s_max[1] <= rotated_cut_origin[1]:
#		return cone_line[y_s_max_idx]
    # Find the intersection which corresponds to transition point
    hyperplane = LineString([(rotated_cut_origin.x, y_s_max[1] + 1),
                             (rotated_cut_origin.y, y_s_min[1] - 1)])
    transition_point = rotated_cone_line.intersection(hyperplane)

    if not transition_point:
        print("Not suppose to happen")
    return rotate(transition_point, theta, origin=Point(0, 0))


def find_best_transition_point(cone_line: LineString,
                               cut_origin: Point, dir_l: float, dir_r: float) -> Optional[Point]:
    """Find the best transition point from the left and right polygon.

    Given left and right polygons, cut segment, and two altitude directions,
    return the best transition point.

    Args:
        cone_line (LineString): Shapely object representing cone line.
        cut_origin (Point): Shapely object representing the root vertex of the cut.
        dir_l (float): direction to explore.
        dir_r (float): direction to explore:
    Returns:
        trans_point (Point): a transition point
    """
    transition_l = find_transition_point(cone_line, dir_l, cut_origin)
    transition_r = find_transition_point(cone_line, dir_r, cut_origin)
    x_s, y_s = cone_line.coords[0]

    dt_l = (transition_l.x - x_s)**2 + (transition_l.y - y_s)**2
    dt_r = (transition_r.x - x_s)**2 + (transition_r.y - y_s)**2

    if dt_l >= dt_r:
        return transition_r

    rotated_cone_line_l = rotate(cone_line, -dir_l, origin=Point(0, 0))
    ds_l = abs(rotated_cone_line_l.coords[1][0] - rotated_cone_line_l.coords[0][0])

    rotated_cone_line_r = rotate(cone_line, -dir_r, origin=Point(0, 0))
    ds_r = abs(rotated_cone_line_r.coords[1][0] - rotated_cone_line_r.coords[0][0])

    if ds_l > ds_r:
        return transition_l
    return transition_r


def perform_cut(P, e):
    """
    Split up P into two polygons by cutting along e
    """
    v, w = e
    chain = P.exterior

    distance_to_v = chain.project(Point(v))
    distance_to_w = chain.project(Point(w))

    if distance_to_w > distance_to_v:
        if round(distance_to_w, 4) >= round(chain.length, 4):
            distance_to_v = chain.project(Point(v))
            left_chain, right_chain = cut(chain, distance_to_v)

            p_l = left_chain.coords[:]
            p_r = right_chain.coords[:]
        else:
            if distance_to_v == 0:
                distance_to_w = chain.project(Point(w))
                right_chain, remaining = cut(chain, distance_to_w)

                p_l = remaining.coords[:]
                p_r = right_chain.coords[:]
            else:
                cut_v_1, cut_v_2 = cut(chain, distance_to_v)

                distance_to_w = cut_v_2.project(Point(w))
                right_chain, remaining = cut(cut_v_2, distance_to_w)

                p_l = cut_v_1.coords[:]+remaining.coords[:-1]
                p_r = right_chain.coords[:]

    else:
        if round(distance_to_v, 4) >= round(chain.length, 4):
            distance_to_w = chain.project(Point(w))
            right_chain, remaining = cut(chain, distance_to_w)

            p_l = remaining.coords[:]
            p_r = right_chain.coords[:]
        else:
            if distance_to_w == 0:
                distance_to_v = chain.project(Point(v))
                right_chain, remaining = cut(chain, distance_to_v)

                p_l = remaining.coords[:]
                p_r = right_chain.coords[:]
            else:
                cut_v_1, cut_v_2 = cut(chain, distance_to_w)


                distance_to_v = cut_v_2.project(Point(v))
                right_chain, remaining = cut(cut_v_2, distance_to_v)
                p_l = cut_v_1.coords[:]+remaining.coords[:-1]
                p_r = right_chain.coords[:]

    return p_l, p_r


def cut(line, distance):
    """
    Splicing a line
    Credits go to author of the shapely manual
    """
    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        print("ERROR: CUT BEYONG LENGTH")
        print(line)
        print(distance)
        return [LineString(line), []]

    coords = list(line.coords)
    pd = 0
    #for i, p in enumerate(coords):
    for i in range(len(coords)):
        if i > 0:
            pd = LineString(coords[:i+1]).length
        #pd = line.project(Point(p))
        if pd == distance:
            return [LineString(coords[:i+1]),
                    LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [LineString(coords[:i] + [(cp.x, cp.y)]),
                    LineString([(cp.x, cp.y)] + coords[i:])]
        if i == len(coords)-1:
            cp = line.interpolate(distance)
            return [LineString(coords[:i] + [(cp.x, cp.y)]),
                    LineString([(cp.x, cp.y)] + coords[i:])]
