# Usage

The Developmental Cognition and Neuroimaging (DCAN) Labs fMRI Pipeline [1].
This BIDS application initiates a functional MRI processing pipeline built
upon the Human Connectome Project's minimal processing pipelines [2].  The
application requires only a dataset conformed to the BIDS specification, and
little-to-no additional configuration on the part of the user. BIDS format
and applications are explained in detail at http://bids.neuroimaging.io/

## Options

    positional arguments:
        bids_dir              Path to the input BIDS dataset root directory. Read
                              more about the BIDS standard in the link in the
                              description. It is recommended to use Dcm2Bids to
                              convert from participant dicoms into BIDS format.
  
        output_dir            Path to the output directory for all intermediate and
                              output files from the pipeline, which is also where
                              logs are stored.

    optional arguments:
        -h, --help            show this help message and exit
        --version, -v         show program's version number and exit
        --participant-label ID [ID ...]
                              Optional list of participant IDs to run. Default is
                              all IDs found under the BIDS input directory. The
                              participant label does not include the "sub-" prefix
  
    --session-id SESSION_ID [SESSION_ID ...]
                              filter input dataset by session id. Default is all ids
                              found under the subject input directory(s). A session
                              id does not include "ses-"
 
    --freesurfer-license LICENSE_FILE
                              If using docker or singularity, you will need to
                              acquire and provide your own FreeSurfer license. The
                              license can be acquired by filling out this form:
                              https://surfer.nmr.mgh.harvard.edu/registration.html
 
    --all-sessions            Collapses all sessions into one when running a
                              subject.
 
    --ncpus NCPUS             Number of cores to use for concurrent processing and
                              algorithmic speedups. Warning: causes ANTs and
                              FreeSurfer to produce non-deterministic results.

    --stage STAGE             Specify a subset of stages to run.
                              Can be used to rerun some or all of the pipeline after
                              completing once, or resume an incomplete runthrough.
                              If a single stage name is given, the pipeline with be 
                              started at that stage. If a string with a ":" is given, 
                              a stage name before the ":" will tell the pipeline where to 
                              start and a stage name after the ":" will tell it where 
                              to stop. If no ":" is found, the pipeline will start 
                              with the stage specified and run through 
                              ExecutiveSummary (or CustomClean/ABCDTask, if specified).
                              Valid stage names: 
                              PreFreeSurfer, FreeSurfer, PostFreeSurfer, FMRIVolume, 
                              FMRISurface, DCANBOLDProcessing, ExecutiveSummary, CustomClean'
    --bandstop LOWER UPPER
                              Parameters for motion regressor band-stop filter [3]. It
                              is recommended for the boundaries to match the inter-
                              quartile range for participant group respiratory rate
                              (breaths per minute), or to match BIDS physio data
                              directly [3]. These parameters are highly recommended
                              for data acquired with a frequency of greater than 1
                              Hz (TR less than 1 second). UPPER cannot exceed the
                              Nyquist folding frequency in bpm ( 0.5 * (60 / TR) ). 
                              Default is no filter.
                        
    --abcd-task               (DEPRECATED. For task analysis of this pipeline's output,
                              refer to DCAN abcd-tfmri-pipeline at
                              https://github.com/DCAN-Labs/abcd-bids-tfmri-pipeline)
                              Runs ABCD task data through task fMRI analysis, adding
                              this stage to the end. 

    --custom-clean JSON       Runs DCAN cleaning script after the pipeline
                              completes successfully to delete pipeline outputs 
                              base on the file structure specified in the custom-
                              clean JSON. Required for the custom clean stage.

    --study-template HEAD BRAIN
                              Template head and brain images for intermediate
                              nonlinear registration and masking, effective where
                              population differs greatly from average adult, e.g. in
                              elderly populations with large ventricles.
  
    --ignore {func,dwi}       Ignore a modality in processing. Option can be
                              repeated. (--ignore dwi is DEPRECATED.)
    --dcmethod {TOPUP,FIELDMAP,NONE}
                              Specify fieldmap-based distortion correction method.
                              Default: auto-detection based on contents of fmap dir

    Runtime options:
      Special changes to runtime behaviors. Debugging features.

    --check-outputs-only      Checks for the existence of outputs for each stage
                              then exit. Useful for debugging.
    --print-commands-only
                              Print run commands for each stage to shell then exit.
    --ignore-expected-outputs
                              Continues pipeline even if some expected outputs are
                              missing. Note that optional outputs, e.g. intermediate files
                              from T2w preprocessing, are not included in the 
                              "expected output". Refer to the included 
                              /app/pipeline_expected_outputs.json for the list
                              of expected outputs per stage.
    References
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


## Example: minimal run command (Docker)

To call using Docker:

    docker run --rm \
        -v /path/to/bids_dataset:/bids_input:ro \
        -v /path/to/outputs:/output \
        -v /path/to/freesurfer/license.txt:/opt/freesurfer/license.txt \
        dcanumn/abcd-hcp-pipeline /bids_input /output --freesurfer-license=/opt/freesurfer/license.txt [OPTIONS]

Note that the mount flag `-v` follows `docker run`, as it is a Docker options whereas `--freesurfer-license` follows `dcanumn/abcd-hcp-pipeline`, as it is an option passed into the pipeline itself.

If you are experiencing file system permission issues on outputs, setting the `--user` flag to `"$(id -u):$(id -g)"` for the docker run command may help.

## Example: minimal run command (Singularity)

To call using Singularity:

    env -i singularity run \   
        -B /path/to/bids_dataset:/bids_input \
        -B /path/to/outputs:/output \
        -B /path/to/freesurfer/license.txt:/opt/freesurfer/licenses.txt \
        ./abcd-hcp-pipeline.sif /bids_input /output --freesurfer-license=/opt/freesurfer/license.txt [OPTIONS]

Note that the license is now mounted directly into the freesurfer folder, and the call to singularity is prefaced by "env -i"

## Advanced Example: run with bandstop filter, study-templates, multiple CPUs

In the case of multiband (fast TR) data, it is recommended to employ a band-stop filder to mitigate artifactually high motion numbers. The band-stop filter used on motion regressors prior to frame-wise displacement calculation has parameters which should be chosen based on subject respiratory rate.

In the example command below we specify a bandstop filter, in breaths per minute (bpm), to be applied in the DCAN BOLD Processing stage. (See reference [3] above for information on bandstop filtering of respiratory motion artifacts in fMRI.) The interval `18.582 25.726` is the interquartile range (25th to 75th percentile) of the subject demographic. Respiratory rate data may be included in the BIDS dataset, or can be estimated post hoc by utilities such as [DCAN movement_regressors_power_plots](https://github.com/DCAN-Labs/movement_regressors_power_plots).

Additionally, we specify study template head and brain images which are used as an intermediate registration target when registering the subject's T1w to the standard space template. For these study templates we will mount an additional path into the Docker container `-v /path/to/template/folder:/atlases`, containing the files `study_head.nii.gz` and `study_brain.nii.gz`. Then, we add these templates in as the study template head and brain `--study-template /atlases/study_head.nii.gz /atlases/study_brain.nii.gz` using the path as mounted into the Docker container `/atlases`.

We have also requested 4 cores for faster processing: `--ncpus 4`

    docker run --rm \
        -v  /path/to/bids_dataset:/bids_input:ro \
        -v /path/to/outputs:/output \
        -v /path/to/freesurfer/LICENSE:/license:ro \
        -v /path/to/template/folder:/atlases \
        dcanumn/abcd-hcp-pipeline /bids_input /output \
            --freesurfer-license /license \
            --bandstop 18.582 25.726 \
            --study-template /atlases/study_head.nii.gz /atlases/study_brain.nii.gz \
            --ncpus 4

## Pipeline options for specific datasets

`--study-template`: For elderly or neurodegenerative populations, using a "study template" tends to improve registration of subject anatomical volumes to atlas. This template is generally constructed using ANTs to build an average of your subjects. It is then used as an intermediate warp stage to assist in nonlinear registration to atlas.

`--abcd-task` is not compatible with a BIDS folder structure, e.g. [DCAN file-mapper](https://github.com/DCAN-Labs/file-mapper) should **not** be used to map the pipeline output into a BIDS derivative if this option is to be used. **Note**: this tag is now deprecated and [DCAN abcd-tfmri-pipeline](https://github.com/DCAN-Labs/abcd-bids-tfmri-pipeline) is now our recommended tool for task analysis of this pipeline's output. 

##  About BIDS datasets for input

This pipeline requires input be a [BIDS-formatted MRI dataset](https://bids-specification.readthedocs.io/en/stable/). Additionally, any functional data **must** be in a subdirectory of a BIDS session directory (e.g. a dataset with `sub-A/ses-01/func` is supported, but `sub-A/func` is not). 

### Example BIDS dataset (with "PEpolar" spin-echo fieldmaps; for more info see section below ):

```
└─ BIDS_input/ 
  ├─ dataset_description.json
  ├─ README
  ├─ CHANGES
  ├─ participants.tsv
  ├─ task-<TASKNAME>_bold.json
  └─ sub-<SUBID>/
    └─ ses-<SESID>/
      └─ anat/
         ├─ sub-<SUBID>_ses-<SESID>[_run-01]_T1w.json
         └─ sub-<SUBID>_ses-<SESID>[_run-01]_T1w.nii.gz
         ├─ sub-<SUBID>_ses-<SESID>[_run-01]_T2w.json
         └─ sub-<SUBID>_ses-<SESID>[_run-01]_T2w.nii.gz
      └─ fmap/
         ├─ sub-SUBID_ses-<SESID>_dir-AP[_run-01]_epi.json
         ├─ sub-SUBID_ses-<SESID>_dir-AP[_run-01]_epi.nii.gz
         ├─ sub-SUBID_ses-<SESID>_dir-PA[_run-01]_epi.json
         └─ sub-SUBID_ses-<SESID>_dir-PA[_run-01]_epi.nii.gz
      └─ func/
         ├─ sub-<SUBID>_ses-<SESID>_task-<TASKNAME>_run-01_bold.json
         ├─ sub-<SUBID>_ses-<SESID>_task-<TASKNAME>_run-01_bold.nii.gz
         ├─ sub-<SUBID>_ses-<SESID>_task-<TASKNAME>_run-02_bold.json
         └─ sub-<SUBID>_ses-<SESID>_task-<TASKNAME>_run-02_bold.nii.gz
```

Also be aware that the pipeline only recognizes a subset of the BIDS entities, modalities and suffixes in the specification for MRI and modality-agnostic files. Unsupported input may result in errors or other unexpected behavior. 

Recognized entities, modalities and suffixes include the following:

general: `sub-`,`ses-`

in `anat` directory: `_T1w`, `_T2w`

in `fmap` directory: `dir-_`, `_epi`

in `func` directory: `task-`, `run-`, `_bold`

**Not** recognized:

`echo-`, `acq-`, `desc-`, `ce-`, `_dwi`, others...

Consult [the BIDS site](https://bids.neuroimaging.io/) for more information and for tools which assist with converting data into BIDS format. Our favorite is [Dcm2Bids](https://github.com/UNFmontreal/Dcm2Bids)

## Fieldmap support for FSL topup / distortion correction

For distortion correction of anatomical and functional data using [FSL topup](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup), the input `fmap` directory must contain either: 

- "PEpolar" spin-echo fieldmap images as specified [here](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#fieldmap-data); if present, topup correction is enabled by default.
- The "Two phase maps and two magnitude images" fieldmap scheme as specified [here](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/magnetic-resonance-imaging-data.html#case-2-two-phase-maps-and-two-magnitude-images) ; if present, gradient echo distortion correction is enabled by default (unless topup correction is enabled). 

The spatial dimensions and voxel size of the fieldmaps must be the same as the corresponding runs in the subject's `func` directory, as resampling is not implemented. 

To specify the mapping between spin-echo fieldmap runs and the functional runs to be distortion-corrected, include an `IntendedFor` key/value pair in the BIDS sidecar JSON of the fieldmap run. For details, see the relevant section of the [BIDS specification](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#using-intendedfor-metadata). 

This software will resolve to using spin-echo fieldmaps if they are present, then gradient echo fieldmaps, then None, consistent with best observed performances.

## Functional runs with different acquisition parameters 

To avoid errors, acquisition parameters (e.g. voxel dimensions, TR, phase encoding direction) should be identical across functional runs within a BIDS session. (The number of frames does not need to be the same for all runs.) 

We recommend that sets of runs with differing acquisition parameters be processed as separate BIDS sessions. Also be aware the pipeline does not recognize BIDS entities such as `acq-` and `desc-` so those should not be used to differentiate runs with different acquisition parameters. 
