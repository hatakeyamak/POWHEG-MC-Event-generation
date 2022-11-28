import sys
import os
import stat
import string
import subprocess
from glob import glob
from top_2_root import top_2_root

def makeRootFiles (process , mass , pdf , renscfact , facscfact ):
    

        
        # check if given argument is a process directory in POWHEG-BOX-V2 or POWHEG-BOX-RES
        if 'POWHEG' not in os.path.dirname(process):
            print 'Error: Argument ' + str(process) + ' is not a POWHEG process directory' + '\nGeneration aborted!'
            return
        
        targetFile = "pwg-all-NLO.root"
        process = process+'/run_PDF_'+pdf+'_M_'+mass+"_muR_"+str(renscfact)+"_muF_"+str(facscfact)
        # generate directory system
        work_dir = os.getcwd()
        process_name = os.path.basename(os.path.abspath(process))
        # create the folder in which the run is executed
        runFolder = os.path.abspath(process)

        if not os.path.exists(runFolder):
            print "runFolder does not exist!!! ", runFolder

        # Need to copy the powheg inputsave file before scripts are run
        os.chdir(runFolder)
        print(runFolder)
        topFiles = glob("pwg-0*-NLO.top")

        for topFile in topFiles:
            # print "Processing ", topFile
            top_2_root(topFile)

        # After all top files are converted, the root files are hadded
        rootFiles = glob("pwg-0*-NLO.root")
        rootFileString = ""
        for rootFile in rootFiles:
            rootFileString += rootFile + " "



        if os.path.exists(targetFile):
            os.remove(targetFile)
        
        cmd = 'hadd '+targetFile+' '+rootFileString
        subprocess.call(cmd, shell = True)

        # if not os.path.isfile("powheg.input-save") :
        #     cmd = 'cp ../powheg.input-save .'
        #     subprocess.call(cmd, shell = True)
        
        # os.chdir(work_dir)
        # # generate a jobscript for each batch
        # for batch in range(nbatches):
        #     filename = os.path.abspath('./GenData/' + process_name) + '/jobscript_batch_' + str(batch) + '.sh'
        #     if os.path.isfile(filename):
        #         os.remove(filename)
        #     with open(filename, 'wb') as scriptfile:
        #         scriptfile.write('#!/bin/bash\n\n')
        #         scriptfile.writelines(['export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase\n',
        #                                 'source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh\n',
        #                                 'export RUCIO_ACCOUNT=$USER\n',
        #                                 'asetup AnalysisBase,21.2.225,here\n',
        #                                 ])
                
        #         scriptfile.writelines(['# run POWHEG process ' + str(process_name) + ' batch number ' + str(batch) + '\n',
        #                                'cd ' + str(os.path.abspath(process)) + '\n'])
        #         if decay == True:
        #             scriptfile.writelines(['echo pwgevents-' + str(batch).zfill(4) + '.lhe | ./lhef_decay\n',
        #                                     'echo "</LesHouchesEvents>" | gzip - | cat - >> pwgevents-' + str(batch).zfill(4) + '-decayed.lhe \n'])
                    
        #         else:
        #             scriptfile.writelines(['echo ' + str(batch) + ' | ./../pwhg_main-gnu' '\n'])

        #         scriptfile.write('cd ' + str(os.path.abspath(work_dir))+'\n')
                
                
        print 'All TOP files are converted and hadded ' + runFolder
        # status = os.stat(filename)
        # os.chmod(filename, status.st_mode | stat.S_IEXEC)

        
        os.chdir(work_dir)
        outputFolder = "powheg_generations"
        if not os.path.exists(outputFolder):
            os.mkdir(outputFolder)


        # os.chdir(outputFolder)
        copy_folder = outputFolder +"/"+process_name
        print "Copying files to " + copy_folder 
        if not os.path.exists(copy_folder):
            os.mkdir(copy_folder)

        cmd = "cp "+ process +"/" + targetFile +" "+ copy_folder+"/."
        subprocess.call(cmd, shell = True)

        os.chdir(work_dir)

                
def main (args = sys.argv[1:]):
        
    process = args[0]
    mass    = args[1]
    pdf     = args[2]
    renscfact   = float(args[3])
    facscfact   = float(args[4])
    
    makeRootFiles(process = process, mass = mass, pdf = pdf, renscfact = renscfact, facscfact = facscfact)
    

if __name__ == '__main__':
    main()
