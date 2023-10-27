import sys
import os
import yaml

import optparse
parser = optparse.OptionParser()
parser.add_option("--init", dest="init", default=False, action="store_true",
    help="If this is the first call to generate events with these setups, use the --init option to initialize directories, configs, etc.. Most of the following option do not have to be specified again after this step and are only needed for the first setup.")

init_opts = optparse.OptionGroup(parser, "Initialization Options")
init_opts.add_option("-p", dest="process", default="./POWHEG-BOX-RES/ttbb", help="path to process (only for --init)")
init_opts.add_option("-i", dest="input_file", default="./POWHEG-MC-Event-generation/ttbb_powheg_inputs/powheg.input_1L", help="path to powheg.input file to use (only for --init)")
init_opts.add_option("-t", dest="tag", default=None, help="give your generation a tag to differentiate it from other generations with the same settings (only for --init)")
init_opts.add_option("-m", dest="mass", default=172.5, help="top mass (only for --init)")
init_opts.add_option("--pdf", dest="pdf", default=320900, help="pdf set (only for --init)")
init_opts.add_option("--mur", dest="muR", default=1.0, help="muR factor (only for --init)")
init_opts.add_option("--muf", dest="muF", default=1.0, help="muF factor (only for --init)")
parser.add_option_group(init_opts)

parser.add_option("-w", dest="workdir", default=None, help="path to workdir that is created after initialization (not needed for --init)")
parser.add_option("-S", dest="stage", default=1, help="parallel stage to run")
parser.add_option("-X", dest="iteration", default=1, help="iteration to run (relevant for stage 1)")
parser.add_option("-n", dest="nbatches", default=1000, help="number of batches")
parser.add_option("--force", dest="force", default=False, action="store_true", help="force re-execution ")
parser.add_option("--validate", dest="validate", default=False, action="store_true", help="Validate the specified stage/iteration")
(opts, args) = parser.parse_args()

# Initialize in first call
if opts.init:
    print("\n##################\n  INITIALIZATION  \n##################\n")
    # check validity of some options:
    if not os.path.exists(opts.input_file):
        raise ValueError(
            f"Input file\n  {opts.input_file}\ndoes not exist")
    if not os.path.exists(opts.process):
        raise ValueError(
            f"Process directory\n  {opts.process}\nin POWHEG-BOX-RES does not exist")

    # determine workdir
    dir_name = f"pdf_{str(opts.pdf)}__mass_{str(opts.mass)}__muR_{str(opts.muR)}__muF_{str(opts.muF)}"
    if opts.tag:
        dir_name = f"{opts.tag}__{dir_name}"

    dir_path = os.path.abspath(os.path.join(".", dir_name))
    if os.path.exists(dir_path):
        raise ValueError(
            f"Working directory\n  ./{dir_name}\nalready exists. If you want to re-initalize this setup delete the directory first to avoid overwriting existing working directories by accident")

    # determine workdir in powheg box
    run_name = f"run__{dir_name}"
    run_dir = os.path.abspath(os.path.join(opts.process, run_name))
    if os.path.exists(run_dir):
        raise ValueError(
            f"Run directory\n  {run_dir}\nalready exists. If you want to re-initalize this setup delete the directory first to avoid overwriting existing event generation by accident")

    print(f"\nCreating working directory at ./{dir_name}")
    os.mkdir(dir_path)
    print(f"\nCreating run directory at {run_dir}")
    os.mkdir(run_dir)

    powheg_input_path = os.path.join(dir_path, "powheg.input")
    print(f"\nCopying powheg input file to working directory:\n\t{powheg_input_path}")
    os.system(f"cp {opts.input_file} {powheg_input_path}")

    # generate a yml file with all settings
    settings = {
        "mass": float(opts.mass),
        "pdf": int(opts.pdf),
        "muR": float(opts.muR),
        "muF": float(opts.muF),
        "tag": opts.tag,
        "powheg.input": powheg_input_path,
        "run_dir": run_dir,
        "name": dir_name,
        "stage1": False,
        "stage1_valid": False,
        "stage1_it": 0,
        "stage2": False,
        "stage2_valid": False,
        "stage3": False,
        "stage3_valid": False,
        "stage4": False,
        "stage4_valid": False,
        }
    yaml_file = os.path.join(dir_path, "settings.yml")
    with open(yaml_file, "w") as yf:
        yaml.dump(settings, yf, default_flow_style=False, indent=4)
    print(f"\nSaved settings in yaml file: {yaml_file}")
    print(settings)
    
    # adding the settings to the powheg input file
    cmd = f'echo "topmass {opts.mass}" >> {powheg_input_path}'
    os.system(cmd)
    cmd = f'echo "lhans1 {opts.pdf}" >> {powheg_input_path}'
    os.system(cmd)
    cmd = f'echo "lhans2 {opts.pdf}" >> {powheg_input_path}'
    os.system(cmd)
    cmd = f'echo "renscfact {opts.muR}" >> {powheg_input_path}'
    os.system(cmd)
    cmd = f'echo "facscfact {opts.muF}" >> {powheg_input_path}'
    os.system(cmd)
    print("\nAdded the pdf, topmass and scale settings to the powheg input file:")
    os.system(f"tail -n 5 {powheg_input_path}")

    print(f"\nIntialization is done, you can now start with the first processing stage. For this, run the submit command with the following arguments:")
    print(f"\n-w ./{dir_name} -S 1 -X 1 -n NBATCHES\n")
    print(f"This command submits NBATCHES condor jobs for parallelstage=1 and xgriditeration=1")
    print(f"The number of events produced per batch job is specified in your powheg.input file")
    with open(powheg_input_path, "r") as f:
        lines = f.readlines()
    nevts = None
    for l in lines:
        if l.startswith("numevts"):
            try:
                nevts = int(l.split(" ")[1])
            except: continue
            break
    if nevts:
        print(f"In your file 'numevts' is set to {nevts}")
    else:
        print("In your powheg.input file no information about the number of events per job could be found. Check that the file has a setting 'numevts'")
    exit()

