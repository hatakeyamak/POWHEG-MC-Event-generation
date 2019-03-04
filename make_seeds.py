'''
Create the seed file pwgseeds.dat for a given number of batches and given processes, which is needed for running POWHEG with the manyseedsflag 
'''



import sys
import os
import random
import string


def make_seeds (nbatches, processes):
    
    # loop over all given processes in the arguments
    for process in processes:
        process = os.path.abspath(process)
        # check if given argument is a process directory in POWHEG-BOX-V2
        if not(os.path.isdir(process)) or  'POWHEG' not in os.path.dirname(process):
            print 'Argument ' + str(process) + ' is not a POWHEG process directory' + '\njob aborted'
            continue
        # if it works go to process directory and write the seed file
        work_dir = os.getcwd()
        os.chdir(os.path.abspath(process))
        # make the seedfile, if already a seedfile exists, rename it and make a new one afterwards
        seedfile = os.path.join(process, "pwgseeds.dat")
        if os.path.exists(os.path.abspath(seedfile)):
            print "The seedfile pwgseeds.dat alread exists. Do you want to overwrite it?"
            confirmation = raw_input("y/n ")
            if any(confirmation == x for x in ["y","Y","yes","Yes", "YES"]):
                print "are you sure?"
                confirmation = raw_input("y/n ")
                if any(confirmation == x for x in ["y","Y","yes","Yes", "YES"]):
                    print "Overwriting pwgseeds.dat"
                else:
                    print "Keeping old pwgseeds.dat" 
                    os.chdir(work_dir)
                    continue
            else:
                print "Keeping old pwgseeds.dat"
                os.chdir(work_dir)
                continue
        seedfile_old = os.path.join(process, "old_pwgseeds.dat")
        if os.path.isfile(os.path.abspath(seedfile)):
            if os.path.exists(seedfile_old):
                os.remove(seedfile_old)
            os.rename(seedfile, seedfile_old)
        with open(seedfile, 'wb') as textfile:
            for i in range(nbatches):
                textfile.write(str(random.randint(0, 99999999))+'\n')
        os.chdir(work_dir)
    
    
    
def main (args = sys.argv[1:]):
    
    if not(args[0].isdigit()):
        print 'Wrong usage! First argument has to be an integer, representing the number of batches, further arguments should be a directory to a POWHEG process\nAbort!'
        exit(0)
    # first argument given is [NEVENTS]
    nbatches = int(args[0])
    # further arguments are the process specific directories
    processes = args[1:]
    
    make_seeds(nbatches = nbatches, processes = processes)
    
    

if __name__ == '__main__':
    main()
