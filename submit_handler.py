import sys
import os
from glob import glob
import subprocess
import re


thisdir = os.path.dirname(os.path.realpath(__file__))
thisdir = os.path.abspath(thisdir)

classdir = os.path.join(thisdir, "base", "classes")

# TODO: check for the submit script and add it
if not classdir in sys.path:
    sys.path.append(classdir)
    
from batchConfig_base import batchConfig_base


# TODO: check if the other python functions for the generation process are in the right path and add them
if not thisdir in sys.path:
    sys.path.append(thisdir)
    
print sys.path

from change_input import change_inputfile
from make_seeds import make_seeds
from create_scripts import create_scripts




def submit_handler(nbatches, processes):
    
    # 1st step: make the seed files (make_seeds) for the according process in POWHEG-BOX-[version]/[ProcessName]/pwgseeds.dat
    if not os.path.isfile(os.path.realpath(processes[0])):
        make_seeds(nbatches, processes)

    print 'Powheg seeds initialized!\n'
        
    
    # 2nd step: create the submit scripts (create_scripts): current_dir/GenData/[ProcessName]/jobscript_batch_[BatchNumber]
    create_scripts(nbatches, processes)
    print 'Jobscripts written!\n'
    
    
    # 3rd step: change the in the process directory already existing powheg.input file to the accoring parallel stage and start the script
    # number of POWHEG generation stages: default 5 stages in parallel generation (see change_input.py for more info)
    stages = [11, 12, 2, 3, 4]
    
    for n, stage in enumerate(stages):
    	print 'Start with generation step parallelstage ' + str(stage) + ':\n'
        # change the powheg.input file for each process according to the stage
        change_inputfile(stage, processes)
        
        jobids =[]
        
        for iprocess, process in enumerate(processes):
            
            if n == 0:
	            # check if old pwggridinfo*.dat, pwg-*.top, pwggrid*.dat, pwgfullgrid*.dat, pwgubound*.dat  files from previous generation exists
	            # if they exist, remove them to make sure to preserve a statistically independent generation process
	            print 'Checking for old generation remnants ......\n'
	            work_dir = os.getcwd()

	            process = os.path.abspath(process)
	            
	            os.chdir(process)
	            genfiles = glob('pwggrid*.dat')
	            genfiles += glob('pwg*.top')
	            genfiles += glob('pwgfullgrid*.dat')
	            genfiles += glob('pwgubound*.dat')
	            genfiles = [os.path.abspath(x) for x	 in genfiles]
	            for genfile in genfiles:
	                os.remove(genfile)
	            print 'Generation remnants removed. Can start clean generation.\n'
            
            # define which scripts should be submitted
            process_name = os.path.basename(process)
            target_dir = os.path.join(work_dir, 'GenData', process_name)
            os.chdir(target_dir)
            scripts = glob("*.sh")
            scripts = [os.path.abspath(x) for x in scripts]
            
            # directory for the array scripts
            foldername = "SubmitArrays"
            if not os.path.exists(foldername):
                os.mkdir(foldername)
            os.chdir(foldername)
            
            # set the job properties
            print 'Setting job porperties ... \n'
            bc = batchConfig_base()
            bc.diskspace = 3000000
            bc.runtime = 86400 #n times 24h 
            
            # submit the batches in the current stage as an arrayjob to the cluster
            print 'Submitting jobs ... \n'
            arrayscriptpath = "stage_" + str(stage) + ".sh"
            jobids += bc.submitArrayToBatch(scripts = scripts, arrayscriptpath = arrayscriptpath)
            print 'Jobs submitted!\n'
            
            os.chdir(work_dir)
            
        # wait till the jobs are finished, before the next stage is started
        print 'Waiting for jobs to finish ... \n'
        bc.do_qstat(jobids)
        print 'Parallelstage ' + str(stage) + ' finished. \n'
        
    # last step: if all generation steps are finished, move the generated events .lhe and the pwgseeds.dat into the Gendata directory
    print 'All generation steps finished. Finalizing ...\n'
    for process in processes:

            process = os.path.abspath(process)
            process_name = os.path.basename(process)
            work_dir = os.path.abspath(os.getcwd())
            target_dir = os.path.join(work_dir, "GenData", process_name)

            # get all the event .lhe files in process directory
            os.chdir(process)
            data_origin = glob('pwgevents-????.lhe')
            data_origin = [os.path.abspath(x) for x in data_origin]

            # check for the highest .lhe-file's batch number in target directory
            os.chdir(target_dir)
            data_target = glob('*.lhe')
            highest = 0
            for datafile in data_target:
            	dataname = os.path.basename(datafile)
            	numbers = re.search(r'\d+', dataname).group()
            	if int(numbers) > highest: highest = int(numbers)

            # put the datafiles into the GenData directory, rename the datafiles, if the batch number already exists
            for datafile in data_origin:
                dataname = os.path.basename(datafile)
                numbers = re.search(r'\d+', dataname).group()                
                dataname = dataname.replace(numbers, str(int(numbers)+ highest))                
                os.rename(datafile, os.path.join(target_dir, dataname))

            # also move the pwgseeds.dat file to the target directory and rename it according to the highest batch number
            seedfile = os.path.abspath(os.path.join(process, 'pwgseeds.dat'))
            os.rename(seedfile, os.path.join(target_dir, 'pwgseeds_batchnum>'+str(highest)+'.dat'))
                
            os.chdir(work_dir)

    print 'Finished! You can find all generated data and the seeds used for the generation within the GenData directory.'
        

def main(args = sys.argv[1:]):
    if not(args[0].isdigit()):
        print 'Wrong usage! First argument has to be an integer, representing the number of batches, further arguments should be directories to a POWHEG process\nAbort!'
        exit(0)
        
    nbatches = int(args[0])
    processes = args[1:]
    
    submit_handler (nbatches = nbatches, processes = processes)

if __name__ == '__main__':
    main()
