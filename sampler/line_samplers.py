#!/usr/bin/env python3


import math
import numpy as np

try:
	from shapely.geometry import LineString
except ImportError: print("Importing Shapely module failed!")


def ilp_finite_dir_line_sampling(cvx_set, connectivity, shared_edges, dir_set, specs):
	"""
	This function samples all of free space with lines.
	:param cvx_set: Set of convex sets
	:param connectivity: Connectivity graph for connectivity between convex cells
	:param shared_edges: Shared edges between convex cells
	:param dir_set: Direction to use for lines
	:param specs: Robot specs
	:return dir_per_poly: Directions to use in each polygon
	"""


	# Number of lines to use in the solution
	num_dirs = len(dir_set)

	# Number of convex cells
	num_polys = len(cvx_set)

	# Separation distance between lines
	radius = specs["radius"]

	# Do first pass to calculate num of incident lines to the shared edge
	init_cost_structure = [[[] for i in range(num_dirs)] for i in range(num_polys)]

	for i in range(len(cvx_set)):

		print("Polygon: %d"%i)

		for j in range(len(dir_set)):

			print("Dir: %d -> "%j, end="")
			# Generate lines in cvx_set[i] with direction [j]
			lines, raw_lines = sample_with_lines(cvx_set[i], dir_set[j], radius)

			# Count number of lines incident to shared edge
			# 	1: Find all the neighbors of cvx_set[i]
			neighbs = find_neighbors(i, connectivity)

			# 	2: For each neighbor, find shared edge
			for neigh in neighbs:
				shared_edge = shared_edges[i][neigh]
				#print("Sh. Edge: %s"%shared_edge)

				#	3: Find num of incident lines to the shared edge
				num_incs = get_incident_lines_num(shared_edge, raw_lines)
				#print("Num of inci: %d"%num)
				print("(%d, %d) "%(neigh, num_incs), end="")

				#	4: Store the cost for each edge
				init_cost_structure[i][j].append((neigh, num_incs))
			print("")
		print("")

	#pretty_print_cost_structure(init_cost_structure)

	return None


def get_incident_lines_num(edge, lines):
	"""
	Calculates the number of lines that intersect the edge
	:param edge: List of 2 tuples
	:param lines: List of lines
	:return num_inciden: Number of lines incident to the edge
	"""

	num_intersections = 0

	edge_ls = LineString(edge)

	for line in lines:
	
		line_ls = LineString(line)
		intersection = line_ls.intersection(edge_ls)

		# Assume it can be eithe empty or point intersection
		if not intersection.is_empty:
			num_intersections += 1


	#print("Edge: %s"%edge)
	#print("Lines: %s"%lines)
	#print("Num: %d"%num_intersections)

	return num_intersections


def pretty_print_cost_structure(cost):
	"""
	Pretty print for cost init_cost_structure
	:param cost: Cost array
	:return: None
	"""

	for i in range(len(cost)):
		print("Poly: %d"%i)
		
		for j in range(len(cost[0])):
			print("Dir: %d -> "%j, end="")


			print("cost: %s"%cost[i][j])
		print("")


def find_neighbors(node, connectivity):
	"""
	Function all the neighbors of i according to connectivity matrix
	:param node: Node
	:return neighbors: All neighbors of i
	"""

	neighbors = []

	for i in range(len(connectivity[node])):
		if connectivity[node][i]:
			neighbors.append(i)

	return neighbors


