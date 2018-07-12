#!/usr/bin/env python3

import argparse
import os

from helpers import read_bids_dataset
from pipelines import (HCPConfiguration, PreFreeSurfer, FreeSurfer,
                       PostFreeSurfer, FMRIVolume, FMRISurface,
                       DCANSignalPreprocessing, ExecutiveSummary)


def _cli():
    """
    command line interface
    :return:
    """
    parser = generate_parser()
    args = parser.parse_args()

    return interface(args.bids_input,  args.output)


def generate_parser(parser=None):
    """
    Generates the command line parser for this program.
    :param parser: optional subparser for wrapping this program as a submodule.
    :return: ArgumentParser for this script/module
    """
    if not parser:
        parser = argparse.ArgumentParser(
            prog='run.py',
            description="""DCAN HCP BIDS App.  This BIDS application 
            initiates a functional MRI processing pipeline based on the Human 
            Connectome Project's minimal processing pipelines with 
            little-to-no configuration required by the user.  BIDS format and 
            applications are explained in more detail at 
            http://bids.neuroimaging.io/
            """)

    parser.add_argument(
        'bids_input',
        help='internal path to the input bids dataset.')
    parser.add_argument(
        'output',
        help='internal path to the output directory.')
    parser.add_argument(
        '--ncpus', type=int,
        help='number of cores to use for concurrent processing of functional '
             'runs.'
    )
    # add subject-list and collect-on-subject options to parser.

    return parser


def interface(bids_input, output, subject_list=None, collect=False):
    """
    main program interface
    :param bids_input: input bids dataset see "helpers.read_bids_dataset" for
    more information.
    :param output: output folder
    :param subject_list: subject and session list filtering.  See
    "helpers.read_bids_dataset" for more information.
    :param collect: treats each subject as having only one session.
    :return:
    """
    assert os.path.isdir(bids_input), bids_input + ' is not a directory!'
    if not os.path.isdir(output):
        os.makedirs(output)
    session_generator = read_bids_dataset(bids_input, subject_list=subject_list,
                                          collect_on_subject=collect)

    for session in session_generator:
        # setup session configuration
        outdir = os.path.join(output, session['subject'], session['session'])
        session_conf = HCPConfiguration(session, outdir)
        # create pipelines
        pre = PreFreeSurfer(session_conf)
        free = FreeSurfer(session_conf)
        post = PostFreeSurfer(session_conf)
        vol = FMRIVolume(session_conf)
        surf = FMRISurface(session_conf)
        fnlpp = DCANSignalPreprocessing(session_conf)
        execsum = ExecutiveSummary(session_conf)

        order = [pre, free, post, vol, surf, fnlpp, execsum]

        for stage in order:
            print('running ' + stage.__class__.__name__)
            print(stage)
            stage.run()


if __name__ == '__main__':
    _cli()
