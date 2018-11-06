## Preparation
For this scripts to work, make sure you have the according POWHEG process installed within your POWHEG-BOX, and you have executed *make pwhg_main* within the process directory. POWHEG will execute the executable *[process_dir]/pwhg_main* more than once during the event generation. So make sure the executable works.

## Configure your process
If your desired POWHEG processes are in principle working, the first step before starting the automation provided by this scripts is to write a powheg.input file (usually there are example files included in the process directory), which satisfy your needs. Next add the line *manyseeds 1* to your **powheg.input** file and save it as **powheg.input-save** within your process' main directory.

Now everything should be prepared to start the "fully" automated event generation.

## Running the parallel event generation on the HTCondor
To start the automation, execute:	python submit_handler.py [number of batches] [list/of/process/dirs]
This will generate pwgevents-[Nbatch].lhe files firstly within the process directory and mv these afterwards automatically to a new made directory ./GenData/[process_name]/ . Be aware, that: 
	- The script will generate the GenData directory in your current working directory. So make sure that you are executing the script, where you want your .lhe event files saved. 
	- Due to some random internal POWHEG settings, you can't generate more than 200 batches at the same time. If you want to generate more batches, just run the submit_handler several times. It will automatically check for the highest batch number already existing in your GenData directory and rename the generated .lhe files with a higher batch number, so no batches will be overwritten.
	- At the moment the submit_handler is only configured for HTCondor systems. So be sure you run your parallel generation on a HTCondor like system.




