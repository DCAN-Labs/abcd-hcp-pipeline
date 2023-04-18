# Installation

## FreeSurfer License

This software includes a FreeSurfer 5.3.0 installation. A FreeSurfer License, available separately, is required to run.

[Follow this link for a FreeSurfer License](https://surfer.nmr.mgh.harvard.edu/fswiki/License)

## Using Docker

Before running, you will need to load the image onto your Docker service by running the following command:

`docker pull dcanumn/abcd-hcp-pipeline`

If you receive a "no space left on device" error during this pull process, you may need to clean up any old/dangling images and containers from the docker registry, and possibly increase the amount of space allocated to Docker. 

## Using Singularity 

You can either pull the image from the Docker repository, or build it from the repository for the image to be saved in the working directory.

`singularity pull docker://dcanumn/abcd-hcp-pipeline`

`singularity build abcd-hcp-pipeline.sif docker://dcanumn/abcd-hcp-pipeline`

These are essentially the same, but in the latter case you have control over the name of the .sif file. 

## Install and run from source (not recommended)

Installing and running the pipeline from source is not recommended, but it is an option if Docker and Singularity are not available on your system. This requires installing the dependencies specified in the pipeline Dockerfile, including the contents of the [DCAN internal-tools](https://github.com/DCAN-Labs/internal-tools) and [DCAN external-software](https://github.com/DCAN-Labs/external-software) Dockerfiles.

Environment variables must be set in accordance with `/app/SetupEnv.sh`; then the pipeline may be run with `python3 /app/run.py <args>`

