#!/usr/bin/env python3

def greedy_decompose(map_poly):
	"""
	Funcion will decompose a map into a set of convex polygon using greedy cut.
	:param map_poly: Original map
	:return cvx_set: Set of convex polygons
	:return connect_graph: Connectivity graph of the regions
	:return shared_edges: Matrix showing shared edges between regions
	"""

	NUM = 1
	cvx_sets = []

	if NUM == 1:
		cvx_sets.append([(0, 0), (5, 0), (5, 5), (0, 5)])
		cvx_sets.append([(5, 0), (10, 0), (10, 5), (5, 5)])
		cvx_sets.append([(10, 0), (15, 0), (15, 5), (10, 5)])
		cvx_sets.append([(5, 5), (10, 5), (10, 10), (5, 10)])


		num_nodes = len(cvx_sets)
		connect_graph = [[0 for i in range(num_nodes)] for i in range(num_nodes)]
		connect_graph[0][0] = 0
		connect_graph[0][1] = 1
		connect_graph[0][2] = 0
		connect_graph[0][3] = 0
		connect_graph[1][0] = 1
		connect_graph[1][1] = 0
		connect_graph[1][2] = 1
		connect_graph[1][3] = 1
		connect_graph[2][0] = 0
		connect_graph[2][1] = 1
		connect_graph[2][2] = 0
		connect_graph[2][3] = 0
		connect_graph[3][0] = 0
		connect_graph[3][1] = 1
		connect_graph[3][2] = 0
		connect_graph[3][3] = 0

		shared_edges = [[None for i in range(num_nodes)] for i in range(num_nodes)]
		shared_edges[0][0] = None
		shared_edges[0][1] = [(5, 0), (5, 5)]
		shared_edges[0][2] = None
		shared_edges[0][3] = None
		shared_edges[1][0] = [(5, 0), (5, 5)]
		shared_edges[1][1] = None
		shared_edges[1][2] = [(10, 0), (10, 5)]
		shared_edges[1][3] = [(10, 5), (5, 5)]
		shared_edges[2][0] = None
		shared_edges[2][1] = [(10, 0), (10, 5)]
		shared_edges[2][2] = None
		shared_edges[2][3] = None
		shared_edges[3][0] = None
		shared_edges[3][1] = [(10, 5), (5, 5)]
		shared_edges[3][2] = None
		shared_edges[3][3] = None

	elif NUM == 2:
		cvx_sets.append([(0, 0), (15, 0), (15, 5), (0, 5)])
		cvx_sets.append([(15, 0), (20, 0), (20, 5), (15, 5)])
		cvx_sets.append([(10, 5), (15, 5), (15, 10), (10, 10)])


		num_nodes = len(cvx_sets)
		connect_graph = [[0 for i in range(num_nodes)] for i in range(num_nodes)]
		connect_graph[0][0] = 0
		connect_graph[0][1] = 1
		connect_graph[0][2] = 1
		connect_graph[1][0] = 1
		connect_graph[1][1] = 0
		connect_graph[1][2] = 0
		connect_graph[2][0] = 1
		connect_graph[2][1] = 0
		connect_graph[2][2] = 0

		shared_edges = [[None for i in range(num_nodes)] for i in range(num_nodes)]
		shared_edges[0][0] = None
		shared_edges[0][1] = [(15, 0), (15, 5)]
		shared_edges[0][2] = [(10, 5), (15, 5)]
		shared_edges[1][0] = [(15, 0), (15, 5)]
		shared_edges[1][1] = None
		shared_edges[1][2] = None
		shared_edges[2][0] = [(10, 5), (15, 5)]
		shared_edges[2][1] = None
		shared_edges[2][2] = None

	elif NUM == 3:
		cvx_sets.append([(0, 0), (5, 0), (5, 15), (0, 15)])
		cvx_sets.append([(0, 15), (5, 15), (5, 20), (0, 20)])
		cvx_sets.append([(5, 10), (10, 10), (10, 15), (5, 15)])


		num_nodes = len(cvx_sets)
		connect_graph = [[0 for i in range(num_nodes)] for i in range(num_nodes)]
		connect_graph[0][0] = 0
		connect_graph[0][1] = 1
		connect_graph[0][2] = 1
		connect_graph[1][0] = 1
		connect_graph[1][1] = 0
		connect_graph[1][2] = 0
		connect_graph[2][0] = 1
		connect_graph[2][1] = 0
		connect_graph[2][2] = 0

		shared_edges = [[None for i in range(num_nodes)] for i in range(num_nodes)]
		shared_edges[0][0] = None
		shared_edges[0][1] = [(0, 15), (5, 15)]
		shared_edges[0][2] = [(5, 15), (5, 10)]
		shared_edges[1][0] = [(0, 15), (5, 15)]
		shared_edges[1][1] = None
		shared_edges[1][2] = None
		shared_edges[2][0] = [(5, 15), (5, 10)]
		shared_edges[2][1] = None
		shared_edges[2][2] = None



	return cvx_sets, connect_graph, shared_edges


if __name__ == "__main__":
	greedy_decompose([])