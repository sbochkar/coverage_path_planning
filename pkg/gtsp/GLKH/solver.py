import os


def solve(problem_name, solver_loc, cost_matrix, cluster_array):
	"""
	This function will generate appropriate files for GTSP
	solver and start the solver.

	:param problem_name: The name of the problem, useful for problem_names
	:param solver_loc: path to the solver
	:param cost_matrix: Matrix with costs
	:param cluster_array: Information about clusters
	:return tour: Tour
	"""

	num_nodes = len(cost_matrix)
	num_clusters = len(cluster_array)

	is_simple = False
	if is_simple:

		props_simp_dict = {'N': num_nodes,
						'M': num_clusters,
				   		'Symmetric': 'false',
				   		'Triangle': 'false'}

		with open(problem_name+".txt", "w") as f:
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
		os.system("cp "+problem_name+".txt "+'gtsp_related/')

	else:

		settings_dict = { 'PROBLEM_FILE': problem_name+'.gtsp',
				'OUTPUT_TOUR_FILE': problem_name+'.tour',
				#'ASCENT_CANDIDATES': 500,
				#'INITIAL_PERIOD': 1000,
				#'MAX_CANDIDATES': 30,
				#'MAX_TRIALS': 1000,
				#'POPULATION_SIZE': 5,
				#'PRECISION': 10,
				#'SEED': 1,
				#'TRACE_LEVEL': 1,
				'RUNS': 1}

		props_dict = { 'NAME': problem_name,
				'COMMENT': problem_name+': CPP using GTSP solver',
				'TYPE': 'AGTSP',
				'DIMENSION': num_nodes,
				'GTSP_SETS': num_clusters,
				'EDGE_WEIGHT_TYPE': 'EXPLICIT',
				'EDGE_WEIGHT_FORMAT': 'FULL_MATRIX'}

		
		# Write GTSP instance settings
		with open(problem_name+'.par', 'w') as f:

			for k, v in settings_dict.iteritems():
				f.write(k+' = '+str(v)+'\n')

		# Write GTSP instance properties
		with open(problem_name+".gtsp", "w") as f:

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
		os.system("cp "+problem_name+".gtsp "+'/pkg/gtsp/solver_logs/')
		os.system("cp "+problem_name+".par "+'/pkg/gtsp/solver_logs/')

		os.system("mv "+problem_name+".gtsp "+solver_loc)
		os.system("mv "+problem_name+".par "+solver_loc+"TMP/")


		cur_dir = os.getcwd()
		os.chdir(solver_loc)
		cmd = "./GLKH "+"TMP/"+problem_name+".par"
	
		#print("[%18s] Launching the GLKH solver."%time_keeping.current_time())
		os.system(cmd)	
		#print("[%18s] GLKH solver has finished."%time_keeping.current_time())

		# Cleanup
		#os.system("rm "+problem_name+".gtsp")
		#os.system("rm "+"TMP/"+problem_name+".par")
		os.system("mv "+problem_name+".gtsp "+cur_dir+"/pkg/gtsp/solver_logs")
		os.system("mv "+"TMP/"+problem_name+".par "+cur_dir+"/pkg/gtsp/solver_logs")


		# Move the resulting file to home folder
		os.system("mv "+problem_name+".tour "+cur_dir+'/pkg/gtsp/solver_logs')

		os.chdir(cur_dir)


def read_tour(problem_name):

	# Read in the results from the TSP solver results
	with open('pkg/gtsp/solver_logs/'+problem_name+".tour", 'r') as f:
		for i in range(6):
			f.readline()

		tour = []
		str = f.readline()
		while "EOF" not in str and "-1" not in str:
			tour.append(int(str)-1)
			str = f.readline()

	return tour