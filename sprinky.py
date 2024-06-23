import os
import datetime
import time
import logging
import argparse
from weather import *
from board import *
from util import *

#file with watering schedule and board config.  Currently must be in directory w/ program. 
SCHEDULE = os.path.dirname(__file__) + "/water_schedule.txt"

#rain threshold - skip watering if rain prediction exceds this value (milimeters)
RAIN_THRESHOLD = 6.0

#setup a logging file.  Name includes date. Note this is the default logger so funcions in
#other files can just pull the default logger and will log to this file with the correct format.
logdate = datetime.datetime.now().strftime('%Y%m')
log = logging.getLogger()
logging.basicConfig(filename= os.path.dirname(__file__) + '/log/' + logdate + '_watering.log', format='%(asctime)s %(message)s', datefmt='%Y/%m/%d-%H:%M:%S', level=logging.INFO)

#read command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-sw", "--skip_weather", help="skip the intenet weather check for predicted precipitation", action='store_true')
parser.add_argument("-e", "--enter", help="use enter key rather than duration to stop watering each bed", action='store_true')
parser.add_argument("-b", "--bed", type=int, help="manually water a single bed. Requires -d  or -e as well")
parser.add_argument("-d", "--duration", type=int, help="duration for manual watering. Used with -b")
parser.add_argument("-v", "--volume",type=int, help="volume for manual watering. Used with -d")

args = parser.parse_args()

# Start logging
log.info("Sprinky Starting")

# Load Configuration Files
sched = loadTabFile(SCHEDULE)

# Predicted weather
if args.skip_weather or args.bed:
    log.info('Skipping the weather check')
else:
    # Check rain prediction for today
    precip = checkRainPrediction()
    if precip >= RAIN_THRESHOLD:
        log.info('Predicted Rain more than enough.  Skipping watering today.')
        print('Going to rain.  Sprinky taking the day off.')
        exit(0)

# Setup Board
boardSetup()

# Enable Power to Bed Valves
openHighSide()
clearWaterMeter()

#If manual bed / duration / volume, just water that bed.
if (args.bed is not None) and ((args.duration and args.volume) or args.enter) :
    if (args.volume):
        waterBedVolume(args.bed, args.volume, args.duration, args.enter)
    else:
        waterBedTime(args.bed, args.duration, args.enter)
    log.info('Manually watered bed ' + str(args.bed))
    log.info('It got ' + str(readWaterMeter()) + ' liters')
    
else:    

    # Execute Watering shedule Schedule
    day = datetime.datetime.today().weekday()
    log.info('Day of Week: ' + str(day))
    for bed in sched:
    
        if '*' in bed['Days'] or str(day) in bed['Days']:
            
            log.info('Starting bed ' + str(bed["Bed_Num"]))
    
            waterBedVolume(bed["Bed_Num"], bed["Volume"], bed["Duration"], args.enter)

            log.info('Complted bed ' + str(bed["Bed_Num"]))
            log.info('It got ' + str(readWaterMeter()) + ' liters')
    
            clearWaterMeter()
        else:
            log.info('Bed ' + str(bed['Bed_Num']) + ' does not get watered today.  Skipping.')


# Board Cleanup
boardCleanup()


# Close Out Log
log.info("Sprinky Finished.")
print("Sprinky has Sprinkled")

