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

    return interface(args.bids_input,  args.output, args.subject_list,
                     args.collect, args.ncpus, args.stage)


def generate_parser(parser=None):
    """
    Generates the command line parser for this program.
    :param parser: optional subparser for wrapping this program as a submodule.
    :return: ArgumentParser for this script/module
    """
    if not parser:
        parser = argparse.ArgumentParser(
            prog='run.py',
            description="""The Developmental Cognition and Neuroimaging (DCAN) 
            lab fMRI Pipeline.  This BIDS application initiates a functional 
            MRI processing pipeline built upon the Human Connectome Project's 
            own minimal processing pipelines.  The application requires only a 
            dataset conformed to the BIDS specification, and little-to-no 
            additional configuration on the part of the user. BIDS format and 
            applications are explained in more detail at 
            http://bids.neuroimaging.io/
            """
        )
    parser.add_argument(
        'bids_input',
        help='path to the input bids dataset root directory.  Read more '
             'about bids format in the link above.  It is recommended to use '
             'dcm2bids to convert from participant dicoms.'
    )
    parser.add_argument(
        'output',
        help='path to the output directory for all intermediate and output '
             'files from the pipeline.'
    )
    parser.add_argument(
        '--participant-label', dest='subject_list', metavar='ID', nargs='+',
        help='optional list of participant ids to run. Default is all ids '
             'found under the bids input directory.'
    )
    parser.add_argument(
        '--all-sessions', dest='collect', action='store_true',
        help='collapses all sessions into one when running a subject.'
    )
    parser.add_argument(
        '--ncpus', type=int, default=1,
        help='number of cores to use for concurrent processing of functional '
             'runs.'
    )
    parser.add_argument(
        '--stage',
        help='begin from a given stage.  Options: PreFreeSurfer, FreeSurfer, '
             'PostFreeSurfer, FMRIVolume, FMRISurface, '
             'DCANSignalPreprocessing, ExecutiveSummary')

    return parser


def interface(bids_input, output, subject_list=None, collect=False, ncpus=1,
              start_stage=None):
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
        outdir = os.path.join(output, 'sub-%s' % session['subject'],
                              'ses-%s' % session['session'])
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
        if start_stage:
            names = [x.__class__.__name__ for x in order]
            assert start_stage in names
            order = order[names.index(start_stage):]

        # run pipelines
        for stage in order:
            print('running ' + stage.__class__.__name__)
            print(stage)
            stage.run(ncpus)


if __name__ == '__main__':
    _cli()
