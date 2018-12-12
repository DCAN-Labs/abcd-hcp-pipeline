#!/usr/bin/env python3

__doc__ = \
"""The Developmental Cognition and Neuroimaging (DCAN) lab fMRI Pipeline [1].
This BIDS application initiates a functional MRI processing pipeline built
upon the Human Connectome Project's minimal processing pipelines [2].  The
application requires only a dataset conformed to the BIDS specification, and
little-to-no additional configuration on the part of the user. BIDS format
and applications are explained in detail at http://bids.neuroimaging.io/
"""
__references__ = \
"""References
----------
[1] dcan-pipelines (for now, please cite [3] in use of this software)
[2] Glasser, MF. et al. The minimal preprocessing pipelines for the Human
Connectome Project. Neuroimage. 2013 Oct 15;80:105-24.
10.1016/j.neuroimage.2013.04.127
[3] Fair, D. et al. Correction of respiratory artifacts in MRI head motion
estimates. Biorxiv. 2018 June 7. doi: https://doi.org/10.1101/337360
[4] Dale, A.M., Fischl, B., Sereno, M.I., 1999. Cortical surface-based
analysis. I. Segmentation and surface reconstruction. Neuroimage 9, 179-194.
[5] M. Jenkinson, C.F. Beckmann, T.E. Behrens, M.W. Woolrich, S.M. Smith. FSL.
NeuroImage, 62:782-90, 2012
[6] Avants, BB et al. The Insight ToolKit image registration framework. Front
Neuroinform. 2014 Apr 28;8:44. doi: 10.3389/fninf.2014.00044. eCollection 2014.
"""
__version__ = "1.0.1"

import argparse
import os

from helpers import read_bids_dataset
from pipelines import (ParameterSettings, PreFreeSurfer, FreeSurfer,
                       PostFreeSurfer, FMRIVolume, FMRISurface,
                       DCANBOLDProcessing, ExecutiveSummary, CustomClean)
from extra_pipelines import ABCDTask


def _cli():
    """
    command line interface
    :return:
    """
    parser = generate_parser()
    args = parser.parse_args()

    return interface(args.bids_dir,  args.output_dir, args.subject_list,
                     args.collect, args.ncpus, args.stage, args.bandstop,
                     args.check_outputs_only, args.abcd_task,
                     args.study_template, args.cleaning_json,
                     args.print, args.ignore_expected_outputs)


def generate_parser(parser=None):
    """
    Generates the command line parser for this program.
    :param parser: optional subparser for wrapping this program as a submodule.
    :return: ArgumentParser for this script/module
    """
    if not parser:
        parser = argparse.ArgumentParser(
            prog='dcan-pipelines',
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__references__
        )
    parser.add_argument(
        'bids_dir',
        help='path to the input bids dataset root directory.  Read more '
             'about bids format in the link in the description.  It is '
             'recommended to use the dcan bids gui or dcm2bids to convert '
             'from participant dicoms to bids.'
    )
    parser.add_argument(
        'output_dir',
        help='path to the output directory for all intermediate and output '
             'files from the pipeline, also path in which logs are stored.'
    )
    parser.add_argument(
        '--version', '-v', action='version', version='%(prog)s ' + __version__
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
             'FMRISurface, DCANBOLDProcessing, ExecutiveSummary, CustomClean'
    )
    parser.add_argument(
        '--bandstop', type=float, nargs=2, metavar=('LOWER', 'UPPER'),
        help='parameters for motion regressor band-stop filter. It is '
             'recommended for the boundaries to match the inter-quartile '
             'range for participant group respiratory rate (bpm), or to match '
             'bids physio data directly [3].  These parameters are highly '
             'recommended for data acquired with a frequency of approx. 1 Hz '
             'or more (TR<=1.0). Default is no filter'
    )
    extras = parser.add_argument_group(
        'special pipeline options',
        description='options which pertain to an alternative pipeline or an '
                    'extra stage which is not\n inferred from the bids data.'
    )
    extras.add_argument(
        '--custom-clean', metavar='JSON', dest='cleaning_json',
        help='runs dcan cleaning script after the pipeline completes'
             'successfully to delete pipeline outputs based on '
             'the file structure specified in the custom-clean json.'
    )
    extras.add_argument(
        '--abcd-task', action='store_true',
        help='runs abcd task data through task fmri analysis, adding this '
             'stage to the end. Warning: Not written for general use: a '
             'general task analysis module will be included in a future '
             'release.'
    )
    extras.add_argument(
        '--study-template', nargs=2, metavar=('HEAD', 'BRAIN'),
        help='template head and brain images for intermediate nonlinear '
             'registration, effective where population differs greatly from '
             'average adult, e.g. in elderly populations with large '
             'ventricles.'
    )
    extras.add_argument(
        '--ignore-func', action='store_true',
        help='pipeline will only process anatomical scans. Must provide this '
             'flag for datasets without bold data.'
    )
    runopts = parser.add_argument_group(
        'runtime options',
        description='special changes to runtime behaviors. Debugging features.'
    )
    runopts.add_argument(
        '--check-outputs-only', action='store_true',
        help='checks for the existence of outputs for each stage then exit. '
             'Useful for debugging.'
    )
    runopts.add_argument(
        '--print-commands-only', action='store_true', dest='print',
        help='print run commands for each stage to shell then exit.'
    )
    runopts.add_argument(
        '--ignore-expected-outputs', action='store_true',
        help='continues pipeline even if some expected outputs are missing.'
    )


    return parser


