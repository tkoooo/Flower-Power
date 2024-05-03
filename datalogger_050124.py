#!/usr/bin/env python3.10
# This driver is only supported by python 3.10 and I have python 3.11 installed as well so force ./filename to be run with this interpreter
# I changed my environment variables to run python 3.10 automatically
# This code is fully working

# Thalia Koutsougeras
# Agilent 34972A datalogger python script for gathering data

# Full descriptions of commands from the manual in the link below:
# http://instructor.physics.lsa.umich.edu/adv-labs/Tools_Resources/HP%2034970%20user's%20guide.pdf


"""
# sfr 3 testing latest
# radout - 202
# radin - 203
# 1 - 212 - G
# 2 - 213 - H
# 3 - 214 - I
# 4 - 215 - J
# 5 - 216 - K
# 6 - 217 - L
# flowmeter - 105
# ghi 1 - 108
# GHI 2 - 110
# dni - 106

"""


import numpy as np # For keysight_ktdaq970 arrays
import pyvisa as visa
import re
import time
from gpiozero import LED # for building pump output
import os
from datetime import datetime

# this function is to make the filename situation not a problem anymore (overwritten files because forgetting to change hardcoded filename)
def generate_filename(date):
    # format the date as MMDDYY
    formatted_date = date.strftime("%m%d%y")

    # generate the base filename
    base_filename = f"measurements_{formatted_date}_"

    # find the next available number for the filename - so that the previous one isn't overwritten
    i = 1
    while True:
        filename = base_filename + str(i) + ".txt"
        if not os.path.exists(filename):
            return filename
        i += 1

