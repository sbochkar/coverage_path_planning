from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LinearRing
from shapely.geometry import LineString
from math import sqrt
from math import atan2
from math import pi
from math import cos
from math import sin
import numpy as np
import visilibity as vis # Need to place somewhere


def find_optimal_cut(P, v):
	"""
	Find optimal cut
	"""


	pois = []

	min_altitude, theta = alt.get_min_altitude(P)

	s = find_cut_space(P, v)

	min_altitude_idx = None

	for si in s:
		# Process each edge si, have to be cw
		lr_si = LinearRing([v[1]]+si)
		if lr_si.is_ccw:
			#print lr_si
			#print lr_si.is_ccw
			si = [si[1]]+[si[0]]
			#print si

		cut_point = si[0]
		#print P, v, cut_point
		p_l, p_r = perform_cut(P, [v[1], cut_point])
		#print p_l, p_r

		dirs_left = directions.get_directions_set([p_l, []])
		dirs_right = directions.get_directions_set([p_r, []])

		#print dirs_left
		#print list(degrees(dir) for dir in dirs_left)
		#print get_altitude([p_l,[]], 3.5598169831690223)
		#print get_altitude([p_r,[]], 0)

		# Look for all transition points
		for dir1 in dirs_left:
			for dir2 in dirs_right:
				tp = find_best_transition_point(si, v[1], dir1, dir2)
				pois.append((tp, dir1, dir2))

	# Evaluate all transition points
	for case in pois:
		p_l, p_r = perform_cut(P, [v[1], case[0]])
		a_l = alt.get_altitude([p_l, []], case[1])
		a_r = alt.get_altitude([p_r, []], case[2])

		if a_l+a_r<=min_altitude:
			min_altitude = a_l+a_r
			min_altitude_idx = case
		

	#print min_altitude, min_altitude_idx[0], degrees(min_altitude_idx[1]), degrees(min_altitude_idx[2])
	return min_altitude_idx


def find_cut_space(P, v):
	"""
	Generate the cut space at v using Visilibity library.
	"""

	# Used for visilibity library
	epsilon = 0.0000001


	cone_of_bisection = find_cone_of_bisection(P, v)
	cone_of_bisection = Polygon(cone_of_bisection)

	P = Polygon(*P)
	intersection = cone_of_bisection.intersection(P)
	print("Intersection: %s"%intersection)

	# Debug visualization
	# Plot the polygon itself
