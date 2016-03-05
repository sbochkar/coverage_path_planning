from py2d.Math import Polygon
import altitudes as alt
from shapely.geometry import LineString


def polygon_generator(map_num):
	"""
	Function returns a map specified by the map_number
	"""

	if map_num == 1:
		ext = [(0.0, 0.0),
			(4.0, 0.0),
			(5.0, 1.0),
			(6.0, 0.0),
			(10.0, 0.0),
			(10.0, 10.0),
			(6.0, 10.0),
			(5.0, 9.0),
			(4.0, 10.0),
			(0.0, 10.0)]

		holes = []
	elif map_num == 2:
		ext = [(0.0,0.0),
				(4.0,0.0),
				(5.0,1.0),
				(6.0,0.0),
				(10.0,0.0),
				(10.0,10.0),
				(6.0,10.0),
				(4.0,7.0),
				(5.0,10.0),
				(0.0,10.0)]

		holes = []

	elif map_num == 3:
		ext = [(1.0, 0),
				(9.0, 0),
				(9.0, 1.0),
				(10.0, 1.0),
				(10.0, 9.0),
				(9.0, 9.0),
				(9.0, 10.0),
				(1.0, 10.0),
				(1.0, 9.0),
				(0.0, 9.0),
				(0.0, 1.0),
				(1.0, 1.0)]

		holes = []

	elif map_num == 4:
		ext = [(0.0, 0),
				(1.0, 0),
				(1.0, 8.0),
				(9.0, 0.0),
				(10.0, 0.0),
				(10.0, 10.0),
				(9.0, 10.0),
				(9.0, 2.0),
				(1.0, 10.0),
				(0.0, 10.0)]

		holes = []

	elif map_num == 5:
		ext = [(0.0, 0),
				(10.0, 0),
				(10.0, 5.0),
				(7.5, 10.0),
				(5.0, 5.0),
				(2.5, 10.0),
				(0.0, 5.0)]

		holes = []

	elif map_num == 6:
		ext = [(0.0, 0),
				(15.0, 0),
				(15.0, 4.0),
				(14.0, 5.0),
				(15.0, 6.0),
				(15.0, 10.0),
				(10,10),
				(10,5),
				(7.5, 10.0),
				(5.0, 5.0),
				(2.5, 10.0),
				(0.0, 5.0)]

		holes = []

	return [ext, holes]


def min_alt_decompose(P):
	"""
	Min Altitude Decomposition
	"""


	# Find all reflex vertices in P
	R = alt.find_reflex_vertices(P)
	D = [P]

	#Cuts at all reflex vertices
	while R:
		v = R.pop()
		for poly in D:
			if v in poly[0]:
				#print poly
				break
			else:
				for hole in poly[1]:
					if v in hole:
						break

		# If cut was made previously to a reflex vertex and its cone of bisection
		# Need to check if it was eliminated here, check later.
		R_temp = alt.find_reflex_vertices(poly)
		if v not in R_temp:
			continue
		# Find optimal cut
		#print poly, v
		cut = alt.find_optimal_cut(poly, v)
		print cut
		# If best cut did not improve
		if cut is None:
			continue
		#print poly, v, cut[0]
		p_l, p_r = alt.perform_cut(poly,[v,cut[0]])
		#print "New polygons"
		#print p_l, p_r
		D.remove(poly)
		D.append([p_l, []])
		D.append([p_r, []])
		#print D
		#print "Finished loop"

	# Start generating additional data structures for passing to the coverage
	# planner
	cvx_set = [poly[0] for poly in D]

	connectivity = [[0 for i in range(len(cvx_set))] for i in range(len(cvx_set))]
	shared_edges = [[None for i in range(len(cvx_set))] for i in range(len(cvx_set))]

	for p_1 in range(len(cvx_set)):
		for p_2 in range(p_1+1, len(cvx_set)):

			# p_1 one polygon
			# p_2 second polygon
			# Test each edge on each polygon looking for overlaping edges
			n_1 = len(cvx_set[p_1])
			n_2 = len(cvx_set[p_2])
			for i in range(n_1):
				edge_1 = [cvx_set[p_1][i]]+[cvx_set[p_1][(i+1)%n_1]]
				for j in range(n_2):
					edge_2 = [cvx_set[p_2][j]]+[cvx_set[p_2][(j+1)%n_2]]

					def check_overlap(edge1, edge2):
						# imrpoved version of the comparison where
						# edges may overlap but not along entire length

						ls_edge1 = LineString(edge1).buffer(0.0001)
						ls_edge2 = LineString(edge2)

						isection = ls_edge1.intersection(ls_edge2)
						if isection.geom_type == "LineString":
							if isection.length > 0.001:
								#print isection
								coords = isection.coords[:]
								return True, coords
							else:
								return False, None
						else:
							return False, None
