def length(tour, segments, cost_matrix):
	"""
	Function will print info about the path
	"""

	tour_length = 0

	# First sum up the lengths of the lines
	for segment in segments:
		tour_length += segment.get_length()

	# Now compute the cost of the transitions
	for i in range(len(tour)-1):
		o_node = tour[i]
		i_node = tour[i+1]

		tour_length += cost_matrix[o_node][i_node]/100

	tour_length += cost_matrix[tour[-1]][tour[0]]/100
	return tour_length
