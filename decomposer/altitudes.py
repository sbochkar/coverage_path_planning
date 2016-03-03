# Modules import
from math import cos
from math import sin
from math import pi
from math import atan2
from math import degrees
from operator import itemgetter
import shapely
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
import numpy as np
import visilibity as vis


def rotate(vertices, theta):
	""" Rotate a set of vertices by theta

	Rotate a set of vertices consisting of (x,y) tuples by applygin rigid
	transformation

	Args:
		vertices: list of (x, y) coordinates
		theta: the angle of rotation

	Returns:
		None
	"""

	cos_th = cos(theta)
	sin_th = sin(theta)

	n = len(vertices)
	if not n:
		print "rotate: points list EMPTY!"
		return None

	new_points = []
	for i in range(n):
		x_new = vertices[i][0]*cos_th-vertices[i][1]*sin_th
		y_new = vertices[i][0]*sin_th+vertices[i][1]*cos_th

		new_points.append( (x_new, y_new) )

	return new_points


def get_altitude(P, theta):
	""" Compute the altitude of polygon P with respect to direction theta.

	Performs rotation of the polygon as to align with x-axis. Perform a
	simplified trapezoidal sweep to compute the altitude.

	Args:
		P: polygon specified in the form of a tuple (ext, [int]). ext is a list
			of (x, y) tuples specifying the exterior of a polygon ccw. [int] is
			a list of lists of (x, y) tupeles specifying holes of a polygon cw.
		theta: angle of measurement with respect to x-axis

	Returns:
		altitude: A scalar value of the altitude
	"""

	ext_orig = P[0]
	if len(P) > 1:
		holes_orig = P[1] 

	# Rotate the polygon to align with x-axis
	ext = rotate(ext_orig, -theta)

	holes = []
	for hole in holes_orig:
		holes.append(rotate(hole, -theta))

	# Form an adjacency list
	adjacency_dict = {}

	n = len(ext)
	for i in range(n):
		adjacency_dict[ext[i]] = [ext[(i+1)%n], ext[(i-1)%n]]

	for hole in holes:
		n = len(hole)
		for i in range(n):
			adjacency_dict[hole[i]] = [hole[(i+1)%n], hole[(i-1)%n]]			

	# Create list of keys sorted by x-coordinates
	keys_sorted_by_x = sorted(adjacency_dict.keys(), key=itemgetter(0))

	# Record the min_x and initialize altitude and key with events
	min_x = keys_sorted_by_x[0][0]
	altitude = 0
	active_event_counter = 0
	repeated_event_keys = []

	# Go through each vertex and increment altitude accordingly
	for i in range(len(keys_sorted_by_x)):

		# If event has been captured by adjacent same level vertex -> ignore
		if keys_sorted_by_x[i] in repeated_event_keys:
			continue

		current_x, current_y = keys_sorted_by_x[i]
		adjacent_x_1, adjacent_y_1 = adjacency_dict[keys_sorted_by_x[i]][0]
		adjacent_x_2, adjacent_y_2 = adjacency_dict[keys_sorted_by_x[i]][1]

		if i>0:
			delta_x = keys_sorted_by_x[i][0]-keys_sorted_by_x[i-1][0]	
			altitude += active_event_counter*delta_x

		# Handle cases where adjacent edges are on the same level as the test pt
		if (adjacent_x_1 > current_x):
			if (adjacent_x_2 == current_x):
				repeated_event_keys.append(adjacency_dict[keys_sorted_by_x[i]][1])
				active_event_counter += 1
			elif (adjacent_x_2 > current_x):
				active_event_counter += 1

			continue

		if (adjacent_x_2 > current_x):
			if (adjacent_x_1 == current_x):
				repeated_event_keys.append(adjacency_dict[keys_sorted_by_x[i]][0])
				active_event_counter += 1
			elif (adjacent_x_1 > current_x):
				active_event_counter += 1

			continue

		if (adjacent_x_1 < current_x):
			if (adjacent_x_2 == current_x):
				repeated_event_keys.append(adjacency_dict[keys_sorted_by_x[i]][1])
				active_event_counter -= 1
			elif (adjacent_x_2 < current_x):
				active_event_counter -= 1

			continue

		if (adjacent_x_2 < current_x):
			if (adjacent_x_1 == current_x):
				repeated_event_keys.append(adjacency_dict[keys_sorted_by_x[i]][0])
				active_event_counter -= 1
			elif (adjacent_x_1 < current_x):
				active_event_counter -= 1

			continue

