try:
	import matplotlib.pyplot as plt
	from shapely.geometry import Polygon
except ImportError: print("Importing modules failed!")


def init_axis():
	"""
	Initializes plotting area
	:param None:
	:return: Axes object
	"""

	fig = plt.figure()
	ax = fig.add_subplot(111)

	return ax


def plot_polygon_outline(ax, polygon):
	"""
	Function will plot the ouline of cleaning area. No decomposition.
	Adjust the axis as well.
	:param ax: Axis object for redundancy
	:param polygon: Possibly with holes
	:return: None
	"""
	pass


def plot_decomposition(ax, cvx_set, shared_edges):
	"""
	Function plots the result of the decomposition.
	:param ax: Axis object for redundancy
	:param shared_edges: Shared edges between cells
	:param cvx_set:A list of convex cells:
	:retur: None
	"""

	# Plot individual cells
	for poly in cvx_set:

		poly_shp = Polygon(poly)
		x, y = poly_shp.exterior.xy
		ax.plot(x, y, color='#6699cc', alpha=0.7,
				linewidth=3, solid_capstyle='round', zorder=1)

	# Plot individual shared edge
	num_nodes = len(shared_edges)
	for i in range(num_nodes):
		for j in range(num_nodes):

			if shared_edges[i][j] is not None:
				x, y = zip(*shared_edges[i][j])
				ax.plot(x, y, color='red', alpha=0.8, linewidth=3, zorder=2)


def plot_shared_edge(ax, shared_edges):
	"""
	Function will plot shared edges.
	:param ax: Axis object
	:param shared_edges: nxn matrix of shared edges
	:return None:
	"""

	num_nodes = len(shared_edges)
	for i in range(num_nodes):
		for j in range(num_nodes):

			if shared_edges[i][j] is not None:
				x, y = zip(*shared_edges[i][j])
				ax.plot(x, y, color='red', alpha=0.8, linewidth=3, zorder=2)


def plot_samples(ax, lines):
	"""
	Function will plot the samples inside the cvx sets
	:param ax: Axis object
	:param lines: List of lines for each convex set
	:return: None
	"""

	for line_set in lines:
		for line in line_set:
			x, y = zip(*line)
			ax.plot(x, y, color='orange', alpha=0.9, linewidth=3, zorder=3)	


def display():
	"""
	Function display the figure
	:return: None
	"""

	plt.show()