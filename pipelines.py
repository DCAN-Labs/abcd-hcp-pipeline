import inspect
import os
import subprocess

from helpers import (get_fmriname, get_readoutdir, get_relpath,
                     ijk_to_xyz)


class HCPConfiguration(object):
    """
    Paths to files and settings required to run DCAN HCP.  Class attributes 
    should be any parameters which should in NO circumstances change between 
    subjects.  Instance attributes will be attributes that might change, 
    for example, repetition time (might) change between scans in an 
    experimental study, but the target atlas wouldn't.
    """

    # @ templates @ #
    # MNI0.7mm template
    t1template = "{HCPPIPEDIR_Templates}/MNI152_T1_1mm.nii.gz"
    # Brain extracted MNI0.7mm template
    t1templatebrain = "{HCPPIPEDIR_Templates}/MNI152_T1_1mm_brain.nii.gz"
    # MNI2mm template
    t1template2mm = "{HCPPIPEDIR_Templates}/MNI152_T1_2mm.nii.gz"
    # MNI0.7mm T2wTemplate
    t2template = "{HCPPIPEDIR_Templates}/MNI152_T2_1mm.nii.gz"
    # Brain extracted MNI0.7mm T2wTemplate
    t2templatebrain = "{HCPPIPEDIR_Templates}/MNI152_T2_1mm_brain.nii.gz"
    # MNI2mm T2wTemplate
    t2template2mm = "{HCPPIPEDIR_Templates}/MNI152_T2_2mm.nii.gz"
    # Brain mask MNI0.7mm template
    templatemask = "{HCPPIPEDIR_Templates}/MNI152_T1_1mm_brain_mask.nii.gz"
    # MNI2mm template
    template2mmmask = "{HCPPIPEDIR_Templates}/MNI152_T1_2mm_brain_mask_dil" \
                      ".nii.gz"
    # Myelin Maps
    refmyelinmaps = "{HCPPIPEDIR_Templates}/standard_mesh_atlases/" \
                    "Conte69.MyelinMap_BC.164k_fs_LR.dscalar.nii"
    # Surface Atlas Templates
    surfatlasdir = "{HCPPIPEDIR_Templates}/standard_mesh_atlases"
    # Grayordinate Templates
    grayordinatesdir = "{HCPPIPEDIR_Templates}/91282_Greyordinates"

    # @ various settings @ #
    # fov size for robust_fov automatic cropping
    brainsize = 150
    # final time series isotropic resolution (mm)
    fmrires = 2.0
    # resolution of greyordinates (mm)
    grayordinateres = 2.0
    # smoothing sigma for final greyordinate data (mm)
    smoothingFWHM = 2.0
    # surface registration algorithm, one of: FS, MSMSulc
    regname = "FS"
    # number of vertices (in thousands) for high and low res surface meshes
    hiresmesh = "164"
    lowresmesh = "32"
    # motion correction method
    mctype = 'MCFLIRT'

    # @ configuration files @ #
    topupconfig = "{HCPPIPEDIR_Config}/b02b0.cnf"
    fnirtconfig = "{HCPPIPEDIR_Config}/T1_2_MNI152_2mm.cnf"
    freesurferlabels = "{HCPPIPEDIR_Config}/FreeSurferAllLut.txt"
    subcortgraylabels = "{HCPPIPEDIR_Config}/FreeSurferSubcortical" \
                            "LabelTableLut.txt"

    def __init__(self, bids_data, output_directory):
        """
        Configuration to run HCP Pipeline on a single subject session.
        :param bids_data: yielded spec from read_bids_dataset
        :param output_directory: output directory for pipeline
        """

        # input bids data struct
        self.bids_data = bids_data

        # @ parameters read from bids @ #
        self.t1w = self.bids_data['t1w']
        self.t1samplespacing = \
            '%.12f' % self.bids_data['t1w_metadata']['DwellTime']
        self.t1samplespacing = self.t1samplespacing.rstrip('0')

        if 't2w' in self.bids_data['types']:
            self.t2w = self.bids_data['t2w']
            self.t2samplespacing = \
                '%.12f' % self.bids_data['t2w_metadata']['DwellTime']
            self.t2samplespacing = self.t2samplespacing.rstrip('0')
        else:
            self.t2w = []
            self.t2samplespacing = None

        # distortion correction method: TOPUP, FIELDMAP, or NONE, inferred
        # from files, defaults to spin echo (topup) if both field maps exist
        self.unwarpdir = get_readoutdir(self.bids_data['t1w_metadata'])
        if 'epi' in self.bids_data['types']:
            self.dcmethod = 'TOPUP'
            # spin echo field map spacing @TODO read during volume per fmap?
            self.echospacing = self.bids_data['fmap_metadata']['positive'][0][
                'EffectiveEchoSpacing']
            self.echospacing = ('%.12f' % self.echospacing).rstrip('0')
            # distortion correction phase encoding direction
            self.seunwarpdir = ijk_to_xyz(
                self.bids_data['func_metadata']['PhaseEncodingDirection'])

            # set unused fmap args
            self.fmapmag = self.fmapphase = self.fmapgeneralelectric = \
                self.echodiff = self.gdcoeffs = None
            # @TODO decide on bfcmethod for fmri data.

        elif 'magnitude' in self.bids_data['types']:
            self.dcmethod = 'FIELDMAP'
            # gradient field map delta TE
            self.echodiff = None  # @TODO

        else:
            self.dcmethod = 'NONE'

        if not hasattr(self, 'fmribfcmethod'):
            self.fmribfcmethod = None

        # @ input files @ #
        self.logs = os.path.join(output_directory, 'hcponeclick')
        self.subject = self.bids_data['subject']
        self.path = os.path.join(output_directory, self.subject)

        # print command for HCP
        self.printcom = ''

    def _params(self):
        params = inspect.getmembers(self, lambda a: not inspect.isroutine(a))
        params = {x[0]: x[1] for x in params if not x[0].startswith('_')}
        return params

    def _format(self):
        params = self._params()
        # format all attributes
        for item, value in params.items():
            if isinstance(value, str):
                setattr(self, item, value.format(**os.environ))

    def get_params(self):
        self._format()
        return self._params()

    def get_bids(self, *args):
        """
        get data from bids struct
        :param args: list of nested dict keys, e.g. one must provide 'fmap',
        'positive' to retrieve the positive spin echo field maps.
        :return: bids data
        """
        val = self.bids_data
        for arg in args:
            val = val[arg]
        return val


