


import sys
import os
import stat
import string

def create_scripts (nbatches, processes):
    
    for process in processes:
        
        # check if given argument is a process directory in POWHEG-BOX-V2 or POWHEG-BOX-RES
        if not(os.path.isdir(process)) or  'POWHEG' not in os.path.dirname(process):
            print 'Error: Argument ' + str(process) + ' is not a POWHEG process directory' + '\nGeneration aborted!'
            continue
        
        # generate directory system
        work_dir = os.getcwd()
        process_name = os.path.basename(os.path.abspath(process))
        if not os.path.exists('./GenData'):
            os.mkdir('./GenData')
        if not os.path.exists('./GenData/' + process_name):
            os.mkdir('./GenData/' + process_name)
        
        # generate a jobscript for each batch
        for batch in range(nbatches):
            filename = os.path.abspath('./GenData/' + process_name) + '/jobscript_batch_' + str(batch+1) + '.sh'
            if os.path.isfile(filename):
                os.remove(filename)
            with open(filename, 'wb') as scriptfile:
                scriptfile.write('#!/bin/bash\n\n')
                scriptfile.writelines(['# set the CMSSW environment and load all needed modules\n', 
                                       '#module use -a /afs/desy.de/group/cms/modulefiles/\n', 
                                       'export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch\n', 
                                       'source $VO_CMS_SW_DIR/cmsset_default.sh\n', 
                                       'export CMSSW_GIT_REFERENCE=/nfs/dust/cms/user/mhorzela/.cmsgit-cache\n', 
                                       'alias cd=\'cd -P\'\n', 
                                       'myvarcwd=$PWD\n', 
                                       'cd /nfs/dust/cms/user/mhorzela/CMSSW_9_4_9/src\n', 
                                       'eval `scramv1 runtime -sh`\n', 
                                       'cd ~\n', 
                                       'echo "setup CMSSW_949 and stuff"\n', 
                                       'cd $myvarcwd\n\n', 
                                       '#add the LHAPDF library path to PATH\n', 
                                       'PATH=$PATH:/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/lhapdf/6.2.1-fmblme/bin/\n', 
                                       'LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/lhapdf/6.2.1-fmblme/bin/\n', 
                                       '#add the FASTJET library path to PATH\n', 
                                       'PATH=$PATH:/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/fastjet/3.1.0/bin/\n', 
                                       'echo "setup POWHEG"\n\n'])
                
                scriptfile.writelines(['# run POWHEG process ' + str(process_name) + ' batch number ' + str(batch+1) + '\n',
                                       'cd ' + str(os.path.abspath(process)) + '\n'])

                scriptfile.writelines(['echo ' + str(batch) + ' | ./pwhg_main' '\n'])

                scriptfile.write('cd ' + str(os.path.abspath(work_dir)))
                
                
        print 'created scripts for POWHEG process ' + process_name
        status = os.stat(filename)
        os.chmod(filename, status.st_mode | stat.S_IEXEC)
                
def main (args = sys.argv[1:]):
    if not(args[0].isdigit()):
        print 'Wrong usage! First argument has to be an integer, representing the number of batches, further arguments should be directors to a POWHEG process\nAbort!'
        exit(0)
        
    nbatches = int(args[0])
    processes = args[1:]
    
    create_scripts(nbatches = nbatches, processes = processes)
    

if __name__ == '__main__':
    main()