#		print("Test point: (%f, %f)"%(current_x, current_y))
#		print("Adj1 point: (%f, %f)"%(adjacent_x_1, adjacent_y_1))
#		print("Adj2 point: (%f, %f)"%(adjacent_x_2, adjacent_y_2))
#		print("Counter: %d"%active_event_counter)
#		print("Altitude: %f"%altitude)
#		print repeated_event_keys
#		print""
	return altitude


def find_reflex_vertices(P):
	"""
	Return a list of reflex vertices in P

	Function will iterate over all vertices in P and return a list of reflex
	vertices

	Args:
		P: (ext, [int]) tuple of list of (x,y) vertices 
			ext is a ccw list of vertices for boundary
			int is cw list of vertices for holes
	Returns:
		R: A list of reflex vertices
	"""

	ext = P[0]
	if len(P) > 1:
		holes = P[1] 	

	R = []

	# Reflex vertices on the boundary first
	n = len(ext)
	for i in range(n):
		p_0 = ext[(i-2)%n]
		p_1 = ext[(i-1)%n]
		p_2 = ext[i]

		dx_1 = float(p_1[0])-float(p_0[0])
		dy_1 = float(p_1[1])-float(p_0[1])
		dx_2 = float(p_2[0])-float(p_1[0])
		dy_2 = float(p_2[1])-float(p_1[1])
		if dx_1*dy_2-dy_1*dx_2 < 0.0:
			R.append(p_1)

	# Reflex vertices from holes
	for hole in holes:
		n = len(hole)
		for i in range(n):
			p_0 = hole[(i-2)%n]
			p_1 = hole[(i-1)%n]
			p_2 = hole[i]

			dx_1 = float(p_1[0])-float(p_0[0])
			dy_1 = float(p_1[1])-float(p_0[1])
			dx_2 = float(p_2[0])-float(p_1[0])
			dy_2 = float(p_2[1])-float(p_1[1])
			if dx_1*dy_2-dy_1*dx_2 < 0.0:
				R.append(p_1)		

	return R


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


def get_directions(P):
	"""
	Generate a list of directions orthogonal to edges of P
		P: ls
	"""
	

	ext = P[0]
	holes = P[1]

	dirs = []

	n = len(ext)
	for i in range(n):
		edge = [ext[i], ext[(i+1)%n]]
		ax, ay = edge[0]
		bx, by = edge[1]

		#print 180*(atan2(by-ay, bx-ax)+pi/2)/pi
		dirs.append(atan2(by-ay, bx-ax)+pi/2)


	for hole in holes:
		n = len(hole)
		for i in range(n):
			edge = [ext[i], ext[(i+1)%n]]
			ax, ay = edge[0]
			bx, by = edge[1]

			#print 180*(atan2(by-ay, bx-ax)+pi/2)/pi
			dirs.append(atan2(by-ay, bx-ax)+pi/2)

	return dirs


