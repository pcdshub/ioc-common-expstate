#!/bin/bash

export PCDS_CONDA_VER=5.1.1
source /cds/group/pcds/pyps/conda/pcds_conda

LAUNCHER="$(readlink -f ${BASH_SOURCE[0]})"
UI="$(dirname ${LAUNCHER})/screen"

pydm --hide-nav-bar --hide-menu-bar --hide-status-bar -m "endstation=${1}" "${UI}/est.py"
