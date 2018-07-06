from itertools import product

from bids.grabbids import BIDSLayout

from pipelines import (HCPConfiguration, PreFreeSurfer, FreeSurfer,
                       PostFreeSurfer, FMRIVolume, FMRISurface)


def read_bids_dataset(bids_input, subject_list=None, collect_on_subject=False):
    """
    extracts and organizes relevant metadata from a bids dataset necessary
    for the dcan-modified hcp fmri processing pipeline.
    :param bids_input: path to input bids folder
    :param subject_list: either, a list of subject ids to filter on,
    OR a dictionary of subject id: list of sessions to filter on.
    :param collect_on_subject:
    :return:
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

    for subject, sessions in subsess:
        # get relevant image modalities
        anat = set_anatomicals(layout, subject, sessions)
        func = set_functionals(layout, subject, sessions)
        fmap = set_fieldmaps(layout, subject, sessions)

        bids_data = {
            'subject': subject,
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
                      type='T2w')
    if len(t2ws):
        t2w_metadata = layout.get_metadata(t2ws[0].filename)
    else:
        t2w_metadata = None
    spec = {
        't1w': t1ws,
        't1w_metadata': t1w_metadata,
        't2w': t2ws,
        't2w_metadata': t2w_metadata
    }
    return spec


def set_functionals(layout, subject, sessions):
    func = layout.get(subject=subject, session=sessions, modality='func',
                      type='bold', extensions='.nii.gz')
    func_metadata = [layout.get_metadata(x.filename) for x in func]
    spec = {
        'func': func,
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
        # @TODO read intendedFor field to map field maps to functionals.
        positive = [i for i, x in enumerate(fmap_metadata) if '-' not in x[
            'PhaseEncodingDirection']]
        negative = [i for i, x in enumerate(fmap_metadata) if '-' in x[
            'PhaseEncodingDirection']]
        fmap = {'positive': [fmap[i] for i in positive],
                'negative': [fmap[i] for i in negative]}
        fmap_metadata = {
            'positive': [fmap_metadata[i] for i in positive],
            'negative': [fmap_metadata[i] for i in negative]
        }
        # @TODO check that no orthogonal field maps were collected.

    # handle case fieldmap # @TODO
    elif 'magnitude' in fmap:
        pass

    spec = {
        'fmap': fmap,
        'fmap_metadata': fmap_metadata
    }
    return spec


if __name__ == '__main__':
    import os
    bids_dir = r'C:\Users\sturgeod\PycharmProjects\dcan_hcp_bids/sub' \
               r'-NDARINV3F6NJ6WW'
    for spec in read_bids_dataset(bids_dir):
        conf = HCPConfiguration(spec, os.getcwd())
        pre = PreFreeSurfer(conf)
