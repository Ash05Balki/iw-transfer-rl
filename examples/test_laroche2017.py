from trlib.policies.valuebased import EpsilonGreedy
from trlib.policies.qfunction import ZeroQ
from sklearn.ensemble.forest import ExtraTreesRegressor
from trlib.experiments.results import Result
from trlib.experiments.visualization import plot_average
from trlib.algorithms.callbacks import  get_callback_list_entry
import numpy as np
from trlib.experiments.experiment import RepeatExperiment
from trlib.environments.puddleworld import PuddleWorld
from trlib.utilities.interaction import generate_episodes
from trlib.policies.policy import Uniform
from trlib.algorithms.transfer.laroche2017 import Laroche2017

result_file = "puddleworld_laroche2017.json"

mdp = PuddleWorld(goal_x=5,goal_y=10, puddle_means=[(1.0,4.0),(1.0, 10.0), (1.0, 8.0), (6.0,6.0),(6.0,4.0)], puddle_var=[(.7, 1.e-5, 1.e-5, .7), (.8, 1.e-5, 1.e-5, .8), (.8, 1.e-5, 1.e-5, .8), (.8, 1.e-5, 1.e-5, .8),(.8, 1.e-5, 1.e-5, .8)])
actions = [0, 1, 2, 3]
pi = EpsilonGreedy(actions, ZeroQ(), 0.3)

regressor_params = {'n_estimators': 50,
                    'criterion': 'mse',
                    'min_samples_split':20,
                    'min_samples_leaf': 2}

source_data = [generate_episodes(mdp, Uniform(actions), 40) for _ in range(3)]

algorithm = Laroche2017(mdp, pi, verbose = True, actions = actions, batch_size = 10, max_iterations = 60, regressor_type = ExtraTreesRegressor, source_datasets=source_data, **regressor_params)

fit_params = {}

callback_list = []
callback_list.append(get_callback_list_entry("eval_policy_callback", field_name = "perf_disc", criterion = 'discounted', initial_states = [np.array([0., 0.]) for _ in range(5)]))
callback_list.append(get_callback_list_entry("eval_greedy_policy_callback", field_name = "perf_disc_greedy", criterion = 'discounted', initial_states = [np.array([0., 0.]) for _ in range(5)]))

experiment = RepeatExperiment("FQI Experiment", algorithm, n_steps = 10, n_runs = 8, callback_list = callback_list, **fit_params)
result = experiment.run(4)
result.save_json(result_file)

result = Result.load_json(result_file)
plot_average([result], "n_episodes", "perf_disc_mean", names = ["FQI"], file_name = "plot")
plot_average([result], "n_episodes", "perf_disc_greedy_mean", names = ["FQI"], file_name = "plot2")

plot_average([Result.load_json("puddleworld_fqi.json"), Result.load_json("puddleworld_laroche2017.json")], "n_episodes", "perf_disc_greedy_mean", names = ["FQI", "Laroche2017"], file_name = "plot3")