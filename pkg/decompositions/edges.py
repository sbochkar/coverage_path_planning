from shapely.geometry import LineString


BUFFER_RADIUS = 10e-10


def check_for_overlap(edge1, edge2):
	"""Perform check for overlap between edges

	Makes use of Shapely library

	Stuff to watch out for:
		For extremly small polygons, this will be an issue
		Don't know how fast shapely is, scalable?

	Args:
		edge1: x,y of first edge
		edge2: x,y of second edge

	Returns:
		has_overlap: Is there overlap
		coords: Coordinates of the overlap
	"""

	ls_edge1 = LineString(edge1).buffer(BUFFER_RADIUS, cap_style=2)
	ls_edge2 = LineString(edge2)

	intersection = ls_edge1.intersection(ls_edge2)

	# Should always be LineString object or a point or empty
	if intersection.geom_type == "LineString":
		if intersection.length > 100*BUFFER_RADIUS:
			coords = intersection.coords[:]
			return True, coords
		else:
			return False, None
	else:
		return False, None
