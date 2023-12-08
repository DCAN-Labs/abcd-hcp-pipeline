## BIDS Directory Structure

Below is an example of the BIDS directory structure, showcasing the systematic organization of neuroimaging data for the ABCD study. This structure adheres to the BIDS standard, allowing researchers and practitioners to easily navigate and understand the contents of the dataset. Each directory and file follows a consistent naming convention, providing valuable context and metadata. It includes a dataset overview, participant information, task metadata, and organized subject and session directories. Each subject's data is structured under "sub-" and "ses-" prefixes, containing anatomical, diffusion, fieldmap, and functional images. Placeholder labels like "SUBID" and "SESID" can be replaced with actual subject and session identifiers, facilitating consistent data organization and sharing within the neuroimaging community. This example aims to exemplify the BIDS principles, emphasizing clarity, reproducibility, and interoperability in the handling of complex neuroscientific data.

```
|--dataset_description.json
|--README
|--CHANGES
|--participants.tsv
|--task-(MID|nback|rest|SST)_bold.json
|--sub-SUBID
   |--ses-SESID
      |--anat
         |--sub-SUBID_ses-SESID_####_rec-normalized_(T1w|T2w).json
         |--sub-SUBID_ses-SESID_####_rec-normalized_(T1w|T2w).nii.gz
      |--dwi
         |--sub-SUBID_ses-SESID_dwi.bval
         |--sub-SUBID_ses-SESID_dwi.bvec
         |--sub-SUBID_ses-SESID_dwi.json
         |--sub-SUBID_ses-SESID_dwi.nii.gz
      |--fmap
         |--sub-SUBID_ses-SESID_(_acq-dwi)_dir-(AP|PA)_run-0#_epi.json
         |--sub-SUBID_ses-SESID_(_acq-dwi)_dir-(AP|PA)_run-0#_epi.nii.gz
      |--func
         |--sub-SUBID_ses-SESID_task-MID_run-0#_bold.json
         |--sub-SUBID_ses-SESID_task-MID_run-0#_bold.nii.gz
```