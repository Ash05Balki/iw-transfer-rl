from trlib.environments.dam import Dam
from trlib.policies.valuebased import EpsilonGreedy
from trlib.policies.qfunction import ZeroQ
from sklearn.ensemble.forest import ExtraTreesRegressor
from trlib.algorithms.callbacks import get_callback_list_entry
import numpy as np
from trlib.experiments.experiment import RepeatExperiment
from trlib.utilities.data import load_object
from trlib.algorithms.transfer.wfqi import WFQI, estimate_weights_mean
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from trlib.environments.puddleworld import PuddleWorld
from trlib.utilities.wfqi_utils import estimate_ideal_weights
from trlib.policies.policy import Uniform
from trlib.environments.acrobot_hybrid import AcrobotHybrid

""" --- ENVIRONMENTS --- """
target_mdp = AcrobotHybrid(m1 = 1.0, m2 = 1.0, l1 = 1.0, l2 = 1.0)
source_mdp_1 = AcrobotHybrid(l1 = 0.8, l2 = 0.6, m1 = 0.9, m2 = 1.)
source_mdp_2 = AcrobotHybrid(l1 = 0.95, l2 = 0.95, m1 = 0.95, m2 = 1.)
source_mdp_3 = AcrobotHybrid(l1 = 0.85, l2 = 0.85, m1 = 0.9, m2 = 0.9)
source_mdps = [source_mdp_1,source_mdp_2,source_mdp_3]

actions = [0, 1]
source_data = [load_object("source_data_" + str(i)) for i in [1,2,3]]

""" --- PARAMS --- """

regressor_params = {'n_estimators': 50,
                    'criterion': 'mse',
                    'min_samples_split':5,
                    'min_samples_leaf': 2}

initial_states = [np.array([-2.0,0.,0.,0.]),np.array([-1.5,0.,0.,0.]),np.array([-1.0,0.,0.,0.]),
                  np.array([-0.5,0.,0.,0.]),np.array([0.0,0.,0.,0.]),np.array([0.5,0.,0.,0.]),
                  np.array([1.0,0.,0.,0.]),np.array([1.5,0.,0.,0.]),np.array([2.0,0.,0.,0.])]

callback_list = []
callback_list.append(get_callback_list_entry("eval_greedy_policy_callback", field_name = "perf_disc_greedy", criterion = 'discounted', initial_states = initial_states))

pre_callback_list = []

fit_params = {}

max_iterations = 50
batch_size = 20
n_steps = 10
n_runs = 20
n_jobs = 5

""" --- WEIGHTS --- """

var_rw = 0.1 ** 2
var_st = 0.1 ** 2
wr,ws = estimate_ideal_weights(target_mdp, source_mdps, [data[0] for data in source_data], var_rw, var_st)

""" --- WFQI --- """

pi = EpsilonGreedy(actions, ZeroQ(), 0.1)

algorithm = WFQI(target_mdp, pi, actions, batch_size = batch_size, max_iterations = max_iterations, regressor_type = ExtraTreesRegressor, source_datasets = source_data, var_rw = var_rw, var_st = var_st, max_gp = 4000,
                 weight_estimator = None, max_weight = 1000, kernel_rw = None, kernel_st = None, weight_rw = True, weight_st = [True, True],
                 subtract_noise_rw = False, subtract_noise_st = False, wr = wr, ws = ws, verbose = True, **regressor_params)

experiment = RepeatExperiment("WFQI-ideal", algorithm, n_steps = n_steps, n_runs = n_runs, callback_list = callback_list)
result = experiment.run(n_jobs)
result.save_json("wfqi-ideal.json")