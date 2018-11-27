# dcan bids fmri-pipeline

This software takes a bids folder as input and determines parameters
for the dcan lab's modified hcp pipeline, calling upon the proper code
to run the subject(s).

### Installation

#### Using Docker

Until we release the image officially on docker hub, we will provide you with 
a tar.gz docker image upon request. you will need to load the image onto your 
docker service before continuing.  Run the following command using the image:

```{bash}
docker load < dcan-pipelines.tar.gz
```

It is common to receive a "no space left on device" error during this build 
process. You man need to clean up any old/dangling images and containers from 
the docker registry, and possibly increase the amount of space allotted to 
docker.

#### Using Singularity

Until we release the image officially on docker hub, we will provide you with
a .img singularity image.  No installation is necessary, this image will be 
provided directly to the singularity service whenever executing the pipeline.

#### Without Using Docker (Native)

If you wish to use this package without docker, you will need to meet the 
current version requirements of each software package contained in the 
version of the dcan pipeline code which you are using.  Note that the version 
of this software is independent of the version of pipeline code, but should be 
compatible with pipeline-code version 2.0 and onward.


```{bash}
# clone the repository
# SSH:
git clone git@gitlab.com:Fair_lab/bidsapp.git
# HTTPS:
git clone https://gitlab.com/Fair_lab/bidsapp.git

# change directory into the repository's folder
cd bidsapp

# install the requirements from within the cloned repository for the user
pip3 install --user -r requirements.txt
```

You will then need to modify the "SetupEnv.sh" file and set the system paths 
to any software dependencies within.

### Usage:

Using the image will require bids formatted input data. Consult 
http://bids.neuroimaging.io/ for more information and for tools which assist 
with converting data into bids format.

These are the basic command invocations.  Options are detailed in the usage
below.

To call using docker:

```{bash}
docker run --rm \
    -v /path/to/bids_dataset:/bids_input:ro \
    -v /path/to/outputs:/output \
    dcan-pipelines /bids_input /output [OPTIONS]
```

To call using singularity:

```{bash}
singularity exec \
    -B /path/to/bids_dataset:/bids_input \
    -B /path/to/outputs:/output \
    ./dcan-pipelines.img /bids_input /output [OPTIONS]
```

To call a native installation:

```{bash}
source ./SetupEnv.sh
./run.py /bids_input /output [OPTIONS]
```

Options:

```{bash}
usage: dcan-pipelines [-h] [--version] [--participant-label ID [ID ...]]
                      [--all-sessions] [--ncpus NCPUS] [--stage STAGE]
                      [--bandstop LOWER UPPER] [--custom-clean JSON]
                      [--abcd-task] [--study-template HEAD BRAIN]
                      [--check-outputs-only] [--print-commands-only]
                      [--ignore-expected-outputs]
                      bids_dir output_dir

The Developmental Cognition and Neuroimaging (DCAN) lab fMRI Pipeline [1].
This BIDS application initiates a functional MRI processing pipeline built
upon the Human Connectome Project's minimal processing pipelines [2].  The
application requires only a dataset conformed to the BIDS specification, and
little-to-no additional configuration on the part of the user. BIDS format
and applications are explained in detail at http://bids.neuroimaging.io/

positional arguments:
  bids_dir              path to the input bids dataset root directory. Read
                        more about bids format in the link in the description.
                        It is recommended to use the dcan bids gui or dcm2bids
                        to convert from participant dicoms to bids.
  output_dir            path to the output directory for all intermediate and
                        output files from the pipeline, also path in which
                        logs are stored.

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --participant-label ID [ID ...]
                        optional list of participant ids to run. Default is
                        all ids found under the bids input directory. A
                        participant label does not include "sub-"
  --all-sessions        collapses all sessions into one when running a
                        subject.
  --ncpus NCPUS         number of cores to use for concurrent processing and
                        algorithmic speedups. Warning: causes ANTs and
                        FreeSurfer to produce non-deterministic results.
  --stage STAGE         begin from a given stage, continuing through. Options:
                        PreFreeSurfer, FreeSurfer, PostFreeSurfer, FMRIVolume,
                        FMRISurface, DCANBOLDProcessing, ExecutiveSummary,
                        CustomClean
  --bandstop LOWER UPPER
                        parameters for motion regressor band-stop filter. It
                        is recommended for the boundaries to match the inter-
                        quartile range for participant group respiratory rate
                        (bpm), or to match bids physio data directly [3].
                        These parameters are highly recommended for data
                        acquired with a frequency of approx. 1 Hz or more
                        (TR<=1.0). Default is no filter

special pipeline options:
  options which pertain to an alternative pipeline or an extra stage which is not
   inferred from the bids data.

  --custom-clean JSON   runs dcan cleaning script after the pipeline
                        completessuccessfully to delete pipeline outputs based
                        on the file structure specified in the custom-clean
                        json.
  --abcd-task           runs abcd task data through task fmri analysis, adding
                        this stage to the end. Warning: Not written for
                        general use: a general task analysis module will be
                        included in a future release.
  --study-template HEAD BRAIN
                        template head and brain images for intermediate
                        nonlinear registration, effective where population
                        differs greatly from average adult, e.g. in elderly
                        populations with large ventricles.

runtime options:
  special changes to runtime behaviors. Debugging features.

  --check-outputs-only  checks for the existence of outputs for each stage
                        then exit. Useful for debugging.
  --print-commands-only
                        print run commands for each stage to shell then exit.
  --ignore-expected-outputs
                        continues pipeline even if some expected outputs are
                        missing.

References
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
```

