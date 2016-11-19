def polygon_area(polygon=[[],[]]):
	"""
	Compute the area of a simple polygon

	P=[Z_0,Z_1,...]
	"""

	num_holes = len(polygon)

	boundary = polygon[0]
	n = len(boundary)
	area = 0.0
	for i in range(n):
		j = (i+1) % n
		area += boundary[i][0] * boundary[j][1]
		area -= boundary[j][0] * boundary[i][1]
	area = abs(area)/2.0

	for hole in polygon[1:]:
		if not hole:
			break

		n = len(hole)
		hole_area = 0.0
		for i in range(n):
			j = (i+1) % n
			hole_area += hole[i][0] * hole[j][1]
			hole_area -= hole[j][0] * hole[i][1]
		area -= abs(hole_area)/2.0

	return area