#	import pylab as p
#	x, y = P.exterior.xy
#	p.plot(x, y)
#	x, y = cone_of_bisection.exterior.xy
#	p.plot(x, y)
#	x, y = intersection.exterior.xy
#	p.plot(x, y)
#	p.show()

	intersection = get_closest_intersecting_polygon(intersection, v)
	#Using the visilibity library, define the reflex vertex
	observer = vis.Point(*v[1])

	# Define the walls of intersection in Visilibity domain
	# To put into standard form, do this
	exterior_coords = intersection.exterior.coords[:-1]
	x_min_idx, x_min = min(enumerate(exterior_coords), key=lambda x: x[0])
	exterior_coords = exterior_coords[x_min_idx:]+exterior_coords[:x_min_idx]

	vis_intersection_wall_points = []
	for point in exterior_coords:
		vis_intersection_wall_points.append(vis.Point(*point))
	#print 'Walls in standard form : ',vis.Polygon(vis_intersection_wall_points).is_in_standard_form()

	#for i in range(len(vis_intersection_wall_points)):
		#print vis_intersection_wall_points[i].x(), vis_intersection_wall_points[i].y()
		#print point.x(), point.y()

	# Define the holes of intersection in Visilibity domain
	vis_intersection_holes = []
	for interior in intersection.interiors:
		vis_intersection_hole_points = []
		for point in list(interior.coords):
			vis_intersection_hole_points.append(vis.Point(*point))

		vis_intersection_holes.append(vis_intersection_hole_points)
		#print 'Hole in standard form : ',vis.Polygon(vis_intersection_hole_points).is_in_standard_form()

	# Construct a convinient list
	env = []
	env.append(vis.Polygon(vis_intersection_wall_points))
	for hole in vis_intersection_holes:
		env.append(vis.Polygon(hole))

	# Construct the whole envrionemt in Visilibity domain
	env = vis.Environment(env)

	# Construct the visible polygon
	observer.snap_to_boundary_of(env, epsilon)
	observer.snap_to_vertices_of(env, epsilon)

	vis_free_space = vis.Visibility_Polygon(observer, env, epsilon)
	#print vis_free_space.n()

	def save_print(polygon):
	    end_pos_x = []
	    end_pos_y = []
	    for i in range(polygon.n()):
	        x = polygon[i].x()
	        y = polygon[i].y()
	        
	        end_pos_x.append(x)
	        end_pos_y.append(y)
	                
	    return end_pos_x, end_pos_y 
	point_x , point_y  = save_print(vis_free_space)
	point_x.append(vis_free_space[0].x())
	point_y.append(vis_free_space[0].y())  


	###
	# At this point, we have visibility polygon.
	# Now we need to find edges of visbility polygon which are on the boundary


	#shp_visib = shapely.geometry.polygon.orient(Polygon(zip(point_x, point_y)),-1)
	shp_visib = Polygon(zip(point_x, point_y))
	shp_ls_visib = LineString(shp_visib.exterior.coords[:])
	shp_pl_visib = shp_ls_visib.buffer(0.001)

	shp_ls_exterior = LineString(P.exterior)
	shp_ls_interior = []
	for interior in P.interiors:
	 	shp_ls_interior.append(LineString(interior))

	# Start adding cut space on the exterior
	cut_space = []
	common_items = []
	#common_items = shp_ls_exterior.intersection(shp_ls_visib)
	common_items = shp_ls_exterior.intersection(shp_pl_visib)

	# Filter out very small segments
	if common_items.geom_type == "MultiLineString":
		for item in common_items:
			linestring = item.coords[:]

			# Examine each edge of the linestring
			for i in range(len(linestring)-1):
				edge = linestring[i:i+2]
				edge_ls = LineString(edge)

				if edge_ls.length > 0.02:
					cut_space.append(edge)

	elif common_items.geom_type == "LineString":

		# Examine each edge of the linestring
		linestring = common_items.coords[:]
		for i in range(len(linestring)-1):
			edge = linestring[i:i+2]
			edge_ls = LineString(edge)

			if edge_ls.length > 0.02:
				cut_space.append(edge)

	#print cut_space

	# Start adding cut space on the holes
	for interior in P.interiors:
		common_items = interior.intersection(shp_ls_visib)
		if common_items.geom_type == "GeometryCollection":
#			print common_items
			for item in common_items:
				if item.geom_type == "LineString":
					cut_space.append(item.coords[:])
		elif common_items.geom_type == "LineString":
			cut_space.append(common_items.coords[:])
		#Point, LineString, GeometryCollection

	#print cut_space

	# PLOTTING
	import pylab as p

	# Plot the polygon itself
	x, y = P.exterior.xy
	p.plot(x, y)

	# plot the intersection of the cone with the polygon
	intersection_x, intersection_y = intersection.exterior.xy
	p.plot(intersection_x, intersection_y)

#	#for interior in shp_intersection.interiors:
#	#	interior_x, interior_y = interior.xy
#	#	p.plot(interior_x, interior_y)
#
#	# Plot the reflex vertex
#	p.plot([observer.x()], [observer.y()], 'go')
#
#	p.plot(point_x, point_y)
#
	p.show()
	#print cut_space
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
			if not poly.intersection(v[1]).is_empty:
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

	s = rotate(s_orig, -theta)
	cut_origin = rotate([cut_origin], -theta)[0]

	y_s_min_idx, y_s_min = min(enumerate(s), key=itemgetter(1))
	y_s_max_idx, y_s_max = max(enumerate(s), key=itemgetter(1))

	x_s_min_idx, x_s_min = min(enumerate(s), key=itemgetter(0))
	x_s_max_idx, x_s_max = max(enumerate(s), key=itemgetter(0))

	# Check the easy cases first
	if y_s_min[1] >= cut_origin[1]:
		return s_orig[y_s_min_idx]
	elif y_s_max[1] <= cut_origin[1]:
		return s_orig[y_s_max_idx]
	else:
		# Find the intersection which corresponds to transition point
		hyperplane = LineString([(x_s_min[0], cut_origin[1]), (cut_origin[0], cut_origin[1])])
		cut_segment = LineString(s)
		transition_point = cut_segment.intersection(hyperplane)

		if not transition_point:
			print "Not suppose to happen"
		return rotate([transition_point.coords[0]], theta)[0]




