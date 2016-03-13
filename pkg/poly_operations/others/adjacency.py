

def get_adjacency_as_matrix(P_set):
	"""
	Generate adjacency matrix for a set of polygons

	:param P_set: A set of polygons in the standard form
	:return adjacency: A matrix where elem 1: if polygons are adjacent
	"""

	adj_matrix = [[None for i in range(len(P_set))] for i in range(len(P_set))]
	# Test each pair of polys and determine if they are adjacent
	for p1_idx in range(len(P_set)):
		for p2_idx in range(p1_idx+1, len(P_set)):

			p1 = P_set[p1_idx]; p2 = P_set[p2_idx]
			p1_ext = p1[0]; p2_ext = p2[0]
			n1 = len(p1_ext); n2 = len(p2_ext)

			print("p1: %s"%(p1,))
			# Test every pair of edges from both polygons to see equality
			for i in range(n1):
				edge1 = [p1_ext[i]]+[p1_ext[(i+1)%n1]]
				for j in range(n2):
					edge2 = [p2_ext[j]]+[p2_ext[(j+1)%n2]]

					print("Edge1: %s Edge2: %s"%(edge1, edge2))
					has_overlap, coords = edges.check_for_overlap(edge1, edge2)
					if has_overlap:
						adj_matrix[p1_idx][p2_idx] = coords
						adj_matrix[p2_idx][p1_idx] = coords

	return adj_matrix


if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))
		from aux.geometry import edges
		
		#P = pl.polygon_generator(1)
		p1 = [[(0,0),(1,0),(1,1),(0,1)],[]]
		p2 = [[(1,0),(2,0),(2,1),(1,1)],[]]
		P = [p1, p2]
		adj = get_adjacency_as_matrix(P)
		print adj
else:
	from ...aux.geometry import edges
