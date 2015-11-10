import os

		
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
