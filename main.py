##Get CGM information from our Sugarmate Account
##When Dexcom login isn't working
##Need to enable API access through the Sugarmate app
##

import os
import re
import platform
from time import sleep
import argparse
import datetime
import logging
from pydexcom import Dexcom

#Process command line arguments
ArgParser=argparse.ArgumentParser(description="Handle Command Line Arguments")
ArgParser.add_argument("--logging", '-l', default="INFO", help="Logging level: INFO (Default) or DEBUG")
ArgParser.add_argument("--polling_interval", help="Polling interval for getting updates from Sugarmate")
ArgParser.add_argument("--time_ago_interval", help="Polling interval for updating the \"Time Ago\" detail")
ArgParser.add_argument("--username", "-u", help="Dexcom Share User Name")
ArgParser.add_argument("--password", "-p", help="Dexcom Share Password")
args=ArgParser.parse_args()

log = logging.getLogger(__file__)
log.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)
if args.logging == "DEBUG":
    log.setLevel(logging.DEBUG)

if args.username != None:
    DEXCOM_ACCOUNT_NAME = args.username

if args.password != None:
    DEXCOM_PASSWORD = args.password

if args.polling_interval != None:
    CHECK_INTERVAL = int(args.polling_interval)
else:
    CHECK_INTERVAL = 60

if args.time_ago_interval != None:
    TIME_AGO_INTERVAL = int(args.time_ago_interval)
else:
    TIME_AGO_INTERVAL = 30

dexcom = Dexcom(DEXCOM_ACCOUNT_NAME, DEXCOM_PASSWORD, ous=True) # `ous=True` if outside of US

if  platform.platform().find("arm") >= 0:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame
    global pygame, lcd
    os.putenv('SDL_FBDEV', '/dev/fb1')
    pygame.init()
    pygame.mouse.set_visible(0)
    lcd=pygame.display.set_mode((480, 320))

def display_reading(reading):

    if not platform.platform().find("arm") >= 0:
        log.debug("Skipping display.  Not on Raspberry Pi")
        return
    global pygame, lcd
    log.debug("Getting ready to display on the LCD panel")

    log.debug("Displaying with Reading of " + str(reading))
    now = datetime.datetime.utcnow()

    match = re.search(r'\((\d+)', reading["WT"])
    reading_timestamp = int(match.group(1)) / 1000
    reading_time = datetime.datetime.utcfromtimestamp(reading_timestamp)

    difference = round((now - reading_time).total_seconds()/60)
    log.debug("Time difference since last good reading is: " + str(difference))
    #print("Time difference since last good reading is: " + str(difference))
    if difference == 0:
        str_difference = "Jetzt"
    elif difference == 1:
        str_difference = "Vor " + str(difference) + " Minute"
    else:
        str_difference = "Vor " + str(difference) + " Minuten"
    log.info("About to update Time Ago Display with reading from " + str_difference)

    try:
        lcd.fill((0,0,0))
        font_color=(255,255,255)

        log.debug("Setting up Difference Display")
        font_time = pygame.font.Font(None, 75)
        text_surface = font_time.render(str_difference, True, font_color)
        rect = text_surface.get_rect(center=(240,25))
        lcd.blit(text_surface, rect)

        log.debug("Setting up Reading Display")
        font_big = pygame.font.SysFont("dejavusans", 180)

        if reading["Trend"] == "DoubleUp" or reading["Trend"] == "SingleUp":
            trend_arrow = chr(int("0x2191", 16))
        elif reading["Trend"] == "FortyFiveUp":
            trend_arrow = chr(int("0x2197", 16))
        elif reading["Trend"] == "Flat":
            trend_arrow = chr(int("0x2192", 16))
        elif reading["Trend"] == "FortyFiveDown":
            trend_arrow = chr(int("0x2198", 16))
        elif reading["Trend"] == "DoubleDown" or reading["Trend"] == "SingleDown":
            trend_arrow = chr(int("0x2193", 16))
        else:
            trend_arrow = "?"
        str_reading = str(reading["Value"]) + trend_arrow
        log.debug("About to push: " + str_reading + " to the display")
        text_surface = font_big.render(str_reading, True, font_color)
        rect = text_surface.get_rect(center=(240,155))
        lcd.blit(text_surface, rect)

        log.debug("About to update the LCD display")
        pygame.display.update()
        pygame.mouse.set_visible(False)
    except Exception as e:
        log.info("Caught an Exception processing the display")
        log.info(e)
    finally:
        log.debug("Done with display")

i=0
while True:
    i += 1
    try:
        r = dexcom.get_current_glucose_reading()
        log.info("Data: " + str(r.json))
        j=r.json
        print(j)
        display_reading(j)

    except Exception as e:
        log.info("Exception processing The Reading, Sleeping and trying again....")
        log.info(e)
    sleep(CHECK_INTERVAL)
