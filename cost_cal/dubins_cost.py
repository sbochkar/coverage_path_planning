import math
import dubins
import floydwarshall as fl

class directions:
	NORTH = 0
	NORTHEAST = 1
	EAST = 2
	SOUTHEAST = 3
	SOUTH = 4
	SOUTHWEST = 5
	WEST = 6
	NORTHWEST = 7


def init_cost_matrix(P, dict_map, lines, specs):
	"""
	This function initializes and computes the cost matrix for GTSP. Using dubins costs
	:param dict_map: DIctionar of mapping from index to (poly, line, dir)
	:param lines: List storing lines and dirs
	:param specs: Vehicle model info
	:return cost_matrix: 2D cost Array
	"""

	# Number of entries in 2D cost array
	num_nodes = len(dict_map)

	# Number of clusters in GTSP instance
	num_clusters = num_nodes/2	# Should always be divisible by two

	cost_matrix = [[0 for i in range(num_nodes)] for i in range(num_nodes)]

	r = specs["radius"]


	for i in range(num_nodes):
		for j in range(num_nodes):

			if i == j:
				cost_matrix[i][j] = 999999999
				continue

			o_poly_idx, o_line_idx, o_dirr_idx = dict_map[i]
			e_poly_idx, e_line_idx, e_dirr_idx = dict_map[j]

			o_line_2 = lines[o_poly_idx][o_line_idx][o_dirr_idx]
			o_line_1 = lines[o_poly_idx][o_line_idx][(1+o_dirr_idx)%2]

			e_line_2 = lines[e_poly_idx][e_line_idx][e_dirr_idx]
			e_line_1 = lines[e_poly_idx][e_line_idx][(1+e_dirr_idx)%2]

			o = tuple(x-y for x,y in zip(o_line_2, o_line_1))
			e = tuple(x-y for x,y in zip(e_line_2, e_line_1))

			o_m = math.sqrt(o[0]**2 + o[1]**2)
			e_m = math.sqrt(e[0]**2 + e[1]**2)

			o = (o[0]/o_m, o[1]/o_m)
			e = (e[0]/e_m, e[1]/e_m)

			dproduct_o = o[0]	# dproduct with x-axis
			dproduct_e = e[0]

			# Need true angle rather than limited to [-pi, 0]
			if o[1] < 0:
				o_angl = -math.acos(dproduct_o)
			else:
				o_angl = math.acos(dproduct_o)

			if e[1] < 0:
				e_angl = -math.acos(dproduct_e)
			else:
				e_angl = math.acos(dproduct_e)

			#print (o_line_2, o_line_1), (i_line_2, i_line_1)
			q0 = (o_line_2[0], o_line_2[1], o_angl)
			q1 = (e_line_1[0], e_line_1[1], e_angl)
			length = dubins.path_length(q0, q1, r)

			# Check for collisions in this step
			from shapely.geometry import Polygon
			from shapely.geometry import LineString
			shp_polygon = Polygon(*P)
			ls_transition = LineString([o_line_2, e_line_1])

			if shp_polygon.contains(ls_transition):
				cost_matrix[i][j] = length
			else:
				cost_matrix[i][j] = 100*length
			#print("(%s, %s): %4f, %4f"%(o_line_2, e_line_2, cross_cost, dist_cost))


	# Generate a cluster_array for completness
	cluster_list = [[] for i in range(num_clusters)]
	for i in range(num_nodes):
		cluster_list[i/2].append(i)

	return cost_matrix, cluster_list


