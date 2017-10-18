import matplotlib.mlab as mlab
import numpy as np
import os
import sys
import subprocess
import re
from ceppa.util.cage import Cage

"""
these method definitions will be monkey-patched onto the mouseDay class
backwardFix
forwardFix
deviceFix
medianRuns
"""

def backwardFix(self):
	"""
	this is the backwardsFix method to fix the sliding path issue.
	"""
	C = Cage()

	nan = np.nan
	# Get the uncorrected position data
	uncorrectedX = self.uncorrectedX
	uncorrectedY = self.uncorrectedY
	deltaX = self.deltaX
	deltaY = self.deltaY

	print "backward fixing.."
	# Create empty arrays
	backwardX = nan * uncorrectedX
	backwardY = nan * uncorrectedY
	# Set the last values
	#backwardX[-1] = mouseCMXSleeping #uncorrectedX[-1]
	#backwardY[-1] = mouseCMYSleeping #uncorrectedY[-1]

	# Loop backward through uncorrected X positions
	for i in range(len(uncorrectedX)+1,0,-1):
		# Position placeholders, a=x,b=y
		if i == len(uncorrectedX)+1:
			#presume they are sleeping at the end.
			a = C.mouseCMXSleeping
			b = C.mouseCMYSleeping
			# For the first iteration, use the last uncorrected x and y coordinates
			#a = uncorrectedX[-1]
			#b = uncorrectedY[-1]
		else:
			# Otherwise, use the last corrected position with delta x and y
			a = backwardX[i-1] - deltaX[i-2]
			b = backwardY[i-1] - deltaY[i-2]

		# Use the cage boundaries if the x position is in violation
		a = max(C.CMXLower, a)
		a = min(C.CMXUpper, a)

		# Use the cage boundaries if the y position is in violation
		b = max(C.mouseCMYAtPhoto,b)
		b = min(C.CMYUpper,b)

		# Apply the nest boundaries
		if a < C.nestRightX:
			b = min(b, C.nestTopY)
		if b > C.nestBottomY:
			a = max(a, C.nestLeftX)
		if a > C.enclosurePenaltyLowerBoundXMin:
			b = max(b,1)

		# Update the x and y positions after all comparisons
		backwardX[i-2] = a
		backwardY[i-2] = b

	backwardX[-1] = backwardX[-2] #a bad fix of a larger problem that the last entries of backward are super crazy
	backwardY[-1] = backwardY[-2]

	# Store the backward corrected position data
	self.backwardX = backwardX
	self.backwardY = backwardY

	#We assume you calculated it because you want to use it / go with it
	self.CT=self.uncorrectedT
	self.CX=self.backwardX
	self.CY=self.backwardY



def forwardFix(self):
	# Get the uncorrected position data
	uncorrectedX = self.uncorrectedX
	uncorrectedY = self.uncorrectedY
	deltaX = self.deltaX
	deltaY = self.deltaY

	print "forward fixing.."

	# Create empty arrays
	forwardX = nan*uncorrectedX
	forwardY = nan*uncorrectedY
	# Set the first values
	forwardX[0] = uncorrectedX[0]
	forwardY[0] = uncorrectedY[0]

	# Loop through the uncorrected X values
	for i in range(0,len(forwardX)-1):

		# Use temporary variables a=x,b=y
		# Set initial value to previous position plus delta x,y
		a = forwardX[i] + deltaX[i]
		b = forwardY[i] + deltaY[i]

		# Use cage boundaries if position is in violation
		a = max(CMXLower,a)
		a = min(CMXUpper,a)
		b = max(mouseCMYAtPhoto,b)
		b = min(CMYUpper,b)

		# Apply nest boundaries
		if a < nestRightX:
			b = min(b,nestTopY)
		if b > nestBottomY:
			a = max(a,nestLeftX)
		if a > enclosurePenaltyLowerBoundXMin:
			b = max(b,1)

		# Update corrected positions
		forwardX[i+1] = a
		forwardY[i+1] = b

	# Store corrected positions in class attributes
	self.forwardX = forwardX
	self.forwardY = forwardY

	#We assume you calculated it because you want to use it / go with it
	self.CT=self.uncorrectedT
	self.CX=self.forwardX
	self.CY=self.forwardY




