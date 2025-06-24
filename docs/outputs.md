# Pipeline Outputs

## Derivatives

Pipeline outputs are mapped into BIDS-compliant derivatives via Filemapper with the following directory structure. A detailed explanation of each file type is provided in the sections below - see `anat/` and `func/` sections. The `<label>` and `<TASK>` placeholders are replaced with the subject ID, session ID, and task name respectively (e.g. `task-rest`). The `<T1w|T2w>` placeholder is replaced with the type of anatomical image (T1-weighted or T2-weighted). 

The `<ATLAS>` placeholder is replaced with the name of the atlas used for functional data for extraction of parcellated timeseries, including Evan Gordon’s 333 ROI AT (Gordon et al., 2014), HCP’s 360 ROI AT (Glasser et al., 2016), Jonathan Power’s 264 ROI AT (Power et al., 2011), and Thomas Yeo’s 118 ROI AT (Yeo et al., 2011). All parcellations additionally include 19 individualized subcortical parcellations. 

 - **Values for `<ATLAS>` include:** 
    - `Gordon2014FreeSurferSubcortical` 
    - `HCP2016FreeSurferSubcortical` 
    - `Markov2012FreeSurferSubcortical`
    - `Power2011FreeSurferSubcortical` 
    - `Yeo2011FreeSurferSubcortical` 


```default
derivatives/ 
|__ abcd-hcp-pipeline_v0.1.4/
    |__ sub-<label>/
        |__ ses-<label>/
            |__ anat/
            |   |__ SUBSES_<T1w|T2w>_space-MNI_brain.nii.gz
            |   |__ SUBSES_T1w_space-MNI_desc-wmparc_dseg.nii.gz
            |   |__ SUBSES_atlas-MNI_space-fsLR32k_desc-smoothed_myelinmap.dscalar.nii
            |   |__ SUBSES_atlas-MNI_space-fsLR32k_myelinmap.dscalar.nii
            |   |__ SUBSES_hemi-<L|R>_space-MNI_mesh-fsLR164k_midthickness.surf.gii
            |   |__ SUBSES_hemi-<L|R>_space-MNI_mesh-fsLR32k_midthickness.surf.gii
            |   |__ SUBSES_hemi-<L|R>_space-MNI_mesh-native_midthickness.surf.gii
            |   |__ SUBSES_hemi-<L|R>_space-T1w_mesh-fsLR32k_midthickness.surf.gii
            |   |__ SUBSES_hemi-<L|R>_space-T1w_mesh-native_midthickness.surf.gii
            |   |__ SUBSES_space-ACPC_dseg.nii.gz
            |   |__ SUBSES_space-fsLR32k_curv.dscalar.nii
            |   |__ SUBSES_space-fsLR32k_sulc.dscalar.nii
            |   |__ SUBSES_space-fsLR32k_sulc.pscalar.nii
            |   |__ SUBSES_space-fsLR32k_thickness.dscalar.nii
            |
            |__ func/
            |   |__ SUBSES_task-<TASK>_bold_atlas-<ATLAS>_desc-filtered_timeseries.ptseries.nii
            |   |__ SUBSES_task-<TASK>_bold_desc-filtered_timeseries.dtseries.nii
            |   |__ SUBSES_task-<TASK>_desc-filtered_motion_mask.mat
            |   |__ SUBSES_task-<TASK>_desc-filteredwithoutliers_motion_mask.mat
            |   |__ SUBSES_task-<TASK>_run-<label>_bold_timeseries.dtseries.nii
            |   |__ SUBSES_task-<TASK>_run-<label>_desc-filtered_motion.tsv
            |   |__ SUBSES_task-<TASK>_run-<label>_desc-filteredincludingFD_motion.tsv
            |   |__ SUBSES_task-<TASK>_run-<label>_desc-includingFD_motion.tsv
            |   |__ SUBSES_task-<TASK>_run-<label>_motion.tsv
            |   |__ SUBSES_task-<TASK>_run-<label>_space-MNI_bold.nii.gz
            |
            |__ img/*
            |__ SUBSES.html
```


### anat/

The derivative files included under the `anat/` directory include the following (`sub-<label>_ses-<label>_` is replaced with an asterisk `*_` for readability):

|                     **Filename**                                                           |       **Description**                                                                                                                 |
| ----------------------------------------------------------------------- | ----------------------------------------------- |
| `*_<T1w|T2w>_space-MNI_<brain|head>.nii.gz`                                            | T1w & T2w brain & head images in MNI space                                                    |
| `*_T1w_space-MNI_desc-wmparc_dseg.nii.gz`                                              | White matter segmentation in MNI space                                                      |
| `*_hemi-<L|R>_space-<MNI|T1w>_mesh-<fsLR32k|fsLR164k|native>_midthickness.surf.gii`    | L/R midthickness in MNI & native space each with 32k, 146k, * native mesh                                   |
| `*_atlas-MNI_space-fsLR32k(_desc-smoothed)_myelinmap.dscalar.nii`                      | Smoothed & unsmoothed myelin map (only if T2w present)                                          |
| `*_space-ACPC_dseg.nii.gz`                                                             | Discrete segmentation (native volume space)                                                              |
| `*_space-fsLR32k_<curv|sulc|thickness>.dscalar.nii`                                    | Dense curvature, sulcal depth, & cortical thickness                                                     |
| `*_space-fsLR32k_sulc.pscalar.nii`                                                     | Parcellated dense subject sulcal depth                                                                           |
              
