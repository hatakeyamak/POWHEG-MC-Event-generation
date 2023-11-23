import sys
import os
import yaml


def setup(opts):
    print("\n##################\n  INITIALIZATION  \n##################\n")
    # check validity of some options:
    if not os.path.exists(opts.input_file):
        raise ValueError(
            f"Input file\n  {opts.input_file}\ndoes not exist")
    if not os.path.exists(opts.process):
        raise ValueError(
            f"Process directory\n  {opts.process}\nin POWHEG-BOX-RES does not exist")

    # determine workdir
    dir_name = f"r{opts.muR}_f{opts.muF}_m{opts.mass}_p{opts.pdf}"
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

    # copy powheg input
    powheg_input_path = os.path.join(dir_path, "powheg.input")
    print(f"\nCopying powheg input file to working directory:\n\t{powheg_input_path}")
    os.system(f"cp {opts.input_file} {powheg_input_path}")
    # get pwg-rwl
    rwl_input_path = os.path.join(os.path.dirname(opts.input_file), f"pwg-rwl.dat_{opts.pdf}")
    if not os.path.exists(rwl_input_path):
        print(f"ERROR: pwg_rwl.dat file does not exist, expect it to be at\n\t{rwl_input_path}\nto match the given pdf set {opts.pdf}")
        exit()
    rwl_path = os.path.join(dir_path, "pwg-rwl.dat")

    # modify the rwl file according to the scale settings
    with open(rwl_input_path, "r") as f:
        lines = f.readlines()
    new_file = []
    in_head = False
    for l in lines:
        new_l = l
        if in_head:
            # modify header lines
            if "renscfact" in l and "facscfact" in l:
                new_l = []
                for elem in l.split(" "):
                    if "renscfact=" in elem or "facscfact" in elem:
                        sc, val = elem.split("=")
                        val = val.replace("d0","").replace("d",".")
                        try:
                            val = float(val)
                        except:
                            raise ValueError(f"Cannot convert {val} to float in line {l}")
                        if "rensc" in sc:
                            val *= float(opts.muR)
                        elif "facsc" in sc:
                            val *= float(opts.muF)
                        val = str(val).replace(".","d")
                        new_l.append(f"{sc}={val}")
                    else:
                        new_l.append(elem)
                new_l = " ".join(new_l)
                print(new_l.strip())

        if "name='scale_variation'" in l:
            # enter header
            print("\nModifying scale settings in pwg-rwl file...")
            in_head = True
        if "</weightgroup>" in l: 
            # leave header
            in_head = False
        new_file.append(new_l)

    with open(rwl_path, "w") as f:
        f.write("".join(new_file))
    print(f"\nWrote rwl input file to working directory:\n\t{rwl_path}\n")

    # generate a yml file with all settings
    settings = {
        "mass": float(opts.mass),
        "pdf": int(opts.pdf),
        "muR": float(opts.muR),
        "muF": float(opts.muF),
        "tag": opts.tag,
        "powheg.input": powheg_input_path,
        "pwg-rwl": rwl_path,
        "run_dir": run_dir,
        "name": dir_name,
        "stage1": False,
        "stage1_it": 0,
        "stage2": False,
        "stage3": False,
        "stage4": False,
        "stage5": False
        }
    yaml_file = os.path.join(dir_path, "settings.yml")
    with open(yaml_file, "w") as yf:
        yaml.dump(settings, yf, default_flow_style=False, indent=4)
    print(f"\nSaved settings in yaml file: {yaml_file}")
    
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
