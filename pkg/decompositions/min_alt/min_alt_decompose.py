import operator


def build_set_shared_edges(v, adj):

	shared_edges = []
	for i in range(len(adj)):
		for j in range(i, len(adj)):

			if not adj[i][j] is None:

				if v in adj[i][j]:
					shared_edges.append((i, j, adj[i][j]))

	return shared_edges


def combine_polygons_from_decomposition(shared_edges, decomposition, adj):

	while shared_edges:

		p1_id, p2_id, test_edge = shared_edges.pop()

		# Get the exterior of the polygon since this is what will be combined
		P1 = decomposition[p1_id][0]
		P2 = decomposition[p2_id][0]

		print P1, P2
		print operations.combine_two_adjacent_polys(P1, P2, test_edge)


def reoptimize(P, decomposition, adj):
	"""
	"""

	# Build a set of reflex verticies
	R = reflex.find_reflex_vertices(P)

	while R:
		# Pick one reflex vertex from R
		v = R.pop()

		# Build a set of all shared edges in the decomposition which shared v
		shared_edges = build_set_shared_edges(v[1], adj)

		if not shared_edges: continue # TODO: ATTEMPT TO DO OPTIMIZING CUT

		combine_polygons_from_decomposition(shared_edges, decomposition, adj)
		# Combine all polygons in shared_edges to form one polygon





def decompose(P):
	"""
	Min altitude decomposition.

	1: Connect all simple chains of a polygon
	2: Perform a series of decomposing cuts
	3: Run an iterative minimization step to reoptimize cuts

	:param P: Polygin in the standard form
	:return decomposition: A set of polygons
	"""

	min_alt, theta = alt.get_min_altitude(P)
	#print("Min Alt: %2f, Theta: %2f"%(min_alt, 180*theta/3.14))
	P_fused, modified_edges = chain_combination.combine_chains(P, theta)

	#D = recursive_cuts(P_fused)
	recursive_cuts(P_fused)
	#print("List of polygons after recursion: %s"%(list_of_polygons,))

	# Need a smarter way of doing this
	#if len(D) == 2:
	#	if not D[1]:
	#		D = [D]


	return list_of_polygons


list_of_polygons = []
def recursive_cuts(P):
	"""
	Recursive cut of Polygon
	"""

	R = reflex.find_reflex_vertices(P)
	while R:
		v = R.pop()

		cut = cuts.find_optimal_cut(P, v)
		#print("Ref: %s"%(v[1],))
		#print("Cut: %s"%(cut,))

		if cut and cut is not None: # Not empty
			p_l, p_r = cuts.perform_cut(P, [v[1], cut[0]])

			#return [recursive_cuts([p_l,[]]), recursive_cuts([p_r,[]])]
			recursive_cuts([p_l,[]])
			recursive_cuts([p_r,[]])
			return
	#return P
	list_of_polygons.append(P)


if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))
		from aux.geometry import rotation
		import reflex
else:
	from ...aux.altitudes import altitude as alt
	from ...decompositions.min_alt import cuts
	from ...poly_operations.others import chain_combination
	from ...poly_operations.others import reflex
	from ...poly_operations.others import operations
