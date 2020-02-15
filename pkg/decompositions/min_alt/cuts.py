from shapely.geometry import Polygon, Point, LinearRing, LineString
from shapely.geometry.polygon import orient
from ...aux.altitudes import altitude as alt
from ...aux.geometry import rotation
from ...poly_operations.others import chain_combination
from ...poly_operations.others import reflex
from ...poly_operations.others import directions
from ...poly_operations.others import adjacency_edges as adj_e

from .cone_of_bisection import get_cone_of_bisection
from .visib_polyg import compute

from math import sqrt


LINE_LENGTH_THRESHOLD = 0.001
BUFFER_RADIUS = 0.0001

# Chech if three points are collinear
def collinear(p1, p2, p3):
	return abs((p1[1]-p2[1])*(p1[0]-p3[0])-(p1[1]-p3[1])*(p1[0]-p2[0])) <= 1e-9

def euc_distance(p1, p2):
	return sqrt((p2[1]-p1[1])**2+(p2[0]-p1[0])**2)

import itertools
def form_collinear_dictionary(s, v):

	collinear_dict = {}
	# Check all pairs of si in s, to see if their endpoitns are collinear
	for si in s:
		if collinear(v[1], si[0], si[1]):
			if euc_distance(v[1], si[0]) < euc_distance(v[1], si[1]):
				collinear_dict[si[1]] = si[0]
			else:
				collinear_dict[si[0]] = si[1]

	for comb in itertools.combinations(s, 2):
		si1 = comb[0];	si2 = comb[1]

		# if one of the points are the same; ignore
		pt_l1 = si1[0]; pt_l2 = si1[1]
		pt_r1 = si2[0]; pt_r2 = si2[1]

		if (pt_l1 == pt_r1) or (pt_l1 == pt_r2) or (pt_r2 == pt_l2) or (pt_r1 == pt_l2):
			continue


		# Case 1 to consider	
		if collinear(v[1], pt_l1, pt_r1):
			if euc_distance(v[1], pt_l1) < euc_distance(v[1], pt_r1):
				collinear_dict[pt_r1] = pt_l1
			else:
				collinear_dict[pt_l1] = pt_r1

		# Case 2 to consider	
		if collinear(v[1], pt_l2, pt_r1):
			if euc_distance(v[1], pt_l2) < euc_distance(v[1], pt_r1):
				collinear_dict[pt_r1] = pt_l2
			else:
				collinear_dict[pt_l2] = pt_r1

		# Case 3 to consider	
		if collinear(v[1], pt_l2, pt_r2):
			if euc_distance(v[1], pt_l2) < euc_distance(v[1], pt_r2):
				collinear_dict[pt_r2] = pt_l2
			else:
				collinear_dict[pt_l2] = pt_r2

		# Case 4 to consider	
		if collinear(v[1], pt_l1, pt_r2):
			if euc_distance(v[1], pt_l1) < euc_distance(v[1], pt_r2):
				collinear_dict[pt_r2] = pt_l1
			else:
				collinear_dict[pt_l1] = pt_r2

	return collinear_dict


