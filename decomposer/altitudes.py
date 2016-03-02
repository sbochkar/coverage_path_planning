# Modules import
from math import cos
from math import sin
from math import pi
from math import atan2
from operator import itemgetter
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

	print t_l, t_r
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


def find_cut_space(P, v):
	"""
	Generate the cut space at v using Visilibity library.
	"""


	epsilon = 0.0000001
	wall_points = []
	for point in P[0]:
		wall_points.append(vis.Point(*point))

	walls = vis.Polygon(wall_points)
	#print walls.is_in_standard_form()

	holes = []
	for hole_list in P[1]:
		hole_points = []
		for point in hole_list:
			hole_points.append(vis.Point(*point))

		holes.append(vis.Polygon(hole_points))
		#print hole.is_in_standard_form()

	if len(holes)>0:
		env = vis.Environment([walls, holes])
	else:
		env = vis.Environment([walls])
	#print env.is_valid(epsilon)

	observer = vis.Point(*v)
	observer.snap_to_boundary_of(env, epsilon)
	observer.snap_to_vertices_of(env, epsilon)
	isovist = vis.Visibility_Polygon(observer, env, epsilon)

	def save_print(polygon):
		end_pos_x = []
		end_pos_y = []
		for i in range(polygon.n()):
			x = polygon[i].x()
			y = polygon[i].y()

			end_pos_x.append(x)
			end_pos_y.append(y)

		return end_pos_x, end_pos_y 

	point_x , point_y  = save_print(isovist)
	point_x.append(isovist[0].x())
	point_y.append(isovist[0].y())  

	print zip(point_x, point_y)

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
			(4,1),
			(5,0),
			(8,0),
			(8,5),
			(0,5)]

	holes = []


	print("Altitude is: %f"%get_altitude([ext, holes], 0))
	print find_reflex_vertices([ext, holes])
	print find_cut_space([ext,holes], find_reflex_vertices([ext, holes])[0])
	#print get_directions([ext, holes])
	#print("Transition point: %s"%(find_transition_point([(0,1),(0,10)], 0, (8,6)),))
	#print("Transition point: %s"%(find_best_transition_point([(0,1),(0,10)], (8,6), 0, 0),))