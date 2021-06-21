from MIDI import MIDIFile
from sys import argv
from array import *
import RPi.GPIO as GPIO
import time

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
velocityIndex = 6

# map our keys to the GPIO pins, in synchronous order
key = ['C5','D5','E5','F5','G5','A5','B5','C6','D6']
outPin = [4, 17, 27, 22, 10, 9, 11, 18, 8]
pumpPin = 25
pumpDuty = 100

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

for x in range(len(outPin)):
    GPIO.setup(outPin[x], GPIO.OUT, initial=GPIO.LOW)

GPIO.setup(pumpPin, GPIO.OUT)
GPIO.output(pumpPin, GPIO.LOW)
pwm = GPIO.PWM(pumpPin, 100) # Set Frequency to 1 KHz
pwm.start(0) # Set the starting Duty Cycle

finalArray = []

def parse(file):
    c=MIDIFile(file)
    c.parse()
    print(str(c))
    parseFlag = True
    recordFlag = False
    initFlag = False

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
                lineChunks[keyIndex] = outPin[key.index(lineChunks[keyIndex])]
                if lineChunks[stateIndex] == 'ON':
                    lineChunks[stateIndex] = 0
                elif lineChunks[stateIndex] == 'OFF':
                    lineChunks[stateIndex] = 1
                if initFlag is True:
                    initTime = lineChunks[timeIndex]
                    initFlag = False
                lineChunks[velocityIndex] = int(float(lineChunks[velocityIndex])*0.8)
                lineChunks[timeIndex] = int((lineChunks[timeIndex]-initTime)*3.90625)
                finalArray.append([lineChunks[timeIndex], lineChunks[keyIndex], lineChunks[stateIndex], lineChunks[velocityIndex]])
            if startString in line and recordFlag is False:
                recordFlag = True
                initFlag = True

    #print(finalArray)

def current_milli_time():
    return round(time.time() * 1000)

parse(argv[1])

endTime = finalArray[len(finalArray)-1][0]

def destroy():
    pwm.stop()
    GPIO.output(pumpPin, GPIO.LOW)
    GPIO.cleanup()

try:

    while True:
        previousTime = current_milli_time()
        timeCount = 0
        indexCount = 0
        while timeCount < endTime:
            if finalArray[indexCount][0] == timeCount:
                GPIO.output(finalArray[indexCount][1],finalArray[indexCount][2])
                pwm.ChangeDutyCycle(finalArray[indexCount][3])
                indexCount += 1
            timeCount = current_milli_time() - previousTime

except KeyboardInterrupt:
    destroy()
