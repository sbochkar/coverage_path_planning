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


def polygon_to_adjacency_dict(P):
	"""
	Thie function will form an adjacency list representing polyong's edges.

	Args:
		P: polygon specified in the form of a tuple (ext, [int]). ext is a
			list of (x, y) tuples specifying the exterior of a polygon ccw.
			[int] is a list of lists of (x, y) tupeles specifying holes of a
			polygon cw.

	"""

	ext = P[0]
	holes = P[1] 

	adjacency_dict = {}

	n = len(ext)
	for i in range(n):
		adjacency_dict[ext[i]] = [ext[(i+1)%n], ext[(i-1)%n]]

	for hole in holes:
		n = len(hole)
		for i in range(n):
			adjacency_dict[hole[i]] = [hole[(i+1)%n], hole[(i-1)%n]]

	return adjacency_dict	


def get_altitude(P, theta):
	"""
	Compute theta altitude of polygon P.

	Rotate the polygon to align sweep with the x-axis.
	Sort all vertices of the polygon by x-coordinate.
	Keep the counter of active corridors.
	Sum up the lengths between events scaled by the counter.

	Args:
		P: polygon specified in the form of a tuple (ext, [int]). ext is a list
			of (x, y) tuples specifying the exterior of a polygon ccw. [int] is
			a list of lists of (x, y) tupeles specifying holes of a polygon cw.
		theta: angle of measurement with respect to x-axis

	Returns:
		altitude: A scalar value of the altitude
	"""

	ext_orig = P[0]
	holes_orig = P[1] 

	# Rotate the polygon to align with x-axis
	holes = []

	ext = rotate(ext_orig, -theta)
	#print ext
	for hole in holes_orig:
		holes.append(rotate(hole, -theta))

	# Form an adjacency list	
	adjacency_dict = polygon_to_adjacency_dict([ext,holes])
	# Create list of verts sorted by x-coordinates
	verts_sorted_by_x = sorted(adjacency_dict.keys(), key=itemgetter(0))

	# Record the min_x and initialize altitude and key with events
	min_x = verts_sorted_by_x[0][0]
	altitude = 0
	active_event_counter = 0
	repeated_event_keys = []

	# Go through each vertex and increment altitude accordingly
	prev_x = -10000000
	checked_verts = []
	#print verts_sorted_by_x
	for i in range(len(verts_sorted_by_x)):
			
		v = verts_sorted_by_x[i]
		#print("%d, %5f, %s)"%(active_event_counter, altitude,v))

		if v in checked_verts:
			continue

		x_v, y_v = v
		x_adj_1, y_adj_1 = adjacency_dict[v][0]
		x_adj_2, y_adj_2 = adjacency_dict[v][1]	

		# Increment the altitude accordingly
		if i>0:
			deltax = x_v-prev_x
			altitude += active_event_counter*deltax
		prev_x = x_v

		# Handle the easy clear cut cases here
		if (x_adj_1 > x_v) and (x_adj_2 > x_v):
			active_event_counter += 1
		elif (x_adj_1 < x_v) and (x_adj_2 < x_v):
			active_event_counter -= 1

		# Handle the cases when some edges are parallel to sweep line
		if (x_adj_1 > x_v) and (x_adj_2 == x_v):
			if resolve_local_equality(adjacency_dict, adjacency_dict[v][1], v) == 1:
				active_event_counter += 1
				checked_verts.append(adjacency_dict[v][1])
		if (x_adj_2 > x_v) and (x_adj_1 == x_v):
			if resolve_local_equality(adjacency_dict, adjacency_dict[v][0], v) == 1:
				active_event_counter += 1
				checked_verts.append(adjacency_dict[v][0])
		if (x_adj_1 < x_v) and (x_adj_2 == x_v):
			if resolve_local_equality(adjacency_dict, adjacency_dict[v][1], v) == -1:
				active_event_counter -= 1
				checked_verts.append(adjacency_dict[v][1])
		if (x_adj_2 < x_v) and (x_adj_1 == x_v):
			if resolve_local_equality(adjacency_dict, adjacency_dict[v][0], v) == -1:
				active_event_counter -= 1
				checked_verts.append(adjacency_dict[v][0])

#		print("Test point: (%f, %f)"%(current_x, current_y))
#		print("Adj1 point: (%f, %f)"%(adjacent_x_1, adjacent_y_1))
#		print("Adj2 point: (%f, %f)"%(adjacent_x_2, adjacent_y_2))
#		print("Counter: %d"%active_event_counter)
#		print("Altitude: %f"%altitude)
#		print repeated_event_keys
#		print""
	return altitude


# Handle the cases where there are edges parallel to the sweep line
def resolve_local_equality(adj_list, v, prev):
	"""
	Recursivley resolve which side the edges lie on
	"""

	adj = [adj_list[v][0], adj_list[v][1]]
	adj.remove(prev)

	x_v, x_y = v
	x, y = adj[0]

	if x > x_v:
		return 1
	elif x < x_v:
		return -1
	else:
		return resolve_local_equality(adj_list, adj[0], v)


