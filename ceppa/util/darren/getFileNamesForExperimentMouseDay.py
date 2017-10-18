# this is used by the object-oriented Experiment classes, don't erase 20130206
import os # needed for os.uname() to identify what computer we are running on
import re # for regular expression parsing of filenames
import sys # to halt on errors

unameReturnValue=os.uname()
opSysName=unameReturnValue[0]
compName=unameReturnValue[1]


def operatingSystemName():
    return opSysName
    
def computerName():
    return compName

def dataDirRoot():
    if computerName() == "Jethro":
        return "/Users/darren/HCM/"
    elif computerName() in ['gos-MacBook-Pro', 'gos-MacBook-Pro.local']:
        return "/data/HCM/"
    elif computerName() == "ucsf2-71-19":
        # return "/home/tecott/HCM/"
        return "/media/BeastHD_/"
    # elif computerName() == "Rams-MacBook-Pro.local":
    #   return "/Users/rammehta/src/HomeCageMonitoring/data/"
    # elif computerName() == "Christopher-Hillars-MacBook-Pro.local":
    #   return "/data/HCM/"
    # elif computerName() == "localhost": #this is just wrong, but
    #   return "/data/HCM/"
    # elif computerName() == "miked-XPS-8700":
    #   return "/data/"
    # else:
    #   return "/data/"
    #   print computerName()
    #   print "ERROR: dataDirRoot() failed because computer is unrecognized."
    #   sys.exit(-1)

# def homeDirectory():
#   if computerName()=="Jethro":
#       return "/Users/darren/"
#   elif computerName()=="ucsf2-71-19":
#       return "/media/BeastHD_/"
#   elif computerName()=="Cassiopeia":
#       return "/home/darren/"
#   elif computerName()=="Christopher-Hillars-MacBook-Pro.local":
#       return "/Users/cav/" 
#   elif computerName()=="localhost": #this is just wrong, but
#       return "/Users/cav/" 
#   elif computerName()=="gos-MacBook-Pro.local":
#       return "/Users/go/"
#   elif computerName() == "miked-XPS-8700":
#       return "home/miked/"
#   else:
#       print computerName()
#       print "ERROR: homeDirectory() failed because computer is unrecognized."
#       return "/Users/darren/"
#       #sys.exit(-1)


# def experimentDirectory(experiment):
#   if experiment == "BTBR":
#       return dataDirRoot()+'Experiments/BTBR/'
#   elif experiment == "StrainSurvey":
#       return dataDirRoot()+'Experiments/SS_Data_051905_FV/'
#   elif experiment == "C57BL6NO":
#       return dataDirRoot()+'Experiments/C57BL6NO/'    
#   elif experiment == "DREADD":
#       return dataDirRoot()+'Experiments/DREADD_HCMe1r1/'  
#   elif experiment == "PCP1":
#       return dataDirRoot()+'Experiments/PCP1_HCMe1r1/'
#   elif experiment == "Hifat1":
#       return dataDirRoot() + 'Experiments/HiFat1/'

#   else:
#       print "ERROR: experiment %s not recognized."%experiment
#       sys.exit(-1)


