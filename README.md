# Instructions for the ttb-jets MC event production with POWHEG-BOX-RES

### Prepare the python scripts for the automated event generation
Clone [this git repository](https://gitlab.cern.ch/kit-cn-cms/powheg-event-generation) and checkout into the tree `production`.
Next set the environment by adding these lines
```console
##########################################################
### Set the PATH environment right for use with POWHEG ###
##########################################################
#add the LHAPDF library path to PATH
PATH=$PATH:/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/lhapdf/6.2.1-fmblme/bin/
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/lhapdf/6.2.1-fmblme/bin/

#add the FASTJET library path to PATH
PATH=$PATH:/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/fastjet/3.1.0/bin/
echo "setup POWHEG"
```
to your setup command file and source it. Next source CMSSW, to ensure a FORTRAN comppiler newer than version 5 is loaded.


### Installation of POWHEG-BOX-RES and ttbb
Checkout
```console
svn checkout --revision 3604 --username anonymous --password anonymous svn://powhegbox.mib.infn.it/trunk/POWHEG-BOX-RES
```
.
This will create a directory `POWHEG-BOX-RES`. Enter it and clone the `ttbb`-process.
```console
cd POWHEG-BOX-RES
git clone ssh://git@gitlab.cern.ch:7999/tjezo/powheg-box-res_ttbb.git ttbb
```
Enter the `ttbb`-directory and compile the Fortran code.
```console
cd ttbb
make
```

### Prepare the run
Copy the input config `powheg.input-save` and the reweighting file `pwg-rwl.dat` into your process directory.
```console
cp /afs/cern.ch/user/m/mhorzela/public/ttbb_PowOl/configs/* /path/to/POWHEG-BOX-RES/ttbb
```

[//]: # cp /nfs/dust/cms/user/mhorzela/{pwg-rwl.dat,powheg.input-save} /path/to/POWHEG-BOX-RES/ttbb

Next do
```console
cp /afs/cern.ch/user/m/mhorzela/public/ttbb_PowOl/grids/nominal/* /path/to/POWHEG-BOX-RES/ttbb
```

[//]: # cp /nfs/dust/cms/user/matsch/ttbb_production/POWHEG-BOX-RES/ttbb/*fullgrid* /path/to/POWHEG-BOX-RES/ttbb
[//]: # cp /nfs/dust/cms/user/matsch/ttbb_production/POWHEG-BOX-RES/ttbb/*pwgubound* /path/to/POWHEG-BOX-RES/ttbb

to prepare the generation of events in parallelstage 4.

### Run the Powheg MC ttb-jets event generation
Now everything should be prepared. First make sure you have a valid voms-proxy.
Start a screen session and setup the environment described above and CMSSW.
Start the event generation by executing
```console
python /path/to/powheg-event-generation/submit_handler.py 1000 /path/to/POWHEG-BOX-RES/ttbb
```
.

If you produce events for the first time, type in yes, to generate a new seedsfile. Next type in 4 to begin the generation in parallelstage 4.

[//]: # The script will automatically produce the MC events in seven stages. 
[//]: # Each stage has to finish completely, before the next stage can start.
[//]: # Alternatively you could also execute the stages by hand. 
[//]: # This is only recommended for debugging and cross-checking.


# Documentation and Prescription :+1:

## Preparation
For this scripts to work, make sure you have the according POWHEG process installed within your POWHEG-BOX, and you have executed `make pwhg_main` within the process directory. 
POWHEG will execute the executable `[process_dir]/pwhg_main` more than once during the event generation. So make sure the executable works.

### How to install POWHEG
#### Download the POWHEG-BOX
To install POWHEG just follow the steps stated at the bottom of the [homepage of the POWHEG-Box](http://powhegbox.mib.infn.it/). 
For most common processes it POWHEG-V2 should be sufficient. If you want to generate some more specific processes, you will need POWHEG-RES.
A list of processes with the needed POWHEG version is also given at the top of [the POWHEG-BOX homepage](http://powhegbox.mib.infn.it/).

#### Setting up the environment
For most POWHEG processes, POWHEG will need additional packages, e.g. the LHAPDF and FASTJET libraries. In CMSSW these libraries are already included. 
You can find the path to the executables in the `[package].xml` files within your `CMSSW_X_X_X/config/toolbox/slc6_amd64_gcc630/tools/selected/` directory.
For most systems it is sufficient to add `lhapdf-config` and the `fastjet-config` executables to your `$PATH`, and in case of the `lhapdf-config` also to your `$LD_LIBRARY_PATH`, environmental variable.
If this doesn't work, well, you're screwed. In this case you have to modify the `Makefile` which rules the compilation of the Fortran code.

#### Compile
Now if everything is set, do:
```console
cd POWHEG-BOX/proc_dir
make <target>
```
whereas `<target>` is `pwhg_main` in our case. 

## Configure your process
If your desired **POWHEG** processes are in principle working, the first step before starting the automation provided by this scripts is to write a `powheg.input` file 
(usually there are example files included in the process directory), which satisfies your needs. 
Next add the line `manyseeds 1` to your `powheg.input` file and save it as `powheg.input-save` within your process' main directory.

Now everything should be prepared to start the "fully" automated event generation.

## Running the parallel event generation on the HTCondor
To start the automation, execute:

```console
python submit_handler.py [number of batches] [list/of/process/dirs]
```

This will generate pwgevents-[Nbatch].lhe files firstly within the process directory and mv these afterwards automatically to a new made directory `./GenData/[process_name]/`. 
If you want to examine the seeds used for the generation, just have a look into the `pwgseeds.dat` file, which is also moved into the same directory. 

Be aware, that: 
 * The script will generate the GenData directory in your current working directory. So make sure that you are executing the script, where you want your .lhe event files saved. 
 * Due to some random internal POWHEG settings, you can't generate more than 200 batches at the same time. If you want to generate more batches, just run the submit_handler several times. It will automatically check for the highest batch number already existing in your GenData directory and rename the generated .lhe files with a higher batch number, so no batches will be overwritten.
 * At the moment the submit_handler is only configured for HTCondor systems. So be sure you run your parallel generation on a HTCondor like system.

## Stuff for more interested users
If **POWHEG** is run in parallelmode, there are 4 parallelstages in the generation process, whereas each has to be finished, before the next stage is started. 
For further information see <http://th-www.if.uj.edu.pl/~erichter/POWHEG-BOX-V2/Docs/V2-paper.pdf>.

If you are interested in how the submit_handler works, either have a look into the python code (recommended: it's very simple and well commented) or investigate the following short overview:
 1. The script calls `make_seeds.py` to make the `pwgseeds.dat` file, which stores the random seeds for the event generation.
 2. It removes all remnants of previous MC event generations.
 3. It writes the bash scripts (`create_scripts.py`), which set the necessary environment for POWHEG to work and execute *pwhg_main* with piping the batch number of the according batch. 
 4. It modifies the `powheg.input` file (by calling `change_input.py`), adding the line `parallelstage X`, whereas `X` is an integer 1, 2, 3 or 4 which corresponds to the parallelstage. 
    If X==1 it additionally adds the line `xgriditeration Y`, where `Y` is an integer bigger than 0. Typically it is sufficient to run the first POWHEG stage in `parallelstage 1` with two grid iterations.
    Therefore the script calls the first stage two times. If more grid iterations are desired, you have to change the code.
 5. It submits the bash scripts to the cluster (`base/classes/batchConfig_base.py`), which executes the bash scripts and waits till all jobs are finished, before the next step is started.
 6. It repeats steps 2. to 5. with raised parallelstage value by 1 untill all parallelstages are finished (parallelstage 4 is the last step) and your desired `pwgevents-[Nbatch].lhe` output are written out.
 7. It moves the `pwgevents-[Nbatch].lhe` and the `pwgseeds.dat` into the `./GenData/[process_name]/` directory. Where you can access it easily as a user.




