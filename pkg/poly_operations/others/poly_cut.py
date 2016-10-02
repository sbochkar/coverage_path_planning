from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
#from descartes.patch import PolygonPatch

def poly_cut(poly, line):
	"""
	Performs cut on a polygon with shapely objects.

	Args:
		P: Shapely Polygon object
		line: cut where the first coordinate is the origin of the cut
	Returns:
		
	"""

	def getExtrapolatedLine(line):
			"""
				Form a line extrapoled in both directions
			"""
			GROW_FACTOR = 10	# Should be a fuction of polygon
			end_points = line.coords

			p1,p2 = end_points
			
			a = (p1[0]-GROW_FACTOR*(p2[0]-p1[0]), p1[1]-GROW_FACTOR*(p2[1]-p1[1]))
			b = (p2[0]+GROW_FACTOR*(p2[0]-p1[0]), p2[1]+GROW_FACTOR*(p2[1]-p1[1]))
			return LineString([a,b])

	# Intersection points of the polygon boundary with the infinite extended line
	cross_pts = []

	intersection_line = getExtrapolatedLine(line)

	# Should be multilinestrings or linestring
	intersection = poly.intersection(line)

	if (isinstance(intersection, LineString)):
			end_points = intersection.coords
			p1,p2 = end_points

			cross_pts.append(p1)
			cross_pts.append(p2)

	elif (isinstance(intersection, MultiLineString)):
		for line in intersection:
			end_points = line.coords
			p1,p2 = end_points

			cross_pts.append(p1)
			cross_pts.append(p2)

	print cross_pts




P = Polygon([(0,0),(1,0),(1,1),(0,1)], [[(0.2,0.2),(0.2,0.8),(0.8,0.8),(0.8,0.2)]])
#P = Polygon([(0,0),(1,0),(1,1),(0,1)])
l = LineString([(0.5,0),(0.5,1)])
poly_cut(P,l)