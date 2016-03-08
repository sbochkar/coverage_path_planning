def get_mapping(segments):
	"""
	Generate a dictionary which maps an integer to a segment and a direction
	Useful for referencing lines and points.
	"""

	mapping = {}

	counter = 0
	for segment in segments:
		for i in range(segment.dirs_num):
			mapping[counter+i] = (segment, i)

		counter += i+1

	return mapping