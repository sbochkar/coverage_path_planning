import dubins
from math import sqrt
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.geometry import LinearRing



def compute_costs(P, mapping, radius):
	"""
	Compute dubins costs between path segments which could be either
	a line or a point.

	TODO: Collision checking!!

	"""


	MAX_COST = 999999999
	num_nodes = len(mapping)

	r = radius
	cost = [[0 for i in range(num_nodes)] for i in range(num_nodes)]
	print("Size: %d nodes."%num_nodes)

	# Populate the cost matrix
	for i in range(num_nodes):
#		print(i)
		for j in range(num_nodes):

			q0 = mapping[i][0].get_exit_info(mapping[i][1])
			q1 = mapping[j][0].get_entrance_info(mapping[j][1])

			# Check for collisions
			x0 = q0[0]; y0 = q0[1]
			x1 = q1[0]; y1 = q1[1]

			if has_collision(P, [(x0, y0), (x1, y1)]):
				length = 9999999
			else:
				length = 100*dubins.path_length(q0, q1, r)

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


def compute_tsp_costs(P, tsp_mapping, radius):
	"""
	Compute direction free costs"
	"""

	MAX_COST = 999999999
	num_nodes = len(tsp_mapping)

	r = radius
	cost = [[0 for i in range(num_nodes)] for i in range(num_nodes)]
	print("Size: %d nodes."%num_nodes)

	# Populate the cost matrix
	for i in range(num_nodes):
		print(i)
		for j in range(num_nodes):

			q0 = tsp_mapping[i][0].get_exit_info(tsp_mapping[i][1])
			q1 = tsp_mapping[j][0].get_entrance_info(tsp_mapping[j][1])

			# Check for collisions
			x0 = q0[0]; y0 = q0[1]
			x1 = q1[0]; y1 = q1[1]

			if has_collision(P, [(x0, y0), (x1, y1)]):
				length = 9999999
			else:
				length = sqrt((x1-x0)**2+(y1-y2)**2)

			cost[i][j] = length


	# Generate a cluster information list
	cluster_list = []

	for i in range(num_nodes):
		cluster_list.append([i])

	return cost, cluster_list	


def has_collision(P, edge):

	exterior = LinearRing(P[0])
	holes = P[1]
	segment = LineString(edge)

	if exterior.intersects(segment): return True

	for hole in holes:
		interior = LinearRing(hole)
		if interior.intersects(segment): return True
	return False

if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))

		from pkg.discritizers import classes
else:
	from ..discritizers import classes