

def compute_min_altitude(P):
	"""
	Function perofrm a series of call to get_altitude, to find the min altitude
	Things to look out for:
		min_alt init value might not be high enough.

	:param poly: Polygon in standard form.

	:return min_alt: Minimum altitude.
	:return min_theta: Direction of minimum altitude.

	"""

	dirs = directions.get_directions_set(P)

	min_dir = min(dirs, key=lambda d: get_altitude(P, d))
	min_alt = get_altitude(P, min_dir)

	return min_alt, min_dir


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

	#print("Starting with theta:%f\n"%theta)
	P = rotation.rotate_polygon(P, -theta)
	adj = ae.compute_edge_adjacency_dict(P)

	# Sort by x-coordinate
	sorted_by_x = sorted(adj.keys(), key=lambda pt: pt[0])

	altitude = 0
	active_event_counter = 0
	prev_x = -10000000
	checked_verts = []
	for i in range(len(sorted_by_x)):
			
		v = sorted_by_x[i]

		if v in checked_verts:
			continue

		x_v, y_v = v
		x_adj_1, y_adj_1 = adj[v][0]
		x_adj_2, y_adj_2 = adj[v][1]

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
			if resolve_local_equality(adj, adj[v][1], v) == 1:
				active_event_counter += 1
				checked_verts.append(adj[v][1])
		if (x_adj_2 > x_v) and (x_adj_1 == x_v):
			if resolve_local_equality(adj, adj[v][0], v) == 1:
				active_event_counter += 1
				checked_verts.append(adj[v][0])
		if (x_adj_1 < x_v) and (x_adj_2 == x_v):
			if resolve_local_equality(adj, adj[v][1], v) == -1:
				active_event_counter -= 1
				checked_verts.append(adj[v][1])
		if (x_adj_2 < x_v) and (x_adj_1 == x_v):
			if resolve_local_equality(adj, adj[v][0], v) == -1:
				active_event_counter -= 1
				checked_verts.append(adj[v][0])

	return altitude


def resolve_local_equality(adj_list, v, prev):
	"""
	Recursivley resolve which side the edges lie on
	"""

	adj = [adj_list[v][0], adj_list[v][1]]
	
	if prev in adj:
		adj.remove(prev)

	x_v, x_y = v
	x, y = adj[0]

	if x > x_v:
		return 1
	elif x < x_v:
		return -1
	else:
		return resolve_local_equality(adj_list, adj[0], v)


if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))
		from aux.geometry import rotation
		from poly_operations.others import adjacency as ae
		from poly_operations.others import directions
else:
	from ...aux.geometry import rotation
	from ...poly_operations.others import adjacency as ae
	from ...poly_operations.others import directions

#print get_min_altitude(([[(0,0),(2,0),(2,1),(0,1)], []]))

