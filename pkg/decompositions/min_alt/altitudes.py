# Modules import
from math import cos
from math import sin
from math import pi
from math import atan2
from math import degrees
from math import sqrt
from operator import itemgetter
import shapely
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import LinearRing
from shapely.geometry import Polygon
import numpy as np
import visilibity as vis



<<<<<<< HEAD
=======

>>>>>>> 977dcaab0c2d498ae2f6d6ef7021c06ac7ffe000
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

<<<<<<< HEAD
=======


>>>>>>> 977dcaab0c2d498ae2f6d6ef7021c06ac7ffe000
def find_cone_of_bisection(P, v):
	"""
	Return a polygon representing the cone of bisection
	"""

	# Compute an approximationg to the radius of the cone of bisection
	shp_polygon = Polygon(P[0], P[1])
	#print("Polygon: %s"%shp_polygon)

	min_x, min_y, max_x, max_y = shp_polygon.bounds
	rad = sqrt((max_x-min_x)**2+(max_y-min_y)**2)

	ext = P[0]
	holes = P[1]

	# Form an adjacency list for easy access to adjacent edges
	adjacency_dict = polygon_to_adjacency_dict(P)

	#Find adjacent edges of v
	v_l_id = adjacency_dict[v][1]; 	v_r_id = adjacency_dict[v][0]
	v_l = v_l_id[1]; v_r = v_r_id[1]
	print("v: %s"%(v,))
	print("v_l: %s, v_r: %s"%(v_l, v_r))

	# Find the angle of v_l with the x-axis
	theta_l = atan2(v_l[1]-v[1], v_l[0]-v[0])
	theta_r = atan2(v_r[1]-v[1], v_r[0]-v[0])
	print("Th_l: %2f, Th_r: %2f"%(degrees(theta_l), degrees(theta_r)))

	# Consider several cases which will determine the measurement for the cone of bisection
	#print degrees(theta_l), degrees(theta_r)
	if theta_l < 0 and theta_r < 0:
		angle = abs(theta_l-theta_r)
		orientation = pi+theta_l+angle/2
		#print degrees(angle), degrees(orientation)
	elif theta_l <= 0 and theta_r >= 0:
		angle = theta_r-theta_l
		#orientation = pi+theta_l+angle/2
		orientation = pi+theta_l+angle/2
	elif theta_l > 0 and theta_r > 0:
		angle = theta_r-theta_l
		orientation = pi+theta_l+angle/2
	elif theta_l > 0 and theta_r < 0:
		angle = 2*pi-(theta_l-theta_r)
		orientation = pi+theta_l+angle/2

	#print("Angle: %f, Orientation: %f"%(degrees(angle),degrees(orientation)))
	p = []

	p.append(v)
	import numpy as np
	for i in np.arange(orientation-angle/2,orientation+angle/2,0.1):
		x = rad*cos(i)
		y = rad*sin(i)

		new_x = v[0]+x
		new_y = v[1]+y

		p.append((new_x, new_y))

	x = rad*cos(orientation+angle/2)
	y = rad*sin(orientation+angle/2)

	new_x = v[0]+x
	new_y = v[1]+y

	p.append((new_x, new_y))

	return p


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




def get_points_from_intersection(intersection):

	if intersection.geom_type == "Point":
		return intersection.x, intersection.y
	elif intersection.geom_type == "MultiPoint":
		return [(point.x, point.y) for point in intersection]
	elif intersection.geom_type == "LineString":
		return [point for point in intersection.coords[:]]
	elif intersection.geom_type == "GeometryCollection":
		points = []
		for item in intersection:
			points.append(get_points_from_intersection(item))
		return points


def get_polygon_bounds(P):
	shp_poly = Polygon(*P)
	minx, miny, maxx, maxy = shp_poly.bounds
	return minx, miny, maxx, maxy


def combine_two_adjacent_polys(p1, p2, e):
	"""
	Assuming they are adjacent
	"""

	v = e[0]; w = e[1]

	p1_v_idx = p1.index(v)
	p2_v_idx = p2.index(v)

	p1_w_idx = p1.index(w)
	p2_w_idx = p2.index(w)

	print("p1_v_i:%d p1_w_i:%d"%(p1_v_idx, p1_w_idx))
	print("p2_v_i:%d p2_w_i:%d"%(p2_v_idx, p2_w_idx))

	if (p1_v_idx == 0) and (p1_w_idx == 1): left_chain = p1[1:]+[p1[0]]
	elif (p1_v_idx == 0) and (p1_w_idx == len(p1-1)): left_chain = p1[:]
	elif p1_v_idx < p1_w_idx: left_chain = p1[p1_w_idx:]+p1[:p1_v_idx+1]
	elif p1_w_idx < p1_v_idx: left_chain = p1[p1_v_idx:]+p1[:p1_w_idx+1]

	if (p2_v_idx == 0) and (p2_w_idx == 1): right_chain = p2[1:]
	elif (p2_v_idx == 0) and (p2_w_idx == len(p2-1)): right_chain = p2[:]
	elif p2_v_idx < p2_w_idx: right_chain = p2[p2_w_idx:]+p2[:p2_v_idx]
	elif p2_w_idx < p2_v_idx: right_chain = p2[p2_v_idx:]+p2[:p2_w_idx]

	print left_chain
	print right_chain
	lr_left = LinearRing(left_chain); lr_right = LinearRing(right_chain)

	if lr_left.is_ccw:
		if lr_right.is_ccw: fuse = left_chain+right_chain
		else: 				fuse = left_chain+right_chain[::-1]
	else:
		if lr_right.is_ccw: fuse = left_chain+right_chain[::-1]
		else: 				fuse = left_chain+right_chain

	return fuse


