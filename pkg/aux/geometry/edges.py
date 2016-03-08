from shapely.geometry import LineString


BUFFER_TOLERANCE = 0.0001

def check_for_overlap(edge1, edge2):
	"""
	Perform check for overlap between edges

	Makes use of Shapely library

	Stuff to watch out for:
		For extremly small polygons, this will be an issue
		Don't know how fast shapely is, scalable?

	:param edge1: x,y of first edge
	:param edge2: x,y of second edge
	:return has_overlap: Is there overlap
	:return coords: Coordinates of the overlap
	"""

	# imrpoved version of the comparison where
	# edges may overlap but not along entire length

	ls_edge1 = LineString(edge1).buffer(BUFFER_TOLERANCE)
	ls_edge2 = LineString(edge2)

	isection = ls_edge1.intersection(ls_edge2)

	# Should always be LineString object or a point or empty
	if isection.geom_type == "LineString":
		if isection.length > 10*BUFFER_TOLERANCE:
			coords = isection.coords[:]
			return True, coords
		else:
			return False, None
	else:
		return False, None