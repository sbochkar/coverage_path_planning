from py2d.Math import Polygon


def decompose(P):
	"""
	Greedy decomposition of a polygon with holes based on works of Author[ ]
	:param P: Polygon in a standard form [ext, [inters]]
	:return cvx_set: Set of convex polygons
	"""

	ext, holes = P

	poly_ext = Polygon.from_tuples(ext)

	poly_holes = []
	for hole in holes:
		poly_hole = Polygon.from_tuples(hole)
		poly_holes.append(poly_hole)

	polygons = Polygon.convex_decompose(poly_ext, poly_holes)

	decomposition = [[poly.as_tuple_list(), []] for poly in polygons]
	
	if not decomposition:
		print "ERROR! Decomposition resulted in empty list"

	return decomposition
