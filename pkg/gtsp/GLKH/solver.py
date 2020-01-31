"""Module defining all interactions with the GTSP solver."""
from typing import List
import subprocess


class GTSPSolver():
    """Container class for GTSP solver. Current implementation uses GLKH."""
    SOLVER_CMD = "GLKH"

    __slots__ = (
        'problem_name',
        'cost_matrix',
        'clusters',
        'problem_params',
        'problem_defs',
    )

    def __init__(self, problem_name: str, cost_matrix: List[List[int]], clusters: List[List[int]]):
        """Constructor for the solver.

        Args:
            problem_name (str): Name this instance of the problem.
            cost_matrix (List): 2D List containing costs.
            clusters (List): 2D List containing cluster info.
        """
        self.problem_name = problem_name
        self.cost_matrix = [list(map(int, row)) for row in cost_matrix]
        self.clusters = [list(map(lambda x: x + 1, row)) for i, row in enumerate(clusters)]
        self.problem_params = {
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
        self.problem_defs = {
            'NAME': problem_name,
            'COMMENT': problem_name + ': CPP using GTSP solver',
            'TYPE': 'AGTSP',
            'DIMENSION': len(cost_matrix),
            'GTSP_SETS': len(clusters),
            'EDGE_WEIGHT_TYPE': 'EXPLICIT',
            'EDGE_WEIGHT_FORMAT': 'FULL_MATRIX'
        }

    def _gen_parameter_file(self):
        """Generate and write parameter file to disk."""
        with open(self.problem_name + '.par', 'w') as file_:
            for key, val in self.problem_params.items():
                file_.write("{} = {}\n".format(key, val))

    def _gen_problem_def_file(self):
        """Generate and write problem definition to disk."""
        # Write GTSP instance properties
        with open(self.problem_name + ".gtsp", "w") as file_:
            for key, val in self.problem_defs.items():
                file_.write(key + ' = ' + str(val) + '\n')

            file_.write("EDGE_WEIGHT_SECTION\n")
            # Converting to str and forming a row.
            for row in self.cost_matrix:
                file_row = " ".join(map(str, row))
                file_.write(file_row + '\n')

            file_.write("GTSP_SET_SECTION\n")
            for i, row in enumerate(self.clusters):
                file_row = " ".join(map(str, row))
                file_.write("{} {} -1\n".format(i + 1, file_row))

            file_.write("EOF\n")
            file_.write("")

    def read_tour_file(self) -> List[int]:
        """Read and return tour from the file generated by the solver.

        Returns:
            A list of verticies representing a tour.
        """
        # Read in the results from the TSP solver results
        with open(self.problem_name + ".tour", 'r') as file_:
            # Some kind of bookkeeping.
            for _ in range(6):
                file_.readline()

            tour: List[int] = []
            file_row = file_.readline()
            while "EOF" not in file_row and "-1" not in file_row:
                tour.append(int(file_row) - 1)
                file_row = file_.readline()
        return tour

    def launch_solver_and_get_tour(self) -> List[int]:
        """Launch external solver with preconfigured parameters.

        Returns:
            A list of verticies representing a tour.
        """
        self._gen_parameter_file()
        self._gen_problem_def_file()

        cmd = [self.SOLVER_CMD, self.problem_name + ".par"]
        subprocess.run(cmd, check=True)

        return self.read_tour_file()