class Stage(object):

    def __init__(self, config):
        self.config = config
        self.kwargs = config.get_params()

    def __str__(self):
        string = ' \\\n    '.join(self.cmdline().split())
        return string

    @property
    def args(self):
        raise NotImplementedError

    @property
    def script(self):
        raise NotImplementedError

    def cmdline(self):
        script = self.script.format(**os.environ)
        return ' '.join((script, self.args))

    def run(self):
        if inspect.isgeneratorfunction(self.cmdline):
            for cmd in self.cmdline():
                subprocess.call(cmd, shell=True)
        else:
            subprocess.call(self.cmdline(), shell=True)


class PreFreeSurfer(Stage):

    script = '{HCPPIPEDIR}/PreFreeSurfer/PreFreeSurferPipeline.sh'

    spec = ' --path={path}' \
           ' --subject={subject}' \
           ' --t1={t1}' \
           ' --t2={t2}' \
           ' --t1template={t1template}' \
           ' --t1templatebrain={t1templatebrain}' \
           ' --t1template2mm={t1template2mm}' \
           ' --t2template={t2template}' \
           ' --t2templatebrain={t2templatebrain}' \
           ' --t2template2mm={t2template2mm}' \
           ' --templatemask={templatemask}' \
           ' --template2mmmask={template2mmmask}' \
           ' --brainsize={brainsize}' \
           ' --fnirtconfig={fnirtconfig}' \
           ' --fmapmag={fmapmag}' \
           ' --fmapphase={fmapphase}' \
           ' --fmapgeneralelectric={fmapgeneralelectric}' \
           ' --echodiff={echodiff}' \
           ' --SEPhaseNeg={sephaseneg}' \
           ' --SEPhasePos={sephasepos}' \
           ' --echospacing={echospacing}' \
           ' --seunwarpdir={seunwarpdir}' \
           ' --t1samplespacing={t1samplespacing}' \
           ' --t2samplespacing={t2samplespacing}' \
           ' --unwarpdir={unwarpdir}' \
           ' --gdcoeffs={gdcoeffs}' \
           ' --avgrdcmethod={dcmethod}' \
           ' --topupconfig={topupconfig}' \
           ' --printcom={printcom}'

    def __init__(self, config):
        super(__class__, self).__init__(config)
        # modify t1/t2 inputs for spec
        self.kwargs['t1'] = '@'.join(self.kwargs.get('t1w'))
        self.kwargs['t2'] = '@'.join(self.kwargs.get('t2w', []))
        if self.kwargs['dcmethod'] == 'TOPUP':
            self.kwargs['sephasepos'], self.kwargs['sephaseneg'] = \
                self._get_intended_sefmaps()

    def _get_intended_sefmaps(self):
        """
        search for intendedFor field from sidecar json, else give the first
        spin echo pair.  @TODO Unfortunately, it will cause problems if someone
        includes the substring "T1w" in a spin echo sidecar name.
        :return: pair of spin echos, parallel
        """
        if '-' in self.kwargs['seunwarpdir']:
            parallel = 'negative'
        else:
            parallel = 'positive'

        for idx, sefm in enumerate(self.config.get_bids('fmap_metadata',
                                                     parallel)):
            intended_targets = sefm.get('intendedFor', [])
            if 'T1w' in ' '.join(intended_targets):
                intended_idx = idx
                break
        else:
            intended_idx = 0

        return self.config.get_bids('fmap', 'positive', intended_idx), \
            self.config.get_bids('fmap', 'negative', intended_idx)

    @property
    def args(self):
        return self.spec.format(**self.kwargs)


