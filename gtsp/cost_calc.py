import math
import os

MAX_COST = 1000


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


def init_dict_mapping(lines):
	"""
	:param lines: List of lists of lists
	:return dict_mapping: A 1:1 mapping from vertex to line direction. This is needed to simplify access to direction.
	"""

	dict_mapping = {}
	counter = 0

	# For each convex polygon
	for poly in range(len(lines)):

		# For each line in convex polygon
		for line in range(len(lines[poly])):

			for dirc in range(len(lines[poly][line])):
				dict_mapping.update({counter:(poly, line, dirc)})
				counter += 1

	return dict_mapping


def init_cost_matrix(dict_map, lines):
	"""
	This function initializes and computer the cost matrix for GTSP.
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

			
def generate_gtsp_instance(filename, solver_loc, cost_matrix, cluster_array):
	"""
	This function will generate appropriate files for GTSP
	solver and start the solver.
	:param cost_matrix:
	:return tour:
	"""

	num_nodes = len(cost_matrix)
	num_clusters = len(cluster_array)

	is_simple = False
	if is_simple:

		props_simp_dict = {'N': num_nodes,
						'M': num_clusters,
				   		'Symmetric': 'false',
				   		'Triangle': 'false'}

		with open(filename+".txt", "w") as f:
			# Write the problem properties first
			for k, v in props_simpl_dict.iteritems():
				f.write(k+': '+str(v)+'\n')

			# Write the node in cluster information
			for i in range(num_clusters):
				row = ""
				for j in range(len(cluster_array[i])):
					row += "%d "%(cluster_array[i][j])

				row += "\n"
				f.write(row)

			# Write the cost matrix
			for i in range(num_nodes):
				row = ""
				for j in range(num_nodes):
					row += "%5d "%cost_matrix[i][j]
				f.write(row+"\n")
		os.system("cp "+filename+".txt "+'gtsp_related/')

	else:

		settings_dict = { 'PROBLEM_FILE': filename+'.gtsp',
				'OUTPUT_TOUR_FILE': filename+'.tour',
				#'ASCENT_CANDIDATES': 500,
				#'INITIAL_PERIOD': 1000,
				#'MAX_CANDIDATES': 30,
				#'MAX_TRIALS': 1000,
				#'POPULATION_SIZE': 5,
				#'PRECISION': 10,
				#'SEED': 1,
				#'TRACE_LEVEL': 1,
				'RUNS': 1}

		props_dict = { 'NAME': filename,
				'COMMENT': filename+': CPP using GTSP solver',
				'TYPE': 'AGTSP',
				'DIMENSION': num_nodes,
				'GTSP_SETS': num_clusters,
				'EDGE_WEIGHT_TYPE': 'EXPLICIT',
				'EDGE_WEIGHT_FORMAT': 'FULL_MATRIX'}

		
		# Write GTSP instance settings
		with open(filename+'.par', 'w') as f:

			for k, v in settings_dict.iteritems():
				f.write(k+' = '+str(v)+'\n')

		# Write GTSP instance properties
		with open(filename+".gtsp", "w") as f:

			for k, v in props_dict.iteritems():
				f.write(k+' = '+str(v)+'\n')


			f.write("EDGE_WEIGHT_SECTION\n")

			for i in range(num_nodes):
				row = ""
				for j in range(num_nodes):
					row += "%5d "%cost_matrix[i][j]

				f.write(row+"\n")
		
			f.write("GTSP_SET_SECTION\n")

			for i in range(num_clusters):
				row = "%d "%(i+1)
				for j in range(len(cluster_array[i])):
					if cluster_array[0][0] == 0:
						row += "%d "%(cluster_array[i][j]+1)
					else:
						row += "%d "%(cluster_array[i][j])

				row += "-1\n"
				f.write(row)



			f.write("EOF\n")
			f.write("")

		# Move the files to GTSP solver location
		os.system("cp "+filename+".gtsp "+'gtsp_related/')
		os.system("cp "+filename+".par "+'gtsp_related/')

		os.system("mv "+filename+".gtsp "+solver_loc)
		os.system("mv "+filename+".par "+solver_loc+"TMP/")


		cur_dir = os.getcwd()
		os.chdir(solver_loc)
		cmd = "./GLKH "+"TMP/"+filename+".par"
	
		#print("[%18s] Launching the GLKH solver."%time_keeping.current_time())
		os.system(cmd)	
		#print("[%18s] GLKH solver has finished."%time_keeping.current_time())

		# Cleanup
		os.system("rm "+filename+".gtsp")
		os.system("rm "+"TMP/"+filename+".par")

		# Move the resulting file to home folder
		os.system("mv "+filename+".tour "+cur_dir+'/gtsp_related/')

		os.chdir(cur_dir)


def read_tour(filename):

	# Read in the results from the TSP solver results
	with open('gtsp_related/'+filename+".tour", 'r') as f:
		for i in range(6):
			f.readline()

		tour = []
		str = f.readline()
		while "EOF" not in str and "-1" not in str:
			tour.append(int(str)-1)
			str = f.readline()

	return tour
