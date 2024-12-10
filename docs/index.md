# ABCD-HCP BIDS fMRI Pipeline

[![DOI](https://zenodo.org/badge/171551109.svg)](https://zenodo.org/badge/latestdoi/171551109)



The ABCD-BIDS pipeline is a [BIDS App](https://bids-apps.neuroimaging.io/) for processing [BIDS-formatted MRI datasets](https://bids-specification.readthedocs.io/en/stable/) using the [DCAN-HCP pipeline](https://github.com/DCAN-Labs/DCAN-HCP) and supporting modules including [DCAN BOLD Processing](https://github.com/DCAN-Labs/dcan_bold_processing) and [DCAN Executive Summary](https://github.com/DCAN-Labs/ExecutiveSummary). The pipeline utilizes methods from both the [Human Connectome Project's minimal preprocessing pipeline](https://doi.org/10.1016/j.neuroimage.2013.04.127) and the [DCAN Labs resting state fMRI analysis tools](https://github.com/DCAN-Labs/dcan_bold_processing) to output preprocessed MRI data in both volume and surface spaces.

Docker images are now available at the [DCAN Docker Hub repo](https://hub.docker.com/r/dcanumn/abcd-hcp-pipeline)

Docker images for older versions (<= 0.0.4) are available at the [old repo](https://hub.docker.com/r/dcanlabs/abcd-hcp-pipeline)

## Pipeline Description
Each stage of the larger pipeline has a distinct beginning and ending which is why we consider them stages.  The pipeline completes each step in serial, though some steps can utilize multiple processor cores to speed up processing time.  Below is a short explanation of each stage's intent and some of the methods.

For full details see the following:

- [Adolescent Brain Cognitive Development (ABCD) Community MRI Collection and Utilities. Feczko, et al. Biorxiv, 2021](https://www.biorxiv.org/content/10.1101/2021.07.09.451638v1)
- [The minimal preprocessing pipelines for the Human Connectome Project. Glasser, et al. NeuroImage. 2013.](https://doi.org/10.1016/j.neuroimage.2013.04.127)
- [Correction of respiratory artifacts in MRI head motion estimates. Fair, et al. NeuroImage. 2019.](https://doi.org/10.1016/j.neuroimage.2019.116400)

### Stage 1: PreFreeSurfer

The primary goal of PreFreeSurfer is to remove distortions from the anatomical data and align and extract the brain in the subject's native volume space.

Notable deviations from the original HCP minimal preprocessing pipeline include the use of [Advanced Normalization Tools (ANTs)](http://stnava.github.io/ANTs/) to perform denoising and N4 bias field correction, which significantly improves results for subjects scanned on General Electric (GE) and Philips scanners that tend to have more noise and are not always normalized following the scan.  We moved Montreal Neurological Institute (MNI) standard space registration to the PostFreeSurfer stage to make use of the refined brain mask created in the FreeSurfer stage.

We also enabled the ability to process subjects without a T2w image.  A T2w image is necessary for myelin mapping estimates, but it does not make a big enough impact on other outputs such as segmentation and surface generation to require it for all image processing.

### Stage 2: FreeSurfer

The brain gets segmented into predefined structures, the white and pial cortical surfaces are reconstructed, and [FreeSurfer's](https://surfer.nmr.mgh.harvard.edu/) standard folding-based surface registration to FreeSurfer's surface atlas is performed.  This stage remains largely unchanged from the original HCP minimal preprocessing pipeline so refer to [Glasser, et al. 2013](https://doi.org/10.1016/j.neuroimage.2013.04.127) for more information.

### Stage 3: PostFreeSurfer

The primary function of the PostFreeSurfer stage is generating CIFTI surface files and applying surface registration to the Conte-69 surface template.  In addition to this, atlas registration is performed.  By using the refined native space brain mask generated in FreeSurfer the pipeline is able to produce a more robust registration.  Furthermore we found that ANTs' diffeomorphic symmetric image normalization method for registration outperforms [FSL's FNIRT](https://fsl.fmrib.ox.ac.uk/fsl/docs/#/)-based registration.  

### Stage 4: FMRIVolume

The FMRIVolume stage marks the start of the functional part of the image processing pipeline and it begins similarly to the anatomical portion with correction of gradient-nonlinearity-induced distortions to the EPIs.  Each volume of the time series is aligned using an [FSL FLIRT](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT) rigid-body (six degrees-of-freedom) registration to the initial frame to correct for motion.  The initial frame is used because it tends to have greater anatomical contrast.  The registration of each volume results in a twelve column text file containing translation and rotation along each axis and their derivatives.  A de-meaned and linearly de-trended motion parameter file is provided as well for nuisance regression.

A pair of spin echo EPI scans with opposite phase encoding directions are used to correct for distortions in the phase encoding direction of each fMRI volume using [FSL's topup](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup). This pair is denoted by the "IntendedFor" field populated in the JSON sidecar metadata associated among field maps.  After removing the distortions, the single-band reference is registered to the T1w image and this registration is used to align all fMRI volumes to the anatomical data independently.  Each fMRI volume is non-linearly registered to MNI space and finally masked.

### Stage 5: FMRISurface

The purpose of the FMRISurface stage is primarily to take a volume time series and map it to the standard CIFTI grayordinates space.  This stage has not been altered from the original pipeline so refer to [Glasser, et al. 2013](https://doi.org/10.1016/j.neuroimage.2013.04.127) for more information.

### Stage 6: DCANBOLDProcessing (DBP)

[DCAN BOLD Processing](https://github.com/DCAN-Labs/dcan_bold_processing) is a signal processing software developed primarily by Dr. Oscar Miranda-Dominguez in the DCAN Labs with the primary function of nuisance regression from the dense time series and providing motion censoring information in accordance with [Power, et al. 2014](https://www.ncbi.nlm.nih.gov/pubmed/23994314).  The motion numbers produced in the FMRIVolume stage are also filtered to remove artifactual motion caused by respiration.  For more information on the respiration filtering see [Correction of respiratory artifacts in MRI head motion estimates. Fair, et al. NeuroImage. 2019.](https://doi.org/10.1016/j.neuroimage.2019.116400).

This stage involves four broad steps:

1. Standard pre-processing
1. Optional application of a respiratory motion filter
1. Motion censoring followed by standard re-processing
1. Construction of parcellated timeseries

#### 1. DBP Standard pre-processing

Standard pre-processing comprises three steps. First all fMRI data are de-meaned and de-trended with respect to time.  Next a general linear model is used to denoise the processed fMRI data.  Denoising regressors comprise signal and movement variables.  Signal variables comprise mean time series for white matter, CSF, and the global signal, which are derived from individualized segmentations generated during PostFreesurfer in ACPC-aligned subject native space.  Movement variables comprise translational (X,Y,Z) and rotational (roll, pitch, and yaw) measures estimated by re-alignment during FMRIVolume and their Volterra expansion.  The inclusion of mean greyordinate timeseries regression is critical for most resting-state functional MRI comparisons, as demonstrated empirically by multiple independent labs (Ciric et al., 2017; Power et al., 2017, 2019b; Satterthwaite et al., 2013).  After denoising the fMRI data, the time series are band-pass filtered between 0.008 and 0.09 Hz using a 2nd order Butterworth filter.  Such a band-pass filter is softer than other filters, and avoids potential aliasing of the time series signal.

##### Global Signal Regression

Global signal regression (GSR) has been consistently shown to reduce the effects of motion on BOLD signals and eliminate known batch effects that directly impact group  comparisons (Ciric et al., 2017; Power et al., 2015, 2019b). Motion censoring (see below) combined with GSR has been shown to be the best existing method for eliminating artifacts produced by motion.

#### 2. DBP Respiratory Motion Filter

In working with ABCD data, we have found that a respiratory artifact is produced within multi-band data (Fair et al., 2020).  While this artifact occurs outside the brain, it can affect estimates of frame alignment, leading to inappropriate motion censoring.  By filtering the frequencies (18.582 to 25.726 breaths per minute) of the respiratory signal from the motion realignment data, our respiratory motion filter produces better estimates of FD. Users may optionally specify upper and lower frequencies to perform respiratory motion filtering.

#### 3. DBP Motion censoring

Our motion censoring procedure is used for performing the standard pre-processing and for the final construction of parcellated timeseries.  For standard pre-processing, data are labeled as "bad" frames if they exceed an FD threshold of 0.3 mm.  Such "bad" frames are removed when demeaning and detrending, and betas for the denoising are calculated using only the "good" frames. For band-pass filtering, interpolation is used initially to replace the "bad" frames and the residuals are extracted from the denoising GLM.  In such a way, standard pre-processing of the timeseries only uses the "good" data but avoids potential aliasing due to missing timepoints.  After motion censoring, timepoints are further censored using an outlier detection approach. Both a mask including outlier detection and a mask without outlier detection are created. These masks are HDF5 compatible .MAT files which contain temporal masks from 0 ("No censoring") to 0.5 mm FD thresholds in steps of 0.01 mm. 

#### 4. DBP Generation of parcellated timeseries for specific atlases

Using the processed resting-state fMRI data, this stage constructs parcellated time series for pre-defined atlases making it easy to construct correlation matrices or perform time series analysis on putative brain areas defined by independent datasets.  The atlases comprise recent parcellations of brain regions that comprise different networks.  In particular, parcellated timeseries are extracted for Evan Gordon’s 333 ROI atlas template (Gordon et al., 2014), Jonathan Power’s 264 ROI atlas template (Power et al., 2011), Thomas Yeo’s 118 ROI atlas template (Yeo et al., 2011), and the HCP’s 360 ROI atlas template (Glasser et al., 2016). These parcellations also include 19 individualized subcortical parcellations.  Since we anticipate newer parcellated atlases as data acquisition, analytic techniques, and knowledge all improve, it is trivial to add new templates for this final stage.

### Stage 7: ExecutiveSummary

The ExecutiveSummary stage produces an HTML visual quality control page that displays a [BrainSprite](https://github.com/simexp/brainsprite.js) viewer of the T1w and T2w segmentation, an overlay of the atlas registration on each single band reference created by FSL's slicer, and a visualization of the movement and grayordinate time series for each fMRI run pre- and post-regression.

### Stage 8: CustomClean

[Custom clean](https://github.com/DCAN-Labs/CustomClean) is an optional (though recommended) stage we use that is especially meant for processing large volumes of data. Custom clean removes some non-critical pipeline outputs to minimize the footprint of a subject's processed dataset and outputs a "cleaning JSON file" with a record of all file removed.

### Stage 9: FileMapper

[File Mapper](https://github.com/DCAN-Labs/file-mapper) is responsible for mapping the HCP pipeline outputs into valid BIDS derivatives.
