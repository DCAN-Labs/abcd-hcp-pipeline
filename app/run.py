#!/usr/bin/env python3
__doc__ = \
"""The Developmental Cognition and Neuroimaging (DCAN) Labs fMRI Pipeline [1].
This BIDS application initiates a functional MRI processing pipeline built
upon the Human Connectome Project's minimal processing pipelines [2].  The
application requires only a dataset conformed to the BIDS specification, and
little-to-no additional configuration on the part of the user. BIDS format
and applications are explained in detail at http://bids.neuroimaging.io/
"""
__references__ = \
"""References
----------
[1] Sturgeon, D., Perrone, A., Earl, E., & Snider, K.
DCAN_Labs/abcd-hcp-pipeline. DOI: 10.5281/zenodo.2587209. (check on
zenodo.org for a version-specific DOI/citation)
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
__version__ = "0.1.6"

import argparse
import os

from helpers import read_bids_dataset, validate_config, validate_license
from pipelines import (ParameterSettings, PreFreeSurfer, FreeSurfer,
                       PostFreeSurfer, FMRIVolume, FMRISurface,
                       DCANBOLDProcessing, ExecutiveSummary, CustomClean,
                       DiffusionPreprocessing)
from extra_pipelines import ABCDTask


def _cli():
    """
    command line interface
    :return:
    """
    parser = generate_parser()
    args = parser.parse_args()

    kwargs = {
        'bids_dir': args.bids_dir,
        'output_dir': args.output_dir,
        'subject_list': args.subject_list,
        'session_list': args.session_list,
        'collect': args.collect,
        'ncpus': args.ncpus,
        'stages': args.stages,
        'bandstop_params': args.bandstop,
        'check_only': args.check_outputs_only,
        'run_abcd_task': args.abcd_task,
        'study_template': args.study_template,
        'cleaning_json': args.cleaning_json,
        'print_commands': args.print,
        'ignore_expected_outputs': args.ignore_expected_outputs,
        'ignore_modalities': args.ignore,
        'freesurfer_license': args.freesurfer_license,
        'dcmethod': args.dcmethod
    }

    return interface(**kwargs)


def generate_parser(parser=None):
    """
    Generates the command line parser for this program.
    :param parser: optional subparser for wrapping this program as a submodule.
    :return: ArgumentParser for this script/module
    """
    if not parser:
        parser = argparse.ArgumentParser(
            prog='abcd-hcp-pipeline',
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__references__,
            usage='%(prog)s bids_dir output_dir --freesurfer-license=<LICENSE>'
                  ' [OPTIONS]'
        )
    parser.add_argument(
        'bids_dir',
        help='Path to the input BIDS dataset root directory.  Read more '
             'about the BIDS standard in the link in the description.  It is '
             'recommended to use Dcm2Bids to convert from participant dicoms '
             'into BIDS format.'
    )
    parser.add_argument(
        'output_dir',
        help='Path to the output directory for all intermediate and output '
             'files from the pipeline, which is also where logs are stored.'
    )
    parser.add_argument(
        '--version', '-v', action='version', version='%(prog)s ' + __version__
    )
    parser.add_argument(
        '--participant-label', dest='subject_list', metavar='ID', nargs='+',
        help='Optional list of participant IDs to run. Default is all IDs '
             'found under the BIDS input directory. The participant label '
             'does not include the "sub-" prefix'
    )
    parser.add_argument(
        '--session-id', dest='session_list', nargs='*',
        metavar='LABEL',
        help='filter input dataset by session id. Default is all ids '
             'found under the subject input directory(s).  A session id '
             'does not include "ses-"'
    )
    parser.add_argument(
        '--freesurfer-license', dest='freesurfer_license',
        metavar='LICENSE_FILE',
        help='If using docker or singularity, you will need to acquire and '
             'provide your own FreeSurfer license. The license can be '
             'acquired by filling out this form: '
             'https://surfer.nmr.mgh.harvard.edu/registration.html'
    )
    parser.add_argument(
        '--dcmethod', dest='dcmethod',
        choices=['TOPUP', 'FIELDMAP', 'NONE'],
        help='Choices: TOPUP, FIELDMAP, NONE '
             'Specifies method used for fieldmap-based distortion ' 
             'correction of anatomical and functional data '
             'Default: automatic detection based on contents '
             'of fmap dir'
    )
    parser.add_argument(
        '--all-sessions', dest='collect', action='store_true',
        help='Collapses all sessions into one when running a subject, '
             'essentially treating data as if it were collected during a '
             'single session (per subject).'
    )
    parser.add_argument(
        '--ncpus', type=int, default=1,
        help='Number of cores to use for concurrent processing and '
             'algorithmic speedups.  Warning: causes ANTs and FreeSurfer to '
             'produce non-deterministic results.'
    )
    parser.add_argument(
        '--stage','--stages', dest='stages',
        help='specify a subset of stages to run.'
             'If a single stage name is given, the pipeline with be '
             'started at that stage. If a string with a ":" is given, '
             'a stage name before the ":" will tell run.py where to '
             'start and a stage name after the ":" will tell it where '
             'to stop. If no ":" is found, the pipeline will start '
             'with the stage specified and run to the end. '
             'Calling run.py with: \n'
             '   --stage="PreFreeSurfer:PreFreeSurfer"  \n'
             'or with: \n'
             '   --stage=":PreFreeSurfer"  \n'
             'will cause only PreFreeSurfer to be run. '
             '(This can be useful to do optional processing between'
             'PreFreeSurfer and FreeSurfer.)'
             'Calling run.py with: \n'
             '   --stages="FreeSurfer:FMRISurface"  \n'
             'will start with stage FreeSurfer and stop after'
             'FMRISurface (before DCANBOLDProcessing).'
             'Default start is PreFreeSurfer and default '
             'stop is ExecutiveSummary. The specifications: \n'
             '   --stages="PreFreeSurfer:ExecutiveSummary"  \n'
             '   --stages=":ExecutiveSummary"  \n'
             '   --stages="PreFreeSurfer:"  \n'
             'are exactly identical to each other and to sending '
             'no --stage argument. '
             'Valid stage names: '
             'PreFreeSurfer, FreeSurfer, PostFreeSurfer, FMRIVolume, '
             'FMRISurface, DCANBOLDProcessing, ExecutiveSummary, CustomClean'
    )
    parser.add_argument(
        '--bandstop', type=float, nargs=2, metavar=('LOWER', 'UPPER'),
        help='Parameters for motion regressor band-stop filter. It is '
             'recommended for the boundaries to match the inter-quartile '
             'range for participant group respiratory rate (breaths per '
             'minute), or to match bids physio data directly [3].  These '
             'parameters are highly recommended for data acquired with a '
             'frequency of greater than 1 Hz (TR less than 1 second). '
             'Default is no filter.'
    )
    extras = parser.add_argument_group(
        'Special pipeline options',
        description='Options which pertain to an alternative pipeline or an '
                    'extra stage which is not\n inferred from the BIDS data.'
    )
    extras.add_argument(
        '--custom-clean', metavar='JSON', dest='cleaning_json',
        help= 'Template JSON specifying files to be removed '
             'in the optional CustomClean stage. Required if '
             'CustomClean is in the list of stages to be run. '
    )
    extras.add_argument(
        '--abcd-task', action='store_true',
        help='Runs ABCD task data through task fMRI analysis, adding this '
             'stage to the end. Warning: Not written for general use: a '
             'general task analysis module will be included in a future '
             'release.'
    )
    extras.add_argument(
        '--study-template', nargs=2, metavar=('HEAD', 'BRAIN'),
        help='Template head and brain images for intermediate nonlinear '
             'registration and masking, effective where population differs '
             'greatly from average adult, e.g. in elderly populations with '
             'large ventricles.'
    )
    extras.add_argument(
        '--ignore', choices=['func', 'dwi'], action='append', default=[],
        help='Ignore a modality in processing. Option can be repeated.'
    )
    runopts = parser.add_argument_group(
        'Runtime options',
        description='Special changes to runtime behaviors. Debugging features.'
    )
    runopts.add_argument(
        '--check-outputs-only', action='store_true',
        help='Checks for the existence of outputs for each stage then exit. '
             'Useful for debugging.'
    )
    runopts.add_argument(
        '--print-commands-only', action='store_true', dest='print',
        help='Print run commands for each stage to shell then exit.'
    )
    runopts.add_argument(
        '--ignore-expected-outputs', action='store_true',
        help='Continues pipeline even if some expected outputs are missing.'
    )

    return parser


def interface(bids_dir, output_dir, subject_list=None, collect=False, ncpus=1,
              stages=None, bandstop_params=None, check_only=False,
              run_abcd_task=False, study_template=None, cleaning_json=None,
              print_commands=False, ignore_expected_outputs=False,
              ignore_modalities=[], freesurfer_license=None, session_list=None,
              dcmethod=None):
    """
    main application interface
    :param bids_dir: input bids dataset see "helpers.read_bids_dataset" for
    more information.
    :param output_dir: output folder
    :param subject_list: subject and session list filtering.  See
    "helpers.read_bids_dataset" for more information.
    :param session_list: session list filtering. See "helpers.read_bids_dataset".
    :param collect: treats each subject as having only one session.
    :param ncpus: number of cores for parallelized processing.
    :param stages: only run a subset of stages.
    :param bandstop_params: tuple of lower and upper bound for stop-band filter
    :param check_only: check expected outputs for each stage then terminate
    :param study_template: specified head and brain templates for intermediate registration
    :param cleaning_json: template JSON for use in optional CustomClean stage
    :param print_commands: flag to print commands only, without running pipeline
    :param ignore_expected_outputs: continue processing even if expected intermediate outputs are missing
    :param ignore_modalities: skip processing of specified modalities (func, dwi)
    :param freesurfer_license: FreeSurfer license file
    :param session_list: list of BIDS sessions, for filtering what input data to process
    :param dcmethod: override default fmap distortion correction method  
    :return:
    """
    if not check_only or not print_commands:
        validate_license(freesurfer_license)
    # read from bids dataset
    assert os.path.isdir(bids_dir), bids_dir + ' is not a directory!'
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    session_generator = read_bids_dataset(
        bids_dir, subject_list=subject_list, 
        collect_on_subject=collect, session_list=session_list
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
        validate_config(session, ignore_modalities)
        modes = session['types']
        run_anat = 'T1w' in modes
        run_func = 'bold' in modes and 'func' not in ignore_modalities
        run_dwi = 'dwi' in modes and 'dwi' not in ignore_modalities
        summary = True

        session_spec = ParameterSettings(session, out_dir)
        if not run_func:
            anat_only = True
            session_spec.set_anat_only(anat_only)

        # set session parameters
        if study_template is not None:
            session_spec.set_study_template(*study_template)
        if dcmethod is not None:
            session_spec.set_dcmethod(dcmethod)
        

        # create pipelines
        order = []
        if run_anat:
            pre = PreFreeSurfer(session_spec)
            free = FreeSurfer(session_spec)
            post = PostFreeSurfer(session_spec)
            order += [pre, free, post]
        if run_func:
            vol = FMRIVolume(session_spec)
            surf = FMRISurface(session_spec)
            boldproc = DCANBOLDProcessing(session_spec)
            order += [vol, surf, boldproc]
        if run_dwi:
            print('dwi preprocessing is still a work in progress. Skipping.')
            if False:
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

        if stages:
            # User can indicate start or end or both; default
            # to entire list built above.
            start_idx = 0
            end_idx = len(order)

            idx_colon = stages.find(":")
            if idx_colon > -1:
                # Start stage is everything before the colon.
                start_stage = stages[:idx_colon]
                # End stage is everything after the colon.
                end_stage = stages[(idx_colon+1):]
            else:
                # No colon means no end stage.
                start_stage = stages
                end_stage = None

            names = [x.__class__.__name__ for x in order]

            if start_stage:
                assert start_stage in names, \
                        '"%s" is unknown, check class name and case for given stage' \
                        % start_stage
                start_idx = names.index(start_stage)

            if end_stage:
                assert end_stage in names, \
                        '"%s" is unknown, check class name and case for given stage' \
                        % end_stage
                end_idx = names.index(end_stage)
                end_idx += 1 # Include end stage.

            # Slice the list.
            order = order[start_idx:end_idx]

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
            print('abcd-hcp-pipeline v%s' % __version__ )
            print('running %s' % stage.__class__.__name__)
            print(stage)
            stage.run(ncpus)


if __name__ == '__main__':
    _cli()

