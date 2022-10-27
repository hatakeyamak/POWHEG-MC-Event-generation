import sys
import os
import stat
import string
import subprocess
from glob import glob

def create_scripts (nbatches, process, mass, pdf, decay = False):
    

        
        # check if given argument is a process directory in POWHEG-BOX-V2 or POWHEG-BOX-RES
        if 'POWHEG' not in os.path.dirname(process):
            print 'Error: Argument ' + str(process) + ' is not a POWHEG process directory' + '\nGeneration aborted!'
            return
        
        # generate directory system
        work_dir = os.getcwd()
        process_name = os.path.basename(os.path.abspath(process))
        if not os.path.exists('./GenData'):
            os.mkdir('./GenData')
        if not os.path.exists('./GenData/' + process_name):
            os.mkdir('./GenData/' + process_name)
        
        # remove all already existing jobscripts in the GenData directory
        os.chdir(os.path.join(os.path.abspath("./GenData/"), process_name))
        for script in glob('*.sh'):
            os.remove(script)
        os.chdir(work_dir)

        # create the folder in which the run is executed
        runFolder = os.path.abspath(process)

        if not os.path.exists(runFolder):
            os.mkdir(runFolder)

        # Need to copy the powheg inputsave file before scripts are run
        os.chdir(runFolder)
        if not os.path.isfile("powheg.input-save") :
            cmd = 'cp ../powheg.input-save .'
            subprocess.call(cmd, shell = True)
        
        os.chdir(work_dir)
        # generate a jobscript for each batch
        for batch in range(nbatches):
            filename = os.path.abspath('./GenData/' + process_name) + '/jobscript_batch_' + str(batch) + '.sh'
            if os.path.isfile(filename):
                os.remove(filename)
            with open(filename, 'wb') as scriptfile:
                scriptfile.write('#!/bin/bash\n\n')
                scriptfile.writelines(['export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase\n',
                                        'source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh\n',
                                        'export RUCIO_ACCOUNT=$USER\n',
                                        'asetup AnalysisBase,21.2.225,here\n',
                                        ])
                
                scriptfile.writelines(['# run POWHEG process ' + str(process_name) + ' batch number ' + str(batch) + '\n',
                                       'cd ' + str(os.path.abspath(process)) + '\n'])
                if decay == True:
                    scriptfile.writelines(['echo pwgevents-' + str(batch).zfill(4) + '.lhe | ./lhef_decay\n',
                                            'echo "</LesHouchesEvents>" | gzip - | cat - >> pwgevents-' + str(batch).zfill(4) + '-decayed.lhe \n'])
                    
                else:
                    scriptfile.writelines(['echo ' + str(batch) + ' | ./../pwhg_main-gnu' '\n'])

                scriptfile.write('cd ' + str(os.path.abspath(work_dir))+'\n')
                
                
        print 'created scripts for POWHEG process ' + process_name
        status = os.stat(filename)
        os.chmod(filename, status.st_mode | stat.S_IEXEC)
                
def main (args = sys.argv[1:]):
    if not(args[0].isdigit()):
        print 'Wrong usage! First argument has to be an integer, representing the number of batches, further arguments should be directors to a POWHEG process\nAbort!'
        exit(0)
        
    nbatches    = int(args[0])
    processes   = args[1]
    mass        = args[2]
    pdf         = args[3]
    
    create_scripts(nbatches = nbatches, process = process, mass = mass, pdf = pdf)
    

if __name__ == '__main__':
    main()
