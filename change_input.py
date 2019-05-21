import os
import sys
import subprocess


# change the input file accoring to the stage of parallel run performing
def change_inputfile(stage, processes):
    
    for process in processes:
        
        process = os.path.abspath(process)
        
        # check if given argument is a process directory in POWHEG-BOX-V2
        if not(os.path.isdir(process)) or  'POWHEG' not in os.path.dirname(process):
            print 'Argument ' + str(process) + ' is not a POWHEG process directory' + '\njob aborted'
            continue
        
        if not os.path.isfile(os.path.join(process, 'powheg.input-save')):
            print 'Template powheg.input-save doesn\'t exist, make sure it does, if you want to run POWHEG in parallel mode.'
            sys.exit()
        
        # change the powheg.input file for the process according to the parallelstage
        workdir = os.getcwd()
        os.chdir(os.path.abspath(process))
        # importance sampling grid calculation
        # stage 1 equivalent to stage 1.1: parallelstage 1 xgriditeration 1
        if str(stage) == str(1) or str(stage) == str(11) :
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 1\" >> powheg.input; echo \"xgriditeration 1\" >> powheg.input'
            subprocess.call(cmd, shell = True)
        # stage 1.2: parallelstage 1 xgriditeration 2
        elif str(stage) == str(12):
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 1\" >> powheg.input; echo \"xgriditeration 2\" >> powheg.input'
            subprocess.call(cmd, shell = True)
        
        # stage 1.3: parallelstage 1 xgriditeration 3
        elif str(stage) == str(13):
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 1\" >> powheg.input; echo \"xgriditeration 3\" >> powheg.input'
            subprocess.call(cmd, shell = True)
            
        # stage 1.3: parallelstage 1 xgriditeration 3
        elif str(stage) == str(14):
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 1\" >> powheg.input; echo \"xgriditeration 4\" >> powheg.input'
            subprocess.call(cmd, shell = True)
            
        # stage 1.3: parallelstage 1 xgriditeration 3
        elif str(stage) == str(15):
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 1\" >> powheg.input; echo \"xgriditeration 5\" >> powheg.input'
            subprocess.call(cmd, shell = True)
            
        # stage 1.3: parallelstage 1 xgriditeration 3
        elif str(stage) == str(16):
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 1\" >> powheg.input; echo \"xgriditeration 6\" >> powheg.input'
            subprocess.call(cmd, shell = True)
            
        # stage 1.3: parallelstage 1 xgriditeration 3
        elif str(stage) == str(17):
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 1\" >> powheg.input; echo \"xgriditeration 7\" >> powheg.input'
            subprocess.call(cmd, shell = True)
            
        # stage 1.3: parallelstage 1 xgriditeration 3
        elif str(stage) == str(18):
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 1\" >> powheg.input; echo \"xgriditeration 8\" >> powheg.input'
            subprocess.call(cmd, shell = True)
            
        # compute NLO and upper bounding envelope for the generation of the underlying born configurations
        elif str(stage) == str(2):
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 2\" >> powheg.input; echo \"xgriditeration 1\" >> powheg.input'
            subprocess.call(cmd, shell = True)
            
        # compute upper bounding coefficients for radiation
        elif str(stage) == str(31) or str(stage) == str(32):
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 3\" >> powheg.input; echo \"xgriditeration 1\" >> powheg.input'
            subprocess.call(cmd, shell = True)
            
        # generate events
        elif str(stage) == str(4):
            cmd = 'cat powheg.input-save > powheg.input; echo \"parallelstage 4\" >> powheg.input; echo \"xgriditeration 1\" >> powheg.input'
            subprocess.call(cmd, shell = True)
        
        # decay event files
        elif str(stage) == "decay":
            cmd = 'cat powheg.input-save > powheg.input'
            subprocess.call(cmd, shell = True)
            
        os.chdir(workdir)



def main (args = sys.argv[1:]):
    if not(args[0].isdigit()):
        print 'Wrong usage! First argument has to be the stage number: \n[1] for importance sampling grid calculation (1st step) \n   optional: [1.1] or [1.2] for the iteration of the grid \n[2] for NLO and upper bounding envelope (2nd step) \n[3] for upper bounding coefficients \n [4] for event generation \nAbort!'
        exit(0)
        
    stage = int(args[0])
    processes = args[1:]
    
    change_inputfile (stage = stage, processes = processes)
    

if __name__ == '__main__':
    main()
