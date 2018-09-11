import os
import re

from itertools import product

from bids.grabbids import BIDSLayout


def read_bids_dataset(bids_input, subject_list=None, collect_on_subject=False):
    """
    extracts and organizes relevant metadata from a bids dataset necessary
    for the dcan-modified hcp fmri processing pipeline.
    :param bids_input: path to input bids folder
    :param subject_list: EITHER, a list of subject ids to filter on,
    OR a dictionary of subject id: list of sessions to filter on.
    :param collect_on_subject: collapses all sessions, for cases with
    non-longitudinal data spread across scan sessions.
    :return: bids data struct (nested dict)
    spec:
    {
      t1w: t1w filename list,
      t2w: t2w filename list,
      t1w_metadata: bids meta data (first t1),
      t2w_metadata: bids meta data (first t2),
      func: fmri filename list,
      func_metadata: bids meta data list,
      fmap: {
        positive: spin echo filename list (if applicable)
        negative: spin echo filename list (if applicable)
      },
      fmap_metadata: {
        positive: bids meta data list (if applicable)
        negative: bids meta data list (if applicable)
      },
    }
    """

    layout = BIDSLayout(bids_input)
    subjects = layout.get_subjects()

    # filter subject list
    if isinstance(subject_list, list):
        subjects = [s for s in subjects if s in subject_list]
    elif isinstance(subject_list, dict):
        subjects = [s for s in subjects if s in subject_list.keys()]

    subsess = []
    # filter session list
    for s in subjects:
        sessions = layout.get_sessions(subject=s)
        if not sessions:
            subsess += [(s, 'session')]
        elif collect_on_subject:
            subsess += [(s, sessions)]
        else:
            subsess += list(product([s], sessions))

    assert len(subsess), 'bids data not found for participants. If labels ' \
            'were provided, check the participant labels for errors.  ' \
            'Otherwise check that the bids folder provided is correct.'

    for subject, sessions in subsess:
        # get relevant image modalities
        anat = set_anatomicals(layout, subject, sessions)
        func = set_functionals(layout, subject, sessions)
        fmap = set_fieldmaps(layout, subject, sessions)

        bids_data = {
            'subject': subject,
            'session': sessions if not collect_on_subject else 'session',
            'types': layout.get(subject=subject, session=sessions,
                                target='type', return_type='id')
        }
        bids_data.update(anat)
        bids_data.update(func)
        bids_data.update(fmap)

        yield bids_data


def set_anatomicals(layout, subject, sessions):
    t1ws = layout.get(subject=subject, session=sessions, modality='anat',
                      type='T1w', extensions='.nii.gz')
    t1w_metadata = layout.get_metadata(t1ws[0].filename)

    t2ws = layout.get(subject=subject, session=sessions, modality='anat',
                      type='T2w', extensions='.nii.gz')
    if len(t2ws):
        t2w_metadata = layout.get_metadata(t2ws[0].filename)
    else:
        t2w_metadata = None
    spec = {
        't1w': [t.filename for t in t1ws],
        't1w_metadata': t1w_metadata,
        't2w': [t.filename for t in t2ws],
        't2w_metadata': t2w_metadata
    }
    return spec


def set_functionals(layout, subject, sessions):
    func = layout.get(subject=subject, session=sessions, modality='func',
                      type='bold', extensions='.nii.gz')
    func_metadata = [layout.get_metadata(x.filename) for x in func]

    spec = {
        'func': [f.filename for f in func],
        'func_metadata': func_metadata[0]
    }
    return spec


def set_fieldmaps(layout, subject, sessions):
    fmap = layout.get(subject=subject, session=sessions, modality='fmap',
                      extensions='.nii.gz')
    fmap_metadata = [layout.get_metadata(x.filename) for x in fmap]

    # handle case spin echo
    types = [x.type for x in fmap]
    indices = [i for i, x in enumerate(types) if x == 'epi']
    if len(indices):
        # @TODO read IntendedFor field to map field maps to functionals.
        positive = [i for i, x in enumerate(fmap_metadata) if '-' not in x[
            'PhaseEncodingDirection']]
        negative = [i for i, x in enumerate(fmap_metadata) if '-' in x[
            'PhaseEncodingDirection']]
        fmap = {'positive': [fmap[i].filename for i in positive],
                'negative': [fmap[i].filename for i in negative]}
        fmap_metadata = {
            'positive': [fmap_metadata[i] for i in positive],
            'negative': [fmap_metadata[i] for i in negative]}
        # @TODO check that no orthogonal field maps were collected.

    # handle case fieldmap # @TODO
    elif 'magnitude' in fmap:
        pass

    spec = {
        'fmap': fmap,
        'fmap_metadata': fmap_metadata
    }
    return spec


def get_readoutdir(metadata):
    """
    get readout direction from bids metadata.  !!Note that this method only
    applies where the nifti orientation is RAS!!
    :param metadata: grabbids metadata dict.
    :return: unwarp dir in cartesian (world) coordinates.
    """
    iopd = metadata['ImageOrientationPatientDICOM']
    ped = metadata['InPlanePhaseEncodingDirectionDICOM']
    # readout direction is opposite the in plane phase encoding direction
    if ped == 'ROW':
        readoutvec = iopd[3:]
    elif ped == 'COLUMN':
        readoutvec = iopd[:3]
    else:
        raise ValueError('phase encoding direction not recognized: ' + ped)

    # convert 3-vector to symbolic unit vector
    i = max([0, 1, 2], key=lambda x: abs(readoutvec[x]))
    readoutdir = ['x', 'y', 'z'][i]
    if readoutvec[i] < 0:
        readoutdir += '-'

    return readoutdir


def get_relpath(filename):
    """
    :param filename: path to bids nifti.
    :return: relative path from the bids subject folder.
    """

    # assumes a session is present
    types_dir = os.path.dirname(filename)
    sessions_dir = os.path.dirname(types_dir)
    subject_dir = os.path.dirname(sessions_dir)

    return os.path.relpath(filename,subject_dir)


def get_fmriname(filename):
    """
    :param filename: path to bids functional nifti
    :return: name of fmri run, e.g. "task-rest01".
    """
    name = os.path.basename(filename)
    expr = re.compile(r'.*(task-[^_]+).*run-([0-9]+).*')
    taskrun = expr.match(name)
    if taskrun:
        fmriname = taskrun.group(1) + taskrun.group(2)
    else:
        # handle optional bids "run" field:
        fmriname = get_taskname(filename)
        fmriname += '01'
    return fmriname


def get_taskname(filename):
    """
    :param filename: path to bids functional nifti
    :return: name of task, e.g. "task-nback"
    """
    name = os.path.basename(filename)
    expr = re.compile(r'.*(task-[^_]+).*')
    task = expr.match(name)
    taskname = task.group(1)
    return taskname


def ijk_to_xyz(vec, patient_orientation=None):
    """
    converts canonical quaternion unit vector symbols to cartesian.
    :param vec: one of i, j, k +/-
    :return: x, y, or z +/-
    """
    vmap = {'i': 'x', 'j': 'y', 'k': 'z',
            'i-': 'x-', 'j-': 'y-', 'k-': 'z-',
            '-i': 'x-', '-j': 'y-', '-k': 'z-'}
    return vmap[vec]
