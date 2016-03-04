import numpy as np

# Messaging and debugging tools
import time
import datetime
import sys

def current_time():
	"""
	This helper function return current time in human readnable format
	:return time: Time string in human readable format
	"""
	ts = time.time()
	return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def floydwarshall(graph, MAX):
    """
    This is a function for Floyd-Warshall algorithm.
    Assigning edge costs to any pair of verticies
    in a graph.
    :param graph: A 2D array specifiying an existance of an edge
    :return mtr_cost: Matrix with true costs
    :return tour: A list of shortest paths between every pair of verticies
    """

    num_verts = len(graph)

    dist = [[0 for x in range(num_verts)] for x in range(num_verts)]
    next_mtr = [[0 for x in range(num_verts)] for x in range(num_verts)]

    for i in range(num_verts):
        for j in range(num_verts):
            next_mtr[i][j] = None
            dist[i][j] = graph[i][j]

            # If edge exists
            if dist[i][j] > 0 and dist[i][j] < MAX:
                next_mtr[i][j] = j
            if i == j:
                dist[i][j] = 0
 
    print("[%18s]		 Starting the main body of F-W."%current_time())
    three_quarter_prog = 3*num_verts/4
    half_prog = num_verts/2

    for k in range(num_verts):
        # Output progress for really big problem sets
        print '\r 		%d iteration'%k,
        sys.stdout.flush()

        if k == half_prog:
                print("\n[%18s]		50%% done after %d iterations"%(current_time(),k))
        if k == three_quarter_prog:
                print("\n[%18s]		75%% done after %d iterations"%(current_time(), k))


        for i in range(num_verts):
            for j in range(num_verts):

                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_mtr[i][j] = next_mtr[i][k]
 
    # Return numpy array just in case
    print

    dist = np.copy(dist)
    next_mtr = np.copy(next_mtr)
    return dist, next_mtr

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

# Standard boileplate to call the main() function to begin the program
if __name__ == '__main__':

    import numpy as np
    graph = np.zeros((5,5))

    MAX = 100
    graph[1][0]=1; graph[0][1]=1
    graph[2][1]=1; graph[1][2]=1
    graph[3][2]=1; graph[2][3]=1
    graph[4][2]=1; graph[2][4]=1
  
    graph[0][2]=MAX; graph[0][3]=MAX; graph[0][4]=MAX
    graph[1][3]=MAX; graph[1][4]=MAX
    graph[2][0]=MAX
    graph[3][0]=MAX; graph[3][1]=MAX; graph[3][4]=MAX
    graph[4][0]=MAX; graph[4][1]=MAX; graph[4][3]=MAX

    cost, next = floydwarshall(graph, MAX)
 
    print return_path(2, 3, next)
    #print cost