def find_cone_of_bisection(P, v):
	"""
	Return a polygon representing the cone of bisection
	"""
	rad = 20

	ext = P[0]
	holes = P[1]

	# Form an adjacency list
	adjacency_dict = {}

	n = len(ext)
	for i in range(n):
		adjacency_dict[ext[i]] = [ext[(i+1)%n], ext[(i-1)%n]]

	for hole in holes:
		n = len(hole)
		for i in range(n):
			adjacency_dict[hole[i]] = [hole[(i+1)%n], hole[(i-1)%n]]

	#Find adjacent edges of v
	v1 = adjacency_dict[v][0]
	v2 = adjacency_dict[v][1]
	triangle = [v2,v,v1]

	#print triangle

	# Find the sweeping angle of the arc
	a0 = atan2(v[1]-v2[1],v[0]-v2[0])
	a1 = atan2(v1[1]-v[1],v1[0]-v[0])

	
	angle = abs(a1-a0)
	#if angle < 0:
	#	angle += 2*pi
	angle = pi-angle

	#print degrees(a0), degrees(a1)
	#print("Arc.ang: %f"%(180-abs(degrees(a1-a0))))
	# Find the center angle of the arc
	#orient = (a0+(pi/2-a1))/2
	orient = pi-(angle/2+abs(a1))

	p = []

	p.append(v)
	import numpy as np
	for i in np.arange(orient-angle/2,orient+angle/2,0.1):
		x = rad*cos(i)
		y = rad*sin(i)

		new_x = v[0]+x
		new_y = v[1]+y

		p.append((new_x, new_y))

	x = rad*cos(orient+angle/2)
	y = rad*sin(orient+angle/2)

	new_x = v[0]+x
	new_y = v[1]+y

	p.append((new_x, new_y))


	return p


def find_cut_space(P, v):
	"""
	Generate the cut space at v using Visilibity library.
	"""


	epsilon = 0.0000001


	# Using shapely library, compute the cone of bisection
	shp_polygon = shapely.geometry.polygon.orient(Polygon(*P))
	shp_cone 	= shapely.geometry.polygon.orient(Polygon(find_cone_of_bisection(P, v)))

	shp_intersection = shapely.geometry.polygon.orient(shp_cone.intersection(shp_polygon))

	#Using the visilibity library, define the reflex vertex
	observer = vis.Point(*v)

	# Define the walls of intersection in Visilibity domain
	# To put into standard form, do this
	exterior_coords = shp_intersection.exterior.coords[:-1]
	x_min_idx, x_min = min(enumerate(exterior_coords), key=itemgetter(1))
	exterior_coords = exterior_coords[7:]+exterior_coords[:7]

	vis_intersection_wall_points = []
	for point in exterior_coords:
		vis_intersection_wall_points.append(vis.Point(*point))
	#print 'Walls in standard form : ',vis.Polygon(vis_intersection_wall_points).is_in_standard_form()

	#for i in range(len(vis_intersection_wall_points)):
		#print vis_intersection_wall_points[i].x(), vis_intersection_wall_points[i].y()
		#print point.x(), point.y()

	# Define the holes of intersection in Visilibity domain
	vis_intersection_holes = []
	for interior in shp_intersection.interiors:
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


	shp_visib = shapely.geometry.polygon.orient(Polygon(zip(point_x, point_y)),-1)
	shp_ls_visib = LineString(shp_visib.exterior.coords[:])

	shp_ls_exterior = LineString(shp_polygon.exterior)
	shp_ls_interior = []
	for interior in shp_polygon.interiors:
	 	shp_ls_interior.append(LineString(interior))

	# Start adding cut space on the exterior
	cut_space = []
	common_items = shp_ls_exterior.intersection(shp_ls_visib)
	for item in common_items:
		if item.geom_type == "LineString":
			cut_space.append(item.coords[:])


	# Start adding cut space on the holes
	for interior in shp_polygon.interiors:
		common_items = interior.intersection(shp_ls_visib)
		if common_items.geom_type == "GeometryCollection":
#			print common_items
			for item in common_items:
				if item.geom_type == "LineString":
					cut_space.append(item.coords[:])
		elif common_items.geom_type == "LineString":
			cut_space.append(common_items.coords[:])
		#Point, LineString, GeometryCollection

	print cut_space

	# PLOTTING
	import pylab as p

	# Plot the polygon itself
	x, y = shp_polygon.exterior.xy
	p.plot(x, y)

	# plot the intersection of the cone with the polygon
	intersection_x, intersection_y = shp_intersection.exterior.xy
	p.plot(intersection_x, intersection_y)

	#for interior in shp_intersection.interiors:
	#	interior_x, interior_y = interior.xy
	#	p.plot(interior_x, interior_y)

	# Plot the reflex vertex
	p.plot([observer.x()], [observer.y()], 'go')

	p.plot(point_x, point_y)

	p.show()
	return cut_space