#	
					is_overlap, coords = check_overlap(edge_1, edge_2)
					if is_overlap:
						connectivity[p_1][p_2] = 1
						connectivity[p_2][p_1] = 1

						shared_edges[p_1][p_2] = coords
						shared_edges[p_2][p_1] = coords

	#print shared_edges
#	prtty_print_set_polygon(cvx_set)
#	prtty_print_connectivity(connectivity)
#	prtty_print_shared_edges(shared_edges)
	return cvx_set, connectivity, shared_edges


def prtty_print_shared_edges(M):

	for i in range(len(M)):
		line_list = []
		print("["),
		for j in range(len(M[0])):
			if M[i][j] is not None:
				line_list.append(M[i][j])
				print("%d"%(len(line_list)-1)),
			else:
				print("N"),

		print("]"),
		for k in range(len(line_list)):
			print("%d: %s; "%(k, line_list[k])),
		print("")



			

def prtty_print_connectivity(M):

	for i in range(len(M)):
		print("%s"%M[i])


def prtty_print_set_polygon(poly_list):

	i = 0
	for poly in poly_list:
		print("Polygon %d: %s"%(i, poly))
		i += 1


def greedy_decompose(P):
	"""
	Funcion will decompose a map into a set of convex polygon using greedy cut.
	:param P: Polygon to decompose
	:return cvx_set: Set of convex polygons
	:return connect_graph: Connectivity graph of the regions
	:return shared_edges: Matrix showing shared edges between regions
	"""

	poly_xy, holes = P

	exter = Polygon.from_tuples(poly_xy)

	# Convert to polygon class
	holes_p = []
	for hole in holes:
		hole_p = Polygon.from_tuples(hole)
		holes_p.append(hole_p)

	# Perform the decomposition
	decomposed = Polygon.convex_decompose(exter, holes_p)
	
	if not decomposed:
		print "ERROR! Decomposition resulted in empty list"


	#for poly in decomposed:
	#	print poly

	#print [decomposed[0].as_tuple_list()[-1] + decomposed[0].as_tuple_list()[0]]

	# Start generating connectivity matricies and shared edges array
	cvx_set = [poly.as_tuple_list() for poly in decomposed]

	connectivity = [[0 for i in range(len(decomposed))] for i in range(len(decomposed))]
	shared_edges = [[None for i in range(len(decomposed))] for i in range(len(decomposed))]


	for c1 in range(len(decomposed)):
		for c2 in range(c1+1, len(decomposed)):

			# Test each edge on each cell to look for same edges
			# This if to find adjacent edges
			for i in range(1, len(decomposed[c1])+1):

				if i == len(decomposed[c1]):
					edge_1 = [decomposed[c1].as_tuple_list()[-1], decomposed[c1].as_tuple_list()[0]]
				else:
					edge_1 = decomposed[c1].as_tuple_list()[i-1:i+1]
				
				for j in range(1, len(decomposed[c2])+1):

					if j == len(decomposed[c2]):
						edge_2 = [decomposed[c2].as_tuple_list()[-1], decomposed[c2].as_tuple_list()[0]]
					else:
						edge_2 = decomposed[c2].as_tuple_list()[j-1:j+1]

					def compare_edges(edge1, edge2):
						for tupl in edge1:
							if tupl not in edge2:
								return False
						return True

					if compare_edges(edge_1, edge_2):
						connectivity[c1][c2] = 1
						connectivity[c2][c1] = 1

						shared_edges[c1][c2] = edge_1
						shared_edges[c2][c1] = edge_1

	#print connectivity
	#for i in range(len(shared_edges)):
	#	print
	#	for j in range(len(shared_edges)):
	#		print("%30s "%shared_edges[i][j]),
	#print shared_edges
	return cvx_set, connectivity, shared_edges