def find_optimal_cut(polygon: Polygon, vertex: Point):
    """Given a polygon and a reflex vertex, finds and returns an optimal decomposing cut.

    Args:
        polygon (List[List[Any]]): Polygon in cannonical form.
        vertex (Tuple[float]): Vertex from which to search an optimal cut.
    """
    pois = []

    min_altitude, _ = alt.get_min_altitude(polygon)
    search_space = find_cut_space(polygon, vertex)
    min_altitude_idx = None

    # First, find edges on cut space that are collinear with reflex vertex
    collinear_dict = form_collinear_dictionary(search_space, vertex)
    for si in search_space:
        # Process each edge si, have to be cw
        lr_si = LinearRing([vertex[1]] + si)
        if lr_si.is_ccw:
            si = [si[1]] + [si[0]]


        cut_point = si[0]
        p_l, p_r = perform_cut(polygon, [vertex[1], cut_point])

        dirs_left = directions.get_directions_set([p_l, []])
        dirs_right = directions.get_directions_set([p_r, []])

        # Look for all transition points
        for dir1 in dirs_left:
            for dir2 in dirs_right:
                tp = find_best_transition_point(si, vertex[1], dir1, dir2)
                # Here check if tp is collinear with vertex
                # If so and invisible, replace with visible collinear point
                if tp in collinear_dict.keys():
                    pois.append((collinear_dict[tp], dir1, dir2))
                else:
                    pois.append((tp, dir1, dir2))

    # Evaluate all transition points
    for case in pois:
        p_l, p_r = perform_cut(polygon, [vertex[1], case[0]])
        a_l = alt.get_altitude([p_l, []], case[1])
        a_r = alt.get_altitude([p_r, []], case[2])

        #from math import degrees

        if round(a_l+a_r, 5) < round(min_altitude, 5):
                min_altitude = a_l+a_r
                min_altitude_idx = case
            

    return min_altitude_idx


def find_cut_space(polygon, vertex):
    """
    Generate the cut space at vertex using Visilibity library.
    """
    c_of_b = get_cone_of_bisection(polygon, vertex)
    c_of_b = Polygon(c_of_b)

    polygon = Polygon(*polygon)

    intersection = c_of_b.intersection(polygon)

    intersection = get_closest_intersecting_polygon(intersection, vertex)


    P_vis = []; vis_holes = []
    P_vis.append(intersection.exterior.coords[:])
    for hole in intersection.interiors:
            vis_holes.append(hole.coords[:])
    P_vis.append(vis_holes)

    point_x, point_y = visib_polyg.compute(vertex, P_vis)
    visible_polygon = Polygon(zip(point_x, point_y))
    # Debug visualization
    # Plot the polygon itself

    # At this point, we have visibility polygon.
    # Now we need to find edges of visbility polygon which are on the boundary

    #visible_polygon = shapely.geometry.polygon.orient(Polygon(zip(point_x, point_y)),-1)
    visible_polygon_ls = LineString(visible_polygon.exterior.coords[:])
    visible_polygon_ls_buffer = visible_polygon_ls.buffer(BUFFER_RADIUS)

    ext_ls = LineString(polygon.exterior)
    holes_ls = []
    for interior in polygon.interiors:
        holes_ls.append(LineString(interior))

    # Start adding cut space on the exterior
    cut_space = []
    common_items = []

    #common_items = ext_ls.intersection(visible_polygon_ls)
    common_items = ext_ls.intersection(visible_polygon_ls_buffer) # Buffer gives better results

    # Filter out very small segments
    # Add environment first
    if common_items.geom_type == "MultiLineString":
        for element in common_items:
            line = element.coords[:]
            # Examine each edge of the linestring
            for i in range(len(line)-1):
                edge = line[i:i+2]
                edge_ls = LineString(edge)

                if edge_ls.length > LINE_LENGTH_THRESHOLD:
                    cut_space.append(edge)
    elif common_items.geom_type == "LineString":
        # Examine each edge of the linestring
        line = common_items.coords[:]
        for i in range(len(line)-1):
            edge = line[i:i+2]
            edge_ls = LineString(edge)

            if edge_ls.length > LINE_LENGTH_THRESHOLD:
                cut_space.append(edge)
    elif common_items.geom_type == "GeometryCollection":
        for item in common_items:
            if item.geom_type == "MultiLineString":
                for element in item:
                    line = element.coords[:]
                    # Examine each edge of the linestring
                    for i in range(len(line)-1):
                        edge = line[i:i+2]
                        edge_ls = LineString(edge)

                        if edge_ls.length > LINE_LENGTH_THRESHOLD:
                            cut_space.append(edge)

            elif item.geom_type == "LineString":
                # Examine each edge of the linestring
                line = item.coords[:]
                for i in range(len(line)-1):
                    edge = line[i:i+2]
                    edge_ls = LineString(edge)

                    if edge_ls.length > LINE_LENGTH_THRESHOLD:
                        cut_space.append(edge)


    ## Now start adding the hole boundaries
    for interior in polygon.interiors:
        common_items = interior.intersection(visible_polygon_ls_buffer)
        if common_items.geom_type == "LineString":
            line = common_items.coords[:]
            for i in range(len(line)-1):
                edge = line[i:i+2]
                edge_ls = LineString(edge)

                if edge_ls.length > LINE_LENGTH_THRESHOLD:
                    cut_space.append(edge)
        elif common_items.geom_type == "MultiLineString":
            for element in common_items:
                line = element.coords[:]
                # Examine each edge of the linestring
                for i in range(len(line)-1):
                    edge = line[i:i+2]
                    edge_ls = LineString(edge)

                    if edge_ls.length > LINE_LENGTH_THRESHOLD:
                        cut_space.append(edge)
        elif common_items.geom_type == "GeometryCollection":
            for item in common_items:

                if item.geom_type == "LineString":
                    line = item.coords[:]
                    for i in range(len(line)-1):
                        edge = line[i:i+2]
                        edge_ls = LineString(edge)

                        if edge_ls.length > LINE_LENGTH_THRESHOLD:
                            cut_space.append(edge)
                elif item.geom_type == "MultiLineString":
                    for element in item:
                        line = element.coords[:]
                        # Examine each edge of the linestring
                        for i in range(len(line)-1):
                            edge = line[i:i+2]
                            edge_ls = LineString(edge)

                            if edge_ls.length > LINE_LENGTH_THRESHOLD:
                                cut_space.append(edge)


    # cut_space could be lines our of order in no particular direciton
    # We want the cut space to be cw oriented

    # First form a list of points