def interface(bids_dir, output_dir, subject_list=None, collect=False, ncpus=1,
              start_stage=None, bandstop_params=None, check_only=False,
              run_abcd_task=False, study_template=None, cleaning_json=None,
              print_commands=False, ignore_expected_outputs=False):
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
    :param check_only: check expected outputs for each stage then terminate
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
        # detect available data for pipeline stages
        modes = session_spec['types']
        anatomical_pipelines = 'T1w' in modes
        functional_pipelines = 'bold' in modes
        dwi_pipelines = 'dwi' in modes
        summary = True

        session_spec = ParameterSettings(session, out_dir)

        # set session parameters
        if study_template is not None:
            session_spec.set_study_template(*study_template)

        # create pipelines
        order = []
        if anatomical_pipelines:
            pre = PreFreeSurfer(session_spec)
            free = FreeSurfer(session_spec)
            post = PostFreeSurfer(session_spec)
            order += [pre, free, post]
        if functional_pipelines:
            vol = FMRIVolume(session_spec)
            surf = FMRISurface(session_spec)
            boldproc = DCANBOLDProcessing(session_spec)
            order += [vol, surf, boldproc]
        if dwi_pipelines:
            diffprep = DiffusionPreprocessing(session_spec)
            order += [diffprep]
        if summary:
            execsum = ExecutiveSummary(session_spec)
            order += [execsum]

        # set user parameters
        if bandstop_params is not None:
            boldproc.set_bandstop_filter(*bandstop_params)

        # add optional pipelines
        if run_abcd_task:
            abcdtask = ABCDTask(session_spec)
            order.append(abcdtask)
        if cleaning_json:
            cclean = CustomClean(session_spec, cleaning_json)
            order.append(cclean)

        if start_stage:
            names = [x.__class__.__name__ for x in order]
            assert start_stage in names, \
                '"%s" is unknown, check class name and case for given stage' \
                % start_stage
            order = order[names.index(start_stage):]

        # special runtime options
        if check_only:
            for stage in order:
                print('checking outputs for %s' % stage.__class__.__name__)
                try:
                    stage.check_expected_outputs()
                except AssertionError:
                    pass
            return
        if print_commands:
            for stage in order:
                stage.deactivate_runtime_calls()
                stage.deactivate_check_expected_outputs()
                stage.deactivate_remove_expected_outputs()
        if ignore_expected_outputs:
            print('ignoring checks for expected outputs.')
            for stage in order:
                stage.activate_ignore_expected_outputs()

        # run pipelines
        for stage in order:
            print('running %s' % stage.__class__.__name__)
            print(stage)
            stage.run(ncpus)


if __name__ == '__main__':
    _cli()