def manual_decompose(map_poly):
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

	elif NUM == 4:
		cvx_sets.append([(0, 0), (1, 0), (1, 3), (0, 3)])
		cvx_sets.append([(1, 0), (2, 0), (2, 2), (1, 2)])
		cvx_sets.append([(2, 0), (3, 0), (3, 1), (2, 1)])
		cvx_sets.append([(3, 0), (5, 0), (5, 2), (3, 2)])
		cvx_sets.append([(4, 2), (5, 2), (5, 3), (4, 3)])
		cvx_sets.append([(3, 3), (5, 3), (5, 4), (3, 4)])
		cvx_sets.append([(2, 4), (5, 4), (5, 5), (2, 5)])
		cvx_sets.append([(1, 4), (2, 4), (2, 5), (0, 5)])
		cvx_sets.append([(1, 3), (2, 3), (2, 4), (1, 4)])
		cvx_sets.append([(0, 3), (1, 3), (1, 4), (0, 5)])



		num_nodes = len(cvx_sets)
		connect_graph = [[0 for i in range(num_nodes)] for i in range(num_nodes)]
	
		connect_graph[0][1] = 1
		connect_graph[0][9] = 1	
		connect_graph[1][0] = 1
		connect_graph[1][2] = 1

		connect_graph[2][1] = 1
		connect_graph[2][3] = 1

		connect_graph[3][2] = 1
		connect_graph[3][4] = 1

		connect_graph[4][3] = 1
		connect_graph[4][5] = 1

		connect_graph[5][4] = 1
		connect_graph[5][6] = 1

		connect_graph[6][5] = 1
		connect_graph[6][7] = 1

		connect_graph[7][6] = 1
		connect_graph[7][8] = 1
		connect_graph[7][9] = 1

		connect_graph[8][7] = 1
		connect_graph[8][9] = 1

		connect_graph[9][0] = 1
		connect_graph[9][7] = 1
		connect_graph[9][8] = 1

		shared_edges = [[None for i in range(num_nodes)] for i in range(num_nodes)]

		shared_edges[0][1] = [(1, 0),(1, 2)]
		shared_edges[0][9] = [(1, 3),(0, 3)]	

		shared_edges[1][0] = [(1, 0),(1, 2)]
		shared_edges[1][2] = [(2, 0),(2, 1)]
		
		shared_edges[2][1] = [(2, 0),(2, 1)]
		shared_edges[2][3] = [(3, 1),(3, 0)]

		shared_edges[3][2] = [(3, 1),(3, 0)]
		shared_edges[3][4] = [(5, 2),(4, 2)]

		shared_edges[4][3] = [(5, 2),(4, 2)]
		shared_edges[4][5] = [(4, 3),(5, 3)]

		shared_edges[5][4] = [(4, 3),(5, 3)]
		shared_edges[5][6] = [(3, 4),(5, 4)]

		shared_edges[6][5] = [(3, 4),(5, 4)]
		shared_edges[6][7] = [(2, 5),(2, 4)]

		shared_edges[7][6] = [(2, 5),(2, 4)]
		shared_edges[7][8] = [(1, 4),(2, 4)]
		shared_edges[7][9] = [(0, 5),(1, 4)]

		shared_edges[8][7] = [(1, 4),(2, 4)]
		shared_edges[8][9] = [(1, 4),(1, 3)]

		shared_edges[9][0] = [(0, 3),(1, 3)]
		shared_edges[9][7] = [(0, 5),(1, 4)]
		shared_edges[9][8] = [(1, 4),(1, 3)]



	return cvx_sets, connect_graph, shared_edges


if __name__ == "__main__":
	poly = [(1.0, 0),
				(2.0, 0),
				(2.0, 1.0),
				(3.0, 1.0),
				(3.0, 2.0),
				(2.0, 2.0),
				(2.0, 3.0),
				(1.0, 3.0),
				(1.0, 2.0),
				(0.0, 2.0),
				(0.0, 1.0),
				(1.0, 1.0)]

	holes = [[(1.2, 1.2),
			  (1.2, 1.8),
			  (1.8, 1.8),
			  (1.8, 1.2)]]

#	poly = [(0.0, 0),
#				(5.0, 0),
#				(5.0, 5.0),
#				(0.0, 5.0)]
#	holes = [[(1, 1),
#			  (1, 4),
#			  (4, 4),
#			  (4, 1)]]

#	poly = [(0.0, 0),
#				(1.0, 0),
#				(1.0, 1.0),
#				(2.0, 1.0),
#				(2.0, 2.0),
#				(0.0, 2.0)]
#
#	holes = []






	map_poly = [poly, holes]

	#greedy_decompose(map_poly)
	min_alt_decompose(polygon_generator(4))