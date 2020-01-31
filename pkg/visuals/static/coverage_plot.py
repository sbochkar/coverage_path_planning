from dubins import shortest_path 
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from descartes import PolygonPatch


def init_axis():
    """
    Initializes plotting area
    :param None:
    :return: Axes object
    """

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.axis("equal")

    ax.get_yaxis().set_ticks([])
    ax.get_xaxis().set_ticks([])

    return ax


def plot_polygon_outline(ax, polygon):
    """
    Function will plot the ouline of cleaning area. No decomposition.
    Adjust the axis as well.
    :param ax: Axis object for redundancy
    :param polygon: Possibly with holes
    :return: None
    """

    P = Polygon(*polygon)
    min_x, min_y, max_x, max_y = P.bounds

    patch = PolygonPatch(P, fc='white', ec='#6699cc', linewidth=3) # facecolor="#6699cc", edgecolor="#6699cc", alpha=0.5, zorder=1)
    ax.add_patch(patch)
    #x, y= P.xy
    #ax.plot(x,y)
    ax.set_xlim([min_x-0.5,max_x+0.5])
    ax.set_ylim([min_y-0.5,max_y+0.5])


def plot_decomposition(ax, decomposition, shared_edges, P):
    """
    Function plots the result of the decomposition.
    :param ax: Axis object for redundancy
    :param shared_edges: Shared edges between cells
    :param cvx_set:A list of convex cells:
    :retur: None
    """

    P = Polygon(*P)
    minx, miny, maxx, maxy = P.bounds

    # Plot individual cells
    for poly in decomposition:

        poly_shp = Polygon(*poly)
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

    ax.set_xlim([minx-0.5,maxx+0.5])
    ax.set_ylim([miny-0.5,maxy+0.5])

def plot_samples(ax, segments):
    """
    Function will plot the samples inside the cvx sets
    :param ax: Axis object
    :param lines: List of lines for each convex set
    :return: None
    """

    from ...discritizers import classes

    for segment in segments:
        if isinstance(segment, classes.PointSegment):
            x, y = segment.coord
            ax.scatter(x, y, color='orange', alpha=0.9, linewidth=3, zorder=3)	
        elif isinstance(segment, classes.LineSegment):
            x, y = zip(*segment.coords)
            ax.plot(x, y, color='orange', alpha=0.9, linewidth=3, zorder=3)	


def plot_grid(ax, grid):
    """
    Function will plot the samples inside the cvx sets
    :param ax: Axis object
    :param lines: List of lines for each convex set
    :return: None
    """
    ax.scatter(zip(*grid)[0], zip(*grid)[1])


def plot_grid_tour(ax, grid, tour, next_mtx):

    def return_path(u, v, next_mtr):
        """
        This function will return a path between a pair
        of verticies
        :param u: 1st vertex
        :param v: 2nd vertex
        :param next_mtr: path tree
        """
        if next_mtr[u][v] is None:
                return []

        path = [u]

        while u != v:
                u = next_mtr[u][v]
                path.append(u)

        return path 

    NUM_NODES_IN_CLUSTER = 8
    path = []

    path.append(grid[tour[0]])
    for i in range(1, len(tour)):
        ver_out = tour[i-1]
        ver_in = tour[i]

        destination_path = return_path(ver_out, ver_in, next_mtx)

        if (len(destination_path)>2):
            for i in range(1, len(destination_path)):
                node_out = destination_path[i-1]/NUM_NODES_IN_CLUSTER
                node_in = destination_path[i]/NUM_NODES_IN_CLUSTER

                path.append(grid[node_in])

                x = zip(*[grid[node_out], grid[node_in]])[0]
                y = zip(*[grid[node_out], grid[node_in]])[1]
                ax.plot(x, y, color='red', linewidth=2)
                
        else:
            node_out = ver_out/NUM_NODES_IN_CLUSTER
            node_in = ver_in/NUM_NODES_IN_CLUSTER
            path.append(grid[node_in])

            x = zip(*[grid[node_out], grid[node_in]])[0]
            y = zip(*[grid[node_out], grid[node_in]])[1]
            ax.plot(x, y, color='black', linewidth=1)


def plot_tour(ax, tour, lines, dict_map):
    """
    Function will plot the GTSP tour.
    :param ax:
    :param tour: tour
    :param lines:
    :param dict_map: 
    """

    for i in range(len(tour)-1):
        o_node = tour[i]
        i_node = tour[i+1]

        o_poly_idx, o_line_idx, o_dirr_idx = dict_map[o_node]
        i_poly_idx, i_line_idx, i_dirr_idx = dict_map[i_node]

        o_pt = lines[o_poly_idx][o_line_idx][o_dirr_idx]
        i_pt = lines[i_poly_idx][i_line_idx][(1+i_dirr_idx)%2]

        dx = i_pt[0] - o_pt[0]
        dy = i_pt[1] - o_pt[1]

        ax.arrow(o_pt[0], o_pt[1], dx, dy, head_width=0.1, ec='green', length_includes_head=True, zorder=4)


def plot_tour_dubins(ax, tour, dict_map, r):
    """
    Function will plot the GTSP tour.
    :param ax:
    :param tour: tour
    :param lines:
    :param dict_map: 
    """

    import math

    n = len(tour)
    for i in range(len(tour)):
        outgoing_node_idx = tour[i]
        incoming_node_idx = tour[(i+1)%n]

        outgoing_segment, dir_o = dict_map[outgoing_node_idx]
        incoming_segment, dir_i = dict_map[incoming_node_idx]

        q0 = outgoing_segment.get_exit_info(dir_o)
        q1 = incoming_segment.get_entrance_info(dir_i)
        #smpls, _ = dubins.path_sample(q0, q1, r, 0.05)
        smpls, _ = shortest_path(q0, q1, r).sample_many(0.1)

        x = []
        y = []
        xarrow = 0
        yarrow = 0
        for smpl in smpls:
            xt, yt, at = smpl
            x.append(xt)
            y.append(yt)

            if len(x) == int(math.floor(len(smpls)/2)):
                # Insert arrow mid way through dubins curve
                xarrow = x[int(math.floor(len(smpls)/2))-2]
                yarrow = y[int(math.floor(len(smpls)/2))-2]

                dx = x[int(math.floor(len(smpls)/2))-1] - x[int(math.floor(len(smpls)/2))-2]
                dy = y[int(math.floor(len(smpls)/2))-1] - y[int(math.floor(len(smpls)/2))-2]


        ax.scatter(x, y, s=0.4, color='green', zorder=4)
        #dx = i_pt[0] - o_pt[0]
        #dy = i_pt[1] - o_pt[1]

        ax.arrow(xarrow, yarrow, dx, dy, head_width=0.15, ec='green', length_includes_head=True, zorder=4)


def display():
    """
    Function display the figure
    :return: None
    """

    plt.show()

