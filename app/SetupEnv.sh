#!/bin/bash

# Set up FSL (if not already done so in the running environment)
# Uncomment the following 2 lines (remove the leading #) and correct the FSLDIR setting for your setup
export FSLDIR=/opt/fsl
. ${FSLDIR}/etc/fslconf/fsl.sh > /dev/null 2>&1

# Let FreeSurfer know what version of FSL to use
# FreeSurfer uses FSL_DIR instead of FSLDIR to determine the FSL version
export FSL_DIR="${FSLDIR}"

# Set up FreeSurfer (if not already done so in the running environment)
# Uncomment the following 2 lines (remove the leading #) and correct the FREESURFER_HOME setting for your setup
export FREESURFER_HOME=/opt/freesurfer
. ${FREESURFER_HOME}/SetUpFreeSurfer.sh > /dev/null 2>&1

# Set up specific environment variables for the HCP Pipeline
export HCPPIPEDIR=/opt/pipeline
export SCRATCHDIR=/tmp

export HCPPIPEDIR_Templates=${HCPPIPEDIR}/global/templates
export HCPPIPEDIR_Config=${HCPPIPEDIR}/global/config
export HCPPIPEDIR_PreFS=${HCPPIPEDIR}/PreFreeSurfer/scripts
export HCPPIPEDIR_FS=${HCPPIPEDIR}/FreeSurfer/scripts
export HCPPIPEDIR_PostFS=${HCPPIPEDIR}/PostFreeSurfer/scripts
export HCPPIPEDIR_fMRISurf=${HCPPIPEDIR}/fMRISurface/scripts
export HCPPIPEDIR_fMRIVol=${HCPPIPEDIR}/fMRIVolume/scripts
export HCPPIPEDIR_tfMRI=${HCPPIPEDIR}/tfMRI/scripts
export HCPPIPEDIR_dMRI=${HCPPIPEDIR}/DiffusionPreprocessing/scripts
export HCPPIPEDIR_dMRITract=${HCPPIPEDIR}/DiffusionTractography/scripts
export HCPPIPEDIR_Global=${HCPPIPEDIR}/global/scripts
export HCPPIPEDIR_tfMRIAnalysis=${HCPPIPEDIR}/TaskfMRIAnalysis/scripts
export MSMCONFIGDIR=${HCPPIPEDIR}/MSMConfig
export MSMBin=${HCPPIPEDIR}/MSMBinaries

# MSMBINDIR
export MSMBINDIR=/opt/msm/Ubuntu


# Set up DCAN Environment Variables
export MCRROOT=/opt/mcr/v96
export DCANBOLDPROCDIR=/opt/dcan-tools/dcan_bold_proc
export DCANBOLDPROCVER=DCANBOLDProc_v4.0.0
export EXECSUMDIR=/opt/dcan-tools/executivesummary
export CUSTOMCLEANDIR=/opt/dcan-tools/customclean
export MATLAB_PREFDIR=/tmp/.matlab/R2019a
export ABCDTASKPREPDIR=/opt/dcan-tools/ABCD_tfMRI

# hacky solution for now...
export SOURCEDATADIR=/bids_input/sourcedata

