import sys
import os

from make_seeds import make_seeds

batch_shell_template = """
#!/bin/bash
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
alias cd='cd -P'

startdir=$PWD
cd {cmssw_base}
eval `scramv1 runtime -sh`
cd $startdir
echo 'CMSSW initialized'

#add the LHAPDF library path to PATH
PATH=$PATH:/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/lhapdf/6.2.1-fmblme/bin/
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/lhapdf/6.2.1-fmblme/bin/
#add the FASTJET library path to PATH
PATH=$PATH:/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/fastjet/3.1.0/bin/
echo 'POWHEG initialized'

# running powheg
cd {run_dir}
echo "Running batch job number $SGE_TASK_ID"
"""

submitTemplateT2B = """
universe = vanilla
executable = /bin/bash
arguments = {arg}
error  = {dir}/{name}submitScript.$(Cluster)_$(ProcId).err
log    = {dir}/{name}submitScript.$(Cluster)_$(ProcId).log
output = {dir}/{name}submitScript.$(Cluster)_$(ProcId).out
run_as_owner = true
+JobFlavour = {runtime}
JobBatchName = {batchname}
"""

submitTemplateNAF = """
universe = vanilla
executable = /bin/bash
arguments = {arg}
error  = {dir}/{name}submitScript.$(Cluster)_$(ProcId).err
log    = {dir}/{name}submitScript.$(Cluster)_$(ProcId).log
output = {dir}/{name}submitScript.$(Cluster)_$(ProcId).out
run_as_owner = true
+RequestRuntime = {runtime}
JobBatchName = {batchname}
"""

submitTemplateLXPLUS = """
universe = vanilla
executable = /bin/bash
arguments = {arg}
error  = {dir}/{name}submitScript.$(Cluster)_$(ProcId).err
log    = {dir}/{name}submitScript.$(Cluster)_$(ProcId).log
output = {dir}/{name}submitScript.$(Cluster)_$(ProcId).out
run_as_owner = true
+JobFlavour = {runtime}
JobBatchName = {batchname}
"""

def submit_handler(settings, nbatches, stage, iteration, workdir, finalization=False):
    run_dir = settings["run_dir"]
    seed_file = make_seeds(nbatches, run_dir)

    # copy powheg.input file and adjust for the current stage
    input_file = os.path.join(settings['run_dir'], 'powheg.input')
    cmd = f"cp {settings['powheg.input']} {input_file}"
    os.system(cmd)
    # add stage to input file
    cmd = f'echo "parallelstage {stage}" >> {input_file}'
    os.system(cmd)
    if int(stage) == 1:
        cmd = f'echo "xgriditeration {iteration}" >> {input_file}'
        os.system(cmd)
    print("The following configuration is now in the powheg.input file:\n")
    os.system(f"tail -n 8 {input_file}")

    # generate a shell script for the batch submit
    gitcache = os.path.join(os.environ["USER"], ".cmsgit-cache")
    cmssw_base = os.path.join(os.environ["CMSSW_BASE"], "src")
    
    shell_code = batch_shell_template.format(
        cmssw_base=cmssw_base, run_dir=run_dir)

    if stage=="decay":
        # TODO separately handle the decay part
        print("decay step still todo")
        exit()
    else:
        shell_code += "echo $SGE_TASK_ID | ./../pwhg_main"

    submit_dir = os.path.join(workdir, "submit")
    if not os.path.exists(submit_dir):
        os.mkdir(submit_dir)
    log_dir = os.path.join(submit_dir, "logs")
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    shell_name = f"run_stage{stage}"
    if stage==1:
        shell_name += f"_it{iteration}"
    shell_path = os.path.join(submit_dir, f"{shell_name}.sh")
    with open(shell_path, "w") as f:
        f.write(shell_code)
    print(f"\nGenerated shell file for job submission at {shell_path}")
    
    # determine runtime
    runtimes = {
        1: (86400, "'tomorrow'"),
        2: (3*86400, "'nextweek'"),
        3: (86400, "'tomorrow'"),
        4: (2*86400, "'testmatch'"),
        "decay": (3600, "'longlunch'"),
        }
    runtime_int, runtime_str = runtimes[stage]
    

    # write condor submit script
    submit_path = os.path.join(submit_dir, f"{shell_name}.sub")
    # setup submit code
    code = ""
    if "naf" in os.environ["HOSTNAME"]: # German DESY NAF HTCondor system
        code += submitTemplateNAF
        runtime = runtime_int
    elif "iihe" in os.environ["HOSTNAME"]: # Belgian IIHE T2B HTCondor system
        code += submitTemplateT2B
        runtime = runtime_str
    elif "lxplus" in os.environ["HOSTNAME"]: # CERN lxplus HTCondor system
        code += submitTemplateLXPLUS
        runtime = runtime_str

    batch_name = f"{shell_name}__{settings['name']}"
    code = code.format(
        arg=os.path.abspath(shell_path),
        dir=os.path.abspath(log_dir),
        runtime=runtime,
        name=settings['name'],
        batchname=batch_name)

    code += "Queue Environment From (\n"
    for taskID in range(nbatches):
        code += f'"SGE_TASK_ID={taskID}"\n'
    code += ")"

    with open(submit_path, "w") as f:
        f.write(code)
    print(f"Generated submit script at {submit_path}")
    
    # submitting
    print(f"Submitting...")
    cmd = f"condor_submit -terse {submit_path}"
    os.system(cmd)

