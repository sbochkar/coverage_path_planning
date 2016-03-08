import dubins


def compute_costs(mapping, radius):
	"""
	Compute dubins costs between path segments which could be either
	a line or a point.

	TODO: Collision checking!!

	"""


	MAX_COST = 999999999
	num_nodes = len(mapping)

	r = radius
	cost = [[0 for i in range(num_nodes)] for i in range(num_nodes)]

	# Populate the cost matrix
	for i in range(num_nodes):
		for j in range(num_nodes):

			q0 = mapping[i][0].get_exit_info(mapping[i][1])
			q1 = mapping[j][0].get_entrance_info(mapping[j][1])
			length = dubins.path_length(q0, q1, r)

			cost[i][j] = length


	# Generate a cluster information list
	cluster_list = []
	node_list = []
	counter = 0

	for i in range(num_nodes):
		segment, direction_id = mapping[i]
		
		if direction_id == 0:
			if node_list:
				cluster_list.append(node_list)
				counter += 1
				node_list = []


		node_list.append(i)
	cluster_list.append(node_list)

	return cost, cluster_list




if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))

		from pkg.discritizers import classes
else:
	from ..discritizers import classes