class FreeSurfer(Stage):

    script = '{HCPPIPEDIR}/FreeSurfer/FreeSurferPipeline.sh'

    spec = ' --subject={subject}' \
           ' --subjectDIR={freesurferdir}' \
           ' --t1={t1_restore}' \
           ' --t1brain={t1_restore_brain}' \
           ' --t2={t2_restore}' \
           ' --printcom={printcom}'

    def __init__(self, config):
        super(__class__, self).__init__(config)
        self.kwargs['freesurferdir'] = os.path.join(
            self.kwargs['path'], 'T1w', 'subject')
        self.kwargs['t1_restore'] = os.path.join(
            self.kwargs['path'], 'T1w', 'T1w_acpc_dc_restore.nii.gz')
        self.kwargs['t1_restore_brain'] = os.path.join(
            self.kwargs['path'], 'T1w', 'T1w_acpc_dc_restore_brain.nii.gz')
        self.kwargs['t2_restore'] = os.path.join(
            self.kwargs['path'], 'T2w', 'T2w_acpc_dc_restore.nii.gz')

    @property
    def args(self):
        return self.spec.format(**self.kwargs)


class PostFreeSurfer(Stage):

    script = '{HCPPIPEDIR}/PostFreeSurfer/PostFreeSurferPipeline.sh'

    spec = ' --path={path}' \
           ' --subject={subject}' \
           ' --surfatlasdir={surfatlasdir}' \
           ' --grayordinatesdir={grayordinatesdir}' \
           ' --grayordinateres={grayordinateres}' \
           ' --hiresmesh={hiresmesh}' \
           ' --lowresmesh={lowresmesh}' \
           ' --subcortgraylabels={subcortgraylabels}' \
           ' --freesurferlabels={freesurferlabels}' \
           ' --refmyelinmaps={refmyelinmaps}' \
           ' --regname={regname}' \
           ' --reference2mm={t1template2mm}' \
           ' --reference2mmmask={template2mmmask}' \
           ' --config={fnirtconfig}' \
           ' --printcom={printcom}'

    def __init__(self, config):
        super(__class__, self).__init__(config)

    @property
    def args(self):
        return self.spec.format(**self.kwargs)