#	temp_points_list = []
#	for line in cut_space:
#		temp_points_list.append(line[0]); temp_points_list.append(line[1]) 
#
#	# Form a polygon with the exterior the points geenrated above
#	temp_poly = Polygon(temp_points_list)
#
#	# Orient the polygon's exterior clockwise
#	orient(temp_poly, sign=-1)
#
#	# Form the final oriented cut space chain
#	cut_space_ring = temp_poly.exterior.coords[:-1]


#	cut_space_chain = []
#	cut_space_chain.append(cut_space[0][0])
#	for line in cut_space:
#		cut_space_chain.append(line[1])
#
#	if LinearRing(cut_space_chain+[v[1]]).is_ccw:
#		cut_space_ring = cut_space_chain[::-1]
#	else:
#		cut_space_ring = cut_space_chain[:]

	# PLOTTING
#	import pylab as p
#	# Plot the polygon itself
#	x, y = P.exterior.xy
#	p.plot(x, y)
#	# plot the intersection of the cone with the polygon
#	intersection_x, intersection_y = intersection.exterior.xy
#	p.plot(intersection_x, intersection_y)
#	p.show()

#	return cut_space_ring
    return cut_space


def get_closest_intersecting_polygon(intersection, v):


	# Need to check the type of intersection
	if intersection.is_empty:
		print("ERROR: intersection of cone with polygon is empty")
		return None
	elif intersection.geom_type == "Point": 
		print("ERROR: intersection of cone with polygon is a point")
		return None
	elif intersection.geom_type == "LineString":
		print("ERROR: intersection of cone with polygon is a line")
		return None
	elif intersection.geom_type == "MultiLineString":
		print("ERROR: intersection of cone with polygon is a multiline")
		return None
	elif intersection.geom_type == "Polygon":
		return intersection
	elif intersection.geom_type == "MultiPolygon":
		for poly in intersection:
			if poly.intersects(Point(v[1])):
				return poly
	elif intersection.geom_type == "GeometryCollection":
		for shape in intersection:
			result =  get_closest_intersecting_polygon(shape, v)
			if result is not None:
				return result