def main():
    Channel_Dict = {105: 'flow', 106: 'dni', 108: 'ghi1', 110: 'ghi2', 202: 'radout', 203: 'radin', 212: 'TC1', 213: 'TC2', 214: 'TC3', 215: 'TC4', 216: 'TC5', 217: 'TC6'}
    
    led = LED(24) # this sets GPIO pin 24 to be the output to the building pump
    led.off() # starting with off
    # it doesn't matter that it says LED, we just want to send out a 3.3V signal
    # led.on() sends out signal, led.off() turns it off

    rm = visa.ResourceManager() # VISA Resource Manager keeps track of instruments and creates sessions to them as requested
    addr = 'USB0::0x0957::0x2007::MY49016664::0::INSTR' # Grabbed from Keysight Connection Expert
    # USB[ board ]:: manufacturer ID :: model code :: serial number [:: USB interface number ][::INSTR]

    # Opening a file for writing to - these are the old hardcoded filenames
    #file_object = open("measurements_042424_T1_test.txt", "w")
    #file_raw = open("measurementsraw_042424_T1_test.txt", "w")

    # Get the current date
    current_date = datetime.now()
    # Generate the filename
    filename = generate_filename(current_date)
    # Open the file
    file_object = open(filename, "w")

    try:
        logger = rm.open_resource(addr) # Open session for the datalogger with resource manager
        print("\n Manufacturer/Model/Serial/Firmware level: ", logger.query('*IDN?')) # Reads out manufacturer, model, serial number, firmware level and options in an ASCII response data element

        logger.timeout =  10000
        #logger.write('*RST') # Resets the instrument - factory reset every time ### TOGGLED OFF

        # You only need to set the time and date once if you don't reset every time
        #logger.write("SYST:DATE 2023,04,19") #<yyyy>,<mm>,<dd>  ### TOGGLED OFF
        #logger.write("SYST:TIME 17,13,00.000") #SYSTem:TIME <hh>,<mm>,<ss.sss> ### TOGGLED OFF

        # FREQUENCY
        logger.write(':SENSe:FREQuency:VOLTage:RANGe:AUTO %d' % (1))
        logger.write(':CONFigure:FREQuency (%s)' % ('105'))


        # GHI SENSOR READINGS (0-40 mV) - The Global Horizontal Irradiande (GHI) measures the total amount of light received by a square meter on the ground.
        # 2 sensors - channels 110, 111
        # First test - channel 110 is circle sensor, 111 is square
        # SENSe - These commands disable or enable autoranging for AC and DC voltage measurements on the specified channels. Autoranging is 
        # convenient because the instrument automatically selects the range for each measurement based on the input signal detected.
        logger.write(':SENSe:VOLTage:DC:RANGe:AUTO %d,(%s)' % (1, '@106, 108, 110'))   

        # CONFigure - These commands configure the channels in the <scan_list> for AC or DC voltage measurements but do not initiate the scan. 
        logger.write(':CONFigure:VOLTage:DC %s,(%s)' % ('AUTO', '@106, 108, 110'))
        

        
        # TEMPERATURE READINGS
        # SENSe - This checks that thermocouple is properly connected 
        logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:CHECk %d,(%s)' % (1, '@202, 203, 212, 213, 214, 215, 216, 217'))
        # SENSe - This selects the thermocouple type to use
        logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:TYPE %s,(%s)' % ('K', '@202, 203, 212, 213, 214, 215, 216, 217'))

        # CONFigure - These commands configure the channels for temperature measurements but do not initiate the scan.
        logger.write(':CONFigure:TEMPerature %s,%s,(%s)' % ('TCouple', 'K', '@202, 203, 212, 213, 214, 215, 216, 217')) ### TOGGLED OFF

        # ROUT - This command selects the channels to be included in the scan list. This command is used in conjunction with the CONFigure commands to set up an 
        #    automated scan. The specified channels supersede any channels previously defined to be part of the scan list. To start the scan, use the INITiate or 
        #    READ? command. 
        logger.write(':ROUTe:SCAN (%s)' % ('@105, 106, 108, 110, 202, 203, 212, 213, 214, 215, 216, 217')) # this is where you put multiple
        

        # READ? - This command changes the instrument's triggering system from the "idle" state to the "wait-for-trigger" state. Scanning will begin when the specified 
        #   trigger conditions are satisfied following the receipt of the READ? command. Readings are then sent immediately to reading memory and the instrument's 
        #   output buffer. On the 34970A, you must then receive the readings into your computer or the instrument will stop scanning when the output buffer becomes full.
        #   Readings are not stored in the instruments internal memory when using READ?. On the 34972A, the readings are always sent to memory and they will still be 
        #   available after READ? finishes.
        #   First 4 FORMat commands are required
        #readings = logger.query(':READ? (%s)' % ('@102'))
        # READ? is the same as INITiate and FETCh? below
        #for n in [1:2]:
            

        # INITiate - This command changes the state of the triggering system from the "idle" state to the "wait-for-trigger" state. Scanning will begin when the 
        #   specified trigger conditions are satisfied following the receipt of the INITiate command. Readings are stored in the instrument's internal reading memory. 
        #   Note that the INITiate command also clears the previous set of readings from memory.
        #   Needs scanning enabled
        logger.write(':INITiate')
        logger.write(':FORMat:READing:CHANnel %d' % (1))
        logger.write(':FORMat:READing:ALARm %d' % (1))
        logger.write(':FORMat:READing:UNIT %d' % (1))
        logger.write(':FORMat:READing:TIME:TYPE %s' % ('ABS'))
        logger.write(':FORMat:READing:ALARm %d' % (1))

        # NO LOOP
        #readings1 = logger.query(':FETCh?')
        #print("output of logger: ", readings1)
        
        #logger.write(':ROUTe:SCAN (%s)' % ('@108, 110, 212, 213, 214, 215, 216, 217')) # this is where you put multiple
        
        # LOOPING
        for n in range(500): #time delay of 2 seconds means 2*30 = 60 so n=30 for 1 minute, n=150 for 5 minutes, n=90 for 3 minutes
            # Fixed the time to use the time of the system instead of the time of the datalogger because the clock is a little fast
            current_time = datetime.now().strftime("%H:%M") #"%H:%M:%S"
            print("current time: ", current_time)
            file_object.write("\n" + current_time + "\n")


            # FETCh? - This command transfers readings stored in non-volatile memory to the instrument's output buffer, where you can read them into your computer. The 
            #    readings stored in memory are not erased when you read them with FETCh?. The format of the readings can be changed using FORMat:READing commands.
            logger.write(':INITiate')
            readings1 = logger.query(':FETCh?')
            print("output of logger: ", readings1)
            #file_raw.write(readings1)
            #file_raw.write("\n")

            # Here we use regex to find expressions starting with a + and also contains a second + until we reach the next group starting with a +
            # Format of 2 readings: example = "+1.46376840E+02 OHM,102,0,+9.90000000E+37 OHM,103,0"
            # Format of 1 reading: "+reading,channel,time"
            pattern = re.compile(r'([+-]?\d*\.?\d+E[+-]?\d+)\s*([A-Za-z,0-9]+)')  # new regex pattern
                # [+-]? matches optional sign
                # \d* matches 0-any digits
                # \.? is optional decimal
                # \d+ is 1-any digits
                # E is exponential for sci notation
                # [+-]?\d+ is exponent part with optional sign and 1-any digits
                # \s* is 0-any whitespaces
                # ([A-Za-z,0-9]+) is 1-any characters of letters or numbers

            assignments = ['flow', 'DNI', 'GHI1', 'GHI2', 'radout', 'radin', 'TC1 - G', 'TC2 - H', 'TC3 - I', 'TC4 - J', 'TC5 - K', 'TC6 - L']

            count = 0
            for m in re.finditer(pattern, readings1): # need to iterate because we need to read multiple channels
                res = m.group(0)
                out = assignments[count] + ": " + res.removesuffix(',')
                print(out) # remove the last comma of each line if there is one
                count +=1
                file_object.write(out) # write out to file
                file_object.write("\n")
            
            # BUILDING LOOP
            pattern = re.compile(r'([+-]?\d*\.?\d+E[+-]?\d+)\s*C,212,\d+')  # Adjusted regex pattern to specifically match TC1

            for m in re.finditer(pattern, readings1):
                res = m.group(1)  # extract
                tc1_value = float(res)

            pattern = re.compile(r'([+-]?\d*\.?\d+E[+-]?\d+)\s*C,217,\d+')  # Adjusted regex pattern to specifically match TC6

            for m in re.finditer(pattern, readings1):
                res = m.group(1)  # extract
                tc6_value = float(res)

            tc_difference = tc6_value - tc1_value
            print("Difference between TC6 and TC1:", tc_difference)

            if tc_difference > 10:
                led.on() # send signal to building pump to turn off and dump heat into building

            time.sleep(2)
        
        
        print("\n Finished requested reading")

        """
        # ALARM - more updated version in another file, don't want to use relay right now
        logger.write(':OUTPut:ALARm1:SOURce (%s)' % ('@105, 106, 107, 108, 201, 202, 203, 204')) 
        #assigns one of four alarm numbers to report any alarm conditions on the specified multiplexer or digital channels.
        logger.write(':CALCulate:LIMit:UPPer %G,(%s)' % (110.0, '@105, 106, 107, 108, 201, 202, 203, 204'))
        #These commands set the lower and upper limits for alarms on the specified channels.
        logger.write(':CALCulate:LIMit:UPPer:STATe %d,(%s)' % (1, '@105, 106, 107, 108, 201, 202, 203, 204'))
        #These commands disable or enable the lower and upper alarm limits on the specified multiplexer channels
        alarm_message = logger.query(':SYSTem:ALARm?') 
        #This query reads the alarm data from the alarm queue (one alarm event is read and deleted from the queue each time this command is executed). 
        #A record of up to 20 alarms can be stored in the instrument's alarm queue.
        temp_values = logger.query_ascii_values(':STATus:ALARm:EVENt?')
        #This command queries the event register for the Alarm Register group.
        register = int(temp_values[0])
        """


    except Exception as e:
        print("\n  Exception:", e.__class__.__name__, e.args)

    finally:
        logger.close() # close out this session
        rm.close() # close the resource manager
        file_object.close()
        #file_raw.close()
        input("\nDone - Press Enter to Exit")


if __name__ == "__main__":
    main()