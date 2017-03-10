import itertools
import edges
from math import sqrt


def compute_adjacency_matrix(polys):
	"""
	Generate an adjacency matrix for a set of polygons in a decomposition.

	Implementation: test each polygon with each other for presence of shared
						edges.

	a_i,j = 1 if polygons i and j are adjacent.

	[TODO]: Add functionality to store multiple shared edges if there any.

	:param polys: A set of polygons in the standard form.
	:return adjacency_matrix: A matrix describing the adjacency graph of decomp.
	"""

	adj_mtx = [[None for i in range(len(polys))] for i in range(len(polys))]

	# Add indicies to polygons for easier references later.
	poly_idx = enumerate(polys)
	for item_a, item_b in itertools.combinations(poly_idx, 2):

		poly_a_idx, poly_a = item_a
		poly_b_idx, poly_b = item_b

		poly_a = poly_a[0]
		poly_b = poly_b[0]

		# Convert polygon verts to pairs of verts representing edges.
		edges_a = [(poly_a[i], poly_a[i+1]) for i in range(len(poly_a)-1)]
		edges_b = [(poly_b[i], poly_b[i+1]) for i in range(len(poly_b)-1)]

		for edge_1, edge_2 in itertools.product(edges_a, edges_b):

			overlap_coords = edges.check_for_overlap(edge_1, edge_2)
			if overlap_coords:

				if adj_mtx[poly_a_idx][poly_b_idx]:

					# Quick and dirty way of picking longer shared edge
					old_line = LineString(adj_mtx[poly_a_idx][poly_b_idx])
					new_line = LineString(overlap_coords)

					if new_line.length > old_line.length:
						adj_mtx[poly_a_idx][poly_b_idx] = overlap_coords
						adj_mtx[poly_b_idx][poly_a_idx] = overlap_coords
				else:
					adj_mtx[poly_a_idx][poly_b_idx] = overlap_coords
					adj_mtx[poly_b_idx][poly_a_idx] = overlap_coords			

	return adj_mtx