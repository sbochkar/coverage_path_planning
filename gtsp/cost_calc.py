import math


MAX_COST = 1000


def init_cost_matrix(lines):
	"""
	This function initializes the cost matrix with appropriate
	size.
	:param lines: a list of lists containing lines
	:param cost_matrix:
	"""

	num_sectors = len(lines)

	# Infer the size of the cost matrix
	row_size = 0
	for i in range(num_sectors):
		row_size += 2*len(lines[i])

	cost_matrix = [[0 for i in range(row_size)] for i in range(row_size)]

	return cost_matrix


def compute_intrasector_transitions(lines):
	"""
	This function computes intrasector tranistion costs.
	Change the cost matrix in-place
	:param cost_matrix: Initialized cost_matrix
	:param lines: A list of list of lines
	:return None:
	"""

	intra_cost = []
	num_clusters = len(lines)

	for clus in range(num_clusters):

		cluster_size = 2*len(lines[clus])
		internal_cost = [[0 for i in range(cluster_size)] for i in range(cluster_size)]
		for line_1 in range(cluster_size):
			for line_2 in range(cluster_size):

				out_line_num = line_1/2
				out_line_dir = line_1%2

				in_line_num = line_2/2
				in_line_dir = line_2%2

				if out_line_num != in_line_num:

					line_1_exit_pt = lines[clus][out_line_num][out_line_dir]
					line_2_entr_pt = lines[clus][in_line_num][(in_line_dir+1)%2]

					internal_cost[line_1][line_2] = sum( (a - b)**2 for a, b in zip(line_1_exit_pt, line_2_entr_pt))
				else:	
					internal_cost[line_1][line_2] = MAX_COST

		intra_cost.append(internal_cost)

	return intra_cost


def compute_intersector_transitions(lines, connectivity):	
	"""
	This function computes intersector transition costs betweeb lines.
	:param lines: List of list of lines
	:param connectivity: Connectivity between regions 
	:return inter_sector_cost: Array
	"""

	inter_cost = [[[] for i in range(len(connectivity))]
					  for i in range(len(connectivity))]


	for poly in range(len(connectivity)):
		for neigh in range(len(connectivity)):

			if connectivity[poly][neigh]:

				out_cluster_size = 2*len(lines[poly])
				in_cluster_size = 2*len(lines[neigh])

				internal_cost = [[MAX_COST for i in range(in_cluster_size)] for i in range(out_cluster_size)] 
		
				for line_1 in range(out_cluster_size):
					for line_2 in range(in_cluster_size):

						out_line_num = line_1/2
						out_line_dir = line_1%2

						in_line_num = line_2/2
						in_line_dir = line_2%2

						line_1_exit_pt = lines[poly][out_line_num][out_line_dir]
						line_2_entr_pt = lines[neigh][in_line_num][(in_line_dir+1)%2]

						internal_cost[line_1][line_2] = sum( (a - b)**2 for a, b in zip(line_1_exit_pt, line_2_entr_pt))

				inter_cost[poly][neigh].extend(internal_cost)

	return inter_cost


def gtsp_cost_matrix(cost_matrix, intra, inter):
	"""
	Function will generate cost matrix for GLKH solver
	:param cost_matrix:
	:param intra:
	:param inter:
	:return cost_matrix:
	"""

	num_clusters = len(inter)
	