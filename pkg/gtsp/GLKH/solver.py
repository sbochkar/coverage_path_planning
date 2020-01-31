import os
import subprocess


def solve(problem_name, solver_loc, cost_matrix, cluster_array):
    """
    This function will generate appropriate files for GTSP
    solver and start the solver.

    :param problem_name: The name of the problem, useful for problem_names
    :param solver_loc: path to the solver
    :param cost_matrix: Matrix with costs
    :param cluster_array: Information about clusters
    :return tour: Tour
    """

    # TODO: Move this preprocessing step somewhere else.
    for i, row in enumerate(cost_matrix):
        cost_matrix[i] = list(map(int, row))
    # TODO: Solidify the format so that there is no such ambiguity.
    for i, row in enumerate(cluster_array):
        cluster_array[i] = list(map(lambda x: x + 1, row))

    num_nodes = len(cost_matrix)
    num_clusters = len(cluster_array)

    settings_dict = {
        'PROBLEM_FILE': problem_name + '.gtsp',
        'OUTPUT_TOUR_FILE': problem_name + '.tour',
        'ASCENT_CANDIDATES': 500,
        'INITIAL_PERIOD': 1000,
        'MAX_CANDIDATES': 30,
        'MAX_TRIALS': 1000,
        'POPULATION_SIZE': 5,
        'PRECISION': 10,
        'SEED': 1,
        'TRACE_LEVEL': 1,
        'RUNS': 1,
    }

    # Write GTSP instance settings
    with open(problem_name + '.par', 'w') as f:
        for key, val in settings_dict.items():
            f.write("{} = {}\n".format(key, val))

    props_dict = {
        'NAME': problem_name,
        'COMMENT': problem_name + ': CPP using GTSP solver',
        'TYPE': 'AGTSP',
        'DIMENSION': num_nodes,
        'GTSP_SETS': num_clusters,
        'EDGE_WEIGHT_TYPE': 'EXPLICIT',
        'EDGE_WEIGHT_FORMAT': 'FULL_MATRIX'
    }

    # Write GTSP instance properties
    with open(problem_name + ".gtsp", "w") as f:
        for k, v in props_dict.items():
            f.write(k + ' = ' + str(v) + '\n')

        f.write("EDGE_WEIGHT_SECTION\n")
        # Converting to str and forming a row.
        for matrix_row in cost_matrix:
            row = " ".join(map(str, matrix_row))
            f.write(row + '\n')

        f.write("GTSP_SET_SECTION\n")
        for i, matrix_row in enumerate(cluster_array):
            row = " ".join(map(str, matrix_row))
            f.write("{} {} -1\n".format(i + 1, row))

        f.write("EOF\n")
        f.write("")

    # Move the files to GTSP solver location
    # os.system("cp "+problem_name+".gtsp "+'/pkg/gtsp/solver_logs/')
    # os.system("cp "+problem_name+".par "+'/pkg/gtsp/solver_logs/')
    #os.system("mv "+problem_name+".gtsp "+solver_loc)
    #os.system("mv "+problem_name+".par "+solver_loc+"TMP/")

    cmd = ["GLKH", problem_name + ".par"]
    subprocess.run(cmd, check=True)

    #os.system("mv "+problem_name+".gtsp "+cur_dir+"/pkg/gtsp/solver_logs")
    #os.system("mv "+"TMP/"+problem_name+".par "+cur_dir+"/pkg/gtsp/solver_logs")
    #os.system("mv "+problem_name+".tour "+cur_dir+'/pkg/gtsp/solver_logs')
    #os.chdir(cur_dir)


def read_tour(problem_name):

    # Read in the results from the TSP solver results
    with open('pkg/gtsp/solver_logs/'+problem_name+".tour", 'r') as f:
        for i in range(6):
            f.readline()

        tour = []
        str = f.readline()
        while "EOF" not in str and "-1" not in str:
            tour.append(int(str)-1)
            str = f.readline()

    return tour
