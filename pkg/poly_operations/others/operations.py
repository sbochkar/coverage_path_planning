from shapely.geometry import LinearRing
from ...poly_operations.others import adjacency as adj


def fuse_polys_around_vertex(v, decomposition):
	"""
	Fuse all cells that contain the vertex

	:param v: The vertex.
	:param decomposition: A decomposition containing a lis of cells. Modified
							in place
	:return None:
	"""

	adjacency = adj.compute_adjacency_matrix(decomposition)
	shared_edge_tuple = get_first_shared_edge(v, adjacency)
	#print adj
#	print("Shared edge tuple: %s"%(shared_edge_tuple,))

	while shared_edge_tuple:
		p1_id, p2_id, test_edge = shared_edge_tuple
#		print("Two adjacent ps: %d, %d"%(p1_id, p2_id))
#		# Get the exterior of the polygon since this is what will be combined
		P1 = decomposition[p1_id][0]
		P2 = decomposition[p2_id][0]


		# Combine the two into one polygon
		polygon = combine_two_adjacent_polys(P1, P2, test_edge)
#		print("Combined chain: %s"%(polygon,))
		# Remove P1 and P2 from decomposition set
		if p1_id > p2_id: decomposition.pop(p1_id); decomposition.pop(p2_id)
		else: decomposition.pop(p2_id); decomposition.pop(p1_id)
#		print("Popoed decomp: %s"%(new_decomposition,))
		# Insert the new polygon in the decomposition, assuming no new holes
		decomposition.append([polygon, []])
		adjacency = adj.compute_adjacency_matrix(decomposition)
#		print("Adj: %s"%(adj,))
#		print("Decomp after pop+add: %s"%(new_decomposition,))
		shared_edge_tuple = get_first_shared_edge(v, adjacency)

	return decomposition


def get_first_shared_edge(v, adj):

	for i in range(len(adj)):
		for j in range(i, len(adj)):

			if not adj[i][j] is None:
				if v[1] in adj[i][j]:
					return (i, j, adj[i][j])
	return []


def combine_two_adjacent_polys(p1, p2, e):
	"""
	Assuming they are adjacent
	"""

	# I think it make sense to round all values here
#	new_p1 = []
#	for v in p1:
#		new_p1.append((round(v[0], 5), round(v[1], 5)))
#	p1 = new_p1
#
#	new_p2 = []
#	for v in p2:
#		new_p2.append((round(v[0], 5), round(v[1], 5)))
#	p2 = new_p2
#
#	new_e = []
#	for v in e:
#		new_e.append((round(v[0], 5), round(v[1], 5)))
#	e = new_e
#
#	print p1, p2


	#v = round(e[0][0], 5), round(e[0][1], 5) ; w = round(e[1][0], 5), round(e[1][1], 5)
	v = e[0]; w = e[1]

	# Make sure the last and first verticies are not same
	if p1[0] == p1[-1]: p1 = p1[:-1]
	if p2[0] == p2[-1]: p2 = p2[:-1]

	p1_v_idx = p1.index(v)
	p2_v_idx = p2.index(v)

	p1_w_idx = p1.index(w)
	p2_w_idx = p2.index(w)

#	print("p1_v_i:%d p1_w_i:%d"%(p1_v_idx, p1_w_idx))
#	print("p2_v_i:%d p2_w_i:%d"%(p2_v_idx, p2_w_idx))

	if (p1_v_idx == 0) and (p1_w_idx == 1): left_chain = p1[1:]+[p1[0]]
	elif (p1_v_idx == 0) and (p1_w_idx == len(p1)-1): left_chain = p1[:]
	elif (p1_w_idx == 0) and (p1_v_idx == 1): left_chain = p1[1:]+[p1[0]]
	elif (p1_w_idx == 0) and (p1_v_idx == len(p1)-1): left_chain = p1[:]
	elif p1_v_idx < p1_w_idx: left_chain = p1[p1_w_idx:]+p1[:p1_v_idx+1]
	elif p1_w_idx < p1_v_idx: left_chain = p1[p1_v_idx:]+p1[:p1_w_idx+1]

	if (p2_v_idx == 0) and (p2_w_idx == 1): right_chain = p2[2:]
	elif (p2_v_idx == 0) and (p2_w_idx == len(p2)-1): right_chain = p2[1:-1]
	elif (p2_w_idx == 0) and (p2_v_idx == 1): right_chain = p2[2:]
	elif (p2_w_idx == 0) and (p2_v_idx == len(p2)-1): right_chain = p2[1:-1]	
	elif p2_v_idx < p2_w_idx: right_chain = p2[p2_w_idx+1:]+p2[:p2_v_idx]
	elif p2_w_idx < p2_v_idx: right_chain = p2[p2_v_idx+1:]+p2[:p2_w_idx]

#	print left_chain
#	print right_chain
	lr_left = LinearRing(p1); lr_right = LinearRing(p2)

	if lr_left.is_ccw:
		if lr_right.is_ccw: fuse = left_chain+right_chain
		else: 				fuse = left_chain+right_chain[::-1]
	else:
		if lr_right.is_ccw: fuse = left_chain+right_chain[::-1]
		else: 				fuse = left_chain+right_chain

	return fuse

#e = [(0.0, 10.0), (4.0, 7.0)]
#p1 = [(0.0, 10.0), (5.0, 1.0), (4.0, 7.0)]
#p2 = [(4.0, 7.0), (5.0, 10.0), (0.0, 10.0)]
#
#print combine_two_adjacent_polys(p1, p2 ,e)

def find_cut_edge(p1, p2, v):
	"""
	Find a shared edge between two polygons
	"""

	idx_1 = p1.index(v)
	idx_2 = p2.index(v)

	p1_edge_1 = [p1[idx_1], p1[(idx_1+1)%len(p1)]]
	p1_edge_2 = [p1[idx_1], p1[(idx_1-1)%len(p1)]]

	p2_edge_1 = [p2[idx_2], p2[(idx_2+1)%len(p2)]]
	p2_edge_2 = [p2[idx_2], p2[(idx_2-1)%len(p2)]]

	if p1_edge_1 == p2_edge_1: return p1_edge_1
	elif p1_edge_1 == p2_edge_2: return p1_edge_1
	elif p1_edge_2 == p2_edge_1: return p1_edge_2
	elif p1_edge_2 == p2_edge_2: return p1_edge_2

	print "SOMETHING WENT WORNG AND SHARED EDGE WAS NOT FOUND"


def find_common_polys(D, v):

	found_polys = []
	for poly in D:
		if v in poly:
			found_polys.append(poly)

	if len(found_polys) > 2:
		"SOMETHING WRONG, MORE THAN ONE COMMON POLYS"

	return found_polys[0], found_polys[1]