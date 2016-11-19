from math import sqrt

from shapely.geometry import LineString

from polygon_area import polygon_area


def convex_divide(polygon=[[],[]], init_poss=[], area_req=1.0):
	"""
	Divide the polygon into len(init_poss) segments of area=area
	"""

	# Just one site then no need for decomposition
	if len(init_poss) == 1:
		return ({"polygon" : polygon,
				"sites"   : init_poss},
				{})


	boundary = polygon[0]


	# Get the distance between closest vertex in boundary of P to q
	# O(n^2logn)
	sites = []
	for x, y in init_poss:
		# Sort by distance from q and record only indecies of sites rather then points
		sorted_boundary = sorted(enumerate(boundary), key=lambda v: (x-v[1][0])**2+(y-v[1][1])**2)
		sites.append(sorted_boundary[0][0])



	# Construct the index list for easier back mapping of site locations
	site_indecies = [[] for i in range(len(boundary))]
	for i,site in enumerate(sites):
		site_indecies[site].append(i)
	sites.sort()



	index = sites[0]
	sites_right = [index]*sites.count(index)

	# Roate the cut CCW until exceeding area req or past the last site
	area_right = 0.0
	while area_right < area_req*len(sites_right) and index != sites[-1]:

		index += 1
		area_right = polygon_area([boundary[:index+1],[]])

		if index > 0 and index-1 in sites and index-1 != sites[0]:
			sites_to_include = [index-1]*(sites.count(index-1))
			sites_right.extend(sites_to_include)


	# If the last site contains multiple sites then include in the sites_array
	if index == sites[-1] and index == sites[0]:
		sites_right = [index]*(sites.count(index)-1)
	elif index == sites[-1] and sites.count(index)>1:
		sites_right.extend([index]*(sites.count(index)-1))

	area_right = polygon_area([boundary[:index+1],[]])


	# Now check the states
	if index == sites[0] and area_right > area_req*len(sites_right):
		print "Hits the first case"

		for front_index in range(sites[0]+1):
			if polygon_area([boundary[front_index:sites[0]+1],[]]) < area_req*len(sites_right):
				break

		higher_area = polygon_area([boundary[front_index-1:sites[0]+1],[]])
		lower_area = polygon_area([boundary[front_index:sites[0]+1],[]])
		req_area = area_req*len(sites_right)


		eq_dist = (req_area-lower_area)/(higher_area-lower_area)

		edge = LineString(boundary[front_index:front_index-2:-1])
		cut_s = edge.interpolate(eq_dist, normalized=True)

		pt = (cut_s.x, cut_s.y)

		P_r = [[pt]+boundary[front_index:sites[0]+1],[]]
		P_l = [boundary[:front_index]+[pt]+boundary[sites[0]:],[]]


	elif index == sites[-1] and area_right < area_req*len(sites_right):
		print "Hits the second case"

		for front_index in range(len(boundary)-1,sites[-1],-1):
			modified_poly = [boundary[front_index:]+boundary[:sites[-1]+1],[]]
			if polygon_area(modified_poly) > area_req*len(sites_right):
				break

		lower_area = polygon_area([boundary[front_index+1:]+boundary[:sites[-1]+1],[]])
		higher_area = polygon_area(modified_poly)
		req_area = area_req*len(sites_right)

		eq_dist = (req_area-lower_area)/(higher_area-lower_area)
		edge = LineString(boundary[front_index+1:front_index-1:-1])
		cut_s = edge.interpolate(eq_dist, normalized=True)
		pt = (cut_s.x, cut_s.y)

		P_r = [[pt]+boundary[front_index+1:]+boundary[:sites[-1]+1],[]]
		P_l = [[pt]+boundary[sites[-1]:front_index+1],[]]


	else:
		print "Hits the third case correctly"

		higher_area = polygon_area([boundary[:index+1],[]])
		lower_area = polygon_area([boundary[:index],[]])
		req_area = area_req*len(sites_right)

		eq_dist = (req_area-lower_area)/(higher_area-lower_area)
		edge = LineString(boundary[index-1:index+1])
		cut_s = edge.interpolate(eq_dist, normalized=True)

		pt = (cut_s.x, cut_s.y)
		P_r = [boundary[:index]+[pt],[]]
		P_l = [[boundary[0]]+[pt]+boundary[index+1:],[]]


	#print site_indecies
	#print sites
	#print sites_right
	return_right_sites = []
	for site in sites_right:

		ret_idx = site_indecies[site].pop()
		sites.remove(site)
		return_right_sites.append(init_poss[ret_idx])

	return_left_sites = []
	for site in sites:
		ret_idx = site_indecies[site].pop()
		return_left_sites.append(init_poss[ret_idx])

	return ({"polygon" : P_r,
			"sites"   : return_right_sites},
			{"polygon" : P_l,
			"sites"   : return_left_sites})



#P = [[(0,0),(1,0),(1,1),(0,1)],[]]
P = [[(1,0),(2,0),(3,1),(3,2),(2,3),(1,3),(0,2),(0,1)],[]]
#q = [(1,0),(1,0),(1,0)]
#q = [(2,0),(2,0),(2,0)]
q = [(0,1),(0,1),(0,1)]
#q = [(2,0),(1,0),(3,1)]
#q = [(1,-4)]
#q = [(0,-2),(10,-3),(10,4)]
#q = [(0,-2),(0,-3),(10,4)]
#q = [(2,0),(2,0),(2,0),(7,7)]

r,l = convex_divide(polygon=P, init_poss=q, area_req=7.0/3.0)

print r
print l

print polygon_area(r["polygon"])
print polygon_area(l["polygon"])
print polygon_area(r["polygon"])+polygon_area(l["polygon"])