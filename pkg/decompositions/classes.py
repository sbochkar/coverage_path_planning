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


	def update_adjacency_matrix(P_list):
		"""

		sd

		Args:
			sadasd:sd

		Returns:
			sdsd
		"""

		return


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
