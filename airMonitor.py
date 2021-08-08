#! /usr/bin/python3

import sys
import os, os.path
import time
import aqi
import getopt
import string
import math
import random
import serial
import smtplib, ssl

debug = False
usbfile = "/dev/ttyUSB0"

aqiThreshold = 100
#threshold to trigger alerts

emailPassword = ""
emailSender = ""
#username to send from

smtpServer = "smtp.gmail.com"

emailReceiver = ""

emailTimeout = 45
#time between each email, in minutes

emailPort = 465

def sendEmail(airQuality, twoFive, ten):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", emailPort, context=context) as server:
        message = "Subject: Air Quality Alert\n\nAQI: "+str(airQuality)+"\nAir Conditions: "+calculateAirQualityConditions(airQuality)+"\n\nPM2.5 Levels: "+str(twoFive)+"\nPM10 Levels: "+str(ten)
        server.login(emailSender, emailPassword)
        server.sendmail(emailSender, emailReceiver, message)

def calculateAirQualityConditions(aqi):
    if (aqi < 51):
        return "Good"
    elif (aqi < 101):
        return "Moderate"
    elif (aqi < 151):
        return "Unhealthy for Sensitive Groups"
    elif (aqi < 201):
        return "Unhealthy"
    elif (aqi < 301):
        return "Very Unhealthy"
    else:
        return "Hazardous"

def startupEmail():
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtpServer, emailPort, context=context) as server:
        message = "Subject: Air Quality Alert\n\nAir Quality Monitor Has Started"
        server.login(emailSender, emailPassword)
        server.sendmail(emailSender, emailReceiver, message)

def main():
    pastThreshold = False
    try:
        ser = serial.Serial(usbfile)
    except IOError as e:
        print("airMonitor.py: I/O error -- %s" % (e.args[0]))
        print("\nRetrying in 20 seconds...")
        time.sleep(20)
        main()

    while True:

        data = []
        for index in range(0,10):
            datum = ser.read()
            data.append(datum)

        pmtwofive = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
        pmten = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10

        airQuality = aqi.to_aqi([
            (aqi.POLLUTANT_PM25, pmtwofive),
            (aqi.POLLUTANT_PM10, pmten),
        ])

        if (airQuality >= aqiThreshold):
            sendEmail(airQuality, pmtwofive, pmten)
            pastThreshold = True

        if (pastThreshold):
            time.sleep(emailTimeout * 60)
        else:
            time.sleep(120)


if __name__=='__main__':
    startupEmail()
    main()
    sys.exit()
