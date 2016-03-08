

def get_edge_adjacency_as_dict(P):
	"""
	Thie function will form an adjacency list representing polyong's edges.

	Args:
		P: polygon specified in the form of a tuple (ext, [int]). ext is a
			list of (x, y) tuples specifying the exterior of a polygon ccw.
			[int] is a list of lists of (x, y) tupeles specifying holes of a
			polygon cw.

	Returns:
		dict: Dict representing an adjacency list of P
	"""

	ext = P[0]
	holes = P[1] 

	adjacency_dict = {}

	n = len(ext)
	for i in range(n):
		unique_id = i, ext[i]
		next_id = (i+1)%n, ext[(i+1)%n]
		prev_id = (i-1)%n, ext[(i-1)%n]
		adjacency_dict[unique_id] = [next_id, prev_id]

	ext_n = n
	for hole in holes:
		n = len(hole)
		for i in range(n):
			unique_id = i+ext_n, hole[i]
			next_id = ((i+1)%n)+ext_n, hole[(i+1)%n]
			prev_id = ((i-1)%n)+ext_n, hole[(i-1)%n]
			adjacency_dict[unique_id] = [next_id, prev_id]

	return adjacency_dict	