def fileNamesForExperiment(experiment, roundNumber, dayNumber, mouseNumber):
    # experimentDirectory=dataDirRoot()+"Experiments/HiFat1/Round1/HFDe1r1d%01d/"%(dayNumber)

    E = experiment
    if E.name == 'HiFat1Experiment':
        experimentDirectory = E.exp_dir + "Round%d/HFD_DayFiles/HFDe1r%dd%01d/" %(roundNumber, roundNumber, dayNumber)
    elif E.name == 'HiFat2Experiment':
        experimentDirectory = E.exp_dir + "HFD2_DayFiles/HFD2_HCMe2r1_d%01d/"%(dayNumber)
    elif E.name == 'TwoCFastExperiment':
        experimentDirectory = E.exp_dir + "2CFast_DayFiles/2CFAST_HCMe1r1_D%02d/" %dayNumber
    elif E.name == 'FluoxetineExperiment':
        experimentDirectory = E.exp_dir + "B6FLX_DayFiles/B6FLX_HCMe1r1_D%02d/" %dayNumber
    elif E.name == 'ZeroLightExperiment':
        experimentDirectory = E.exp_dir + "ZeroLight_DayFiles/Day%01d/" %dayNumber

    allFiles=os.listdir(experimentDirectory)
    mouseString="%04d"%(mouseNumber)
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.ME[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            MEFileName=experimentDirectory+filename

    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.LE[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            LEFileName=experimentDirectory+filename
                                                # Sys A and Sys B failed. 
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.PE[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            PEFileName=experimentDirectory+filename
                                                # Sys A and Sys B failed. 
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.AM[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            AMFileName=experimentDirectory+filename

    return AMFileName, LEFileName, MEFileName, PEFileName



# def fileNamesForHiFat1(exp_dir, roundNumber, dayNumber, mouseNumber):
#     # experimentDirectory=dataDirRoot()+"Experiments/HiFat1/Round1/HFDe1r1d%01d/"%(dayNumber)

#     experimentDirectory = exp_dir + "Round%d/HFD_DayFiles/HFDe1r%dd%01d/" %(roundNumber, roundNumber, dayNumber)
#     allFiles=os.listdir(experimentDirectory)
#     mouseString="%04d"%(mouseNumber)
#     for filename in allFiles:
#         patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.ME[0-9]$'
#         answer=re.search(patternWeAreLookingFor,filename)
#         if answer!=None:
#             MEFileName=experimentDirectory+filename
#     for filename in allFiles:
#         patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.LE[0-9]$'
#         answer=re.search(patternWeAreLookingFor,filename)
#         if answer!=None:
#             LEFileName=experimentDirectory+filename
#     for filename in allFiles:
#         patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.PE[0-9]$'
#         answer=re.search(patternWeAreLookingFor,filename)
#         if answer!=None:
#             PEFileName=experimentDirectory+filename
#     for filename in allFiles:
#         patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.AM[0-9]$'
#         answer=re.search(patternWeAreLookingFor,filename)
#         if answer!=None:
#             AMFileName=experimentDirectory+filename     
#     return AMFileName, LEFileName, MEFileName, PEFileName


# def fileNamesForHiFat2(exp_dir, roundNumber, dayNumber, mouseNumber):
#     experimentDirectory = exp_dir + "HFD2_DayFiles/HFD2_HCMe2r1_d%01d/"%(dayNumber)
#     allFiles=os.listdir(experimentDirectory)
#     mouseString="%04d"%(mouseNumber)
#     for filename in allFiles:
#         patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.ME[0-9]$'
#         answer=re.search(patternWeAreLookingFor,filename)
#         if answer!=None:
#             MEFileName=experimentDirectory+filename
#     for filename in allFiles:
#         patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.LE[0-9]$'
#         answer=re.search(patternWeAreLookingFor,filename)
#         if answer!=None:
#             LEFileName=experimentDirectory+filename
#     for filename in allFiles:
#         patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.PE[0-9]$'
#         answer=re.search(patternWeAreLookingFor,filename)
#         if answer!=None:
#             PEFileName=experimentDirectory+filename
#     for filename in allFiles:
#         patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.AM[0-9]$'
#         answer=re.search(patternWeAreLookingFor,filename)
#         if answer!=None:
#             AMFileName=experimentDirectory+filename     
#     return AMFileName, LEFileName, MEFileName, PEFileName


#Round numbers are 2 through 8 inclusive
#days are 1 through 16 inclusive
#the (crazy file name's notion of) instance is between 1 and 3 usually
#although by the time Darren has cleaned up, instances 1,2,3 with be instances 0,1,and 2
#strainNumbers range between 0 and 16 inclusive, although Strain 0 is actually the same as Strain 1, both are C57BL6 
#mouseNumber is (usually, not always) 1000*roundnumber + 100*instance+strainNumber

def fileNamesForStrainSurvey(exp_dir, roundNumber, dayNumber, mouseNumber):
    if roundNumber>8 or roundNumber<2:
        print "ERROR: the only StrainSurvey rounds were round 2, round 3, ..., round 8"
        sys.exit(-1)
    if dayNumber<1 or dayNumber>16:
        print "ERROR: each round had days 1 through day 16, no other days existed."
        
    successful=0
    successfullyFoundLEFile=0
    successfullyFoundMEFile=0
    successfullyFoundPEFile=0
    experimentDirectory = exp_dir + "EventFiles/EventFiles_SSe1r%d/"%(roundNumber)  # this has to be generalized to other experiments.
    #print "Directory is %s"%experimentDirectory
    
    allDirectories=os.listdir(experimentDirectory)
    #print allDirectories
    #directorySuffix="e1r%dd%d"%(roundNumber,dayNumber)
    for directory in allDirectories:
        #print "checking directory %s"%directory
        patternWeAreLookingFor='[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'+"e1r%dd%d$"%(roundNumber,dayNumber)
        #print "for pattern %s"%patternWeAreLookingFor 
        answer=re.search(patternWeAreLookingFor,directory)
        if answer!=None:
            correctDirectory=directory
            #print "Yo, found Event Directory = %s"%correctDirectory
            break
    experimentDirectory=experimentDirectory+correctDirectory+'/'
    #print experimentDirectory
    allFiles=os.listdir(experimentDirectory)
    mouseString="%04d"%(mouseNumber)
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.ME[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            MEFileName=experimentDirectory+filename
            successfullyFoundMEFile=1
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.LE[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            LEFileName=experimentDirectory+filename
            successfullyFoundLEFile=1
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.PE[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            PEFileName=experimentDirectory+filename
            successfullyFoundPEFile=1

    if not successfullyFoundLEFile:
        print "Something is wrong: "
        print "\n\n\nFor Round %d, Day %d, mouseNumber %d we cannot file an LEFile!"%(roundNumber, dayNumber, mouseNumber)
        sys.exit(-1)

    if not successfullyFoundMEFile:
        print "Something is wrong: "
        print "\n\n\nFor Round %d, Day %d, mouseNumber %d we cannot file an MEFile!"%(roundNumber, dayNumber, mouseNumber)
        sys.exit(-1)

    if not successfullyFoundPEFile:
        print "Something is wrong: "
        print "\n\n\nFor Round %d, Day %d, mouseNumber %d we cannot file an PEFile!"%(roundNumber, dayNumber, mouseNumber)
        sys.exit(-1)

    #BEGIN AMFILE GRABBING
    successfullyFoundAMFile=0
    experimentDirectory=exp_dir + "AMFiles/AMFiles_SSe1r%d/"%(roundNumber)
    #print "AM Directory is %s"%experimentDirectory
    
    allDirectories=os.listdir(experimentDirectory)
    #print allDirectories
    
    for directory in allDirectories:
        #print "checking directory %s"%directory
        patternWeAreLookingFor='[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'+"e1r%dd%d$"%(roundNumber,dayNumber)
        #print "for pattern %s"%patternWeAreLookingFor 
        answer=re.search(patternWeAreLookingFor,directory)
        if answer!=None:
            correctDirectory=directory
            #print "Yo, found AM Directory = %s"%correctDirectory
            break
    
    experimentDirectory=experimentDirectory+correctDirectory+'/'
    #print experimentDirectory
    allFiles=os.listdir(experimentDirectory)
    mouseString="%04d"%(mouseNumber)
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.AM[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            AMFileName=experimentDirectory+filename
            successfullyFoundAMFile=1
    
    if not successfullyFoundAMFile:
        print "Something is wrong: "
        print "\n\n\nFor Round %d, Day %d, mouseNumber %d we cannot file an AMFile!"%(roundNumber, dayNumber, mouseNumber)
        sys.exit(-1)
    """ 
    print "\n\n\nFor Round %d, Day %d, mouseNumber %d the AM, LE, ME, and PE files are"%(roundNumber, dayNumber, mouseNumber)
    print AMFileName
    print ""
    print LEFileName
    print ""
    print MEFileName
    print ""
    print PEFileName
    """
    return successful, AMFileName, LEFileName, MEFileName, PEFileName
    


#It is often that you have the short name of the experiment FileFolder, the 
#numerical mouse number, and the numerical (like 1-21) day number, and you need to know the
#fully pathed file names of the LE, ME, PE files, which are like 04271015.ME7

def fileNamesForExperimentMouseDay(experimentDirectoryName, mouseNumber, dayNumber):
    stop
    if experimentDirectoryName=='C57BL6NO':
        experimentDirectory=dataDirRoot()+"Experiments/C57BL6NO/C57BL6NO_DayFiles/C57BL6NO_HCMe1r1_d%d/"%(dayNumber)
    # elif experimentDirectoryName=='DREADD_HCMe1r1':
    #     experimentDirectory=dataDirRoot()+"Experiments/DREADD_HCMe1r1/DREADD_DayFiles/DREADD_HCMe1r1_D%d/"%(dayNumber)
    # elif experimentDirectoryName=='HFD2_HCMe2r1':
    #     experimentDirectory=dataDirRoot()+"Experiments/HFD2_HCMe2r1/HFD2_DayFiles/HFD2_HCMe2r1_D%02d/"%(dayNumber)
    # elif experimentDirectoryName=='SHANK3':
    #     experimentDirectory=dataDirRoot()+"Experiments/SHANK3/SHANK3_DayFiles/SHANK3_HCMe1r1_D%02d/"%(dayNumber)
    # elif experimentDirectoryName=='16P11DUPL_HCMe1r1':
    #     experimentDirectory=dataDirRoot()+"Experiments/16P11DUPL_HCMe1r1/16P11DUPL_DayFiles/16P11DUPL_HCMe1r1_D%02d/"%(dayNumber)
    # elif experimentDirectoryName=='CORTTREAT':
    #     experimentDirectory=dataDirRoot()+"Experiments/CORTTREAT/CORTTREAT_HCMe1r1_D%02d/"%(dayNumber)
    # elif experimentDirectoryName=='Act2C1_HCMe1r1':
    #     experimentDirectory=dataDirRoot()+"Experiments/Act2C1_HCMe1r1/Act2C1_DayFiles/Act2C1_HCMe1r1_D%d/"%(dayNumber)
    # elif experimentDirectoryName == '5-7DHT_HCMe1r1':
    #     experimentDirectory=dataDirRoot()+"Experiments/5-7DHT_HCMe1r1/5-7DHT_HCMe1r1_D%02d/"%(dayNumber)
    # elif experimentDirectoryName == 'Viaat2C1_HCMe1r1':
    #     experimentDirectory=dataDirRoot()+"Experiments/Viaat2C1_HCMe1r1/Viaat2C1_HCMe1r1_D%02d/"%(dayNumber)
    # elif experimentDirectoryName == 'Stress3_HCMe1r1':
    #     experimentDirectory=dataDirRoot()+"Experiments/Stress3_HCMe1r1/Stress3_HCMe1r1_D%02d/"%(dayNumber)
    elif experimentDirectoryName == 'PCP1_HCMe1r1':
        experimentDirectory=dataDirRoot()+"Experiments/PCP1_HCMe1r1/PCP1_HCMe1r1_D%02d/"%(dayNumber)
    elif experimentDirectoryName == 'HiFat1':
        experimentDirectory=dataDirRoot()+"Experiments/HiFat1/Round1/HFDe1r1d%01d/"%(dayNumber)
        
    else:
        experimentDirectory=dataDirRoot()+"Experiments/"+experimentDirectoryName+"/Data/Day%d/"%(dayNumber)
    
    stop
    # experimentDirectory = 
    allFiles=os.listdir(experimentDirectory)
    mouseString="%04d"%(mouseNumber)
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.ME[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            MEFileName=experimentDirectory+filename
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.LE[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            LEFileName=experimentDirectory+filename
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.PE[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            PEFileName=experimentDirectory+filename
    for filename in allFiles:
        patternWeAreLookingFor='^[0-9][0-9][0-9][0-9]'+mouseString+'\.AM[0-9]$'
        answer=re.search(patternWeAreLookingFor,filename)
        if answer!=None:
            AMFileName=experimentDirectory+filename     
    return AMFileName, LEFileName, MEFileName, PEFileName




if __name__=='__main__':
    print "operatingSystemName = "
    print opSysName
    print "computerName = "
    print compName
    print "dataDirRoot = "
    print dataDirRoot()

