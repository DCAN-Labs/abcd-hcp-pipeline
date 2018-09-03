#! /usr/bin/env python3

import argparse
import os

from helpers import read_bids_dataset
from pipelines import (ParameterSettings, PreFreeSurfer, FreeSurfer,
                       PostFreeSurfer, FMRIVolume, FMRISurface,
                       DCANBOLDProcessing, ExecutiveSummary)


def _cli():
    """
    command line interface
    :return:
    """
    parser = generate_parser()
    args = parser.parse_args()

    return interface(args.bids_dir,  args.output_dir, args.subject_list,
                     args.collect, args.ncpus, args.stage, args.bandstop)


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
        'bids_dir',
        help='path to the input bids dataset root directory.  Read more '
             'about bids format in the link above.  It is recommended to use '
             'the dcan bids gui or dcm2bids to convert from participant '
             'dicoms.'
    )
    parser.add_argument(
        'output_dir',
        help='path to the output directory for all intermediate and output '
             'files from the pipeline, also path in which logs are stored.'
    )
    parser.add_argument(
        '--participant-label', dest='subject_list', metavar='ID', nargs='+',
        help='optional list of participant ids to run. Default is all ids '
             'found under the bids input directory.  A participant label '
             'does not include "sub-"'
    )
    parser.add_argument(
        '--all-sessions', dest='collect', action='store_true',
        help='collapses all sessions into one when running a subject.'
    )
    parser.add_argument(
        '--ncpus', type=int, default=1,
        help='number of cores to use for concurrent processing and '
             'algorithmic speedups.  Warning: causes ANTs and FreeSurfer to '
             'produce non-deterministic results.'
    )
    parser.add_argument(
        '--stage',
        help='begin from a given stage, continuing through.  Options: '
             'PreFreeSurfer, FreeSurfer, PostFreeSurfer, FMRIVolume, '
             'FMRISurface, DCANBOLDProcessing, ExecutiveSummary'
    )
    parser.add_argument(
        '--bandstop', type=float, nargs=2, metavar=('LOWER', 'UPPER'),
        help='parameters for motion regressor band-stop filter. It is '
             'recommended for the boundaries to match the inter-quartile range '
             'for participant group heart rate (bpm), or to match bids physio '
             'data directly.  These parameters are only recommended for data '
             'acquired with a frequency of approx. 1 Hz or more.  Default is '
             'no filter'
             # 'to use physio data from bids, or to use no filter if physio is '
             # 'not available.' @TODO implement physio
    )

    return parser


def interface(bids_dir, output_dir, subject_list=None, collect=False, ncpus=1,
              start_stage=None, bandstop_params=None):
    """
    main application interface
    :param bids_dir: input bids dataset see "helpers.read_bids_dataset" for
    more information.
    :param output_dir: output folder
    :param subject_list: subject and session list filtering.  See
    "helpers.read_bids_dataset" for more information.
    :param collect: treats each subject as having only one session.
    :param ncpus: number of cores for parallelized processing.
    :param start_stage: start from a given stage.
    :param bandstop_params: tuple of lower and upper bound for stop-band filter
    :return:
    """

    # read from bids dataset
    assert os.path.isdir(bids_dir), bids_dir + ' is not a directory!'
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    session_generator = read_bids_dataset(
        bids_dir, subject_list=subject_list, collect_on_subject=collect
    )

    # run each session in serial
    for session in session_generator:
        # setup session configuration
        out_dir = os.path.join(
            output_dir,
            'sub-%s' % session['subject'],
            'ses-%s' % session['session']
        )
        session_spec = ParameterSettings(session, out_dir)

        # create pipelines
        pre = PreFreeSurfer(session_spec)
        free = FreeSurfer(session_spec)
        post = PostFreeSurfer(session_spec)
        vol = FMRIVolume(session_spec)
        surf = FMRISurface(session_spec)
        boldproc = DCANBOLDProcessing(session_spec)
        execsum = ExecutiveSummary(session_spec)

        # set user parameters
        if bandstop_params is not None:
            boldproc.set_bandstop_filter(*bandstop_params)

        # determine pipeline order
        order = [pre, free, post, vol, surf, boldproc, execsum]
        if start_stage:
            names = [x.__class__.__name__ for x in order]
            assert start_stage in names, \
                '"%s" is unknown, check class name and case for given stage' \
                % start_stage
            order = order[names.index(start_stage):]

        # run pipelines
        for stage in order:
            print('running ' + stage.__class__.__name__)
            print(stage)
            stage.run(ncpus)


if __name__ == '__main__':
    _cli()
