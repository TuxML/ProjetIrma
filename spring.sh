#!/bin/bash
#OAR -l /cpu=1/core=4,walltime=1:00:00
#OAR -p virt='YES'

nb=0

if [ -z "$1" ]; then
	nb=1
else
	nb=$1
fi

#OAR --array-param-file ./params.txt
#OAR -O /temp_dd/igrida-fs1/alemasle/oar_output/job.%jobid%.output
#OAR -E /temp_dd/igrida-fs1/alemasle/oar_output/job.%jobid%.error

. /etc/profile.d/modules.sh

set -x

module load veertuosa/0.0.1

VM_NAME=TuxML_${OAR_JOBID}

veertuosa_launch --name ${VM_NAME} --image /temp_dd/igrida-fs1/alemasle/images/TuxMLDebian.qcow2

VM_CMD=""

for i in $(seq $1); do
	VM_CMD+="/TuxML/runandlog.py; "
done

ssh-vm $VM_NAME "$VM_CMD"
