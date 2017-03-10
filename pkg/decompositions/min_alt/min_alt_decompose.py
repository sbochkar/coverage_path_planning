from shapely.geometry import LineString
from shapely.geometry import LinearRing
from math import sqrt
import operator
import itertools


def reoptimize(workspace, decomposition):
	"""
	Reoptimize a decomposition for minimum overall altitude of workspace.

	Assumes the decomposition on workspace is convex.

	:param workspace: A polygon, possibly with holes, that was decomposed.
	:param decomposition: Convex decomposition performed on polygon.
	:param adj: Adjacency graph for decomposition.
	:return decomposition: Modified decomposition.
	"""

	reflex_verts = rlx.find_reflex_vertices(workspace)

	while reflex_verts:

		reflex_vert = reflex_verts.pop()

		# Decomposition is modified in-place
		decomposition = ops.fuse_polys_around_vertex(reflex_vert, decomposition)
		
		adjacency_matrix = adj.compute_adjacency_matrix(decomposition)

		cell, cell_id = find_poly_containing_vertex(decomposition, reflex_vert)
		# If multiple polygon were found, this will pick the first one.
		if not cell:
			print("[ERROR] Did not find a polygon containing a vertex!")
			# The operation failed on this vertex, try the next one.
			continue

		min_alt, min_theta = alt.get_min_altitude(cell)

		# Update v within cell
		test_lr = LinearRing(cell[0])
		if not test_lr.is_ccw: cell[0] = cell[0][::-1]
		v_new = update_v_id(cell, reflex_vert)

		# Find an optimal cut from v[1] within cell
		cut = cuts.find_optimal_cut(cell, v_new)
#		print("Proposed cut: %s"%(cut,))
		# Evaluate the potential optimal cut
		if cut and cut is not None: # Not empty
			p_l, p_r = cuts.perform_cut(cell, [reflex_vert[1], cut[0]])

			p_l = round_vertecies(p_l)
			p_r = round_vertecies(p_r)
			#print p_l
			#print p_r
			altitude_pl = alt.get_min_altitude([p_l,[]])
			altitude_pr = alt.get_min_altitude([p_r,[]])

			# If cut improves altitude
			if altitude_pr+altitude_pl < min_alt:

				decomposition.pop(cell_id)
				decomposition.append([p_l, []])
				decomposition.append([p_r, []])

				# Need to process all polygons in the decomposition to introduce
				# 	aditional veritices where cuts were made
				decomposition = post_processs_decomposition(decomposition)
				#print decompsition
#		print("Decomp. after one reflex: %s"%(decomposition,))
	#print decomposition
	return decomposition


def old_decompose(polygon):
	"""
	Mininimum altitude decomposition.
	
	[Older Implementation] Holes are recombines with the boundar via vertical
	cuts.

	:param polygon: Polygin in the standard form.
	:return decomposition: A set of polygons representing a decomposition
	"""

	min_alt, min_theta = alt.min_altitude(polygon)
	P_fused, modified_edges = chain_combination.combine_chains(polygon, min_theta)

	recursive_cuts(P_fused)

	return list_of_polygons




def find_poly_containing_vertex(decomposition, v):
	"""
	"""

	for i in range(len(decomposition)):

		chain = decomposition[i][0]

		if v[1] in chain:
			return decomposition[i], i

	return []


def update_v_id(polygon, v):

	for i in range(len(polygon[0])):
		if v[1] == polygon[0][i]: return (i, v[1])


def round_vertecies(polygon):
	new_p = []
	for v in polygon:
		new_p.append((round(v[0],5), round(v[1],5)))
	return new_p

def euc_distance(p1, p2):
	return sqrt((p2[1]-p1[1])**2+(p2[0]-p1[0])**2)

