#!/bin/bash

echo "$@"
# Activate the conda environment
source /opt/conda/etc/profile.d/conda.sh
conda activate myenv

chmod +x "$1"
# Execute any arguments passed to the script, or default to bash if none provided
exec "$@"