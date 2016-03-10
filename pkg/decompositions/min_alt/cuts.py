def find_optimal_cut(P, v):
	"""
	Find optimal cut
	"""


	dirs_left = []
	dirs_right = []
	pois = []

	a, theta = get_min_altitude(P)
	#print a, theta

	s = find_cut_space(P, v)
	#print s
	min_altitude = a
	min_altitude_idx = None

	for si in s:
		# Process each edge si, have to be cw
		lr_si = LinearRing([v]+si)
		if lr_si.is_ccw:
			#print lr_si
			#print lr_si.is_ccw
			si = [si[1]]+[si[0]]
			#print si

		cut_point = si[0]
		#print P, v, cut_point
		p_l, p_r = perform_cut(P, [v, cut_point])
		#print p_l, p_r

		dirs_left = get_directions([p_l, []])
		dirs_right = get_directions([p_r, []])
		#print dirs_left
		#print list(degrees(dir) for dir in dirs_left)
		#print get_altitude([p_l,[]], 3.5598169831690223)
		#print get_altitude([p_r,[]], 0)

		# Look for all transition points
		for dir1 in dirs_left:
			for dir2 in dirs_right:
				tp = find_best_transition_point(si, v, dir1, dir2)
				pois.append((tp, dir1, dir2))

	# Evaluate all transition points
	for case in pois:
		p_l, p_r = perform_cut(P, [v, case[0]])
		a_l = get_altitude([p_l, []], case[1])
		a_r = get_altitude([p_r, []], case[2])
		if a_l+a_r<=min_altitude:
			min_altitude = a_l+a_r
			min_altitude_idx = case
		

	#print min_altitude, min_altitude_idx[0], degrees(min_altitude_idx[1]), degrees(min_altitude_idx[2])
	return min_altitude_idx