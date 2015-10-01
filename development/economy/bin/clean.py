#!/usr/bin/env python
""" This script solves and simulates the first RESTUD economy for a variety
of alternative degrees of ambiguity.
"""

# standard library
import argparse
import shutil
import glob
import os

# Check for Python 3
import sys
if not (sys.version_info[0] == 3):
    raise AssertionError('Please use Python 3')
    
''' Functions
'''


def cleanup():
    """ Clean directory.
    """

    files = glob.glob('*')

    for file_ in files:

        if file_ in ['graphs', 'acropolis.pbs', 'model.robupy.ini', 'bin', 'clean', 'create']:
            continue

        try:
            os.unlink(file_)
        except IsADirectoryError:
            shutil.rmtree(file_)

''' Execution of module as script.
'''
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Clean directory.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Run function
    cleanup()
