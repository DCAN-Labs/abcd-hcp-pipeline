# dcan bids fmri-pipeline

This software takes a bids folder as input and determines parameters
for the dcan lab's modified hcp pipeline, calling upon the proper code to run the
subject(s).

To Call:

```{bash}
docker run --rm \
    -v /path/to/bids_dataset:/bids_input:ro \
    -v /path/to/outputs:/output \
    dcan/fmri-pipeline /bids_input /output [OPTIONS]
```

Usage:

```{bash}
usage: run.py [-h] [--participant-label ID [ID ...]] [--all-sessions]
              [--ncpus NCPUS] [--stage STAGE]
              bids_input output

The Developmental Cognition and Neuroimaging (DCAN) lab fMRI Pipeline. This
BIDS application initiates a functional MRI processing pipeline built upon the
Human Connectome Project's own minimal processing pipelines. The application
requires only a dataset conformed to the BIDS specification, and little-to-no
additional configuration on the part of the user. BIDS format and applications
are explained in more detail at http://bids.neuroimaging.io/

positional arguments:
  bids_input            path to the input bids dataset root directory. Read
                        more about bids format in the link above. It is
                        recommended to use the dcan bids gui or dcm2bids
                        to convert from participant dicoms.
  output                path to the output directory for all intermediate and
                        output files from the pipeline.

optional arguments:
  -h, --help            show this help message and exit
  --participant-label ID [ID ...]
                        optional list of participant ids to run. Default is
                        all ids found under the bids input directory.
  --all-sessions        collapses all sessions into one when running a
                        subject.
  --ncpus NCPUS         number of cores to use for concurrent processing of
                        functional runs.
  --stage STAGE         begin from a given stage. Options: PreFreeSurfer,
                        FreeSurfer, PostFreeSurfer, FMRIVolume, FMRISurface,
                        DCANSignalPreprocessing, ExecutiveSummary
```

#### Additional Configuration:

software will use spin echo field maps if they are present, then
gradient field maps, then None, consistent with best observed
 performances.

For complex use of spin echo field maps, i.e. mapping a pair to each
individual functional run, it is necessary to insert the "intendedFor"
field into the bids input sidecar jsons, which specifies a functional
run for each field map.  This field is explained in greater detail
within the bids specification.

#### Some current limitations:

The default bandpass filter utilized (only for multiband/fast TR data)
in the final preprocessing stage has been set to match a reasonable
respiration rate range for young adults (10-20 yrs).  The potential
effects on older populations are not well tested, and you may need
to specify a different notch filter range for a significantly different
age group.

software does not currently support dynamic acquisition parameters for
a single modality (e.g. different phase encoding direction for 2 fmri).
Otherparameters may only be tested by creating separate bids input
datasets.

user must ensure that PhaseEncodingDirection is properly set in both
spin echo field map and functional data, as dcm2bids does not always
get this right.
