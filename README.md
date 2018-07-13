# dcan_hcp_bids

This software takes a bids folder as input and determines parameters
for the dcan hcp pipeline, calling upon the proper code to run the
subject(s).

Usage:

```{bash}
docker run --rm \
    -v /path/to/bids_dataset:/bids_input:ro \
    -v /path/to/outputs:/output \
    dcan/fmri-pipeline /bids_input /output
```

Some current limitations:

software does not support dynamic acquisition parameters for a single
modality (e.g. different phase encoding direction for 2 fmri).  Other
parameters may only be tested by creating separate bids input datasets.

software will use spin echo field maps if they are present, then
gradient field maps, then None.

user must ensure that PhaseEncodingDirection is properly set in both
spin echo field map and functional data, as dcm2bids does not always
get this right.


