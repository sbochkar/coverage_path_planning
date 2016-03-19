from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.ops import cascaded_union


def covered_area(tour, mapping, r):
	"""
	Function will print info about the path
	"""

	segment_area = 0
	polygons = []
	# Now compute the cost of the transitions
	for i in range(len(tour)):
		segment = mapping[tour[i]][0]

		coords = segment.coords
		line = LineString(coords)
		polygons.append(line.buffer(r))

	total_area = cascaded_union(polygons)

	return total_area.area

def polygon_area(P):

	Poly = Polygon(*P)

	return Poly.area