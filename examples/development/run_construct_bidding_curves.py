"""Run script for formulating bidding strategies."""

import numpy as np
import os
import pandas as pd
from matplotlib import pyplot as plt

import cobmo.building_model
import cobmo.config
import cobmo.optimization_problem
import cobmo.data_interface
import cobmo.utils


def main():

    # Settings.
    scenarios = pd.read_csv(os.path.join(cobmo.config.config['paths']['data'], 'scenarios.csv'))
    results_path = cobmo.utils.get_results_path(__file__)

    # Recreate / overwrite database, to incorporate changes in the CSV files.
    cobmo.data_interface.recreate_database()

    # Obtain building model.
    for scenario_name in scenarios['scenario_name'][:20]:
        print(scenario_name)
        building = cobmo.building_model.BuildingModel(str(scenario_name))

        # Obtain and solve baseline optimization problem.
        optimization_problem = cobmo.optimization_problem.OptimizationProblem(
            building
        )
        (
            control_vector_optimization,
            state_vector_optimization,
            output_vector_optimization,
            operation_cost,
            investment_cost,  # Zero when running (default) operation problem.
            storage_capacity  # Zero when running (default) operation problem.
        ) = optimization_problem.solve()

        timesteps = building.timesteps
        building_bids = pd.DataFrame(0.0, timesteps, ['P_min', 'P_max', 'C_min', 'C_max', 'm', 'b'])
        building_bids.loc[:, 'P_min'] = output_vector_optimization.loc[:, 'grid_electric_power'].values
        building_bids.loc[timesteps, 'C_min'] = building.electricity_price_timeseries.loc[timesteps, 'price'].values

        for timestep in timesteps:
            recourse_problem = cobmo.optimization_problem.OptimizationProblem(
                building,
                problem_type='load_maximization',
                load_maximization_time=timestep
            )
            (
                control_vector_recourse,
                state_vector_recourse,
                output_vector_recourse,
                recourse_operation_cost,
                recourse_investment_cost,  # Zero when running (default) operation problem.
                recourse_storage_capacity  # Zero when running (default) operation problem.
            ) = recourse_problem.solve()

            max_load_at_timestep = output_vector_recourse.at[timestep, 'grid_electric_power']
            energy_at_timestep = max_load_at_timestep*0.5/1000 # convert W to kWh
            delta_C_at_timestep = (recourse_operation_cost-operation_cost)/energy_at_timestep
            building_bids.at[timestep, 'P_max'] = max_load_at_timestep
            building_bids.at[timestep, 'C_max'] = building_bids.at[timestep, 'C_min'] - delta_C_at_timestep

        building_bids['m'] = (building_bids['C_min'] - building_bids['C_max'])/(building_bids['P_min'] - building_bids['P_max'])
        building_bids['b'] = building_bids['C_min'] - building_bids['P_min']*building_bids['m']

        # Store optimization results as CSV.
        # control_vector_optimization.to_csv(os.path.join(results_path, 'control_vector_optimization.csv'))
        # state_vector_optimization.to_csv(os.path.join(results_path, 'state_vector_optimization.csv'))
        # output_vector_optimization.to_csv(os.path.join(results_path, 'output_vector_optimization.csv'))
        building_bids.to_csv(os.path.join(results_path, 'building_bids_{}.csv'.format(scenario_name)))

    # Plot bidding curves
    # for timestep in timesteps:
    #     fig,ax = plt.subplots(figsize=(5,5))
    #     x = building_bids.loc[timestep, ['P_min', 'P_max']].values
    #     y = building_bids.loc[timestep, ['C_min', 'C_max']].values
    #     ax.plot(x,y)
    #     ax.axhline(0, color='black')
    #     plt.show()

    # Print results path.
    print(f"Results are stored in: {results_path}")


if __name__ == '__main__':
    main()
