from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.ops import cascaded_union
from ..discritizers import classes


def covered_area(tour, mapping, r):
	"""
	Function will print info about the path
	"""

	if isinstance(mapping[tour[0]][0], classes.PointSegment):
		coord = mapping[tour[0]][0].coord
		seg = Point(coord)
	elif isinstance(mapping[tour[0]][0], classes.LineSegment):
		coords = mapping[tour[0]][0].coords
		seg = LineString(coords)

	segment_area = seg.buffer(r)
	
	polygons = []
	# Now compute the cost of the transitions
	for i in range(1, len(tour)):
		segment = mapping[tour[i]][0]

		if isinstance(segment, classes.PointSegment):
			coord = segment.coord
			seg = Point(coord)
		elif isinstance(segment, classes.LineSegment):
			coords = segment.coords
			seg = LineString(coords)

		#polygons.append(seg.buffer(r))
		segment_area = segment_area.union(seg.buffer(r+0.00001))

	#total_area = cascaded_union(polygons)

	#return total_area.area
	return segment_area.area

def polygon_area(P):

	Poly = Polygon(*P)

	return Poly.area