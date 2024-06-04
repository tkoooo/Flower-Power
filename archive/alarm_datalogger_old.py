#!/usr/bin/env python3.10
# This driver is only supported by python 3.10 and I have python 3.11 installed as well so force ./filename to be run with this interpreter
# I changed my environment variables to run python 3.10 automatically
# This code is fully working

# Thalia Koutsougeras
# Agilent 34972A datalogger python script for gathering temperatures from thermocouples

# Full descriptions of commands from the manual in the link below:
# http://instructor.physics.lsa.umich.edu/adv-labs/Tools_Resources/HP%2034970%20user's%20guide.pdf

"""
# Channel Assignments:
# 105 - TC1 (C)
# 106 - TC2 (C)
# 107 - TC3 (C)
# 108 - TC4 (C)
# 109 - PV Inlet (C)
# 110 - TR Outlet (C)
# 111 - PV Outlet (C)
# 112 - TR Inlet (C)
# 113 - TR Pump Outlet P (V)
# 114 - TR Outlet P (V)
# 120 - Outside Temp (C)
# 201 - TC5 (C)
# 202 - TC6 (C)
# 203 - TC7 (C)
# 204 - TC8 (C)

"""

"""
# SFR2 TESTING:
# 1 - 101 - L
# 2 - 102 - G
# 3 - 103 - H
# 4 - 104 - I
# 5 - 105 - J
# 6 - 106 - K
# '@101, 102, 103, 104, 105, 106'
# '@201, 202, 203, 204, 205, 206'
"""

"""
# sfr 2 tESTING  3/6/24
# 1 - 212 - G
# 2 - 213 - H
# 3 - 214 - I
# 4 - 215 - J
# 5 - 216 - K
# 6 - 217 - L
# ghi 1 - 108
# GHI 2 - 110
# dni - 106
# '@212, 213, 214, 215, 216, 217'

# 3/7/24 switched 2 and 6 bc L is the one floating in the wind

sfr3 test 1 4/12
105 - flowmeter 
106 - dni
108 - ghi 
110 - ghi

"""


import numpy as np # For keysight_ktdaq970 arrays
import pyvisa as visa
import re
import time


def main():
    Channel_Dict = {105: 'TC1', 106: 'TC2', 107: 'TC3', 108: 'TC4', 109: 'PV Inlet', 110: 'TR Outlet', 111: 'PV Outlet', 112: 'TR Inlet', 113: 'TR Pump Outlet P', 
                    114: 'TR Outlet P', 120: 'Outside Temp', 201: 'TC5', 202: 'TC6', 203: 'TC7', 204: 'TC8'}

    rm = visa.ResourceManager() # VISA Resource Manager keeps track of instruments and creates sessions to them as requested
    addr = 'USB0::0x0957::0x2007::MY49016664::0::INSTR' # Grabbed from Keysight Connection Expert
    # USB[ board ]:: manufacturer ID :: model code :: serial number [:: USB interface number ][::INSTR]

    try:
        #print("\n  keysight_ktdaq970 Python\n")
        #print("\n available instruments: ", rm.list_resources()) # Print out list of available instruments
        logger = rm.open_resource(addr) # Open session for the datalogger with resource manager
        print("\n Manufacturer/Model/Serial/Firmware level: ", logger.query('*IDN?')) # Reads out manufacturer, model, serial number, firmware level and options in an ASCII response data element

        logger.timeout =  10000

        logger.write('*CLS')

        
        # TEMPERATURE READINGS
        # SENSe - This checks that thermocouple is properly connected 
        logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:CHECk %d,(%s)' % (1, '@202'))
        # SENSe - This selects the thermocouple type to use
        logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:TYPE %s,(%s)' % ('K', '@202'))

        # CONFigure - These commands configure the channels for temperature measurements but do not initiate the scan.
        logger.write(':CONFigure:TEMPerature %s,%s,(%s)' % ('TCouple', 'K', '@202')) ### TOGGLED OFF

        # ROUT - This command selects the channels to be included in the scan list. This command is used in conjunction with the CONFigure commands to set up an 
        #    automated scan. The specified channels supersede any channels previously defined to be part of the scan list. To start the scan, use the INITiate or 
        #    READ? command. 
        
        
        # ALARM
        logger.write(':OUTPut:ALARm1:CLEar')
        logger.write(':OUTPut:ALARm:MODE %s' % ('LATC')) #TRAC
        logger.write(':OUTPut:ALARm:SLOPe %s' % ('POSitive'))
        logger.write(':OUTPut:ALARm1:SOURce (%s)' % ('@202')) 
        #assigns one of four alarm numbers to report any alarm conditions on the specified multiplexer or digital channels.

        logger.write(':CALCulate:LIMit:UPPer %G,(%s)' % (29, '@202')) #+3.5E+01
        #These commands set the lower and upper limits for alarms on the specified channels.

        logger.write(':CALCulate:LIMit:UPPer:STATe %d,(%s)' % (1, '@202'))
        #These commands disable or enable the lower and upper alarm limits on the specified multiplexer channels

        logger.write(':ROUTe:SCAN (%s)' % ('@202')) # this is where you put multiple

        #alarm_message = logger.query(':SYSTem:ALARm?') 
        #This query reads the alarm data from the alarm queue (one alarm event is read and deleted from the queue each time this command is executed). 
        #A record of up to 20 alarms can be stored in the instrument's alarm queue.

        alarm_message = logger.query(':SYSTem:ALARm?')
        print("\n messg: ", alarm_message)
        print("\n")

        temp_values = logger.query_ascii_values(':STATus:ALARm:EVENt?')
        #This command queries the event register for the Alarm Register group.
        register = int(temp_values[0])

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
        
        
        #logger.write(':INITiate')
        readings1 = logger.query(':FETCh?')
        print("output of logger: ", readings1)

        alarm_message = logger.query(':SYSTem:ALARm?')
        print("\n messg: ", alarm_message)
        print("\n")
        

        """
        # LOOPING
        for n in range(5): #time delay of 2 seconds means 2*30 = 60 so n=30 for 1 minute, n=150 for 5 minutes, n=90 for 3 minutes

            # FETCh? - This command transfers readings stored in non-volatile memory to the instrument's output buffer, where you can read them into your computer. The 
            #    readings stored in memory are not erased when you read them with FETCh?. The format of the readings can be changed using FORMat:READing commands.
            logger.write(':INITiate')
            readings1 = logger.query(':FETCh?')
            print("output of logger: ", readings1)
            
            #temp_valuesal = logger.query_ascii_values(':STATus:ALARm:EVENt?')
            #This command queries the event register for the Alarm Register group.
            #print("\n tempvaluesal: ", temp_valuesal)
            #registeral = int(temp_values[0])
            #print("\n registeral: ", registeral)
            alarm_message = logger.query(':SYSTem:ALARm?')
            print("\n messg: ", alarm_message)
            print("\n")
            

            time.sleep(5)
        """
        
        

        print("\n Finished requested reading")
        


    except Exception as e:
        print("\n  Exception:", e.__class__.__name__, e.args)

    finally:
        logger.close() # close out this session
        rm.close() # close the resource manager
        input("\nDone - Press Enter to Exit")


if __name__ == "__main__":
    main()
