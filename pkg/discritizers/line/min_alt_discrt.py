from shapely.geometry import LinearRing
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely import affinity


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
	offset_ext = lr_ext.parallel_offset(width/2, side='left', join_style=1)

	lr_new_holes = []
	for hole in P[1]:
		lr_hole = LinearRing(hole)
		offset_hole = lr_hole.parallel_offset(width/2, side='left', join_style=1)
		lr_new_holes.append(offset_hole)

	if offset_ext.is_empty:
		print(offset_ext)
		print("Line generation ERROR: Shrunk polygon is not valid")
		return []
	
	shrunk_polygon = Polygon(offset_ext, lr_new_holes)

	if not shrunk_polygon.is_valid:
		print("Line generation ERROR: Shrunk polygon is not valid")
		return []


	minx, miny, maxx, maxy = shrunk_polygon.bounds

	# Start generating lines from left to right equidistance from each other
	segments = []
	cur_x = minx
	finishing_touches = False

	while (cur_x <= maxx) or (finishing_touches):

		if finishing_touches:
			cur_x = maxx-0.001

		# Crudely deal with the very first line
		if cur_x == minx:
			test_line = LineString([(cur_x+0.001, miny), (cur_x+0.001, maxy)])
		else:
			test_line = LineString([(cur_x, miny), (cur_x, maxy)])


		intersection = shrunk_polygon.intersection(test_line)
		# Handle each type of intersection separatly
		if intersection.geom_type == "Point":
			new_coord = rotation.rotate_points(intersection.coords[:], theta)
			segments.append(classes.PointSegment(*new_coord))
		elif intersection.geom_type == "LineString":
			# Rotate back and append
			new_coords = rotation.rotate_points(intersection.coords[:], theta)
			segments.append(classes.LineSegment(new_coords))
		elif intersection.geom_type == "MultiLineString":
			for line in intersection:
				new_coords = rotation.rotate_points(line.coords[:], theta)
				segments.append(classes.LineSegment(new_coords))
		elif intersection.geom_type == "GeometricCollection":
			for element in intersection:
				if element.geom_type == "Point":
					new_coord = rotation.rotate_points(element.coords[:], theta)
					segments.append(classes.PointSegment(*new_coord))
				elif element.geom_type == "LineString":
					new_coords = rotation.rotate_points(element.coords[:], theta)
					segments.append(classes.LineSegment(new_coords))
				elif element.geom_type == "MultiLineString":
					for line in element:
						new_coords = rotation.rotate_points(line.coords[:], theta)
						segments.append(classes.LineSegment(new_coords))

		cur_x += width

		if (cur_x > maxx) and (cur_x <= maxx+width/2):
			finishing_touches = True
		else:
			finishing_touches = False


	# Process the last segment


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