def get_min_altitude(P):
	"""
	Function perofrm a series of call to get_altitude, to find the min altitude
	"""

	dirs = get_directions(P)

	min_alt = 1000000000
	min_dir = 0
	for theta in dirs:
		test_alt = get_altitude(P, theta)
		if test_alt <= min_alt:
			min_alt = test_alt
			min_dir = theta

	#print min_alt, min_dir
	return min_alt, min_dir


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

	# Add check for checking the type of polygon
	if len(P) == 2:
		# Standard form of a polygon
		ext = P[0]
		holes = P[1] 	
	else:
		ext = P
		holes = []

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
		#print edge
		ax, ay = edge[0]
		bx, by = edge[1]

		#print 180*(atan2(by-ay, bx-ax)+pi/2)/pi
		dirs.append(atan2(by-ay, bx-ax)+pi/2)


	for hole in holes:
		n = len(hole)
		for i in range(n):
			edge = [hole[i], hole[(i+1)%n]]
			ax, ay = edge[0]
			bx, by = edge[1]

			#print 180*(atan2(by-ay, bx-ax)+pi/2)/pi
			dirs.append(atan2(by-ay, bx-ax)+pi/2)

	return dirs


def find_cone_of_bisection(P, v):
	"""
	Return a polygon representing the cone of bisection
	"""

	# Compute an approximationg to the radius of the cone of bisection
	shp_polygon = Polygon(P[0], P[1])
	min_x, min_y, max_x, max_y = shp_polygon.bounds
	rad = sqrt((max_x-min_x)**2+(max_y-min_y)**2)

	ext = P[0]
	holes = P[1]

	# Form an adjacency list for easy access to adjacent edges
	adjacency_dict = {}

	n = len(ext)
	for i in range(n):
		adjacency_dict[ext[i]] = [ext[(i+1)%n], ext[(i-1)%n]]

	for hole in holes:
		n = len(hole)
		for i in range(n):
			adjacency_dict[hole[i]] = [hole[(i+1)%n], hole[(i-1)%n]]

	#Find adjacent edges of v
	v_l = adjacency_dict[v][1]
	v_r = adjacency_dict[v][0]

	# Find the angle of v_l with the x-axis
	theta_l = atan2(v_l[1]-v[1], v_l[0]-v[0])
	theta_r = atan2(v_r[1]-v[1], v_r[0]-v[0])
	#print degrees(theta_l), degrees(theta_r)

	# Consider several cases which will determine the measurement for the cone of bisection
	#print degrees(theta_l), degrees(theta_r)
	if theta_l < 0 and theta_r < 0:
		angle = abs(theta_l-theta_r)
		orientation = pi+theta_l+angle/2
		#print degrees(angle), degrees(orientation)
	elif theta_l < 0 and theta_r >= 0:
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
	shp_pl_visib = shp_ls_visib.buffer(0.001)

	shp_ls_exterior = LineString(shp_polygon.exterior)
	shp_ls_interior = []
	for interior in shp_polygon.interiors:
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

	#print cut_space

	# PLOTTING
	import pylab as p

	# Plot the polygon itself
#	x, y = shp_polygon.exterior.xy
#	p.plot(x, y)

	# plot the intersection of the cone with the polygon
#	intersection_x, intersection_y = shp_intersection.exterior.xy
#	p.plot(intersection_x, intersection_y)

	#for interior in shp_intersection.interiors:
	#	interior_x, interior_y = interior.xy
	#	p.plot(interior_x, interior_y)

	# Plot the reflex vertex
#	p.plot([observer.x()], [observer.y()], 'go')

#	p.plot(point_x, point_y)

#	p.show()
	#print cut_space
	return cut_space


def find_optimal_cut(P, v):
	"""
	Find optimal cut
	"""


	dirs_left = []
	dirs_right = []
	pois = []

	a, theta = get_min_altitude(P)
	#print a, theta

	s = find_cut_space(P, v)
	#print s
	min_altitude = a
	min_altitude_idx = None

	for si in s:
		# Process each edge si, have to be cw
		lr_si = LinearRing([v]+si)
		if lr_si.is_ccw:
			#print lr_si
			#print lr_si.is_ccw
			si = [si[1]]+[si[0]]
			#print si

		cut_point = si[0]
		#print P, v, cut_point
		p_l, p_r = perform_cut(P, [v, cut_point])
		#print p_l, p_r

		dirs_left = get_directions([p_l, []])
		dirs_right = get_directions([p_r, []])
		#print dirs_left
		#print list(degrees(dir) for dir in dirs_left)
		#print get_altitude([p_l,[]], 3.5598169831690223)
		#print get_altitude([p_r,[]], 0)

		# Look for all transition points
		for dir1 in dirs_left:
			for dir2 in dirs_right:
				tp = find_best_transition_point(si, v, dir1, dir2)
				pois.append((tp, dir1, dir2))

	# Evaluate all transition points
	for case in pois:
		p_l, p_r = perform_cut(P, [v, case[0]])
		a_l = get_altitude([p_l, []], case[1])
		a_r = get_altitude([p_r, []], case[2])
		if a_l+a_r<=min_altitude:
			min_altitude = a_l+a_r
			min_altitude_idx = case
		

	#print min_altitude, min_altitude_idx[0], degrees(min_altitude_idx[1]), degrees(min_altitude_idx[2])
	return min_altitude_idx


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


