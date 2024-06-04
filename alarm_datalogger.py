# This driver is only supported by python 3.10 and I have python 3.11 installed as well so force ./filename to be run with this interpreter

# Thalia Koutsougeras
# Agilent 34972A datalogger python script specifically for working with the alarm output

# Full descriptions of commands from the manual in the link below:
# http://instructor.physics.lsa.umich.edu/adv-labs/Tools_Resources/HP%2034970%20user's%20guide.pdf


import numpy as np
import pyvisa as visa
import re
import time


def main():
    rm = visa.ResourceManager() # VISA Resource Manager keeps track of instruments and creates sessions to them as requested
    addr = 'USB0::0x0957::0x2007::MY49016664::0::INSTR' # Grabbed from Keysight Connection Expert
    # USB[ board ]:: manufacturer ID :: model code :: serial number [:: USB interface number ][::INSTR]

    try:
        logger = rm.open_resource(addr) # Open session for the datalogger with resource manager
        print("\n Manufacturer/Model/Serial/Firmware level: ", logger.query('*IDN?')) # Reads out manufacturer, model, serial number, firmware level and options in an ASCII response data element

        logger.timeout =  10000

        logger.write('*CLS')
        
        # TEMPERATURE READINGS - just testing out on 1 thermocouple
        # SENSe - This checks that thermocouple is properly connected 
        logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:CHECk %d,(%s)' % (1, '@202'))
        # SENSe - This selects the thermocouple type to use
        logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:TYPE %s,(%s)' % ('K', '@202'))
        # CONFigure - These commands configure the channels for temperature measurements but do not initiate the scan.
        logger.write(':CONFigure:TEMPerature %s,%s,(%s)' % ('TCouple', 'K', '@202')) ### TOGGLED OFF
        
        
        # ALARM SETUP
        logger.write(':OUTPut:ALARm1:CLEar')
        logger.write(':OUTPut:ALARm:MODE %s' % ('LATC')) #TRAC
        # see pg 128 of manual to choose latch or track mode
        logger.write(':OUTPut:ALARm:SLOPe %s' % ('POSitive')) #rising edge - so +5V triggers the alarm
        logger.write(':OUTPut:ALARm1:SOURce (%s)' % ('@202')) # scanning channel 202 specifically to trigger an alarm
        #assigns one of four alarm numbers to report any alarm conditions on the specified multiplexer or digital channels.

        logger.write(':CALCulate:LIMit:UPPer %G,(%s)' % (29, '@202')) #setting the temperature at which the alarm will trip
        #These commands set the lower and upper limits for alarms on the specified channels.

        logger.write(':CALCulate:LIMit:UPPer:STATe %d,(%s)' % (1, '@202'))
        #These commands disable or enable the lower and upper alarm limits on the specified multiplexer channels

        logger.write(':ROUTe:SCAN (%s)' % ('@202')) # this has to go after the alarm setup

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

        readings1 = logger.query(':FETCh?')
        print("output of logger: ", readings1)

        alarm_message = logger.query(':SYSTem:ALARm?')
        print("\n messg: ", alarm_message)
        print("\n")
    
        print("\n Finished requested reading")
        


    except Exception as e:
        print("\n  Exception:", e.__class__.__name__, e.args)

    finally:
        logger.close() # close out this session
        rm.close() # close the resource manager
        input("\nDone - Press Enter to Exit")


if __name__ == "__main__":
    main()