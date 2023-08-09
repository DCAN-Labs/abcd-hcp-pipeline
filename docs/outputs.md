# Pipeline Outputs

The outputs are organized in the following structure: 

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

## Notes: CPU and disk usage

The pipeline may take over 24 hours if run on a single core. It is recommended to use at least 4 cores and allow for at least 12GB of memory total (so at least 3GB per core) to be safe. For sessions containing multiple runs, fMRI processing can be done in parallel, so using a number of cores which evenly divides your number of runs is optimal.

Temporary/Scratch space: All intermediate processing is done in the designated output folder. Be sure this location has sufficient disk space and read/write performance for your processing jobs. 

## Other notes

Development on DWI processing and diffusion fieldmap support has been discontinued. For processing diffusion data, consider [QSIPrep](https://qsiprep.readthedocs.io/en/latest/) or other alternatives. In addition, the processing of functional bold data will fail if you have dwi data without field maps. The `--ignore dwi` flag does not fix this. Currently, we suggest you temporarily remove the dwi data to process your subjects through our pipeline if your data does not have field maps.

The ideal motion filtering parameters for `--bandstop` have not been robustly tested across repetition times or populations outside of adolescents, so the proper range should be decided upon carefully. Consult reference [3] in the [usage](usage.md) for more information. 

Additional issues are documented on the [GitHub issues page](https://github.com/DCAN-Labs/abcd-hcp-pipeline/issues). Users are also encouraged to use the issues page to submit their own bug reports, feature requests, and other feedback. 