#### Example

Running a subject with a bandstop filter and study-templates

first, ensure that you have constructed a bids\_input folder which conforms to 
bids specifications.  You may use 
[dcm2bids](https://github.com/cbedetti/Dcm2Bids) for this purpose.

for study templates, we will mount an additional path into the docker 
container which contains these extra files: study\_head.nii.gz, and 
study\_brain.nii.gz


```{bash}
docker run --rm \
    -v  /path/to/bids_dataset:/bids_input:ro \
    -v /path/to/outputs:/output \
    -v /path/to/template/folder:/atlases
    dcan-pipelines /bids_input /output \
        --bandstop 18.582 25.726 
        --study-template /atlases/study_head.nii.gz /atlases/study_brain.nii.gz
```

note that the mount flag "-v" follows "docker run", as it is a docker option, 
whereas the "--bandstop" and "--study-template" flags follow "dcan-pipelines", 
as they are options passed into this program.


### Additional Information:

#### Outputs

The outputs are organized in the following structure:

output_dir/sub-id/ses-session/
- files/
- logs/

##### files

- T1w:  contains native space anatomical data as well as intermediate 
preprocessing files. 
- T1w/participantID: The participant ID folder within T1w is the FreeSurfer 
subject folder. 
- MNINonLinear: contains the final space results of anatomy in 164k 
resolution. 
- MNINonLinear/Results: final space functional data.
- MNINonLinear/fsaverage_32K: final space anatomy in 32k resolution, where 
functional data is ultimately projected.
- task-taskname: these folders contain intermediate functional preprocessing 
files.
- executive_summary: the .html file within can be opened for quality 
inspection of pipeline results.

##### logs

logs contains the log files for each stage. In the case of an error, consult 
these files *in addition to* the standard err/out of the app itself (by 
default this is printed to the command line).

status.json codes:

- unchecked: 999
- succeeded: 1
- incomplete: 2
- failed: 3
- not_started: 4


#### Rerunning

The --stage option exists so you can restart the pipeline in the case that 
it terminated prematurely

#### Special Pipelines

The special pipeline options are designed for use with specific data sets. 

If you are using an elderly or neurodegenerative population, adding a 
"study template" tends to improve results. This is generally constructed 
using ANTs to build an average template of your subjects. This template is 
then used as an intermediate warp stage, assisting in nonlinear registration 
of subjects with large ventricles.

It should be noted that "abcd-task" is not compatible with a bids folder 
structure, and an actual task module will be added in a future version which 
will allow bids formatted task data to be processed automatically.

#### Misc.

The pipeline may take over 24 hours if run on a single core.  It is 
recommended to use at least 4 cores and allow for at least 12GB of memory to 
be safe.  Most fMRI processing can be done in parallel, so using a number of 
cores which divides your number of fMRI runs is optimal.

Temporary/Scratch space:  By default, everything is processed in the 
output folder. We will work on a more efficient use of disk space in the 
future, along with the ability to use a temporary file system mount for
hot read/writes.

software will resolve to using spin echo field maps if they are present, 
then gradient field maps, then None, consistent with best observed
performances. Note that there are no errors or warnings if multiple 
modalities are present.

For specified use of spin echo field maps, i.e. mapping a pair to each
individual functional run, it is necessary to insert the "IntendedFor"
field into the bids input sidecar jsons, which specifies a functional
run for each field map.  This field is explained in greater detail
within the bids specification.

In the case of multiband (fast TR) data, it is recommended to employ a
band-stop filter to mitigate artifactually high motion numbers.  The
band-stop filter used on motion regressors prior to frame-wise
displacement calculation has parameters which must be chosen based on
subject respiratory rate.

#### Some current limitations

diffusion field maps are still a work in progress, as this data differs
significantly between scanner make/model. We will happily add new formats 
to the pipeline, so please post an issue if you run into fieldmap trouble.

DTI processing is to be included in a future release. Demand for this 
feature would speed up its release.

The ideal motion filtering parameters have not been robustly tested
across repetition times or populations outside of adolescents.
Additionally, automatic reading of physio data from bids format has not
yet been implemented, so the proper range should be decided upon carefully.
Consult [3] in the usage for more information.

software does not currently support dynamic acquisition parameters for
a single modality (e.g. different phase encoding direction for 2 fmri).
Other parameters would have to be processed by creating separate bids
datasets for sessions with varied fmri parameters.

