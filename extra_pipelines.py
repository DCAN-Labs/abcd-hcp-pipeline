import os
import re

from itertools import product

from pipelines import Stage
from helpers import get_fmriname, get_taskname


class ABCDTask(Stage):

    script = '{HCPPIPEDIR}/TaskfMRIAnalysis/TaskfMRIAnalysis.sh'

    spec = '--path={path} ' \
           '--subject={subject} ' \
           '--lvl1tasks={lvl1tasks} ' \
           '--lvl1fsfs={lvl1fsfs} ' \
           '--lvl2task={lvl2task} ' \
           '--lvl2fsf={lvl2fsf} ' \
           '--lowresmesh={lowresmesh} ' \
           '--grayordinatesres={grayordinatesres} ' \
           '--origsmoothingFWHM={smoothingFWHM} ' \
           '--confound={confound} ' \
           '--finalsmoothingFWHM={finalsmoothingFWHM} ' \
           '--temporalfilter={temporalfilter} ' \
           '--vba={vba} ' \
           '--regname={regname} ' \
           '--parcellation={parcellation} ' \
           '--parcellationfile={parcellationfile}'

    smoothing_list = [2, 5]

    @property
    def args(self):
        self.kwargs['vba'] = 'NO'
        self.kwargs['confound'] = 'censor.txt'
        self.kwargs['temporalfilter'] = 200
        parcels = [('NONE', 'NONE')] #  self.get_parcels()
        task_d = self.get_tasklist()

        # construct task fmri permutations
        for parcel, smoothing, task in \
                product(parcels, self.smoothing_list, list(task_d.items())):
            self.kwargs['fmriname'] = task[0] + '_s%s' % smoothing
            self.kwargs['parcellation'] = parcel[0]
            self.kwargs['parcellationfile'] = parcel[1]
            self.kwargs['finalsmoothingFWHM'] = smoothing
            self.kwargs['lvl1tasks'] = '@'.join(task[1])
            self.kwargs['lvl1fsfs'] = '@'.join(task[1])
            self.kwargs['lvl2task'] = task[0]
            self.kwargs['lvl2fsf'] = task[0]
            self.kwargs['regname'] = "NONE"

            kw = {k: (v if v is not None else "NONE")
                  for k, v in self.kwargs.items()}
            yield self.spec.format(**kw)

    def cmdline(self):
        script = self.script.format(**os.environ)
        for argset in self.args:
            yield ' '.join((script, argset))

    def setup(self):
        """
        run task fmri prep
        :return:
        """
        super(__class__, self).setup()
        # construct command line call
        setup_script = '%s/tfMRI.py' % \
                       os.environ['ABCDTASKPREPDIR']
        arg1 = self.kwargs['path']
        arg2 = self.kwargs['sourcedata_root']
        arg3 = self.kwargs['subject']
        arg4 = self.kwargs['session']
        anat_metadata = self.config.get_bids('t1w_metadata')
        # get make/software information
        make = anat_metadata['Manufacturer']
        if make == 'GE':
            reg = re.compile(r'.*(DV2[56]).*')
            software_version = reg.match(anat_metadata[
                                             'SoftwareVersions']).group(1)
        else:
            software_version = 'NA'
        cmd = ' '.join((setup_script, arg1, arg2, arg3, arg4, make,
                        software_version))
        print(cmd)

        log_dir = self._get_log_dir()
        out_log = os.path.join(log_dir, self.__class__.__name__ + '_setup.out')
        err_log = os.path.join(log_dir, self.__class__.__name__ + '_setup.err')
        result = self.call(cmd, out_log, err_log)

    def get_tasklist(self):
        """

        :return: dictionary of task basename: list of task names (with number)
        """
        tasks = self.config.get_bids('func')
        fmri_names = [get_fmriname(t) for t in tasks]

        # filter out resting state data
        pattern = re.compile(r'^((?!rest).)*$')
        is_task = [pattern.match(t) is not None for t in fmri_names]
        fmri_names = [t for i, t in enumerate(fmri_names) if is_task[i]]
        task_names = list(set(
            get_taskname(t) for i, t in enumerate(tasks) if is_task[i]
        ))
        task_dictionary = {}
        for name in task_names:
            task_dictionary[name] = [t for t in fmri_names if name in t]
        return task_dictionary

    def get_parcels(self):
        """
        returns a list of label name, filename pairs for the labels in the
        dcan bold proc folder.
        """
        parcellation_folder = '%s/templates/parcellations' % \
                              os.environ['DCANBOLDPROCDIR']
        walker = list(os.walk(parcellation_folder))
        # find all folders which contain a space subdirectory
        candidates = [x for x in walker if 'fsLR' == os.path.basename(x[0])]
        # check that the proper dlabel files can be found.
        parcels = []
        for x in candidates:
            label_name = os.path.basename(os.path.dirname(x[0]))
            if '%s.32k_fs_LR.dlabel.nii' % label_name in x[2]:
                parcels.append((
                    label_name,
                    os.path.join(
                        x[0], '%s.32k_fs_LR.dlabel.nii' % label_name)
                ))
            else:
                print('%s is a bad label file directory' % label_name)
        return parcels
