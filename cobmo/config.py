"""Configuration parameters."""

import datetime
import logging
import os

# Path definitions.
cobmo_path = os.path.dirname(os.path.dirname(os.path.normpath(__file__)))
data_path = os.path.join(cobmo_path, 'data')
results_path = os.path.join(cobmo_path, 'results')

# Generate timestamp (for saving results with timestamp).
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Optimization solver settings.
solver_name = 'gurobi'  # Must be valid input string for Pyomo's `SolverFactory`.
solver_output = True  # If True, activate verbose solver output.

# Logger settings.
logging_level = logging.DEBUG
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(logging.Formatter('%(levelname)s | %(name)s | %(message)s'))
# logging_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s'))


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(logging_handler)
    logger.setLevel(logging_level)
    return logger