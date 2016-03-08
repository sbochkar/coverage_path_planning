from shapely.geometry import LinearRing
from shapely.geometry import LineString
from shapely.geometry import Polygon


def discritize_set(D, width):
	"""
	Wrapper for discritization. Given a set of polygon in standard form.
	Generate segments
	"""

	segments = []
	for poly in D:
		segments.extend(discritize(poly, width))

	return segments

def discritize(P, width):
	"""
	Function will discritize the free space of a given polygon with minimum
	number of lines
	:param P: polygon in standard form
	:param width: distance between lines
	:return lines: a set of segments which could be lines of points
	"""

	altitude, theta = alt.get_min_altitude(P)
	segments = populate_with_lines(P, width, theta)

	return segments


def populate_with_lines(P, width, theta):
	"""
	Populate the free space of P with lines oriented at theta space width appart
	Approach:
		Utilize from shapely:
				Polygon, parallel_offset 

		Get the chains of exterior and holes
		Parallel offset them by width in appropriate directions
		Create a polygon with the new chains
		If valid, generate lines on this
		Return coordinates

	Thigns to watch out for:
		What to do with invalid polygons
		Narrow corridors between holes may result in no lines even when
			there is space for it. Because of equidistance between lines

		We can get disconnected polygons if there narrow corridors

		The uncovered area in the end of the polygon can be handled easily here
	Returns a set of lines and their coordinates
	"""


	P = rotation.rotate_polygon(P, -theta)

	# Parallel offset the boundaries of ext and holes
	lr_ext = LinearRing(P[0])
	offset_ext = lr_ext.parallel_offset(width, side='left', join_style=1)

	lr_new_holes = []
	for hole in P[1]:
		lr_hole = LinearRing(hole)
		offset_hole = lr_hole.parallel_offset(width, side='left', join_style=1)
		lr_new_holes.append(offset_hole)


	shrunk_polygon = Polygon(lr_ext, lr_new_holes)

	if not shrunk_polygon.is_valid:
		print("Line generation ERROR: Shrunk polygon is not valid")
		return None


	minx, miny, maxx, maxy = shrunk_polygon.bounds

	# Start generating lines from left to right equidistance from each other
	segments = []
	cur_x = minx

	while cur_x <= maxx:

		test_line = LineString([(cur_x, miny), (cur_x, maxy)])

		intersection = shrunk_polygon.intersection(test_line)

		# Handle each type of intersection separatly
		if intersection.geom_type == "Point":
			segments.append(classes.PointSegment((intersection.x, intersection.y)))
		elif intersection.geom_type == "LineString":
			segments.append(classes.LineSegment(intersection.coords[:]))
		elif intersection.geom_type == "MultiLineString":
			for line in intersection:
				segments.append(classes.LineSegment(line.coords[:]))
		elif intersection.geom_type == "GeometricCollection":
			for element in intersection:
				if element.geom_type == "Point":
					segments.append(classes.PointSegment((element.x, element.y)))
				elif element.geom_type == "LineString":
					segments.append(classes.LineSegment(element.coords[:]))
				elif element.geom_type == "MultiLineString":
					for line in element:
						segments.append(classes.LineSegment(line.coords[:]))

		cur_x += width

	return segments


if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))
		from aux.geometry import edges
		from aux.altitudes import altitude as alt
		from aux.geometry import rotation

		sys.path.insert(0, os.path.abspath(".."))
		import classes
else:
	from ...aux.geometry import rotation
	from ...aux.altitudes import altitude as alt
	from ...poly_operations.others import directions
	from .. import classes

#print populate_with_lines(([[(0,0),(10,0),(4.8,5),(10,10),(0,10)], []]), 0.1, 0)