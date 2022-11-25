#!/usr/bin/env python

###############################################################
##  Author:   David Hall
##  Email:    David(dot)Hall(at)physics(dot)ox(dot)ac(dot)uk
##  Date:     15th August 2013
##  Program:  top2root
##
##  This program reads in a topdrawer file and converts the
##  plots contained within to the ROOT histogram format.
##  It assumes that you have a copy of PyROOT installed and
##  the appropriate environment variables set.
###############################################################
import sys, os,re,ROOT
import array

class DataPoint:
    def __init__(self, x, y, dy=0):
        self.x  = x
        self.y  = y
        self.dy = dy

class Plot:
    def __init__(self, input): 
        self.data           = []
        self.xaxislowbound  = []
        self.xaxishighbound = []
        self.binEntries     = []
        self.binUncert      = []

        self.xaxistitle = ""
        self.yaxistitle = ""

        dataFlag = False
        for line in input:
            if not dataFlag:
                if 'TITLE TOP' in line:
                    self.title = self.GetTitle(line)
                elif 'index' in line:
                    self.title = re.search(r'#(.*?)index', line).group(1)
                elif 'TITLE BOTTOM' in line:
                    self.xaxistitle = self.GetTitle(line)
                elif 'TITLE LEFT' in line:
                    self.yaxistitle = self.GetTitle(line)
                # elif 'SET LIMITS X' in line:
                #     self.xaxislowbound  = float(line.split()[-2])
                #     self.xaxishighbound = float(line.split()[-1])
                elif (not 'index' in line) and line.strip():
                    split_line = line.split()
                    self.xaxislowbound.append(float(split_line[0])) 
                    self.xaxishighbound.append(float(split_line[1]))
                    xValue = (float(split_line[1])-float(split_line[0]))/2.
                    self.binEntries.append(DataPoint(xValue,float(split_line[2]),float(split_line[3]) ))
                    # self.binUncert.append(float(split_line[3]))
                elif 'INTGRL' in line:
                    self.integral = float(line.split('INTGRL =')[1].split()[0])
                elif 'SET ORDER X Y' in line:   # Start data points
                    dataFlag = True
                    continue

            if dataFlag:
                if 'PLOT' in line:    # End data points
                    dataFlag = False
                else:
                    values = [float(word) for word in line.split()]
                    self.data.append(DataPoint(*values))

    def GetTitle(self, string):
        title = string.split('"')[1]
        return ' '.join(title.split())

    def GetDx(self):
        sumbins = 0.0
        for datum in self.data:
            sumbins += datum.y
        return self.integral / sumbins

    def GetTH1(self):
        lowXArray   = array.array('d',self.xaxislowbound)
        highXArray  = array.array('d',self.xaxishighbound)
        lowXArray.append(highXArray[len(highXArray)-1])
        hist = ROOT.TH1D(self.title.replace(' ', '_'), self.title, len(lowXArray)-1, lowXArray)
        hist.GetXaxis().SetTitle(self.xaxistitle)
        hist.GetYaxis().SetTitle(self.yaxistitle)
        for datum in self.binEntries:
            hist.SetBinContent(hist.FindBin(datum.x), datum.y)
            hist.SetBinError  (hist.FindBin(datum.x), datum.dy)
        return hist

    def GetTGraph(self):
        graph = ROOT.TGraphErrors()
        graph.SetNameTitle(self.title.replace(' ', '_'), self.title)
        graph.GetXaxis().SetTitle(self.xaxistitle)
        graph.GetYaxis().SetTitle(self.yaxistitle)
        for i, datum in enumerate(self.data):
            graph.SetPoint(i, datum.x, datum.y)
            graph.SetPointError(i, self.GetDx(), datum.dy)
        return graph

def top_2_root(inFilename, isGraph = False):

    import ROOT
    ROOT.gROOT.SetBatch()

    # for inFilename in args:
    base, ext = os.path.splitext(inFilename)
    if not ext:
        print '%s has no file extension' % inFilename
        return
    outFilename = base + os.extsep + 'root'

    ##############################
    #   Read-in topdrawer file   #
    ##############################
    print "reading ", inFilename
    print "creating ", outFilename
    inFile = open(inFilename, 'r')
    top_plots, plot_lines = [], []
    #skip first line with 
    first_plot_isSet = False
    for line in inFile:
        if line.strip():
            plot_lines.append(line)
        elif plot_lines:
            top_plots.append(Plot(plot_lines))
        else:
            plot_lines = []

        # if ('index' in line) and first_plot_isSet:
        #     top_plots.append(Plot(plot_lines))
        #     plot_lines[:] = []
        # else:
        #     plot_lines.append(line)
        #     first_plot_isSet=True            
    inFile.close()

    ##############################
    #   Write out to ROOT file   #
    ##############################
    outFile = ROOT.TFile(outFilename, 'recreate')
    root_plots = [plot.GetTGraph() if isGraph else plot.GetTH1() for plot in top_plots]

    for plot in root_plots:
        plot.Write()
    outFile.Close()


if __name__ == '__main__':
    import optparse

    ##############################
    #  Parse command line input  #
    ##############################
    usage = 'usage: %prog [-g] infile1.top infile2.top ...'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-g', '--graph', action='store_true', dest='isGraph', default=False,
                      help='Output TGraph (TH1 is default)')
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error('Please enter topdrawer filename')

    try:
        import ROOT
    except ImportError:
        print 'Please ensure your ROOT installation is in your PYTHONPATH'
        sys.exit(1)
    ROOT.gROOT.SetBatch()

    for inFilename in args:
        base, ext = os.path.splitext(inFilename)
        if not ext:
            print '%s has no file extension' % inFilename
            continue
        outFilename = base + os.extsep + 'root'

        ##############################
        #   Read-in topdrawer file   #
        ##############################
        inFile = open(inFilename, 'r')
        top_plots, plot_lines = [], []
        for line in inFile:
            if 'NEW PLOT' in line:
                top_plots.append(Plot(plot_lines))
                plot_lines[:] = []
            else:
                plot_lines.append(line)            
        inFile.close()

        ##############################
        #   Write out to ROOT file   #
        ##############################
        outFile = ROOT.TFile(outFilename, 'recreate')
        root_plots = [plot.GetTGraph() if options.isGraph else plot.GetTH1() for plot in top_plots]

        for plot in root_plots:
            plot.Write()
        outFile.Close()
