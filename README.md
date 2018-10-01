# dcan bids fmri-pipeline

This software takes a bids folder as input and determines parameters
for the dcan lab's modified hcp pipeline, calling upon the proper code
to run the subject(s).

#### Installation

```{bash}
# clone the repository
# SSH:
git clone git@gitlab.com:Fair_lab/bidsapp.git
# HTTPS:
git clone https://gitlab.com/Fair_lab/bidsapp.git

# change directory into the repository's folder
cd bidsapp

# install the requirements from within the cloned repository
pip3 install --user -r requirements.txt
```

#### Usage:

To Call:

```{bash}
docker run --rm \
    -v /path/to/bids_dataset:/bids_input:ro \
    -v /path/to/outputs:/output \
    dcan/fmri-pipeline /bids_input /output [OPTIONS]
```

Usage:

```{bash}
run.py <bids_dir> <output_dir> [OPTIONS]

positional arguments:
  bids_dir              path to the input bids dataset root directory. Read
                        more about bids format in the link above. It is
                        recommended to use the dcan bids gui or dcm2bids to
                        convert from participant dicoms.
  output_dir            path to the output directory for all intermediate and
                        output files from the pipeline, also path in which
                        logs are stored.

optional arguments:
  -h, --help            show this help message and exit
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
                        FMRISurface, DCANBOLDProcessing, ExecutiveSummary
  --bandstop LOWER UPPER
                        parameters for motion regressor band-stop filter. It
                        is recommended for the boundaries to match the inter-
                        quartile range for participant group heart rate (bpm),
                        or to match bids physio data directly. These
                        parameters are only recommended for data acquired with
                        a frequency of approx. 1 Hz or more. Default is no
                        filter
  --check-only          checks for the existence of outputs for each stage.
                        Useful for debugging.
  --abcd-task           runs abcd task data through task fmri analysis, adding
                        this stage to the end
```

#### Additional Configuration:

Temporary/Scratch space:  If you need to make use of a particular mount
for fast file io, you can provide the docker command with an additional
volume mount: `docker run -v /my/fast/file/mnt:/tmp` on most systems, 
you can add an argument to docker: `docker run --tmpfs /tmp`

software will use spin echo field maps if they are present, then
gradient field maps, then None, consistent with best observed
performances.

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

#### Some current limitations:

diffusion field maps are still a work in progress, as this data differs
significantly between scanner makes. We will happily add new formats to 
the pipeline, so please post an issue if you run into fieldmap trouble.

The ideal motion filtering parameters have not been robustly tested
across repetition times or populations outside of adolescents.
Additionally, automatic reading of physio data from bids format has not
yet been implemented.

software does not currently support dynamic acquisition parameters for
a single modality (e.g. different phase encoding direction for 2 fmri).
Other parameters would have to be processed by creating separate bids
datasets for sessions with varied fmri parameters.

