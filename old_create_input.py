##################################################################################################################################
# This python script generates the batches' powheg.input files for the chosen processes, setting the batch number as seed        #
# for any Powheg process and stores them into ./GenData/[ProcessName]/ .                                                         #
#                                                                                                                                #
# Also it sets the number of events per batch and renames the files according to [NAMEofPROCESS]_[NBATCH]_[SEED]_powheg.input    #                           
#                                                                                                                                #
# USAGE: python test.py [NEVENTS] [NBATCHES] [file1] [file2] ... [fileN]                                                         # 
#   fileN are the appropriate powheg.input files for the processes                                                               #
#   NEVENTS is the number of events per batch                                                                                    #
##################################################################################################################################

import sys
import os



# function to set NEVENTS and SEED in the base powheg.input and write it to filename
def generate_file(powheginput_file, seed, nevents, filename):
    # make the seed at least 8 characters long
    for iseed in range(0, 8-len(str(seed))):
        seed = '0' + str(seed)
    s = powheginput_file % {
            'SEED' : str(seed),
            'NEVENTS' : str(nevents)
            }
    with open(filename, "w") as outfile:
        outfile.write(s)
    print 'finished writing: ', os.path.basename(filename)
    
    

def main(args = sys.argv[1:]):
    
    # first argument given is [NEVENTS]
    nevents = int(args[0])
    # second argument is [NBATCHES]
    nbatches = int(args[1])
    # further arguments are the process specific powheg.input files
    configs = args[2:] 
    
    # loop over all given processes in the arguments
    for config in configs:
        # check if given argument is a powheg.input file
        if not(os.path.isfile(config)) or 'powheg.input' not in config:
            print 'argument ' + str(config) + ' is not a powheg.input file'
            break
        
        # get the name of the process
        tmp_dirname = os.path.dirname(os.path.abspath(config))
        tmp_processname = tmp_dirname.split('/')
        process_name = tmp_processname[len(tmp_processname)-3]
        
        # make a directory for the according process to dump your input files in
        if not os.path.exists('./GenData'):
            os.mkdir('./GenData')
        if not os.path.exists('./GenData/' + process_name):
            os.mkdir('./GenData/' + process_name)
        
        # read the according powheg.input file in and write it into a string
        print '_'*150
        print "reading config:", config
        print ''
        
        powheginput_file = ""
        lines = []
        with open(config, "r") as infile:
            lines = infile.read().splitlines()
        powheginput_file = "\n".join(lines)
        
        # generate the [NAMEofPROCESS]_[NBATCH]_powheg.input files
        path_base = os.path.basename(config)
        for i in range(0,nbatches):
            # set the seed
            seed = i+1
            
            # rename the powheg.input file according to the pattern [NAMEofPROCESS]_[NBATCH]_powheg.input
            filename = path_base.replace("powheg.input", process_name + "_{0}_{1}_powheg.input".format(nevents,seed))
            # set the path of the new powheg.input file to ./GenData/[NameOfProcess]/
            filename = os.path.abspath('./GenData/' + process_name) + '/' + os.path.basename(filename)
            
            # actually generate your desired .input files
            generate_file(powheginput_file = powheginput_file, seed = seed, nevents = nevents, filename = filename)
            
        print '\nAll input files created for POWHEG process:\t', process_name, '\nYou can find them in ', os.path.abspath('./GenData/' + process_name)
        print '_'*150

if __name__ == '__main__':
    main()