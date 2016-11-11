#!/usr/bin/env python
from statsmodels.tools.eval_measures import rmse
import numpy as np
import argparse
import os

from respy.python.simulate.simulate_auxiliary import format_float
from respy.python.process.process_python import process
from respy import RespyCls, simulate


def dist_input_arguments(parser):
    """ Check input for estimation script.
    """
    # Parse arguments
    args = parser.parse_args()

    # Distribute arguments
    init_file = args.init_file

    # Check attributes
    assert (os.path.exists(init_file))

    # Finishing
    return init_file


def _prepare_wages(data_obs, data_sim, which):
    """ Prepare the results from the wages for the print out.
    """
    if which == 'Occupation A':
        choice_ind = 1
    else:
        choice_ind = 2

    rslt = dict()
    for label in ['Observed', 'Simulated']:
        rslt[label] = []
        if label == 'Observed':
            data = data_obs
        else:
            data = data_sim
        for period in range(len(data_obs['Period'].unique())):
            is_occupation = data['Choice'] == choice_ind
            series = data['Wage'].ix[is_occupation][:, period]
            rslt[label] += [list(series.describe().values)]

    return rslt


def _prepare_choices(data_obs, data_sim):
    """ This function prepares the information about the choice probabilities
    for easy printing.
    """
    rslt_full = dict()
    rslt_shares = dict()

    for label in ['Observed', 'Simulated']:

        rslt_full[label] = []
        rslt_shares[label] = []

        if label == 'Observed':
            data = data_obs
        else:
            data = data_sim

        for period in range(len(data_obs['Period'].unique())):
            shares = []
            total = data['Choice'].loc[:, period].count()
            for choice in [1, 2, 3, 4]:
                count = np.sum(data['Choice'].loc[:, period] == choice)
                shares += [count / float(total)]
            rslt_full[label] += [[total] + shares]
            rslt_shares[label] += shares

    # We also prepare the overall RMSE.
    rmse_choice = rmse(rslt_shares['Observed'], rslt_shares['Simulated'])

    return rslt_full, rmse_choice


def scripts_compare(init_file):
    """ Construct some model fit statistics by comparing the observed and
    simulated dataset.
    """
    # Read in baseline model specification.
    respy_obj = RespyCls(init_file)

    # First we need to read in the empirical data
    data_sim = simulate(respy_obj)[1]
    data_obs = process(respy_obj)

    # Distribute class attributes
    max_obs = len(data_obs['Period'].unique())

    # Prepare results
    rslt_choice, rmse_choice = _prepare_choices(data_obs, data_sim)
    rslt_A = _prepare_wages(data_obs, data_sim, 'Occupation A')
    rslt_B = _prepare_wages(data_obs, data_sim, 'Occupation B')

    with open('compare.respy.info', 'w') as file_:

        file_.write('\n Comparing the Observed and Simulated Economy\n\n')

        # Comparing the choice distributions
        file_.write('\n   Choices \n\n')
        fmt_ = '{:>15}' * 7 + '\n'
        labels = ['Data', 'Period', 'Count', 'White', 'Blue', 'School', 'Home']
        file_.write(fmt_.format(*labels) + '\n')
        for period in range(max_obs):
            for name in ['Observed', 'Simulated']:
                line = [name, period] + rslt_choice[name][period]
                fmt_ = '{:>15}' * 3 + '{:15.2f}' * 4 + '\n'
                file_.write(fmt_.format(*line))
            file_.write('\n')
        line = '   Overall RMSE {:14.5f}\n'.format(rmse_choice)
        file_.write(line)

        # Comparing the wages distributions
        file_.write('\n\n   Outcomes \n\n')
        fmt_ = '{:>15}' * 8 + '\n'

        labels = []
        labels += ['Data', 'Period', 'Count', 'Mean', 'Std.']
        labels += ['25%', '50%', '75%']

        file_.write(fmt_.format(*labels) + '\n')
        for rslt, name in [(rslt_A, 'Occupation A'), (rslt_B, 'Occupation B')]:
            file_.write('\n    ' + name + ' \n\n')
            for period in range(max_obs):
                for label in ['Observed', 'Simulated']:
                    counts = int(rslt[label][period][0])
                    line = [label, period, counts]
                    # The occurance of NAN requires special care.
                    stats = rslt[label][period][1:]
                    stats = [format_float(x) for x in stats]
                    file_.write(fmt_.format(*line + stats))
                file_.write('\n')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=
        'Compare observed and simulated economy.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--init_file', action='store', dest='init_file',
        default='model.respy.ini', help='initialization file')

    init_file = dist_input_arguments(parser)

    scripts_compare(init_file)