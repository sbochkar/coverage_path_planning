import visilibity as vis
from shapely.geometry import LinearRing


def compute(v, P):
	"""
	Compute the visible part of P from v
	"""

	#print("Previsible polygon: %s"%(P,))
	# Used for visilibity library
	epsilon = 0.01

	#Using the visilibity library, define the reflex vertex
	observer = vis.Point(*v[1])

	# To put into standard form, do this
	if not LinearRing(P[0]).is_ccw:
		ext = P[0][::-1]
	else:
		ext = P[0]
	x_min_idx, x_min = min(enumerate(ext), key=lambda x: x[1])
	ext = ext[x_min_idx:]+ext[:x_min_idx]

	#print x_min_idx, x_min

	# Define the walls of intersection in Visilibity domain
	wall_points = []
	for point in ext:
		wall_points.append(vis.Point(*point))
	#print 'Walls in standard form : ',vis.Polygon(wall_points).is_in_standard_form()

	#for i in range(len(vis_intersection_wall_points)):
		#print vis_intersection_wall_points[i].x(), vis_intersection_wall_points[i].y()
		#print point.x(), point.y()

	# Define the holes of intersection in Visilibity domain
	holes = []
	for interior in P[1]:
		hole_points = []
		for point in interior:
			hole_points.append(vis.Point(*point))

		holes.append(hole_points)
		#print 'Hole in standard form : ',vis.Polygon(hole_points).is_in_standard_form()

	# Construct a convinient list
	env = []
	env.append(vis.Polygon(wall_points))
	for hole in holes:
		env.append(vis.Polygon(hole))

	# Construct the whole envrionemt in Visilibity domain
	env = vis.Environment(env)

	# Construct the visible polygon
	observer.snap_to_boundary_of(env, epsilon)
	observer.snap_to_vertices_of(env, epsilon)

	vis_free_space = vis.Visibility_Polygon(observer, env, epsilon)

	point_x, point_y  = save_print(vis_free_space)
	point_x.append(vis_free_space[0].x())
	point_y.append(vis_free_space[0].y())  

	return point_x, point_y


def save_print(polygon):
	end_pos_x = []
	end_pos_y = []
	for i in range(polygon.n()):
		x = polygon[i].x()
		y = polygon[i].y()

		end_pos_x.append(x)
		end_pos_y.append(y)

	return end_pos_x, end_pos_y 