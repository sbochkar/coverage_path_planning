import math


def init_cost_matrix(dict_map, lines):
	"""
	This function initializes and computes the cost matrix for GTSP.
	:param dict_map: DIctionar of mapping from index to (poly, line, dir)
	:param lines: List storing lines and dirs
	:return cost_matrix: 2D cost Array
	"""

	# Number of entries in 2D cost array
	num_nodes = len(dict_map)

	# Number of clusters in GTSP instance
	num_clusters = num_nodes/2	# Should always be divisible by two

	cost_matrix = [[0 for i in range(num_nodes)] for i in range(num_nodes)]

#	# VER 1.0: Direct distance from node to node, even between non adjacent polys
#	# Important to remeber that dirr encodes the direction rather than point of entry.
#	# So dirr is actually just a point in the list but it represent a direction
#	# If entrance to line is in dirrection dirr, the actual point of entrance is the other point
#	for i in range(num_nodes):
#		for j in range(num_nodes):
#
#			if i == j:
#				continue
#
#			o_poly_idx, o_line_idx, o_dirr_idx = dict_map[i]
#			i_poly_idx, i_line_idx, i_dirr_idx = dict_map[j]
#
#			o_dirr = lines[o_poly_idx][o_line_idx][o_dirr_idx]
#			i_dirr = lines[i_poly_idx][i_line_idx][(1+i_dirr_idx)%2]
#
#			cost = sum( (a - b)**2 for a, b in zip(o_dirr, i_dirr)) 
#
#			cost_matrix[i][j] = cost

	# VER 2.0: Cost account for change in direction. Use cross product to infer the cost
	#			of changin the dirction
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

			# Deduce the direction of the transitin line
			t_line_2 = e_line_1
			t_line_1 = o_line_2
			#print t_line_2

			o = tuple(x-y for x,y in zip(o_line_2, o_line_1))
			e = tuple(x-y for x,y in zip(e_line_2, e_line_1))
			t = tuple(x-y for x,y in zip(t_line_2, t_line_1))

			#print (o_line_2, o_line_1), (i_line_2, i_line_1)

			o_m = math.sqrt(o[0]**2 + o[1]**2)
			e_m = math.sqrt(e[0]**2 + e[1]**2)
			t_m = math.sqrt(t[0]**2 + t[1]**2)

			if (o_poly_idx == e_poly_idx) and (o_line_idx == e_line_idx):
				cross_cost = 2.0
				dist_cost = o_m

			else:
				o = (o[0]/o_m, o[1]/o_m)
				e = (e[0]/e_m, e[1]/e_m)
				t = (t[0]/t_m, t[1]/t_m)

				o_cross = abs((o[0]*t[1] - o[1]*t[0]))
				e_cross = abs((t[0]*e[1] - t[1]*e[0]))

				# Turns out we need to know the angle for a more accurate cost assignment
				dproduct_o = sum((a*b) for a, b in zip(o, t))
				dproduct_e = sum((a*b) for a, b in zip(t, e))

				o_angl = math.acos(dproduct_o)
				e_angl = math.acos(dproduct_e)

				if o_angl > math.pi/2:
					if e_angl > math.pi/2:
						cross_cost = 2+o_cross+e_cross
					else:
						cross_cost = 1+o_cross+e_cross
				else:
					if e_angl > math.pi/2:
						cross_cost = 1+o_cross+e_cross
					else:
						cross_cost = o_cross+e_cross

				dist_cost = t_m

			MULTIPLIER = 100

			cost_matrix[i][j] = (1+cross_cost*MULTIPLIER)*dist_cost
			#print("(%s, %s): %4f, %4f"%(o_line_2, e_line_2, cross_cost, dist_cost))


	# Generate a cluster_array for completness
	cluster_list = [[] for i in range(num_clusters)]
	for i in range(num_nodes):
		cluster_list[i/2].append(i)


	return cost_matrix, cluster_list