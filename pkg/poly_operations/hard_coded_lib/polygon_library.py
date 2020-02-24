

def polygon_generator(map_num):
    """Hard coded polygons

    Args:
        map_num (int): Poly ID
    Returns:
        P: Polygon in standard form
    """
    if map_num == 0:
        ext = [(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (0.0, 2.0)]
        holes = [[(0.6, 0.6), (0.6, 1.4), (1.4, 1.4), (1.4, 0.6)],
                 [(2.5, 0.6), (2.5, 1.4), (3.5, 1.4), (3.5, 0.6)]]


    if map_num == 1:
        ext = [(0.0, 0.0), (4.0, 0.0), (5.0, 1.0), (6.0, 0.0), (10.0, 0.0), (10.0, 5.0), (6.0, 5.0), (5.0, 4.0), (4.0, 5.0), (0.0, 5.0)]
        holes = []

    elif map_num == 2:
            ext = [(0.0, 0.0), (4.0, 0.0), (5.0, 1.0), (6.0, 0.0), (10.0, 0.0), (10.0, 10.0), (6.0, 10.0), (4.0, 7.0), (5.0, 10.0), (0.0, 10.0)]
            holes = []

    elif map_num == 3:
            ext = [(1.0, 0), (9.0, 0.0), (9.0, 1.0), (10.0, 1.0), (10.0, 9.0), (9.0, 9.0), (9.0, 10.0), (1.0, 10.0), (1.0, 9.0), (0.0, 9.0), (0.0, 1.0), (1.0, 1.0)]
            holes = []

    elif map_num == 4:
            ext = [(0.0, 0.0), (1.0, 0.0), (1.0, 8.0), (9.0, 0.0), (10.0, 0.0), (10.0, 10.0), (9.0, 10.0), (9.0, 2.0), (1.0, 10.0), (0.0, 10.0)]
            holes = []

    elif map_num == 5:
            ext = [(0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (7.5, 10.0), (5.0, 5.0), (2.5, 10.0), (0.0, 5.0)]
            holes = []

    elif map_num == 6:
            ext = [(0.0, 0.0), (15.0, 0), (15.0, 4.0), (14.0, 5.0), (15.0, 6.0), (15.0, 10.0), (10.0, 10.0), (10.0, 5.0), (7.5, 10.0), (5.0, 6.0), (2.5, 10.0), (0.0, 2.0)]
            holes = []

    elif map_num == 7:
        ext = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
        holes = [[(1.0, 1.0), (1.0, 9.0), (9.0, 9.0), (9.0, 1.0)]]

    elif map_num == 8:
        ext = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]

        holes = [[(1.0, 1.0), (1.0, 4.0), (2.0, 4.0), (2.0, 3.0), (8.0, 3.0), (8.0, 8.0), (2.0, 8.0), (2.0, 7.0), (1.0, 7.0), (1.0, 9.0), (9.0, 9.0), (9.0, 1.0)],
                 [(3.0, 4.0), (3.0, 7.0), (7.0, 7.0), (7.0, 4.0)]]

    elif map_num == 9:
        ext = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
        holes = [[(1.0, 1.0), (1.0, 9.0), (4.0, 9.0), (4.0, 1.0)],
                 [(6.0, 1.0), (6.0, 9.0), (9.0, 9.0), (9.0, 1.0)]]

    elif map_num == 10:	# No holes one
            ext = [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (6.0, 4.0), (6.0, 0.0), (10.0, 0.0), (10.0, 6.0), (8.0, 7.0), (7.5, 8.0), (10.0, 7.5), (10.0, 10.0), (0.0, 10.0), (0.0, 5.0), (5.0, 6.0), (5.0, 5.0), (0.0, 4.0)]
            holes = []
                            
    elif map_num == 11:
            ext = [(0.0, 0.0), (6.0, 0.0), (6.0, 5.0), (4.0, 5.0), (4.0, 3.0), (5.0, 3.0), (5.0, 2.0), (3.0, 2.0), (3.0, 6.0), (7.0, 6.0), (7.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
            holes = [[(4.0, 7.0), (3.5, 8.0), (4.5, 9.0), (6.0, 8.0)]]

    elif map_num == 12:
            ext = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
            holes = [[(7.0, 1.0), (7.0, 3.0), (8.0, 3.0), (8.0, 1.0)],
                     [(2.0, 3.0), (1.0, 4.0), (1.5, 4.5), (3.0, 5.0), (3.5, 4.5), (3.0, 3.0)],
                     [(8.0, 5.0), (4.0, 7.0), (6.0, 9.0), (7.0, 8.0), (6.0, 7.0), (8.0, 6.0), (8.5, 6.5), (9.0, 6.0)]]

    elif map_num == 13:
            ext = [(0.0, 0.0), (4.0, 0.0), (4.0, 5.0), (2.0, 5.0), (2.0, 6.0), (5.0, 6.0), (5.0, 0.0), (10.0, 0.0), (10.0, 4.0), (7.0, 4.0), (7.0, 5.0), (10.0, 5.0), (10.0, 10.0), (0.0, 10.0)]
            holes = [[(3.0, 7.0), (2.0, 8.0), (3.0, 9.0), (6.0, 8.0)],
                     [(7.0, 7.0), (7.0, 9.0), (8.0, 9.0), (8.0, 7.0)]]

    elif map_num == 14:
        ext = [(0.0, 0.0), (4.0, 0.0), (4.0, 5.0), (3.0, 5.0), (3.0, 6.0), (5.0, 6.0), (5.0, 0.0), (10.0, 0.0), (10.0, 4.0), (8.0, 4.0), (8.0, 5.0), (10.0, 5.0), (10.0, 10.0), (0.0, 10.0)]
        holes = [[(2.0, 6.0), (2.0, 7.0), (3.0, 7.0), (3.0, 6.0)],
                 [(8.0, 5.0), (8.0, 6.0), (9.0, 6.0), (9.0, 5.0)]]

    elif map_num == 20:
        ext = [(0.0, 0.0), (10.0, 0.0), (17.0, 3.0), (17.0, 10.0), (5.0, 10.0), (0.0, 7.0)]
        holes = [[(1.0, 1.0), (1.0, 3.0), (2.0, 3.0), (2.0, 1.0)],
                 [(3.0, 1.0), (3.0, 3.0), (4.0, 3.0), (4.0, 1.0)]]
#
#					[(5.0, 1.0),
#					(5.0, 5.0),
#					(6.0, 5.0),
#					(6.0, 1.0)],
#
#					[(7.0, 1.0),
#					(7.0, 5.0),
#					(8.0, 5.0),
#					(8.0, 1.0)],
#
#					[(9.0, 1.0),
#					(9.0, 5.0),
#					(10.0, 5.0),
#					(10.0, 1.0)],
#
#					[(11.0, 2.0),
#					(11.0, 5.0),
#					(12.0, 5.0),
#					(12.0, 2.0)],
#					
#					[(13.0, 3.0),
#					(13.0, 5.0),
#					(14.0, 5.0),
#					(14.0, 3.0)],
#					
#					[(15.0, 3.0),
#					(15.0, 4.0),
#					(16.0, 4.0),
#					(16.0, 3.0)],
#
#					[(15.0, 5.0),
#					(15.0, 6.0),
#					(16.0, 6.0),
#					(16.0, 5.0)],
#
#					[(2.0, 6.0),
#					(1.0, 7.0),
#					(4.0, 8.0),
#					(5.0, 7.0)],
#
#					[(7.0, 6.0),
#					(7.0, 8.0),
#					(8.0, 8.0),
#					(8.0, 7.0),
#					(9.0, 7.0),
#					(9.0, 6.0)],
#
#
#					[(10.0, 6.0),
#					(10.0, 7.0),
#					(11.0, 7.0),
#					(11.0, 8.0),
#					(12.0, 8.0),
#					(12.0, 6.0)]
    elif map_num == 21:
        ext = [(0, 0), (20, 0), (20, 2), (2, 2), (2, 20), (0, 20)]
        holes = []
    return [ext, holes]