def find_cut_edge(p1, p2, v):
	"""
	Find a shared edge between two polygons
	"""

	idx_1 = p1.index(v)
	idx_2 = p2.index(v)

	p1_edge_1 = [p1[idx_1], p1[(idx_1+1)%len(p1)]]
	p1_edge_2 = [p1[idx_1], p1[(idx_1-1)%len(p1)]]

	p2_edge_1 = [p2[idx_2], p2[(idx_2+1)%len(p2)]]
	p2_edge_2 = [p2[idx_2], p2[(idx_2-1)%len(p2)]]

	if p1_edge_1 == p2_edge_1: return p1_edge_1
	elif p1_edge_1 == p2_edge_2: return p1_edge_1
	elif p1_edge_2 == p2_edge_1: return p1_edge_2
	elif p1_edge_2 == p2_edge_2: return p1_edge_2

	print "SOMETHING WENT WORNG AND SHARED EDGE WAS NOT FOUND"


def find_common_polys(D, v):

	found_polys = []
	for poly in D:
		if v in poly:
			found_polys.append(poly)

	if len(found_polys) > 2:
		"SOMETHING WRONG, MORE THAN ONE COMMON POLYS"

	return found_polys[0], found_polys[1]

if __name__ == "__main__":

#	ext = [(0.0, 0.0),
#			(4.0, 0.0),
#			(5.0, 1.0),
#			(6.0, 0.0),
#			(10.0, 0.0),
#			(10.0, 10.0),
#			(6.0, 10.0),
#			(5.0, 9.0),
#			(4.0, 10.0),
#			(0.0, 10.0)]
#
#	holes = []
#	ext = [(0,0),
#			(4,0),
#			(4,1),
#			(6,1),
#			(6,0),
#			(10,0),
#			(10,10),
#			(6,10),
#			(6,9),
#			(4,9),
#			(4,10),
#			(0,10)]

#	ext = [(0,0),
#			(10,0),
#			(10,10),
#			(0,10),
#			(0,6),
#			(1,6),
#			(1,4),
#			(0,4)]
#
#	holes = [[(3,1),
#			(3,2),
#			(4,2),
#			(4,3),
#			(3,3),
#			(3,4),
#			(6,4),
#			(6,3),
#			(5,3),
#			(5,2),
#			(6,2),
#			(6,1)]]

#	ext = [(0,0),
#		(10,0),
#		(10,10),
#		(0,10)]
#	holes = [[(2,2),
#				(8,2),
#				(8,8),
#				(2,8)]]

#	ext = [(0,0),
#			(8,0),
#			(8,2),
#			(2,2),
#			(2,8),
#			(8,8),
#			(8,2),
#			(8,0),
#			(10,0),
#			(10,10),
#			(0,10)]
#	holes = []


	P = [ext, holes]
#	print("Altitude is: %f"%get_altitude([ext, holes], 0))
	#print find_cut_space([ext,holes], find_reflex_vertices([ext, holes])[0])
#	(pt, dir1, dir2) = find_optimal_cut([ext, holes], (5,1))
	#print alt, pt, degrees(dir1), degrees(dir2)
#	find_cone_of_bisection([ext, holes], (4,1))
	#print get_directions([ext, holes])
	#print("Transition point: %s"%(find_transition_point([(0,1),(0,10)], 0, (8,6)),))
	#print("Transition point: %s"%(find_best_transition_point([(0,1),(0,10)], (8,6), 0, 0),))


#	ext = [(0,0),
#			(10,0),
#			(10,10),
#			(0,10)]
#
#	holes = [[(2,2),
#			(2,3),
#			(3,3),
#			(3,2)],
#			[(1,4),
#			(1,5),
#			(3,5),
#			(3,4)]]

#	ext = [(0,0),
#			(10,0),
#			(10,10),
#			(0,10)]
#
#	holes = [[(1,1),
#			(1,4),
#			(2,4),
#			(2,3),
#			(8,3),
#			(8,8),
#			(2,8),
#			(2,7),
#			(1,7),
#			(1,9),
#			(9,9),
#			(9,1)],
#			[(3,4),
#			(3,7),
#			(7,7),
#			(7,4)]]


#	print combine_chains(P)
	p1 = [(1,0), (1,1), (2,1), (2,0)]
	p2 = [(0,0), (1,0), (1,1), (0,1)]
	e = [(1,0), (1,1)]
#	print combine_two_adjacent_polys(p1,p2,e)
#	print find_cut_edge(p1,p2,e[0])