class FMRIVolume(Stage):

    script = '{HCPPIPEDIR}/fMRIVolume/GenericfMRIVolumeProcessingPipeline.sh'

    spec = ' --path={path}' \
           ' --subject={subject}' \
           ' --fmriname={fmriname}' \
           ' --fmritcs={fmritcs}' \
           ' --fmriscout={fmriscout}' \
           ' --SEPhaseNeg={sephaseneg}' \
           ' --SEPhasePos={sephasepos}' \
           ' --fmapmag={fmapmag}' \
           ' --fmapphase={fmapphase}' \
           ' --fmapgeneralelectric={fmapgeneralelectric}' \
           ' --echospacing={echospacing}' \
           ' --echodiff={echodiff}' \
           ' --unwarpdir={seunwarpdir}' \
           ' --fmrires={fmrires}' \
           ' --dcmethod={dcmethod}' \
           ' --gdcoeffs={gdcoeffs}' \
           ' --topupconfig={topupconfig}' \
           ' --printcom={printcom}' \
           ' --biascorrection={fmribfcmethod}' \
           ' --mctype={mctype}'

    def __init__(self, config):
        super(__class__, self).__init__(config)

    def __str__(self):
        string = ''
        for cmd in self.cmdline():
            string += ' \\\n    '.join(cmd.split()) +'\n'
        return string

    def _get_intended_sefmaps(self):
        """
        search for intendedFor field from sidecar json to determine
        appropriate field map pair, else give the first spin echo pair.
        :return: pair of spin echo filenames, positive then negative
        """
        if '-' in self.kwargs['seunwarpdir']:
            parallel = 'negative'
        else:
            parallel = 'positive'

        for idx, sefm in enumerate(self.config.get_bids('fmap_metadata',
                                                     parallel)):
            intended_targets = sefm.get('intendedFor', [])
            if get_relpath(self.kwargs['fmritcs']) in ' '.join(
                    intended_targets):
                intended_idx = idx
                break
        else:
            intended_idx = 0

        return self.config.get_bids('fmap', 'positive', intended_idx), \
            self.config.get_bids('fmap', 'negative', intended_idx)

    @property
    def args(self):
        for fmri in self.config.get_bids('func'):
            self.kwargs['fmritcs'] = fmri
            self.kwargs['fmriname'] = get_fmriname(fmri)
            self.kwargs['fmriscout'] = None  # not implemented
            if self.kwargs['dcmethod'] == 'TOPUP':
                self.kwargs['sephasepos'], self.kwargs['sephaseneg'] = \
                    self._get_intended_sefmaps()
            yield self.spec.format(**self.kwargs)

    def cmdline(self):
        script = self.script.format(**os.environ)
        for argset in self.args:
            yield ' '.join((script, argset))


class FMRISurface(Stage):

    script = '{HCPPIPEDIR}/fMRISurface/GenericfMRISurfaceProcessingPipeline.sh'

    spec = ' --path={path}' \
           ' --subject={subject}' \
           ' --fmriname={fmriname}' \
           ' --lowresmesh={lowresmesh}' \
           ' --fmrires={fmrires}' \
           ' --smoothingFWHM={smoothingFWHM}' \
           ' --grayordinateres={grayordinateres}' \
           ' --regname={regname}'

    def __init__(self, config):
        super(__class__, self).__init__(config)

    def __str__(self):
        string = ''
        for cmd in self.cmdline():
            string += ' \\\n    '.join(cmd.split()) + '\n'
        return string

    @property
    def args(self):
        for fmri in self.config.get_bids('func'):
            self.kwargs['fmriname'] = get_fmriname(fmri)
            yield self.spec.format(**self.kwargs)

    def cmdline(self):
        script = self.script.format(**os.environ)
        for argset in self.args:
            yield ' '.join((script, argset))
