import RPi.GPIO as GPIO
import logging
import os
import time
from util import *

BOARD_CONFIG = os.path.dirname(__file__) + "/board_config.txt"

#ToDo: Need to set this to number of pulses per liter
PULSE_PER_LITER = 400

#Counter on pulses received on an input (e.g. water meter)
pulses = 0

# Dictionary to go from pin function to number initialized in boardSetup
pinLookup = {}

#Call back to count input pulses
def pulseCount(channel):
    log = logging.getLogger()
    global pulses
    pulses += 1
    log.debug("Pulse Detected:" +str(pulses))
    
#Initialize board     
def boardSetup():
    log = logging.getLogger()
    
    log.info('Setting up board')
    
    #get the board configuration information
    boardConfig = loadTabFile(BOARD_CONFIG)
    
    #Configure GPIO
    GPIO.setmode(GPIO.BOARD)
    
    # Loop through each element in board config
    for pinConfig in boardConfig:
        # Apply Configuration To Pins
        if (pinConfig["IO"] == "OUT"):
            # Configure outputs and set them low
            GPIO.setup(pinConfig["Num"],GPIO.OUT)
            GPIO.output(pinConfig["Num"],GPIO.LOW)
        else:
            # Configure inputs and set any callbacks
            GPIO.setup(pinConfig["Num"],GPIO.IN)
            if(pinConfig["Callback"] != None):
                if (pinConfig["Callback"] == "COUNT"):
                    GPIO.add_event_detect(pinConfig["Num"],GPIO.RISING,callback=pulseCount)
                else:
                    log.error("Error, unrecognized callback " + pinConfig["Callback"])
                   
        # Record Pin into pin lookup dictionary
        pinLookup[pinConfig["PinName"]] = pinConfig["Num"]
            
    log.info('Board setup complete')
    
    return()

# Any cleanup actions
def boardCleanup():
    #CleanUpGPIO
    GPIO.cleanup()

# This sets up the mux to connect to a specified output
def connectMux(num):
    log = logging.getLogger()
    
    log.info('Setting mux to bed ' + str(num))

    # Set mux enable pin high to disable output
    GPIO.output(pinLookup["sigEna"],GPIO.HIGH)
    
    # Decompose Address into binary high/low
    pinList = [pinLookup["addr0"],pinLookup["addr1"],pinLookup["addr2"],pinLookup["addr3"]]
    valueList = [num>>i&1 for i in range(4)]
    
    log.debug('Mux pinList: ' + str(pinList))
    log.debug('Mux valueList: ' + str(valueList))
    
    # Set Mux Address Pins
    GPIO.output(pinList,valueList)
    
    # Set mux enable pin low to enable output
    GPIO.output(pinLookup["sigEna"],GPIO.LOW)

# Water the specified bed for the specified time or enter key
def waterBedTime(bedNum,duration, enter):
    log = logging.getLogger()
    
    if enter:
        log.info('Watering bed ' + str(bedNum) + ' for manual duration')
    else:
        log.info('Watering bed ' + str(bedNum) + ' for ' + str(duration) + ' seconds')
    
    #Connect Mux to the desired bed
    connectMux(bedNum)
    
    # Set sigVal high to open the valve to specified bed
    GPIO.output(pinLookup["sigVal"],GPIO.HIGH)
    
    #if user asked for manual enter key control, use that. Otherwise use watering duration.
    if enter:
        input("Bed " +str(bedNum) + " Powered... press Enter to Continue...")
    else:    
        # wait until watering is complete
        time.sleep(duration)
    
    # Set sigVal low to close the valve to specified bed
    GPIO.output(pinLookup["sigVal"],GPIO.LOW)
    
    log.info('Watering Done')

# Water the specified bed for the specified time or enter key
def waterBedVolume(bedNum,volume,duration, enter):
    log = logging.getLogger()

    if enter:
        log.info('Watering bed ' + str(bedNum) + ' for manual duration')
    else:
        log.info('Watering bed ' + str(bedNum) + ' with ' + str(volume) +' liters for a maximum of ' + str(duration) + ' seconds')

    #Connect Mux to the desired bed
    connectMux(bedNum)

    # Set sigVal high to open the valve to specified bed
    GPIO.output(pinLookup["sigVal"],GPIO.HIGH)

    #if user asked for manual enter key control, use that. Otherwise use watering duration.
    if enter:
        input("Bed " +str(bedNum) + " Powered... press Enter to Continue...")
    else:
        # wait until watering is complete
        start_time = time.time()
        # water for a maximum of duration seconds
        while (time.time() < start_time + duration):
            # stop if water meter reaches desired volume
            if (readWaterMeter() >= volume):
                break
            time.sleep(0.5)

    # Set sigVal low to close the valve to specified bed
    GPIO.output(pinLookup["sigVal"],GPIO.LOW)

    log.info('Watering Done')


# Open High Side Valve and enable Power to Bed Valves
def openHighSide():
    GPIO.output(pinLookup["powEna"],GPIO.HIGH)
    time.sleep(1)
    GPIO.output(pinLookup["powJump"],GPIO.HIGH)
    time.sleep(1) # wait 1 second
    GPIO.output(pinLookup["powJump"],GPIO.LOW)
 
#Reset water meter 
def clearWaterMeter():
    global pulses
    pulses = 0
    
#Read water meter    
def readWaterMeter():
    return pulses / PULSE_PER_LITER 

    

