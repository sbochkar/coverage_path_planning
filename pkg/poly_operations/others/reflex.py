def find_reflex_vertices(P):
	"""
	Return a list of reflex vertices in P

	Function will iterate over all vertices in P and return a list of reflex
	vertices

	Args:
		P: (ext, [int]) tuple of list of (x,y) vertices 
			ext is a ccw list of vertices for boundary
			int is cw list of vertices for holes
	Returns:
		R: A list of reflex vertices
	"""

	R = []
	adj_dict = adj.get_edge_adjacency_as_dict(P)

	for v in adj_dict.keys():
		p_0 = adj_dict[v][1]
		p_1 = v
		p_2 = adj_dict[v][0]

		dx_1 = float(p_1[1][0])-float(p_0[1][0])
		dy_1 = float(p_1[1][1])-float(p_0[1][1])
		dx_2 = float(p_2[1][0])-float(p_1[1][0])
		dy_2 = float(p_2[1][1])-float(p_1[1][1])
		if dx_1*dy_2-dy_1*dx_2 < 0.0:
			R.append(p_1)
	return R


if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))
		#from poly_operations.others import adjancency_edges
		import adjacency_edges as adj
else:
	import adjacency_edges as adj