def deviceFix(self):
	# Get the device data
	move=self.ME
	lick=self.LE[1:,:]
	photo=self.PE[1:,:]

	print "devices fixing.."
	# Define the position codes
	positionCode = 1
	photoStartCode = 2
	lickStartCode = 3
	photoStopCode = 4
	lickStopCode = 6

	# Label the position events with positionCodes
	moveLabels = positionCode*np.ones((move.shape[0],1),'double')
	move = np.hstack((move,moveLabels))
	del moveLabels #no longer needed

	# Define the positions of the devices
	lickXY = np.array([0.0, 0.0+3.0]) #Maybe Evan was wrong, this is the Alan measurement
	photoXY = np.array([-12.7500+0.0, -2.6+3.000]) #according to Evan, this is what the center of mass of an eating mouse should be

    # Make photobeam break events
	if photo.shape[0]>0:
		photoStartLabels = photoStartCode*np.ones((photo.shape[0],1),'double')
		photoPositions = np.kron(np.ones((photo.shape[0],1)),photoXY)
		temp = np.zeros((photo.shape[0],1),'double')
		temp[:,0] = photo[:,0]
		photoStart = np.hstack((temp,photoPositions,photoStartLabels))
		photoStopLabels = photoStopCode*np.ones((photo.shape[0],1),'double')
		temp[:,0] = photo[:,0]+photo[:,1]+0.0001
		photoStop = np.hstack((temp,photoPositions,photoStopLabels))
	else:
		print "Warning: Device fix just experienced no photo events in the whole day! - mouse%d, day%d" %(self.individual.mouseNumber, self.dayNumber)
		photoStart = np.ones((photo.shape[0],4),'double') #hopefully it understands 0 by 4 matrices
		photoStop = np.ones((photo.shape[0],4),'double')

    # Make lickometer events
	if lick.shape[0]>0:
		lickStartLabels = lickStartCode*np.ones((lick.shape[0],1),'double')
		lickPositions = np.kron(np.ones((lick.shape[0],1)),lickXY)
		temp = np.zeros((lick.shape[0],1),'double')
		temp[:,0] = lick[:,0]
		lickStart = np.hstack((temp,lickPositions,lickStartLabels))
		lickStopLabels = lickStopCode*np.ones((lick.shape[0],1),'double')
		temp[:,0] = lick[:,0]+lick[:,1]
		lickStop = np.hstack((temp,lickPositions,lickStopLabels))
	else:
		print "Warning: Device fix just experienced no lick events in the whole day! - mouse%d, day%d" %(self.individual.mouseNumber, self.dayNumber)
		lickStart = np.ones((lick.shape[0],4),'double') #hopefully it understands 0 by 4 matrices
		lickStop = np.ones((lick.shape[0],4),'double')

    # Make the time-sorted list of events
	allEvents = np.vstack((photoStart,move,photoStop,lickStart,lickStop))
	uncorrectedPositions = allEvents[:,1:3]
	allEvents = np.hstack((allEvents,uncorrectedPositions)) # we are going to carry the uncorrected position data with us
	sortedEvents = allEvents[allEvents[:,0].argsort()]
	del allEvents # now that the sortedEvents list is created, allEvents is a liability, so we neutralize

	temp = np.zeros((sortedEvents.shape[0],1),'double')
	temp[:,0] = np.array(range(sortedEvents.shape[0]),'double')
	sortedEvents = np.hstack((sortedEvents,temp))
	numberOfEvents = sortedEvents.shape[0]
	positionRunStartingIndices = np.zeros(numberOfEvents,'int')
	positionRunStopIndices = np.zeros(numberOfEvents,'int')
	eventTypes = np.array(sortedEvents[:,3],'int')

	n=0
	k=0
	if eventTypes[0] == positionCode:
		isThereAnInitialSequenceOfPositions = True
	else:
		isThereAnInitialSequenceOfPositions = False

	isThereAFinalSequenceOfPositions = True
	while n<numberOfEvents and eventTypes[n] == positionCode:  #this while loop should make n be the index of the first lick or photo event
		n = n+1

	if n < numberOfEvents:
		firstNonPositionIndex = n
	else:
		exit(1)

	while True:
		while n < numberOfEvents and eventTypes[n] != positionCode:
		#this while loop should make n be the index of the start of a run of positions
			n = n+1

		lastNonPositionIndex = n-1 #this will happen many times, but on the last time it will be assigned the correct value

		if n < numberOfEvents:
			positionRunStartingIndices[k] = n
		else:
			isThereAFinalSequenceOfPositions = False
			break

		while n < numberOfEvents and eventTypes[n] == positionCode:
			n = n+1
		if n < numberOfEvents:
			positionRunStopIndices[k] = n
			k = k+1 #we have found another fully anchored run with a define start and end
		else:
			break

	positionRunStartingIndices = positionRunStartingIndices[:k]
	positionRunStopIndices = positionRunStopIndices[:k]
	temp1 = np.zeros((k,1),'double')
	temp1[:,0] = positionRunStartingIndices
	temp2 = np.zeros((k,1),'double')
	temp2[:,0] = positionRunStopIndices
	runStartAndStopIndices = np.hstack((temp1,temp2))

    # Fix the runs so they start and stop at their known positions
	fixedEvents = sortedEvents.copy()
	for i in range(k):
		startIndex = positionRunStartingIndices[i]
		stopIndex = positionRunStopIndices[i]
		startEventType = eventTypes[startIndex-1]
		stopEventType = eventTypes[stopIndex]
		supposedStartPosition = sortedEvents[startIndex,1:3]
		supposedStopPosition = sortedEvents[stopIndex-1,1:3]
		if startEventType == lickStopCode or startEventType == lickStartCode:
			knownStartPosition = lickXY
		elif startEventType == photoStopCode or startEventType == photoStartCode:
			knownStartPosition = photoXY
		else:
			sys.exit(0)

		if stopEventType == lickStopCode or stopEventType == lickStartCode:
			knownStopPosition = lickXY
		elif stopEventType == photoStopCode or stopEventType == photoStartCode:
			knownStopPosition = photoXY
		elif stopEventType == lickStopCode or stopEventType == lickStartCode:
			knownStopPosition = lickXY
		elif stopEventType == photoStopCode or stopEventType == photoStartCode:
			knownStopPosition = photoXY
		else:
			sys.exit(0)
		if stopIndex >= startIndex+2:
			initiallyTranslateBy = knownStartPosition-supposedStartPosition
			correctionNeededByEnd = knownStopPosition-(supposedStopPosition+initiallyTranslateBy)
			timesFromZeroToOne = np.zeros((stopIndex-startIndex,1),'double')
			timesFromZeroToOne[:,0] = (sortedEvents[startIndex:stopIndex,0]-sortedEvents[startIndex-1,0])*1.0/(sortedEvents[stopIndex,0]-sortedEvents[startIndex-1,0])

			fixedEvents[startIndex:stopIndex,1:3] = sortedEvents[startIndex:stopIndex,1:3] + np.kron(np.ones((stopIndex-startIndex,1)),initiallyTranslateBy) + np.kron(timesFromZeroToOne,correctionNeededByEnd)

		if stopIndex == startIndex+1:
			fixedEvents[startIndex,1:3] = knownStartPosition


    # Fix positions prior to first lick/eat event
	if isThereAnInitialSequenceOfPositions:
		initiallyTranslateBy = sortedEvents[firstNonPositionIndex,1:3]-sortedEvents[firstNonPositionIndex-1,1:3];
		fixedEvents[:firstNonPositionIndex,1:3] = sortedEvents[:firstNonPositionIndex,1:3]+np.kron(np.ones((firstNonPositionIndex,1)),initiallyTranslateBy)

    # Fix positions after the last lick/eat event
	if isThereAFinalSequenceOfPositions:
		initiallyTranslateBy = sortedEvents[lastNonPositionIndex,1:3]-sortedEvents[lastNonPositionIndex+1,1:3];
		theLengthInQuestion = sortedEvents.shape[0]-lastNonPositionIndex-1
		fixedEvents[lastNonPositionIndex+1:,1:3] = sortedEvents[lastNonPositionIndex+1:,1:3]+np.kron(np.ones((theLengthInQuestion,1)),initiallyTranslateBy)

	# Store fixed data in numpy array
	sortedEvents=fixedEvents

	# Get the movement indices
	moveInd = mlab.find(sortedEvents[:,3]==1)
	sortedEvents = sortedEvents[moveInd,:]
	# Get the time and position data
	Time = sortedEvents[:,0]
	deviceFixX = sortedEvents[:,1]
	deviceFixY = sortedEvents[:,2]

	self.Time = Time
	self.deviceFixX = deviceFixX
	self.deviceFixY = deviceFixY

	#We assume you calculated it because you want to use it / go with it
	self.CT=self.uncorrectedT
	self.CX=self.deviceFixX
	self.CY=self.deviceFixY




def medianRuns(self):
	# Get fixed data from class attributes
	deviceFixX = self.deviceFixX
	deviceFixY = self.deviceFixY
	backwardX = self.backwardX
	backwardY = self.backwardY
	forwardX = self.forwardX
	forwardY = self.forwardY

	# Create empty arrays of median positions
	medianX = nan*deviceFixX
	medianY = nan*deviceFixY
	# Loop through the values and assign the median
	for w in range(0,len(medianX)):
		medianX[w] = np.median((deviceFixX[w],backwardX[w],forwardX[w]))
		medianY[w] = np.median((deviceFixY[w],backwardY[w],forwardY[w]))
	# Store median position in class attributes
	self.medianX = medianX
	self.medianY = medianY

	#We assume you calculated it because you want to use it / go with it
	self.CT=self.uncorrectedT
	self.CX=self.medianX
	self.CY=self.medianY
