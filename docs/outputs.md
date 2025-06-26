# Pipeline Outputs

## Raw Outputs

The raw outputs are organized in the following structure (not all folders are listed here): 

    output_dir/
    └── sub-<SUBID>/
        └── ses-<SESID>/
            ├── files/
            │   ├── DCANBOLDProc_<ver>/
            │   ├── summary_DCANBOLDProc_<ver>/
            │   │   └── executivesummary/
            │   |        └── executive_summary_sub-<SUBID>_ses-<SESID>.html
            │   ├── MNINonLinear/
            │   │   ├── Results/
            │   │   ├── fsaverage_LR32k/
            │   ├── T1w/
            │   │   └── <SUBID>/
            │   ├── [T2w/]
            │   └── ses-<SESID>_task-<taskname>_run-<num>/
            └── logs/
        
### files

* `summary_DCANBOLDProc_<ver>/executivesummary`: The .html file within can be opened for quality inspection of pipeline results. See the [ExecutiveSummary GitHub](https://github.com/DCAN-Labs/ExecutiveSummary) for more info. 
* `MNINonLinear`: Contains the final space results of anatomy in 164k resolution.
* `MNINonLinear/fsaverage_LR32k`: Final space anatomy in 32k resolution, where functional data is ultimately projected.
* `MNINonLinear/Results`: Final space functional data in the CIFTI 91282 'grayordinates' format. Runs within each BIDS task are concatenated.
* `T1w`: Contains native space anatomical data as well as intermediate preprocessing files.
* `T1w/SUBID`: The participant ID folder within T1w is the FreeSurfer subject folder. 
* `T2w`: If a T2w for the subject was provided, this folder will store the native space data.
* `ses-<SESID>_task-<taskname>_run-<num>`: These folders contain intermediate functional preprocessing files from the fMRIVolume stage.

### logs

`logs` contains folders for each stage that contain the log files for that stage. In the case of an error, consult these files *in addition* to the standard error and standard output of the app itself (by default this is printed to the command line).

`status.json` codes:

* unchecked: 999
* succeeded: 1
* incomplete: 2
* failed: 3
* not_started: 4

## BIDS Derivatives

Pipeline outputs are mapped into BIDS-compliant derivatives via [File-mapper](https://github.com/DCAN-Labs/file-mapper) with the following directory structure. A detailed explanation of each file type is provided in the sections below - see anat/ and func/ sections. The `<SUBID>`, `<SESID>`, and `<TASK>` placeholders are replaced with the subject ID, session ID, and task name respectively (e.g. task-rest). The `<T1w|T2w>` placeholder is replaced with the type of anatomical image (T1-weighted or T2-weighted). The `<label>` placeholder is replaced with the run number.

The `<ATLAS>` placeholder is replaced with the name of the atlas used for functional data for extraction of parcellated timeseries, including Evan Gordon’s 333 ROI AT (Gordon et al., 2014), HCP’s 360 ROI AT (Glasser et al., 2016), Jonathan Power’s 264 ROI AT (Power et al., 2011), and Thomas Yeo’s 118 ROI AT (Yeo et al., 2011). All parcellations additionally include a subcortical segmentation with ROIs taken from the standard HCP 91k-grayordinate CIFTI template. 

* **Values for `<ATLAS>` include:**
    * Gordon2014FreeSurferSubcortical
    * HCP2016FreeSurferSubcortical
    * Markov2012FreeSurferSubcortical
    * Power2011FreeSurferSubcortical
    * Yeo2011FreeSurferSubcortical

Please note that this derivative structure is primarily used for ABCD data in the ABCC collection. The file-mapper github has the most [updated config file](https://github.com/DCAN-Labs/file-mapper/blob/main/examples/updated-filemapper_abcd-hcp-pipeline-v0.1.4.json) used for ABCC. 

```
derivatives/
└── abcd-hcp-pipeline_v0.1.4/
    └── sub-<SUBID>/
        └── ses-<SESID>/
            ├── anat/
            │   ├── SUBSES_<T1w|T2w>_space-MNI_brain.nii.gz
            │   ├── SUBSES_T1w_space-MNI_desc-wmparc_dseg.nii.gz
            │   ├── SUBSES_atlas-MNI_space-fsLR32k_desc-smoothed_myelinmap.dscalar.nii
            │   ├── SUBSES_atlas-MNI_space-fsLR32k_myelinmap.dscalar.nii
            │   ├── SUBSES_hemi-<L|R>_space-MNI_mesh-fsLR164k_midthickness.surf.gii
            │   ├── SUBSES_hemi-<L|R>_space-MNI_mesh-fsLR32k_midthickness.surf.gii
            │   ├── SUBSES_hemi-<L|R>_space-MNI_mesh-native_midthickness.surf.gii
            │   ├── SUBSES_hemi-<L|R>_space-T1w_mesh-fsLR32k_midthickness.surf.gii
            │   ├── SUBSES_hemi-<L|R>_space-T1w_mesh-native_midthickness.surf.gii
            │   ├── SUBSES_space-ACPC_dseg.nii.gz
            │   ├── SUBSES_space-fsLR32k_curv.dscalar.nii
            │   ├── SUBSES_space-fsLR32k_sulc.dscalar.nii
            │   ├── SUBSES_space-fsLR32k_sulc.pscalar.nii
            │   └── SUBSES_space-fsLR32k_thickness.dscalar.nii
            ├── func/
            │   ├── SUBSES_task-<TASK>_bold_atlas-<ATLAS>_desc-filtered_timeseries.ptseries.nii
            │   ├── SUBSES_task-<TASK>_bold_desc-filtered_timeseries.dtseries.nii
            │   ├── SUBSES_task-<TASK>_desc-filtered_motion_mask.mat
            │   ├── SUBSES_task-<TASK>_desc-filteredwithoutliers_motion_mask.mat
            │   ├── SUBSES_task-<TASK>_run-<label>_bold_timeseries.dtseries.nii
            │   ├── SUBSES_task-<TASK>_run-<label>_desc-filtered_motion.tsv
            │   ├── SUBSES_task-<TASK>_run-<label>_desc-filteredincludingFD_motion.tsv
            │   ├── SUBSES_task-<TASK>_run-<label>_desc-includingFD_motion.tsv
            │   ├── SUBSES_task-<TASK>_run-<label>_motion.tsv
            │   └── SUBSES_task-<TASK>_run-<label>_space-MNI_bold.nii.gz
            ├── img/*
            └── SUBSES.html
```

### anat/

The derivative files included under the `anat/` directory include the following (`sub-<label>_ses-<label>_` is replaced with an asterisk `*_` for readability):

|                     **Filename**                                                           |       **Description**                                                                                                                 |
| ----------------------------------------------------------------------- | ----------------------------------------------- |
| `*_<T1w/T2w>_space-MNI_<brain/head>.nii.gz`                                            | T1w & T2w brain & head images in MNI space                                                    |
| `*_T1w_space-MNI_desc-wmparc_dseg.nii.gz`                                              | White matter segmentation in MNI space                                                      |
| `*_hemi-<L/R>_space-<MNI/T1w>_mesh-<fsLR32k/fsLR164k/native>_midthickness.surf.gii`    | L/R midthickness in MNI & native space each with 32k, 164k, * native mesh                                   |
| `*_atlas-MNI_space-fsLR32k(_desc-smoothed)_myelinmap.dscalar.nii`                      | Smoothed & unsmoothed myelin map (only if T2w present)                                          |
| `*_space-ACPC_dseg.nii.gz`                                                             | Discrete segmentation (native volume space)                                                              |
| `*_space-fsLR32k_<curv/sulc/thickness>.dscalar.nii`                                    | Dense curvature, sulcal depth, & cortical thickness                                                     |
| `*_space-fsLR32k_sulc.pscalar.nii`                                                     | Parcellated dense subject sulcal depth                                                                           |
                                                              

### func/

The derivative files provided under `func/` including the following (`sub-<label>_ses-<label>_` is replaced with an asterisk `*_` for readability):

|            **Filename**                                                                     |         **Description**                                                                                                                |
| ----------------------------------------------------------------------- | ----------------------------------------------- |                                         
| `*_task-<MID/nback/rest/SST>_bold_desc-filtered_timeseries.dtseries.nii`               | Concatenated functional task dense time series post-DCANBOLDProc (regression and filtering) in HCP standard 91k CIFTI space           |
| `*_task-<MID/nback/rest/SST>_bold_atlas-<ATLAS>_desc-filtered_timeseries.ptseries.nii` | Concatenated functional task parcellated time series                     |
| `*_task-<MID/nback/rest/SST>_bold_desc-filtered(withoutliers)_motion_mask.mat`         | "5 contiguous frames" algorithm censoring file of temporal masks by FD threshold (0mm->0.5mm) with or without outliers |
| `*_task-<MID/nback/rest/SST>_run-#_bold_timeseries.dtseries.nii`                       | Individual functional task run dense time series in Atlas space                                                        |
| `*_task-<MID/nback/rest/SST>_run-#_bold_desc-(filtered)includingFD_motion.tsv`         | Movement-artifact-filtered movement numbers with or without FD                                                         |
| `*_task-<MID/nback/rest/SST>_run-#_motion.tsv`                                         | Unfiltered raw movement numbers without FD                                                                             |
| `*_task-<MID/nback/rest/SST>_run-#_space-MNI_bold.nii.gz`                              | Motion-corrected individual functional task run in MNI space in a volume                                               |
| `*_task-rest_bold_atlas-Gordon2014FreeSurferSubcortical_desc-filtered_timeseries_thresh-fd0p2mm_censor-<5min/10min/belowthresh>_conndata-network_connectivity.pconn.nii`                              | Parcellated dense connectivity matrix for resting state data at varying censor thresholds                                               |
| `*_task-rest_bold_atlas-Gordon2014FreeSurferSubcortical_desc-filtered_timeseries_thresh-fd0p2mm_censor-<5min/10min/belowthresh>_conndata-network_connectivity.txt`                              | Censored frames for parcellated dense connectivity matrices at varying censor thresholds                                               |


#### Motion files

The HDF5 compatible motion .MAT files are a product of the DCANBOLDProcessing stage of the pipeline that should be used for motion censoring. These files use the motion censoring algorithm from the [Power, et al, 2014 paper](https://www.sciencedirect.com/science/article/pii/S1053811913009117) that excludes periods of data below FD thresholds which are less than five contiguous frames between sequential censored frames. They contain a 1x101 MATLAB cell of MATLAB structs where each struct is the censoring info at a given framewise displacement (FD) threshold (0 to 1 millimeters in steps of 0.01 millimeters). 

## Other notes

Development on DWI processing and diffusion fieldmap support has been discontinued. For processing diffusion data, consider [QSIPrep](https://qsiprep.readthedocs.io/en/latest/) or other alternatives. In addition, the processing of functional bold data will fail if you have dwi data without field maps. The `--ignore dwi` flag does not fix this. Currently, we suggest you temporarily remove the dwi data to process your subjects through our pipeline if your data does not have field maps.

The ideal motion filtering parameters for `--bandstop` have not been robustly tested across repetition times or populations outside of adolescents, so the proper range should be decided upon carefully. Consult reference [3] in the [usage](usage.md) for more information. 

Additional issues are documented on the [GitHub issues page](https://github.com/DCAN-Labs/abcd-hcp-pipeline/issues). Users are also encouraged to use the issues page to submit their own bug reports, feature requests, and other feedback. 