### func/

The derivative files provided under `func/` including the following (`sub-<label>_ses-<label>_` is replaced with an asterisk `*_` for readability):

|            **Filename**                                                                     |         **Description**                                                                                                                |
| ----------------------------------------------------------------------- | ----------------------------------------------- |                                         
| `*_task-<MID|nback|rest|SST>_bold_desc-filtered_timeseries.dtseries.nii`               | Concatenated functional task dense time series post-DANBOLDProc (regression and filtering) in Atlas space              |
| `*_task-<MID|nback|rest|SST>_bold_atlas-<ATLAS>_desc-filtered_timeseries.ptseries.nii` | Concatenated functional task parcellated time series                     |
| `*_task-<MID|nback|rest|SST>_bold_desc-filtered(withoutliers)_motion_mask.mat`         | "5 contiguous frames" algorithm censoring file of temporal masks by FD threshold (0mm->0.5mm) with or without outliers |
| `*_task-<MID|nback|rest|SST>_run-#_bold_timeseries.dtseries.nii`                       | Individual functional task run dense time series in Atlas space                                                        |
| `*_task-<MID|nback|rest|SST>_run-#_bold_desc-(filtered)includingFD_motion.tsv`         | Movement-artifact-filtered movement numbers with or without FD                                                         |
| `*_task-<MID|nback|rest|SST>_run-#_motion.tsv`                                         | Unfiltered raw movement numbers without FD                                                                             |
| `*_task-<MID|nback|rest|SST>_run-#_space-MNI_bold.nii.gz`                              | Motion-corrected individual functional task run in MNI space in a volume                                               |



#### Motion files

The HDF5 compatible motion .MAT files are a product of the DCANBOLDProcessing stage of the pipeline that should be used for motion censoring. These files use the motion censoring algorithm from [Power et al., 2014](https://www.sciencedirect.com/science/article/pii/S1053811913009117) that excludes periods of data below FD thresholds which are less than five contiguous frames between sequential censored frames. They contain a 1x51 MATLAB cell of MATLAB structs where each struct is the censoring info at a given framewise displacement (FD) threshold (0 to 0.5 millimeters in steps of 0.01 millimeters). 


## Intermediate Pipeline Outputs

The raw file outputs produced by the pipeline are organized in the following structure: 

```default
output_dir/
|__ sub-id
    |__ ses-session
        |__ files
        |   |__DCANBOLDProc<ver>
        |   |__summary_DCANBOLDProc<ver>
        |   |  |__executivesummary
        |   |__ MNINonLinear
        |   |   |__ fsaverage_LR32k
        |   |   |__ Results
        |   |__ T1w
        |   |   |__ id
        |   |__[T2w]   
        |   |__ task-<taskname>
        |__ logs
```

### files
* `summary_DCANBOLDProc,ver./executivesummary`: The .html file within can be opened for quality inspection of pipeline results.
* `MNINonLinear`: Contains the final space results of anatomy in 164k resolution.
* `MNINonLinear/fsaverage_LR32k`: Final space anatomy in 32k resolution, where functional data is ultimately projected.
* `MNINonLinear/Results`: Final space functional data in the CIFTI 91282 'grayordinates' format. Runs within each BIDS task are concatenated.
* `T1w`: Contains native space anatomical data as well as intermediate preprocessing files.
* `T1w/id`: The participant ID folder within T1w is the FreeSurfer subject folder. 
* `T2w`: T2w native space data, if T2w for subject was provided.
* `task-taskname`: These folders contain intermediate functional preprocessing files from the fMRIVolume stage.

### logs

`logs` contains the log files for each stage. In the case of an error, consult these files *in addition* to the standard error and standard output of the app itself (by defualt this is printed to the command line).

`status.json` codes:

* unchecked: 999

* succeeded: 1

* incomplete: 2

* failed: 3

* not_started: 4

### Notes: CPU and disk usage

The pipeline may take over 24 hours if run on a single core. It is recommended to use at least 4 cores and allow for at least 12GB of memory total (so at least 3GB per core) to be safe. For sessions containing multiple runs, fMRI processing can be done in parallel, so using a number of cores which evenly divides your number of runs is optimal.

Temporary/Scratch space: All intermediate processing is done in the designated output folder. Be sure this location has sufficient disk space and read/write performance for your processing jobs. 

### Other notes

Development on DWI processing and diffusion fieldmap support has been discontinued. For processing diffusion data, consider [QSIPrep](https://qsiprep.readthedocs.io/en/latest/) or other alternatives. In addition, the processing of functional bold data will fail if you have dwi data without field maps. The `--ignore dwi` flag does not fix this. Currently, we suggest you temporarily remove the dwi data to process your subjects through our pipeline if your data does not have field maps.

The ideal motion filtering parameters for `--bandstop` have not been robustly tested across repetition times or populations outside of adolescents, so the proper range should be decided upon carefully. Consult reference [3] in the [usage](usage.md) for more information. 

Additional issues are documented on the [GitHub issues page](https://github.com/DCAN-Labs/abcd-hcp-pipeline/issues). Users are also encouraged to use the issues page to submit their own bug reports, feature requests, and other feedback. 