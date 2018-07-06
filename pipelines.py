import inspect
import os
import subprocess


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
    # Atlas Myelin Maps for surface registration
    referencemyelinmaps = "{HCPPIPEDIR_Templates}/standard_mesh_atlases/" \
                          "Conte69.MyelinMap_BC.164k_fs_LR.dscalar.nii"

    # @ various settings @ #
    # fov size for robust_fov automatic cropping
    brainsize = 150
    # final time series isotropic resolution (mm)
    fmrires = 2.0
    # resolution of greyordinates (mm)
    greyordinatesres = 2.0
    # smoothing sigma for final greyordinate data (mm)
    smoothingFWHM = 2.0
    # surface registration algorithm, one of: FS, MSMSulc
    regname = "FS"
    # number of vertices (in thousands) for high and low res surface meshes
    highresmesh = "164"
    lowresmesh = "32"

    # @ configuration files @ #
    topupconfig = "{HCPPIPEDIR_Config}/b02b0.cnf"
    fnirtconfig = "{HCPPIPEDIR_Config}/T1_2_MNI152_2mm.cnf"
    freesurferlabels = "{HCPPIPEDIR_Config}/FreeSurferAllLut.txt"
    subcorticalgraylabels = "{HCPPIPEDIR_Config}/FreeSurferSubcortical" \
                            "LabelTableLut.txt"

    def __init__(self, bids_data, output_directory):
        """
        Configuration to run HCP Pipeline on a single subject session.
        :param bids_data: yielded spec from read_bids_dataset
        :param output_directory: output directory for pipeline
        """

        # input bids data struct
        self.bids_data = bids_data

        # environment script to be sourced prior to configuration
        os.environ['HCPPIPEDIR'] = '/opt/pipeline'
        self.environment_script = os.path.join('/opt/pipeline', 'setup_env.sh')

        # @  dynamic parameters read from bids @ #
        self.t1w = bids_data['t1w']
        self.t1samplespacing = self.bids_data['t1w_metadata']['DwellTime']
        if self.bids_data['t2w']:
            self.t2w = bids_data['t2w']
            self.t2samplespacing = self.bids_data['t2w_metadata']['DwellTime']

        # distortion correction method: TOPUP, FIELDMAP, or NONE, inferred
        # from files, defaults to spin echo (topup) if both field maps exist
        if 'epi' in self.bids_data['types']:
            self.dcmethod = 'TOPUP'
            # spin echo field map spacing @TODO read during volume per fmap?
            self.echospacing = self.bids_data['fmap_metadata']['positive'][0][
                'EffectiveEchoSpacing']
            # distortion correction phase encoding direction
            self.unwarpdir = self.bids_data['func_metadata'][
                'PhaseEncodingDirection']
            # @TODO decide on bfcmethod for fmri data.
            # self.

        elif 'magnitude' in self.bids_data['types']:
            self.dcmethod = 'FIELDMAP'
            # gradient field map delta TE
            self.echodiff = None  # @TODO
            self.unwarpdir = None

        else:
            self.dcmethod = 'NONE'

        # @ input files @ #
        self.logs = os.path.join(output_directory, 'hcponeclick')
        self.subject = self.bids_data['subject']
        self.path = output_directory

    def _params(self):
        params = inspect.getmembers(self, lambda a: not inspect.isroutine(a))
        params = [x for x in params if not x[0].startswith('_')]
        return params

    def _format(self):
        # source environment script
        if self.environment_script:
            cmd = ['bash', '-c', 'source']
            cmd += [self.environment_script]
            subprocess.call(cmd)

        params = self._params()

        # format all attributes
        for item, value in params:
            if isinstance(value, str):
                setattr(self, item, value.format(os.environ))

    def get_params(self):
        self._format()
        return self._params()


class Stage(object):

    def __init__(self, config):
        self.config = config
        self.formatter = config.get_params()

    def __str__(self):
        string = self.cmdline.split().join(' \\\n    ')
        return string

    @property
    def args(self):
        raise NotImplementedError

    @property
    def script(self):
        raise NotImplementedError

    def cmdline(self):
        return ' '.join((self.script, self.args))

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
           ' --topupconfig={topupconfig}'

    def __init__(self, config):
        super(__class__, self).__init__(config)
        # modify t1/t2 inputs for spec
        self.formatter['t1w'] = '@'.join(self.formatter.get('t1w'))
        self.formatter['t2w'] = '@'.join(self.formatter.get('t2w', []))

    @property
    def args(self):
        return self.spec.format(self.formatter)


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

    @property
    def args(self):
        return self.spec.format(self.formatter)


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
           ' --reference2mm={reference2mm}' \
           ' --reference2mmmask={reference2mmmask}' \
           ' --config={fnirtconfig}' \
           ' --printcom={printcom}'

    def __init__(self, config):
        super(__class__, self).__init__(config)

    @property
    def args(self):
        return self.spec.format(self.formatter)


class FMRIVolume(Stage):

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
           ' --unwarpdir={unwarpdir}' \
           ' --fmrires={fmrires}' \
           ' --dcmethod={dcmethod}' \
           ' --gdcoeffs={gdcoeffs}' \
           ' --topupconfig={topupconfig}' \
           ' --printcom={printcom}' \
           ' --biascorrection={fmribfcmethod}' \
           ' --mctype={mctype}'

    def __init__(self, config):
        super(__class__, self).__init__(config)

    @property
    def args(self):
        return self.spec.format(self.formatter)


class FMRISurface(Stage):

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

    @property
    def args(self):
        return self.spec.format(self.formatter)