def find_transition_point(s_orig, theta, cut_origin):
	"""
	Returns transition for a polygon, a cut space segment, and a direction of
		altitude

	Function will perform a series of geometric functions to return a transition
		point.

	Args:
		s: a straight line segment
		theta: direction w.r.t. x-axis
		cut_origin: vertex of origin of cone of bisection
	Returns:
		trans_point: a transition point
	"""

	s = rotation.rotate_points(s_orig, -theta)
	cut_origin = rotation.rotate_points([cut_origin], -theta)[0]

	y_s_min_idx, y_s_min = min(enumerate(s), key=lambda x: x[1][1])
	y_s_max_idx, y_s_max = max(enumerate(s), key=lambda x: x[1][1])

	x_s_min_idx, x_s_min = min(enumerate(s), key=lambda x: x[1][0])
	x_s_max_idx, x_s_max = max(enumerate(s), key=lambda x: x[1][0])

	# Check the easy cases first
	if x_s_min[0] >= cut_origin[0]:
		return s_orig[x_s_min_idx]
	elif x_s_max[0] <= cut_origin[0]:
		return s_orig[x_s_max_idx]
#	if y_s_min[1] >= cut_origin[1]:
#		return s_orig[y_s_min_idx]
#	elif y_s_max[1] <= cut_origin[1]:
#		return s_orig[y_s_max_idx]
	else:
		# Find the intersection which corresponds to transition point
		hyperplane = LineString([(cut_origin[0], y_s_max[1]+1), (cut_origin[0], y_s_min[1]-1)])
		#hyperplane = LineString([(x_s_min[0], cut_origin[1]), (cut_origin[0], cut_origin[1])])
		cut_segment = LineString(s)
		transition_point = cut_segment.intersection(hyperplane)

		if not transition_point:
			print("Not suppose to happen")
		return rotation.rotate_points([transition_point.coords[0]], theta)[0]







def find_best_transition_point(s, cut_origin, dir_l, dir_r):
	"""
	Find the best transition point from the left and right polygon

	Given left and right polygons, cut segment, and two altitude directions,
	return the best transition point.

	Args:

		s:
		dir_l:
		dir_r:
	Returns:
		trans_point: a transition point
	"""


	from math import degrees
	t_l = find_transition_point(s, dir_l, cut_origin)
	t_r = find_transition_point(s, dir_r, cut_origin)
	x_s, y_s = s[0]

	x_t_l, y_t_l = t_l
	x_t_r, y_t_r = t_r

	dt_l = (x_t_l-x_s)**2+(y_t_l-y_s)**2
	dt_r = (x_t_r-x_s)**2+(y_t_r-y_s)**2

	if dt_l >= dt_r:
		return t_r
	else:

		s_l = rotation.rotate_points(s,-dir_l)
		ds_l = abs(s_l[1][0]-s_l[0][0])

		s_r = rotation.rotate_points(s,-dir_r)
		ds_r = abs(s_r[1][0]-s_r[0][0])

		if ds_l > ds_r:
			return t_l
		else:
			return t_r


def perform_cut(P, e):
	"""
	Split up P into two polygons by cutting along e
	"""

	v = e[0]
	w = e[1]
	chain = LineString(P[0]+[P[0][0]])

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
	#			p_l = right_chain.coords[:] 
	#			p_r = remaining.coords[:]+cut_v_1.coords[:]

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
			return [
				LineString(coords[:i+1]),
				LineString(coords[i:])]
		if pd > distance:
			cp = line.interpolate(distance)
			return [
				LineString(coords[:i] + [(cp.x, cp.y)]),
				LineString([(cp.x, cp.y)] + coords[i:])]
		if i == len(coords)-1:
			cp = line.interpolate(distance)
			return [
				LineString(coords[:i] + [(cp.x, cp.y)]),
				LineString([(cp.x, cp.y)] + coords[i:])]


def iterative_project(line, distance):
    """
    To account for self crossing edges
    """
    pass
