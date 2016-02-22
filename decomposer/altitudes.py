# Modules import
from math import cos
from math import sin
from math import pi
from operator import itemgetter


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

	ext = [(0, 0),
		(10, 0),
		(10, 10),
		(0, 10),
		(2, 5)]

# Make sure holes are cw.
	holes = [[(3,2),
			  (3,4),
			  (5,4),
			  (4,3),
			  (5,2)]]

	print("Altitude is: %f"%get_altitude([ext, holes], 0))
	print find_reflex_vertices([ext, holes])