def combine_chains(P):
	"""
	Combine the chains of a polygon to form one non-simple connected chain
	"""

	alt, theta = get_min_altitude(P)

	ext = P[0]
	ext = rotate(ext, -theta)
	minx, miny, maxx, maxy = get_polygon_bounds([ext, []])

	chains = {}

	holes_orig = P[1]
	n = 0
	for hole in holes_orig:
		chains[n] = rotate(hole, -theta)
		n += 1

	chains[n] = ext
	# Loop over the whole chain dict except the last case
	for i in range(len(chains)-1):
		chain = chains[i]

		R = find_reflex_vertices(chain)
		for v in R:
			#print("Reflex v: %s"%(v,))
			hyperplane = LineString([(v[0],maxy), (v[0],miny)])
			#print("Hyperplane: %s"%hyperplane)

			# Initialize up and down arrays
			up = []; down = []

			for j in range(len(chains)):
				intersection = hyperplane.intersection(LinearRing(chains[j]))

				# Empty intersection means other holes weren't aligned with the
				# hyperplane therefore no intersection is expected
				#print("Isection Type: %s"%intersection.geom_type)
				if intersection.is_empty: continue
				points = get_points_from_intersection(intersection)
				#print points

				# Insert intersections into respective arrays
				for x, y in points:
					if y > v[1]:
						up.append(((x,y), j))
						continue
					elif y < v[1]:
						down.append(((x,y), j))
						continue
					elif y == v[1]:
						up.append(((x,y), j))
						down.append(((x,y), j))
						continue


			# Sort the up and down arrays
			up = sorted(up, key=lambda elem: elem[0][1])
			down = sorted(down, key=lambda elem: elem[0][1])
			#print("Up: %s"%up)
			#print("Down: %s"%down)
			# If closest points is hole itself, go to the next reflex vertex
			if (up[1][1] == i) and (down[-2][1] == i): continue
			if up[1][1] == i: cut_parameters = down[-2]; break
			if down[-2][1] == i: cut_parameters = up[1]; break
			cut_parameters = up[1]; break # Maybe need to choose smartly

		#print("Cutting from: %s to %s"%(v, cut_parameters))
		orig_chain = LineString(chain+[chain[0]])
		dest_chain = LineString(chains[cut_parameters[1]]+[chains[cut_parameters[1]][0]])
		#print orig_chain, dest_chain

		distance_to_v = orig_chain.project(Point(v))
		distance_to_w = dest_chain.project(Point(cut_parameters[0]))
		#print("Dist_v: %2f, Dist_w: %2f"%(distance_to_v, distance_to_w))
		#print("Orig_l: %2f, Dist_l: %2f"%(orig_chain.length, dest_chain.length))

		if distance_to_v == 0:
			orig_chain_1 = []; orig_chain_2 = orig_chain.coords[:]
		else:
			orig_chain_1, orig_chain_2 = cut(orig_chain, distance_to_v)
		if distance_to_w == 0:
			dest_chain_1 = []; dest_chain_2 = dest_chain.coords[:]
		else:
			dest_chain_1, dest_chain_2 = cut(dest_chain, distance_to_w)
			#print cut(dest_chain, distance_to_w)

		#if LinearRing(dest_chain).is_ccw:
		final_chain = dest_chain_1.coords[:]+\
						orig_chain_2.coords[:-1]+\
						orig_chain_1.coords[:]+\
						dest_chain_2.coords[:-1]

		# Now modify the chains array accoridngly to propagate the fusion method
		if cut_parameters[1] == (len(chains)-1):
			chains[len(chains)-1] = final_chain
		else:
			chains[cut_parameters[1]] = final_chain

		#print chains
	return rotate(chains[len(chains)-1], theta)


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
#			(5,1)]]

#	print("Altitude is: %f"%get_altitude([ext, holes], 3*pi/2))
	#print find_cut_space([ext,holes], find_reflex_vertices([ext, holes])[0])
#	(pt, dir1, dir2) = find_optimal_cut([ext, holes], (5,1))
	#print alt, pt, degrees(dir1), degrees(dir2)
	#find_cone_of_bisection([ext, holes], (4,1))
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

	ext = [(0,0),
			(10,0),
			(10,10),
			(0,10)]

	holes = [[(1,1),
			(1,4),
			(2,4),
			(2,3),
			(8,3),
			(8,8),
			(2,8),
			(2,7),
			(1,7),
			(1,9),
			(9,9),
			(9,1)],
			[(3,4),
			(3,7),
			(7,7),
			(7,4)]]



	P = [ext, holes]

#	print combine_chains(P)
	p1 = [(1,0), (1,1), (2,1), (2,0)]
	p2 = [(0,0), (1,0), (1,1), (0,1)]
	e = [(1,0), (1,1)]
	print combine_two_adjacent_polys(p1,p2,e)