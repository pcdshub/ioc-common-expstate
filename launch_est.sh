#!/bin/bash

export PCDS_CONDA_VER=5.1.1
source /cds/group/pcds/pyps/conda/pcds_conda
export PYTHONPATH=/reg/g/psdm/web/ws/prod/apps/LogBookClient:${PYTHONPATH}
export PATH=/reg/g/pcds/engineering_tools/R2.0.1/scripts:${PATH}

LAUNCHER="$(readlink -f ${BASH_SOURCE[0]})"
UI="$(dirname ${LAUNCHER})/screen"

inssta=`get_info --getHutch`:`get_info --getstation`

caget IOC:${inssta}:EXPSTATE:State.INDX >/dev/null 2>&1
if [ $? != 0 ]; then 
    zenity --info --text="Cannot access IOC:"${inssta}":EXPSTATE:State.INDX.  Is the ioc-"`get_info --gethutch`"-expstate IOC down?" >/dev/null 2>&1
    exit 0
fi

pydm --hide-nav-bar --hide-menu-bar --hide-status-bar -m "endstation=${inssta},$*" "${UI}/est.py"