def find_cone_of_bisection(P, v):
	"""
	Return a polygon representing the cone of bisection
	"""


	ext = P[0]
	holes = P[1]

	Pp = Polygon(P[0], P[1])

	minx, miny, maxx, maxy = Pp.bounds
	rad = sqrt((maxx-minx)**2+(maxy-miny)**2)	# "Dimater" of the polygon

	# Form an adjacency list for easy access to adjacent edges
	adj = adj_e.get_edge_adjacency_as_dict(P)

	#Find adjacent edges of v
	v_l = adj[v][1][1]; v_r = adj[v][0][1]

	# Find the angle of v_l with the x-axis
	theta_l = atan2(v_l[1]-v[1][1], v_l[0]-v[1][0])
	theta_r = atan2(v_r[1]-v[1][1], v_r[0]-v[1][0])

	# Consider several cases which will determine the measurement for the cone of bisection
	if theta_l < 0 and theta_r < 0:
		angle = abs(theta_l-theta_r)
		orientation = pi+theta_l+angle/2
	elif theta_l <= 0 and theta_r >= 0:
		angle = theta_r-theta_l
		orientation = pi+theta_l+angle/2
	elif theta_l > 0 and theta_r > 0:
		angle = theta_r-theta_l
		orientation = pi+theta_l+angle/2
	elif theta_l > 0 and theta_r < 0:
		angle = 2*pi-(theta_l-theta_r)
		orientation = pi+theta_l+angle/2
	else:
		print("ERROR: CONE OF BISECTION<: IF DID NTO CAPTURE")

	p = []

	p.append(v[1])
	for i in np.arange(orientation-angle/2,orientation+angle/2,0.1):
		x = rad*cos(i)
		y = rad*sin(i)

		new_x = v[1][0]+x
		new_y = v[1][1]+y

		p.append((new_x, new_y))

	x = rad*cos(orientation+angle/2)
	y = rad*sin(orientation+angle/2)

	new_x = v[1][0]+x
	new_y = v[1][1]+y

	p.append((new_x, new_y))

	return p


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


	t_l = find_transition_point(s, dir_l, cut_origin)
	t_r = find_transition_point(s, dir_r, cut_origin)

	x_s, y_s = s[0]

	x_t_l, y_t_l = t_l

	x_t_r, y_t_r = t_r

	dt_l = (x_t_l-x_s)**2+(y_t_l-y_s)**2
	dt_r = (x_t_r-x_s)**2+(y_t_r-y_s)**2

	#print t_l, t_r
	if dt_l >= dt_r:
		return t_r
	else:

		s_l = rotate(s,-dir_l)
		ds_l = abs(s_l[1][0]-s_l[0][0])

		s_r = rotate(s,-dir_r)
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
#	print distance_to_v, distance_to_w, e
	if distance_to_w > distance_to_v:
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
		if distance_to_w == 0:
			distance_to_v = chain.project(Point(v))
			right_chain, remaining = cut(chain, distance_to_v)

			p_l = remaining.coords[:]
			p_r = right_chain.coords[:]		
		else:
#			print "here"
			cut_v_1, cut_v_2 = cut(chain, distance_to_w)
			#print("Cut1: %s"%cut_v_1)
#			print("Cut2: %s"%cut_v_2)

			distance_to_v = cut_v_2.project(Point(v))
#			print("Dist: %2f. Length: %2f"%(distance_to_v, cut_v_2.length) )
			right_chain, remaining = cut(cut_v_2, distance_to_v)
#			print remaining.coords[:]
			p_l = cut_v_1.coords[:]+remaining.coords[:-1]
			p_r = right_chain.coords[:]
#			p_l = right_chain.coords[:] 
#			p_r = remaining.coords[:]+cut_v_1.coords[:]
#			print p_l, p_r
	#print p_r
	return p_l, p_r

def cut(line, distance):
	"""
	Splicing a line
	Credits go to author of the shapely manual
	"""
	# Cuts a line in two at a distance from its starting point
	if distance <= 0.0 or distance >= line.length:
		return [LineString(line)]
	coords = list(line.coords)
	for i, p in enumerate(coords):
		pd = line.project(Point(p))
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


if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))
		from aux.geometry import rotation
		import reflex
else:
	from ...aux.altitudes import altitude as alt
	from ...poly_operations.others import chain_combination
	from ...poly_operations.others import reflex
	from ...poly_operations.others import directions
	from ...poly_operations.others import adjacency_edges as adj_e
