from shapely.geometry import LinearRing


def combine_two_adjacent_polys(p1, p2, e):
	"""
	Assuming they are adjacent
	"""

	v = e[0]; w = e[1]

	# Make sure the last and first verticies are not same
	if p1[0] == p1[-1]: p1 = p1[:-1]
	if p2[0] == p2[-1]: p2 = p2[:-1]

	p1_v_idx = p1.index(v)
	p2_v_idx = p2.index(v)

	p1_w_idx = p1.index(w)
	p2_w_idx = p2.index(w)

#	print("p1_v_i:%d p1_w_i:%d"%(p1_v_idx, p1_w_idx))
#	print("p2_v_i:%d p2_w_i:%d"%(p2_v_idx, p2_w_idx))

	if (p1_v_idx == 0) and (p1_w_idx == 1): left_chain = p1[1:]+[p1[0]]
	elif (p1_v_idx == 0) and (p1_w_idx == len(p1)-1): left_chain = p1[:]
	elif (p1_w_idx == 0) and (p1_v_idx == 1): left_chain = p1[1:]+[p1[0]]
	elif (p1_w_idx == 0) and (p1_v_idx == len(p1)-1): left_chain = p1[:]
	elif p1_v_idx < p1_w_idx: left_chain = p1[p1_w_idx:]+p1[:p1_v_idx+1]
	elif p1_w_idx < p1_v_idx: left_chain = p1[p1_v_idx:]+p1[:p1_w_idx+1]

	if (p2_v_idx == 0) and (p2_w_idx == 1): right_chain = p2[2:]
	elif (p2_v_idx == 0) and (p2_w_idx == len(p2)-1): right_chain = p2[1:]
	elif (p2_w_idx == 0) and (p2_v_idx == 1): right_chain = p2[2:]
	elif (p2_w_idx == 0) and (p2_v_idx == len(p2)-1): right_chain = p2[1:]	
	elif p2_v_idx < p2_w_idx: right_chain = p2[p2_w_idx+1:]+p2[:p2_v_idx]
	elif p2_w_idx < p2_v_idx: right_chain = p2[p2_v_idx+1:]+p2[:p2_w_idx]

#	print left_chain
#	print right_chain
	lr_left = LinearRing(left_chain); lr_right = LinearRing(right_chain)

	if lr_left.is_ccw:
		if lr_right.is_ccw: fuse = left_chain+right_chain
		else: 				fuse = left_chain+right_chain[::-1]
	else:
		if lr_right.is_ccw: fuse = left_chain+right_chain[::-1]
		else: 				fuse = left_chain+right_chain

	return fuse


#p1 = [
#		(2, 2),
#		(1, 3),
#		(0, 3),
#		(0, 0),
#		(1, 0),
#		(2, 1),
#		(2, 2),
#		]
#
#p2 = [
#		(3, 3),
#		(4, 3),
#		(4, 0),
#		(3, 0),
#		(2, 1),
#		(2, 2),
#		(3, 3),
#	]
#
#e = [(2, 1), (2, 2)]
#print combine_two_adjacent_polys(p1, p2 ,e)


def find_cut_edge(p1, p2, v):
	"""
	Find a shared edge between two polygons
	"""

	idx_1 = p1.index(v)
	idx_2 = p2.index(v)

	p1_edge_1 = [p1[idx_1], p1[(idx_1+1)%len(p1)]]
	p1_edge_2 = [p1[idx_1], p1[(idx_1-1)%len(p1)]]

	p2_edge_1 = [p2[idx_2], p2[(idx_2+1)%len(p2)]]
	p2_edge_2 = [p2[idx_2], p2[(idx_2-1)%len(p2)]]

	if p1_edge_1 == p2_edge_1: return p1_edge_1
	elif p1_edge_1 == p2_edge_2: return p1_edge_1
	elif p1_edge_2 == p2_edge_1: return p1_edge_2
	elif p1_edge_2 == p2_edge_2: return p1_edge_2

	print "SOMETHING WENT WORNG AND SHARED EDGE WAS NOT FOUND"


def find_common_polys(D, v):

	found_polys = []
	for poly in D:
		if v in poly:
			found_polys.append(poly)

	if len(found_polys) > 2:
		"SOMETHING WRONG, MORE THAN ONE COMMON POLYS"

	return found_polys[0], found_polys[1]