# run the actual submit after successful initialization
# check that all necessary files and paths exist
if not os.path.exists(opts.workdir):
    raise ValueError(
        f"Working directory\n  {opts.workdir}\ndoes not exist")
settings_path = os.path.abspath(os.path.join(opts.workdir, "settings.yml"))
if not os.path.exists(settings_path):
    raise ValueError(
        f"Settings file in workdir\n  {settings_path}\ndoes not exist")
# read yaml file
with open(settings_path, "r") as yf:
    settings = yaml.full_load(yf)

powheg_input_path = settings["powheg.input"]
if not os.path.exists(powheg_input_path):
    raise ValueError(
        f"Powheg input file in workdir\n  {powheg_input_path}\ndoes not exist")

run_dir = settings["run_dir"]
if not os.path.exists(run_dir):
    raise ValueError(
        f"Run directory\n  {run_dir}\ndoes not exist")

# check if the requested stage has already been run
if int(opts.stage) in [1,2,3,4]:
    stage_status = settings[f"stage{opts.stage}"]
    if stage_status and not opts.force:
        print(f"\nParallelstage {opts.stage} has already been run for this setup. If you want to force a re-run, please re-execute this command and add the flag '--force'.")
        exit()
    if int(opts.stage) == 1:
        it_status = settings[f"stage1_it"]
        if it_status != int(opts.iteration)-1 and not opts.force:
            print(f"\nThe last validated iteration is X={it_status} and you requested X={opts.iteration} (should be X={it_status+1}). Make sure this is what you want to do, or adjust the requested iteration. You can force the iteration you requested by re-executing this command and adding the flag '--force'.")
            exit()
    else:
        last_stage_valid = settings[f"stage{int(opts.stage)-1}_valid"]
        if (not last_stage_valid) and not opts.force:
            print(f"\nYou requested to run stage S={opts.stage}, but the last stage has not yet been validated. You can validate the previous stage by appending '--validate' to the submit command of the previous stage to register its succesful completion. You can also force the execution of your current stage by re-executing the command and adding the flag '--force'.")
            exit()


## TODO validation
## TODO validate that the number of batches matches the previous iteration
from submit_handler import submit_handler
submit_handler(
    settings=settings,
    nbatches=int(opts.nbatches),
    stage=int(opts.stage),
    iteration=int(opts.iteration),
    workdir=opts.workdir,
    finalization=False
    )


