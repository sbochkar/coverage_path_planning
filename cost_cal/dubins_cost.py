import math
import dubins

def init_cost_matrix(dict_map, lines, specs):
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

			cost_matrix[i][j] = length
			#print("(%s, %s): %4f, %4f"%(o_line_2, e_line_2, cross_cost, dist_cost))


	# Generate a cluster_array for completness
	cluster_list = [[] for i in range(num_clusters)]
	for i in range(num_nodes):
		cluster_list[i/2].append(i)

	return cost_matrix, cluster_list