def sample_with_lines(shape, theta, r):
	"""
	This function generates a set of lines inside convex polygon
	TODO: Handle rare case where intersection may result in 3 points in consecutive
	edges
	:param shape: Polygon which is to be sampled with lines
	:param theta: Direction specifier for lines
	:param r: Separation distance between lines
	:return line_coords: Final coordinate of lines inside convex polygons
	:return orig_line_coords: Raw line without offsetting the endpoints
	"""

	num_lines = 0			# Counter for num of lines
	num_edges = 0			# Counter for number of edges in polygon
	
	line_coords = []		# Storing coords for lines
	orig_line_coords = []	# Storing unprocesed corrds for lines
	y_coords = []			# Storing y-coords of lines
	

	# Create a copy of (X, Y) list and rotate it
	rotated_shape = list(shape)
	rotate(rotated_shape, theta)
	num_edges = len(rotated_shape)


	# Located bounds of the polygon
	x_lower_bound = min(x for x, y in rotated_shape)
	x_upper_bound = max(x for x, y in rotated_shape)

	y_lower_bound = min(y for x, y in rotated_shape)
	y_upper_bound = max(y for x, y in rotated_shape)

	# Number of parallel lines to expect
	# End y coordinate for those lines
	y = y_lower_bound + r

	while y < y_upper_bound-r:
		num_lines += 1
		y_coords.append(y)
		y += 2*r


	# Find end points of line candidates
	for i in range(num_lines):
		line_dict = {'end_pts':[], 'offset': []}

		line_candidate = LineString([(x_lower_bound, y_coords[i]),
									 (x_upper_bound, y_coords[i])])


		for j in range(1, num_edges+1):

			if j == num_edges:
				edge = LineString([rotated_shape[-1], rotated_shape[0]])
			else:
				edge = LineString([rotated_shape[j], rotated_shape[j-1]])

			intersect_pt = line_candidate.intersection(edge)
			
			if not intersect_pt.is_empty and type(intersect_pt) is not LineString:
								
				if j == num_edges:
					offset = getOffsetFromEdge([rotated_shape[0], 
										rotated_shape[-1]],
										r)

				else:
					offset = getOffsetFromEdge([rotated_shape[j], 
										rotated_shape[j-1]],
										r)

				found = False
				for point in line_dict['end_pts']:
					if np.allclose(intersect_pt.coords[0], point):
						found = True
						break

				if not found:
					line_dict['end_pts'].append(intersect_pt.coords[0])
					line_dict['offset'].append(offset)


		# Intersections have been determined for one line, now process
		x1, y1 = line_dict['end_pts'][0]
		x2, y2 = line_dict['end_pts'][1]
		ofs1, ofs2 = line_dict['offset']

		# Make sure line is long enough to accomodate offset
		if abs(x2 - x1) >= ofs1+ofs2:
			if x1 < x2:
				temp = [(x1+ofs1, y1), (x2-ofs2, y2)]
			else:
				temp = [(x1-ofs2, y1), (x2+ofs1, y2)]

			line_coords.append(rotate(temp, -theta))
			orig_line_coords.append(rotate([(x1, y1), (x2, y2)], -theta))

	return line_coords, orig_line_coords


def rotate(points, theta):
	"""
	Rotate the list of points by theta degrees
	:param points: list of (x, y) coordinates
	:param theta: the angle of rotation
	:return: 0 - failed 1 -success
	"""

	new_points = []

	cos_th = math.cos(theta)
	sin_th = math.sin(theta)

	n = len(points)

	if not n:
		print("rotate: points list EMPTY!")
		return None

	for i in range(n):

		# x' = x*cos(th)-y*sin(th)
		# y' = x*sin(th)+y*cos(th)
		x_new = points[i][0]*cos_th-points[i][1]*sin_th
		y_new = points[i][0]*sin_th+points[i][1]*cos_th

		new_points.append( (x_new, y_new) )

	return new_points


def getOffsetFromEdge(line_seg, r):
	"""
	Function returns the horizontal offset from an edge of polygon that is a shotest
	distance r from line_seg
	:param line_seg: [ ( x1, y1 ), ( x2, y2 ) ]
	:param r: scalar
	"""

	x1 = line_seg[0][0]
	y1 = line_seg[0][1]
	x2 = line_seg[1][0]
	y2 = line_seg[1][1]

	if abs(y2-y1) <= 0.01:
		print("getOffsetFromEdge: Line segment is horizontal!")
		return 0

	term_1 = math.pow((x2-x1)/(y2-y1), 2)
	term_2 = r*math.sqrt(term_1+1)

	return term_2