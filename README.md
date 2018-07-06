# dcan_hcp_bids

This software takes a bids folder as input and determines parameters
for the dcan hcp pipeline, calling upon the proper code to run the
subject(s).

Some current limitations:

software does not support dynamic acquisition parameters per modality.
Other parameters may only be tested by creating separate bids folders.

software does not support mixing and matching of field map correction
method.  The same method will be applied to functional and anatomical
data.

user must ensure that PhaseEncodingDirection is properly set in both
spin echo field map and functional data, as dcm2bids does not always
get this right.


