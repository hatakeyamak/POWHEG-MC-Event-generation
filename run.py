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

lhe_opts = optparse.OptionGroup(parser, "LHE Options")
lhe_opts.add_option("-N", dest="nevents", default=1000, type=int, help="number of events per job")
lhe_opts.add_option("-d","--decay",dest="ttbar_decay_channel", default=None, help="speficy ttbar decay channel [0L/1L/2L/incl]")
lhe_opts.add_option("--process-lhe","--lhe",dest="process_lhe", default=False, action="store_true", help="process the output of the LHE step (4) after its completion")
parser.add_option_group(lhe_opts)

parser.add_option("-w", dest="workdir", default=None, help="path to workdir that is created after initialization (not needed for --init)")
parser.add_option("-S", dest="stage", default=1, help="parallel stage to run")
parser.add_option("-X", dest="iteration", default=1, help="iteration to run (relevant for stage 1)")
parser.add_option("-n", dest="nbatches", default=1000, help="number of batches")
parser.add_option("--force","-f", dest="force", default=False, action="store_true", help="force re-execution ")
parser.add_option("--validate","-v", dest="validate", default=False, action="store_true", help="Validate the specified stage/iteration")
(opts, args) = parser.parse_args()

if opts.process_lhe: 
    # set stage 4 and validate flags for LHE processing
    opts.stage = 4
    opts.validate = True
elif int(opts.stage) == 4:
    # make sure a ttbar decay channel is specified
    if opts.ttbar_decay_channel is None:
        raise ValueError(
            f"Need to specify a ttbar decay channel for LHE production [0L/1L/2L/incl]")
    elif not opts.ttbar_decay_channel in ["0L", "1L", "2L", "incl"]:
        raise ValueError(
            f"Invalid choice for ttbar decay channel ({opts.ttbar_decay_channel}). The options are [0L/1L/2L/incl]")


# Initialize in first call
if opts.init:
    import setup
    setup.setup(opts)
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
if opts.stage == "decay": 
    opts.stage = "5"
    print(f"You chose stage 'decay' which will be referred to as stage '5' internally.")
if int(opts.stage) in [1,2,3,4,5]:
    stage_status = settings[f"stage{opts.stage}"]
    if stage_status and not opts.force:
        print(f"\nParallelstage {opts.stage} has already been run for this setup. If you want to force a re-run, please re-execute this command and add the flag '--force'.")
        exit()
    if int(opts.stage) == 1:
        it_status = settings[f"stage1_it"]
        if it_status < int(opts.iteration)-1 and not opts.force:
            val = "NONE" if it_status == 0 else f"X={it_status}"
            print(f"\nThe last validated iteration is {val} and you requested X={opts.iteration}. Make sure this is what you want to do, or adjust the requested iteration. You can force the iteration you requested by re-executing this command and adding the flag '--force' or validate the previous iteration via '--validate'.")
            exit()
    else:
        last_stage_valid = settings[f"stage{int(opts.stage)-1}"]
        if (not last_stage_valid) and not (opts.force or opts.validate):
            print(f"\nYou requested to run stage S={opts.stage}, but the last stage has not yet been validated. You can validate the previous stage by appending '--validate' to the submit command of the previous stage to register its succesful completion. You can also force the execution of your current stage by re-executing the command and adding the flag '--force'.")
            exit()

from validate import check_stage_output
if opts.validate:
    print(f"Validating output of stage={opts.stage}, iteration={opts.iteration}...")
    # validate stage
    all_exist, missing_ids = check_stage_output(
        settings=settings,
        nbatches=int(opts.nbatches),
        stage=int(opts.stage),
        iteration=int(opts.iteration),
        workdir=opts.workdir,
        )
    if not all_exist:
        print(f"Not all files were found in output directory\n\t{settings['run_dir']}")
        print(f"List of jobids with missing files: {missing_ids}")
        if not opts.force:
            print(f"Validation unsuccessful, exiting.")
            exit()
    else:
        print(f"Validation successful, changing status in workdir...")
        if not opts.process_lhe:
            if int(opts.stage)==1:
                settings[f"stage1_it"] = int(opts.iteration)
            else:
                settings[f"stage{opts.stage}"] = True

            with open(settings_path, "w") as yf:
                yaml.dump(settings, yf, default_flow_style=False, indent=4)
            print(f"You can now proceeed with the next stage.")
            exit()
    
else:
    # check if the output of the requested stage is already available
    any_exist, _ = check_stage_output(
        settings=settings,
        nbatches=int(opts.nbatches),
        stage=int(opts.stage),
        iteration=int(opts.iteration),
        workdir=opts.workdir,
        any_exist=True
        )
    if any_exist and not opts.force:
        print(f"\nFound output files of stage={opts.stage}, it={opts.iteration} in output directory\n\t{settings['run_dir']}")
        query = input(f"Stop execution (stop/quit/s/q/n) or delete old files (delete/del/d/y)? ")
        if query[0].lower() in ["d","y"]:
            print("Deleting old files...")
            # TODO
            print("not yet implemented ..")
            exit()
        else:
            print("Exiting.") 
        exit()

if opts.process_lhe:
    from lhe_postprocess import lhe_postprocess
    # make new lhe directory in working area
    lhe_dir = os.path.join(opts.workdir, "lhe")
    if not os.path.exists(lhe_dir):
        os.mkdir(lhe_dir)
    v = 1
    while os.path.exists(os.path.join(lhe_dir, f"v{v}")):
        v += 1
    out_dir = os.path.abspath(os.path.join(lhe_dir, f"v{v}"))
    os.mkdir(out_dir)
    lhe_postprocess(
        settings=settings,
        out_dir=out_dir
        )
    exit()

## TODO validation
## TODO validate that the number of batches matches the previous iteration
from submit_handler import submit_handler
submit_handler(
    settings=settings,
    nbatches=int(opts.nbatches),
    stage=int(opts.stage),
    iteration=int(opts.iteration),
    nevt=int(opts.nevents),
    ttbardecay=opts.ttbar_decay_channel,
    workdir=opts.workdir,
    finalization=False
    )


