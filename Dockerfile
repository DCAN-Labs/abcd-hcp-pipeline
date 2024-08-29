FROM dcanumn/internal-tools:v1.0.12

ARG DEBIAN_FRONTEND=noninteractive

#----------------------------------------------------------
# Install common dependencies and create default entrypoint
#----------------------------------------------------------
RUN apt-get update && apt-get install -yq --no-install-recommends \
        apt-utils \
        graphviz \
        python-pip \
        python3 \
        python3-dev \
        wget

RUN pip install pyyaml numpy pillow pandas
RUN apt-get update && apt-get install -yq --no-install-recommends python3-pip
RUN pip3 install setuptools wheel

# include bidsapp interface
COPY ["app", "/app"]
RUN chmod -R 775 /app
RUN pip3 install -r "/app/requirements.txt"

# dcan hcp code
RUN git clone -b 'v2.0.1' --single-branch --depth 1 https://github.com/DCAN-Labs/DCAN-HCP.git /opt/pipeline
# abcd task prep
RUN git clone -b 'v0.0.0' --single-branch --depth 1 https://github.com/DCAN-Labs/abcd_task_prep.git ABCD_tfMRI

# unless otherwise specified...
ENV OMP_NUM_THREADS=1
ENV SCRATCHDIR=/tmp/scratch
ENV ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=1
ENV TMPDIR=/tmp

# make app directories
RUN mkdir /bids_input /output /atlases /config

# setup entrypoint
COPY ["./entrypoint.sh", "/entrypoint.sh"]
RUN chmod -R 775 /entrypoint.sh
COPY ["LICENSE", "/LICENSE"]
ENTRYPOINT ["/entrypoint.sh"]
WORKDIR /
CMD ["--help"]
