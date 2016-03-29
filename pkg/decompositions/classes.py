import edges


class Decomposition:
	"""Set of Polygons in a decomposition.

	Decomposition container. Stores a set of Polygons. A set of reflex
	verticies. Several functions are also provided for operations.

	Attributes:
		polygon_original: Original polygon before decomposition
		polygons_list: A list of polygons in decomposition
		reflex_verts: Reflex verticies of the original undecomposed
						polygon
		adjacency_matrix: Adjacency matrix describing adjacency between
						polygons. An element is None if no adjacency,
							an edge if there is an adjacency.

	"""


	def __init__(self, P, P_list, reflex_verts):

		self.polygon_original = P
		self.reflex_verts_list = reflex_verts
		self.polygons_list = P_list
		self.adjacency_matrix = []


	def update_adjacency_matrix(self):
		"""Compute the adjacency matrix for a set of polygons

		Computes a matrix of adjacency between polygons in the decomposition.
		nxn matrix where n is the number of polygons. Element (i,j) is None if
		polygon i and polygon j are not adjacent. If they are adjacent, then
		element (i,j) contains an edge that is shared between the two polygons.
		Checks each unique pair of polygons to check for adjacency edges. Also
		adds new verticies to polygons if necessary. This is a requirement for
		the decomposition method.

		Args:
			self: Instance of Decomposition class

		Returns:
			adjacency_matrix: Matrix of adjacency
		"""


		self.adjacency_matrix = [[None for i in range(len(P_list))]
							 		for i in range(len(P_list))]



		for i in range(len(self.polygons_list)):
			for j in range(i+1, len(self.polygons_list)):

				# Only check exteriors
				p1 = self.polygons_list[i][0]; p2 = self.polygons_list[j][0]
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
							p1_new = p1
							p2_new = p2
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

		# Test each pair of polys and determine if they are adjacent
		for p1_idx in range(len(P_list)):
			for p2_idx in range(p1_idx+1, len(P_list)):

				p1 = P_list[p1_idx]; p2 = P_list[p2_idx]
				p1_ext = p1[0]; p2_ext = p2[0]
				n1 = len(p1_ext); n2 = len(p2_ext)

				#print("p1: %s"%(p1,))
				# Test every pair of edges from both polygons to see equality
				for i in range(n1):
					edge1 = [p1_ext[i]]+[p1_ext[(i+1)%n1]]
					for j in range(n2):
						edge2 = [p2_ext[j]]+[p2_ext[(j+1)%n2]]

	#					print("Edge1: %s Edge2: %s"%(edge1, edge2))
						has_overlap, coords = edges.check_for_overlap(edge1, edge2)
						if has_overlap:
	#						print coords
							adj_matrix[p1_idx][p2_idx] = coords
							adj_matrix[p2_idx][p1_idx] = coords

		return adj_matrix











	def get_poly(poly_id):
		"""Test

		Test

		Args:
			sds

		Returns:
			sds
		"""

		return


	def remove_poly(poly_id):
		"""Test

		Test

		Args:
			sds

		Returns:
			sds
		"""

		return


	def insert_poly(poly):
		"""Test

		Test

		Args:
			sds

		Returns:
			sds
		"""

		return


	def get_polygon_containing_point(point):			
		"""Test

		Test

		Args:
			sds

		Returns:
			sds
		"""


		return