def init_cost_matrix_grid(pts, r):
	"""
	This function will generate a edge cost matrix to be used in GTSP solver.

	1st: Generate a connectivity graph where only adjacent nodes are connected
		 Treat this step as a TSP instance, aka, every point is the location 
		 and not orientation

	2nd: Pass this graph to Floyd-Warshall algorithm to find cost of edges 
		 connecting nodes that are not adjacent

	:param grid: A list of tuples representing the verticies of the lattice
	:return cost_mtr: A 2D matrix with edge costs
	"""

	TOLERANCE = 0.01
	MAX_COST = 1000
	NUM_NODES_IN_CLUSTER = 8 # MUST BE INT
	num_clusters = len(pts)
	num_verts = num_clusters*NUM_NODES_IN_CLUSTER
	
	## Generate a connectivity matrix connecting only adjacent points
	init_cost_mtr = [[0 for x in range(num_verts)] for x in range(num_verts)]

	adj_straight_cell_dist = r*math.sqrt(2)
	adj_diag_cell_dist = r*2

	#print pts
	#print("[%18s] 	Started to populate matrix."%current_time())
	for i in range(len(init_cost_mtr)):
		for j in range(len(init_cost_mtr)):

			out_vert = i/NUM_NODES_IN_CLUSTER
			in_vert  = j/NUM_NODES_IN_CLUSTER

			if out_vert == in_vert:
				if i == j:
					init_cost_mtr[i][j] = 0
				else:
					init_cost_mtr[i][j] = MAX_COST
			else:
				pt1 = pts[out_vert]
				pt2 = pts[in_vert]

				dist = math.sqrt((pt2[0]-pt1[0])**2+(pt2[1]-pt1[1])**2)

				if ((dist > (1-TOLERANCE)*adj_straight_cell_dist and
					dist < (1+TOLERANCE)*adj_straight_cell_dist) or 
				   (dist > (1-TOLERANCE)*adj_diag_cell_dist and
					dist < (1+TOLERANCE)*adj_diag_cell_dist)):

					# One of the NUM_NODES_IN_CLUSTER orientation for an edge
					direction = get_dir_sqr(pt1, pt2)
					#print("x: %s, y: %s, dir: %d"%(pt1, pt2, direction))
				
					# Decode direction from vertex number
					out_dir = i%NUM_NODES_IN_CLUSTER
					in_dir = j%NUM_NODES_IN_CLUSTER

					# Very ugly way to assign costs				
					if direction == directions.NORTH:
						if out_dir > 4:
							cost_out = direction+NUM_NODES_IN_CLUSTER-out_dir
						else:
							cost_out = out_dir-direction

						if in_dir > 4:
							cost_in = direction+NUM_NODES_IN_CLUSTER-in_dir
						else:
							cost_in = in_dir-direction

					elif direction == directions.NORTHEAST:
						if out_dir < direction:
							cost_out = 1
						elif out_dir > 5:
							cost_out = direction+NUM_NODES_IN_CLUSTER-out_dir
						else:
							cost_out = out_dir-direction

						if in_dir < direction:
							cost_in = 1
						elif in_dir > 5:
							cost_in = direction+NUM_NODES_IN_CLUSTER-in_dir
						else:
							cost_in = in_dir-direction

					elif direction == directions.EAST:
						if out_dir < direction:
							cost_out = 2-out_dir
						elif out_dir > 6:
							cost_out = direction+NUM_NODES_IN_CLUSTER-out_dir
						else:
							cost_out = out_dir-direction

						if in_dir < direction:
							cost_in = 2-in_dir
						elif in_dir > 6:
							cost_in = direction+NUM_NODES_IN_CLUSTER-in_dir
						else:
							cost_in = in_dir-direction

					elif direction == directions.SOUTHEAST:
						if out_dir < direction:
							cost_out = 3-out_dir
						else:
							cost_out = out_dir-direction

						if in_dir < direction:
							cost_in = 3-in_dir
						else:
							cost_in = in_dir-direction

					elif direction == directions.SOUTH:
						if out_dir < direction:
							cost_out = 4-out_dir
						else:
							cost_out = out_dir-direction

						if in_dir < direction:
							cost_in = 4-in_dir
						else:
							cost_in = in_dir-direction

					elif direction == directions.SOUTHWEST:
						if out_dir < 1:
							cost_out = 3
						elif out_dir < direction:
							cost_out = 5-out_dir
						else:
							cost_out = out_dir-direction

						if in_dir < 1:
							cost_in = 3
						elif in_dir < direction:
							cost_in = 5-in_dir
						else:
							cost_in = in_dir-direction

					elif direction == directions.WEST:
						if out_dir < 2:
							cost_out = 2+out_dir
						elif out_dir < direction:
							cost_out = 6-out_dir
						else:
							cost_out = out_dir-direction

						if in_dir < 2:
							cost_in = 2+in_dir
						elif in_dir < direction:
							cost_in = 6-in_dir
						else:
							cost_in = in_dir-direction

					elif direction == directions.NORTHWEST:
						if out_dir <= 4:
							cost_out = out_dir
						else:
							cost_out = direction-out_dir

						if in_dir <= 4:
							cost_in = in_dir
						else:
							cost_in = direction-in_dir

					# Total cost
					init_cost_mtr[i][j] = (cost_out+cost_in+1)*dist
					#print("Odi:  %s,       Idi %s, "%(in_dir, out_dir))
					#print("Out:  %s,       In: %s,         Tot: %f"%(cost_out, cost_in, (cost_out+cost_in+1)*dist))

				else:
					init_cost_mtr[i][j] = MAX_COST

	## ----------------------------------------------------------------


	## Feed init_cost_mtr to another algorithm to find min distance
	#  between verticies that are not adjacent
	#print("[%18s] 	Launched Floyd-Warshall algorithm with %d verticies."%(current_time(), num_verts))
	cost, next_mtx = fl.floydwarshall(init_cost_mtr, MAX_COST)

	return cost, next_mtx

def get_dir_sqr(pt1, pt2):
	"""
	This function will determine an approximate direction
	from pt1 to pt2 in a hexagonally tiled space
	:param pt1: Tuple representing first point
	:param pt2: Tuple representign the second point
	:return: Direction
	0 = North
	1 = NorthEast
	2 = East
	3 = SouthEast
	4 = South
	5 = SouthWest
	6 = West
	7 = NorthWest
	"""

	TOLERANCE = 0.01

	x1, y1 = pt1
	x2, y2 = pt2

	if (y2-y1)>TOLERANCE:
		if (x2-x1)>TOLERANCE:
			return directions.NORTHEAST
		elif (x1-x2)>TOLERANCE:
			return directions.NORTHWEST
		else:
			return directions.NORTH
	elif (y1-y2)>TOLERANCE:
		if (x2-x1)>TOLERANCE:
			return directions.SOUTHEAST
		elif (x1-x2)>TOLERANCE:
			return directions.SOUTHWEST
		else:
			return directions.SOUTH
	else:
		if (x2-x1)>TOLERANCE:
			return directions.EAST
		elif (x1-x2)>TOLERANCE:
			return directions.WEST

	#print '\033[91m['+current_time+"] Error in deducing direction!"+'\033[0m'