def find_optimal_cut(P, v):
	"""
	Find optimal cut
	"""


	dirs_left = []
	dirs_right = []
	pois = []

	# Get altitude of P
	a = get_altitude(P, pi/2)

	s = find_cut_space(P, v)
	cut_point = s[0][1]

	p_l, p_r = perform_cut(P, [v, cut_point])

	dirs_left = get_directions([p_l, []])
	dirs_right = get_directions([p_r, []])
	#print dirs_left
	#print list(degrees(dir) for dir in dirs_left)

	#print get_altitude([p_l,[]], 3.5598169831690223)
	#print get_altitude([p_r,[]], 0)

	for si in s:
		for dir1 in dirs_left:
			for dir2 in dirs_right:
				tp = find_best_transition_point(si, v, dir1, dir2)
				pois.append((tp, dir1, dir2))

	# Evaluate all transition points
	min_cost = a;
	min_cost_idx = -1;
	for case in pois:
		p_l, p_r = perform_cut(P, [v, case[0]])

		a_l = get_altitude([p_l, []], case[1])
		a_r = get_altitude([p_r, []], case[2])
		#print a_l, a_r
		if a_l+a_r<=min_cost:
			min_cost = a_l+a_r
			min_cost_idx = case

	print min_cost, min_cost_idx



def perform_cut(P, e):
	"""
	Split up P into two polygons
	"""


	v = e[0]
	w = e[1]
	chain = LineString(P[0]+[P[0][0]])

	distance_to_v = chain.project(Point(v))
	cut_v_1, cut_v_2 = cut(chain, distance_to_v)

	distance_to_w = cut_v_2.project(Point(w))
	right_chain, remaining = cut(cut_v_2, distance_to_w)

	p_l = cut_v_1.coords[:]+remaining.coords[:-1]
	p_r = right_chain.coords[:]

#	print p_l, p_r
	return p_l, p_r

def cut(line, distance):
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


if __name__ == "__main__":

#	ext = [(0, 0),
#			(12, 0),
#			(12, 20),
#			(0, 20)]
#
#	holes = [[(1, 1),
#			(2, 1),
#			(2, 2),
#			(1, 2)],
#			[(8,8),
#			(9, 8),
#			(9, 9),
#			(8, 9)]]

#	ext = [(0, 0),
#		(10, 0),
#		(10, 10),
#		(0, 10),
#		(2, 5)]
#
#	# Make sure holes are cw.
#	holes = [[(3,2),
#			  (3,4),
#			  (5,4),
#			  (4,3),
#			  (5,2)]]

#	ext = [(0,0),
#			(10,0),
#			(10,1),
#			(8,6),
#			(5,5),
#			(0,1)]
#
#	holes = []

	ext = [(0,0),
			(3,0),
			(4,4),
			(5,0),
			(8,0),
			(8,5),
			(0,5)]

	holes = []
#	holes = [[(2.5,0.5),
#			 (1,0.5),
#			 (1,3),
#			 (2.5,3)],
#			 [(6,3),
#			 (6,4),
#			 (7,4),
#			 (7,3)],
#			 [(3,3.5),
#			 (3,4),
#			 (5,4),
#			 (5,3.5)]]


	print("Altitude is: %f"%get_altitude([ext, holes], pi/2))
	#print find_reflex_vertices([ext, holes])
	#print find_cut_space([ext,holes], find_reflex_vertices([ext, holes])[0])
	find_optimal_cut([ext, holes], (4,4))
	#find_cone_of_bisection([ext, holes], (4,1))
	#print get_directions([ext, holes])
	#print("Transition point: %s"%(find_transition_point([(0,1),(0,10)], 0, (8,6)),))
	#print("Transition point: %s"%(find_best_transition_point([(0,1),(0,10)], (8,6), 0, 0),))