def post_processs_decomposition(decomp):

	for a in range(len(decomp)):
		for b in range(a+1, len(decomp)):

			p1 = decomp[a][0] #ext only
			p2 = decomp[b][0] #ext only

			p1_new = p1
			p2_new = p2

			n1 = len(p1); n2 = len(p2)

			# Test every pair of edges from both polygons to see equality
			for i in range(n1):
				edge1 = [p1[i]]+[p1[(i+1)%n1]]

				for j in range(n2):
					edge2 = [p2[j]]+[p2[(j+1)%n2]]

					#print("Edge1: %s Edge2: %s"%(edge1, edge2))
					has_overlap, coords = edges.check_for_overlap(edge1, edge2)
					if has_overlap:

						# Consider each edge separately.
						if euc_distance(edge1[0], coords[0])<euc_distance(edge1[0], coords[1]):
							if euc_distance(edge1[0], coords[0]) > 0.001: new_edge1 = [edge1[0]]+[coords[0]]
							else: new_edge1 = [edge1[0]]

							if euc_distance(edge1[1], coords[1]) > 0.001: new_edge1 = new_edge1+[coords[1]]+[edge1[1]]
							else: new_edge1 = new_edge1 + [edge1[1]]
						else:
							if euc_distance(edge1[0], coords[1]) > 0.001: new_edge1 = [edge1[0]]+[coords[1]]
							else: new_edge1 = [edge1[0]]

							if euc_distance(edge1[1], coords[0]) > 0.001: new_edge1 = new_edge1+[coords[0]]+[edge1[1]]
							else: new_edge1 = new_edge1 + [edge1[1]]

						if euc_distance(edge2[0], coords[0])<euc_distance(edge2[0], coords[1]):
							if euc_distance(edge2[0], coords[0]) > 0.001: new_edge2 = [edge2[0]]+[coords[0]]
							else: new_edge2 = [edge2[0]]

							if euc_distance(edge2[1], coords[1]) > 0.001: new_edge2 = new_edge2+[coords[1]]+[edge2[1]]
							else: new_edge2 = new_edge2 + [edge2[1]]
						else:
							if euc_distance(edge2[0], coords[1]) > 0.001: new_edge2 = [edge2[0]]+[coords[1]]
							else: new_edge2 = [edge2[0]]

							if euc_distance(edge2[1], coords[0]) > 0.001: new_edge2 = new_edge2+[coords[0]]+[edge2[1]]
							else: new_edge2 = new_edge2 + [edge2[1]]

#						print("Nedge1: %s"%(new_edge1,))
#						print("Nedge2: %s"%(new_edge2,))
#
						# Now insert new_edges to the polygon
						if len(new_edge1) == 3:
							p1_new.insert(i+1, new_edge1[1])
						elif len(new_edge1) == 4:
							p1_new.insert(i+1, new_edge1[1])
							p1_new.insert(i+2, new_edge1[2])

						if len(new_edge2) == 3:
							p2_new.insert(j+1, new_edge2[1])
						elif len(new_edge1) == 4:
							p2_new.insert(j+1, new_edge2[1])
							p2_new.insert(j+2, new_edge2[2])

#						print("Before Proces: %s"%(decomp[a],))
						decomp[a] = [p1_new, []]
#						print("After Proces:  %s"%(decomp[a],))
						decomp[b] = [p2_new, []]

	return decomp





list_of_polygons = []
def recursive_cuts(polygon):
	"""
	Recursive cut of Polygon
	"""

	reflex_verts = reflex.find_reflex_vertices(polygon)
	while reflex_verts:
		v = reflex_verts.pop()

		cut = cuts.find_optimal_cut(polygon, v)
		#print("Ref: %s"%(v[1],))
		#print("Cut: %s"%(cut,))

		if cut and cut is not None: # Not empty
			p_l, p_r = cuts.perform_cut(polygon, [v[1], cut[0]])

			#return [recursive_cuts([p_l,[]]), recursive_cuts([p_r,[]])]
			recursive_cuts([p_l,[]])
			recursive_cuts([p_r,[]])
			return
	#return polygon
	list_of_polygons.append(polygon)


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
	from ...poly_operations.others import reflex as rlx
	from ...poly_operations.others import operations as ops
	from ...poly_operations.others import adjacency as adj
	from ...aux.geometry import edges
