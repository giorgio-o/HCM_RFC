import numpy as np
import os
import sys
import subprocess
import re
import shutil
import time


# this is to be mouseDay's loadData method, but it is so big and ugly we want to define it in a separate source file 
# then we monkey-patch it on 


def corrupt_orig_data_file_handler(fullFilePE):
    print "Original data file has a problem, this is an exception handler!"
    print "the trouble is with file %s"%fullFilePE
    directory, basename = os.path.split(fullFilePE)
    print directory
    print basename
    if not basename[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        print 'First character of original data file name should be a number, stopping'
        sys.exit(0)

    bad_file_backup = os.path.join(directory, 
                                   'before_removal_of_last_bad_line_' + basename
                                   )
    
    print "saving a copy of the corrupt original to"
    print bad_file_backup
    shutil.copyfile(fullFilePE, bad_file_backup)
    
    lines = open(fullFilePE).readlines()
    while len(lines[-1])<=1:
        lines=lines[:-1]
    print "The last (bad) line used to be:"
    print lines[-1]
    
    print "Going to overwrite original with a fixed version"
    open(fullFilePE, 'w').writelines(lines[:-1])
    try:
        PE = np.loadtxt(fullFilePE,delimiter=',',dtype=np.double, ndmin=2)
    except ValueError:  
        print "Something scary has happened:  fixing it did not fix it!"
        print "Go check what is still wrong with file"
        print fullFilePE
        sys.exit(-1)

    return PE
    

def loadOriginalData(self):
    """
    I am a method of the mouseDay class.  
    If a mouseDay has already been given attributes 
    MEFileName, PEFileName, LEFileName, and AMFileName, and MSIFile
    then I can be called without crashing.
    
    """ 

    nan = np.nan
    fullFileME = self.MEFileName
    fullFilePE = self.PEFileName
    fullFileLE = self.LEFileName        
    fullFileAM = self.AMFileName
    self.foodGramsPerDay = self.chow_eaten_grams # copy to access via old names, needs refactoring
    self.waterGramsPerDay = self.water_drunk_grams # copy to access via old names, needs refactoring
    print "loading original data.."
    # Load the data files into a numpy arrays
    if fullFileME[-1] == 'y':
        print "YO the ME file should NOT end in a y"
        sys.exit(1)
    binaryME = fullFileME+'.npy' # a binary version of the raw ME file that loads faster 
    # print "About to ATTEMPT to load binary file %s"%binaryME
    try:
        comp_time_1 = time.clock()
        ME = np.load(binaryME)
        comp_time_2 = time.clock()
        print "Loading ME file %s from binary format takes merely %f seconds." % (binaryME, comp_time_2 - comp_time_1)
    except IOError:
        print "There is not a binary version apparently? Attempting to (slowly) load .csv version of ME file. %s" % (fullFileME)
        comp_time_1 = time.clock()
        try:
            ME = np.loadtxt(fullFileME,delimiter=',',dtype=np.double, ndmin=2)
        except IOError:
            raise IOError("Something the matter when loading .csv file %s"%(fullFileME))
        comp_time_2 = time.clock()
        print "Loading .csv version of ME file %s from SSD took %f seconds, which is kind of a long time." % (fullFileME, comp_time_2 - comp_time_1)
        try:
            np.save(binaryME, ME)
            print "Binary version written to %s so we never have to read the .csv version again." % (binaryME)
        except IOError:
            raise IOError()
    
    self.recordingStartTime=ME[0,0]/1000.0 #this is what we have been told

    #print "So we assume recording started at %f"%(self.recordingStartTime/3600.0)
    #print fullFileAM
    # # old darren stuff (1)
    # #print "So we assume recording started at %f"%(self.recordingStartTime/3600.0)
    # #print fullFileAM
    # random_int = np.random.randint(2000000000)
    # full_temp_file_name = "%stemporaryAMData%d.txt"%(self.experiment.binary_dir, random_int)
    # subprocess.call([dataDirRoot()+"AMFileReaderDir/readAMFile %s > %s"%(fullFileAM, full_temp_file_name)],shell=True)
    # AMData=np.loadtxt(full_temp_file_name)
    # subprocess.call(["rm %s"%(full_temp_file_name)],shell=True) # be careful, this is deleting stuff
    
    # # hacked by mike, try except added by Gio
    try:
        AMData=np.fromfile(fullFileAM,dtype='H',count=7) #Pull 1st 7 2-byte elements (type short) from AM file
    except IOError:
        AMData = np.array([])

    StartBin=AMData[3] # 4th element (6 bytes in) is start bin
    BinSize=AMData[4] # 5th element (8 bytes in) is bin size (=30)
    EndBin=AMData[6] #7th element (12 bytes in) is end bin
    self.recordingEndTime=(int(StartBin)+int(EndBin))*int(BinSize)-0.001 #Use AMData to get end of recording time
    #print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n AMData:"
    #print AMData
    extendedME=np.zeros((ME.shape[0]+1,ME.shape[1]),dtype=np.double)
    extendedME[:-1,:]=ME
    ME=extendedME
    
    try:
        PE = np.loadtxt(fullFilePE,delimiter=',',dtype=np.double, ndmin=2)
    except ValueError:
        PE = corrupt_orig_data_file_handler(fullFilePE)
        
    try:
        LE = np.loadtxt(fullFileLE,delimiter=',',dtype=np.double, ndmin=2)
    except ValueError:
        LE = corrupt_orig_data_file_handler(fullFileLE)

    # Convert time to seconds since midnight
    LE = LE/1000.0
    PE = PE/1000.0      
    # Convert x and y positions to cm
    ME = ME/1000.0
    self.ME_original = ME.copy()
    
    # Get the delta x and y data        
    deltaX = ME[:,1]
    deltaY = ME[:,2]
    # Convert to cumulative times and positions
    ME = np.cumsum(ME,axis=0)

    # # old darren stuff (2)
    # self.recordingEndTime=AMData[1]/1000.0 #try to use AMData to get end of recording time
    ME[-1,0]=self.recordingEndTime  
    #print "supposedly the system stops recording at %f seconds from midnight"%(self.recordingEndTime/3600.0)
    PE[:,0] = np.cumsum(PE[:,0])
    LE[:,0] = np.cumsum(LE[:,0])
    
    if PE.shape[0]>1:
        PE=PE[1:,:] #first one is just the start of recording, so chuck it
    # else:
    #    self.experiment.log_serious_problem(  "ERROR: no photobeam events on this day! see %s to confirm."%(fullFilePE)  ) 
    if LE.shape[0]>1:
        LE=LE[1:,:] #first one is just the start of recording, so chuck it
    # else:
    #    self.experiment.log_serious_problem(  "ERROR: no lick events on this day! see %s to confirm."%(fullFileLE)  )
        
    self.firstLickTime=LE[0,0]
    self.firstFeedTime=PE[0,0]
    #print "The first licking event is at %f"%(self.firstLickTime/3600.0)
    #print "The first feeding event is at %f"%(self.firstFeedTime/3600.0)
    if self.firstFeedTime<self.recordingStartTime:
        print "Error: firstFeedTime earlier than recordingStartTime"
        sys.exit(-1)
    if self.firstLickTime<self.recordingStartTime:
        print "Error: firstLickTime earlier than recordingStartTime"
        sys.exit(-1)

    self.lastLickTime=LE[-1,0]+LE[-1,1]
    #print "The last lickometer time is %f"%(self.lastLickTime/3600.0)
    self.lastFeedTime=PE[-1,0]+PE[-1,1]
    #print "The last feeding photobeam time is %f"%(self.lastFeedTime/3600.0)
    if self.lastFeedTime>self.recordingEndTime:
        print "Error: lastFeedTime past recordingEndTime"
        sys.exit(-1)
    if self.lastLickTime>self.recordingEndTime:
        print "Error: lastLickTime past recordingEndTime"
        sys.exit(-1)
    # Get the uncorrected position data
    uncorrectedT = ME[:,0]
    uncorrectedX = ME[:,1]
    uncorrectedY = ME[:,2]
    # Store data as class attributes
    self.recording_start_stop_time = np.array([self.recordingStartTime, self.recordingEndTime], dtype=np.double)         #TICKET: probably wrong (from Darren)
    self.ME = ME
    self.PE = PE
    self.LE = LE
    self.deltaX = deltaX
    self.deltaY = deltaY
    # the MouseDay will store a copy of the uncorrected trajectory info
    self.uncorrectedX = uncorrectedX
    self.uncorrectedY = uncorrectedY
    self.uncorrectedT = uncorrectedT
    # in the absence of a better option, we point to the uncorrected stuff
    self.CT=uncorrectedT
    self.CX=uncorrectedX
    self.CY=uncorrectedY

    
