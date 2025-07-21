import sys
import os

from make_seeds import make_seeds

batch_shell_template = """#!/bin/bash
source /cvmfs/grid.desy.de/etc/profile.d/grid-ui-env.sh

# Dump all code into 'MC_Generation_Script_{job_id}.sh'
cat <<'EndOfMCGenerationFile' > MC_Generation_Script_{job_id}.sh
#!/bin/bash

echo "Processing job number {job_id} ... "
export HOME=/afs/desy.de/user/p/perezdan
CWD=`pwd -P`
mkdir -p /tmp/job_{job_id}
cd /tmp/job_{job_id}

### Setup CMSSW ###
cd /data/dust/user/perezdan/Misc/Me2025/POWHEG-v1
export SCRAM_ARCH=el8_amd64_gcc10
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_12_4_11/src ] ; then
    echo release CMSSW_12_4_11 already exists
else
    scram p CMSSW CMSSW_12_4_11
fi
cd CMSSW_12_4_11/src
eval `scram runtime -sh`

# Running PowHeg
cd {run_dir}
echo {job_id} | ./../pwhg_main

### Cleaning ###
cd $CWD
rm -rf /tmp/job_{job_id}
echo "shell script has finished"

# End of MC_Generation_Script_{job_id}.sh
EndOfMCGenerationFile

# Make file executable
chmod +x MC_Generation_Script_{job_id}.sh

# Run in EL8 container
export SINGULARITY_CACHEDIR="/tmp/$(whoami)/singularity"
singularity run -B /afs -B /data -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/el8:x86_64 $(echo $(pwd)/MC_Generation_Script_{job_id}.sh)
"""

submitTemplate = """
+RequestRuntime       = 200000
RequestMemory         = 2000
universe              = vanilla
executable            = {dir}/mc_generation_job_$(ProcId).sh
output                = {dir}/mc_generation_job_$(ProcId).out
error                 = {dir}/mc_generation_job_$(ProcId).err
log                   = {dir}/mc_generation_job_$(ProcId).log
transfer_executable   = True
queue {nJobs}
"""

def submit_handler(settings, nbatches, stage, iteration, nevt, ttbardecay, workdir, finalization=False):
    run_dir = settings["run_dir"]
    seed_file = make_seeds(nbatches, run_dir)

    if stage==4:
        # copy rwl file
        cmd = f"cp {settings['pwg-rwl']} {settings['run_dir']}"
        os.system(cmd)

    # copy powheg.input file and adjust for the current stage
    input_file = os.path.join(settings['run_dir'], 'powheg.input')
    cmd = f"cp {settings['powheg.input']} {input_file}"
    os.system(cmd)
    # add stage to input file
    n_lines = 6
    if int(stage) < 5: # different for decay stage
        cmd = f'echo "parallelstage {stage}" >> {input_file}'
        os.system(cmd)
        cmd = f'echo "xgriditeration {iteration}" >> {input_file}'
        os.system(cmd)
        n_lines += 2
    cmd = f'echo "numevts {nevt}" >> {input_file}'
    os.system(cmd)
    # add ttbar decay information and nevents per job to powheg config
    if int(stage) == 4:
        # cmd = f'echo "numevts {nevt}" >> {input_file}'
        # os.system(cmd)
        # ttdecay
        if ttbardecay == "0L":
            decay_id = "00022"
        elif ttbardecay == "1L":
            decay_id = "11111"
        elif ttbardecay == "2L":
            decay_id = "22200"
        else: #incl
            decay_id = "22222"
        cmd = f'echo "topdecaymode {decay_id}" >> {input_file}'
        os.system(cmd)
        n_lines += 2
        if ttbardecay == "1L":
            cmd = f'echo "semileptonic 1" >> {input_file}'
            os.system(cmd)
            n_lines += 1

    print("The following configuration is now in the powheg.input file:\n")
    os.system(f"tail -n {n_lines} {input_file}")

    submit_dir = os.path.join(workdir, "submit")
    if not os.path.exists(submit_dir):
        os.mkdir(submit_dir)
    
    # create batch submit scripts
    for iJob in range(nbatches):
        shell_path = os.path.join(submit_dir, f"mc_generation_job_{str(iJob)}.sh")
        shell_code = batch_shell_template.format(run_dir=run_dir,job_id=iJob)
        with open(shell_path, "w") as f:
            f.write(shell_code)
    os.system(f"chmod u+x {submit_dir}/*.sh")
    
    # write condor submit script
    submit_path = os.path.join(submit_dir, f"mc_generation_jobs.sub")
    code = submitTemplate.format(
        dir=os.path.abspath(submit_dir),
        nJobs=nbatches)
    with open(submit_path, "w") as f:
        f.write(code)
    
    print(f"Generated submit script at {submit_path}")

