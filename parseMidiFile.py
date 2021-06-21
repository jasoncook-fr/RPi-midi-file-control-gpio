from MIDI import MIDIFile
from sys import argv
from array import *

'''
After reading the raw data of our midi file
insert here the unique character strings discovered
to signal the start and the end of the segment we wish to use.
Three index values also are to be changed according to the placement
found in the raw readout (timestamp, key, and on/off state)
'''

startString = "Set Tempo"
endString = "End Of Track"
timeIndex = 0  # time value, starts with MIDI@ in the raw readout
keyIndex = 2   # key value
stateIndex = 3 # on/off value

# map our keys to the GPIO pins, in order
keys = ['C5','D5','E5','F5','G5','A5','B5','C6','D6']
outPins = [17, 18, 27, 22, 23, 24, 25, 4, 2]

def parse(file):
    c=MIDIFile(file)
    c.parse()
    print(str(c))
    parseFlag = True
    recordFlag = False
    initFlag = False
    finalArray = []

    for idx, track in enumerate(c):
        if parseFlag is False:
            break
        track.parse()
        fileString = str(track)
        fileChunks = fileString.split('\n')
        #print(fileChunks)
        for line in fileChunks:
            if endString in line:
                parseFlag = False
                break
            if recordFlag is True:
                lineChunks = line.split(' ')
                lineChunks[timeIndex] = lineChunks[timeIndex].replace('MIDI@', '')
                lineChunks[timeIndex] = int(lineChunks[timeIndex])
                if lineChunks[stateIndex] == 'ON':
                    lineChunks[stateIndex] = 1
                elif lineChunks[stateIndex] == 'OFF':
                    lineChunks[stateIndex] = 0
                if initFlag is True:
                    initTime = lineChunks[timeIndex]
                    initFlag = False
                lineChunks[timeIndex] = int((lineChunks[timeIndex]-initTime)*3.90625)
                finalArray.append([lineChunks[timeIndex], lineChunks[keyIndex], lineChunks[stateIndex]])
            if startString in line and recordFlag is False:
                recordFlag = True
                initFlag = True

    print(finalArray)

parse(argv[1])
