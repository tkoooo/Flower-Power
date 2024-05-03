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
# 1 - 212 - L
# 2 - 213 - G
# 3 - 214 - H
# 4 - 215 - I
# 5 - 216 - J
# 6 - 217 - K
# ghi 1 - 108
# GHI 2 - 110
# '@212, 213, 214, 215, 216, 217'
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

    # Opening a file for writing to
    file_object = open("measurements_030724_T1_movingonsun3_highMFR.txt", "w")

    try:
        #print("\n  keysight_ktdaq970 Python\n")
        #print("\n available instruments: ", rm.list_resources()) # Print out list of available instruments
        logger = rm.open_resource(addr) # Open session for the datalogger with resource manager
        print("\n Manufacturer/Model/Serial/Firmware level: ", logger.query('*IDN?')) # Reads out manufacturer, model, serial number, firmware level and options in an ASCII response data element

        logger.timeout =  10000
        #logger.write('*RST') # Resets the instrument - factory reset every time ### TOGGLED OFF

        # You only need to set the time and date once if you don't reset every time
        #logger.write("SYST:DATE 2023,03,07") #<yyyy>,<mm>,<dd>  ### TOGGLED OFF
        #logger.write("SYST:TIME 14,46,00.000") #SYSTem:TIME <hh>,<mm>,<ss.sss> ### TOGGLED OFF

        #print("time testing\n") 
        #print(logger.write("FORM:READ:TIME:TYPE?"))


    
        # RESISTANCE READINGS UPDATED 11/27/23
        # WE PROBABLY WON'T NEED THIS CODE 
        #SENSe - This command disables or enables autoranging for 2-wire (RESistance) or 4-wire (FRESistance) resistance measurements on the specified channels.
        #   autoranging automatically selects range for signal detected
        #logger.write(':INSTrument:DMM %d' % (1)) #turns the internal DMM on for a multiplexer module - this didn't help
        #logger.write(':SENSe:RESistance:RANGe:AUTO %d,(%s)' % (1, '@102, 103'))
        
        # CONFigure - These commands configure the channels for 2-wire (RESistance) or 4-wire (FRESistance) resistance measurements but do not initiate the scan. 
        #   does not place the instrument in the "wait-for-trigger" state. Use the INITiate or READ? command in conjunction with CONFigure to place the instrument 
        #   in the "wait-for-trigger" state.
        #logger.write(':CONFigure:RESistance (%s)' % ('@102, 103'))




        # GHI SENSOR READINGS (0-40 mV) - The Global Horizontal Irradiande (GHI) measures the total amount of light received by a square meter on the ground.
        # 2 sensors - channels 110, 111
        # First test - channel 110 is circle sensor, 111 is square
        # SENSe - These commands disable or enable autoranging for AC and DC voltage measurements on the specified channels. Autoranging is 
        # convenient because the instrument automatically selects the range for each measurement based on the input signal detected.
        logger.write(':SENSe:VOLTage:DC:RANGe:AUTO %d,(%s)' % (1, '@106, 108, 110'))

        # CONFigure - These commands configure the channels in the <scan_list> for AC or DC voltage measurements but do not initiate the scan. 
        logger.write(':CONFigure:VOLTage:DC %s,(%s)' % ('AUTO', '@106, 108, 110'))
        
        # ROUT - This command selects the channels to be included in the scan list. 
        #logger.write(':ROUTe:SCAN (%s)' % ('@108,110'))

        
        # TEMPERATURE READINGS
        # SENSe - This checks that thermocouple is properly connected 
        logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:CHECk %d,(%s)' % (1, '@212, 213, 214, 215, 216, 217'))
        # SENSe - This selects the thermocouple type to use
        logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:TYPE %s,(%s)' % ('K', '@212, 213, 214, 215, 216, 217'))

        # CONFigure - These commands configure the channels for temperature measurements but do not initiate the scan.
        logger.write(':CONFigure:TEMPerature %s,%s,(%s)' % ('TCouple', 'K', '@212, 213, 214, 215, 216, 217')) ### TOGGLED OFF

        # ROUT - This command selects the channels to be included in the scan list. This command is used in conjunction with the CONFigure commands to set up an 
        #    automated scan. The specified channels supersede any channels previously defined to be part of the scan list. To start the scan, use the INITiate or 
        #    READ? command. 
        logger.write(':ROUTe:SCAN (%s)' % ('@106, 108, 110, 212, 213, 214, 215, 216, 217')) # this is where you put multiple
        

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
        for n in range(300): #time delay of 2 seconds means 2*30 = 60 so n=30 for 1 minute, n=150 for 5 minutes, n=90 for 3 minutes
            # Display time of this measurement and also write to file
            time_values = logger.query_ascii_values(':SYSTem:TIME?')
            hh = int(time_values[0])
            mm = int(time_values[1])
            sss = time_values[2]
            print("\n\n Current time: ", hh, ":", mm)
            time_string = "\nCurrent time: " + str(hh) + ":" + str(mm) + "\n"
            file_object.write(time_string)


            # FETCh? - This command transfers readings stored in non-volatile memory to the instrument's output buffer, where you can read them into your computer. The 
            #    readings stored in memory are not erased when you read them with FETCh?. The format of the readings can be changed using FORMat:READing commands.
            logger.write(':INITiate')
            readings1 = logger.query(':FETCh?')
            print("output of logger: ", readings1)

            # Here we use regex to find expressions starting with a + and also contains a second + until we reach the next group starting with a +
            # Format of 2 readings: example = "+1.46376840E+02 OHM,102,0,+9.90000000E+37 OHM,103,0"
            # Format of 1 reading: "+reading,channel,time"
            #pattern = re.compile(r'[+].*?([+][0-9A-Z, ]+)') #old regex - wasn't correct
            pattern = re.compile(r'([+-]?\d*\.?\d+E[+-]?\d+)\s*([A-Za-z,0-9]+)')  # new regex pattern
                # [+-]? matches optional sign
                # \d* matches 0-any digits
                # \.? is optional decimal
                # \d+ is 1-any digits
                # E is exponential for sci notation
                # [+-]?\d+ is exponent part with optional sign and 1-any digits
                # \s* is 0-any whitespaces
                # ([A-Za-z,0-9]+) is 1-any characters of letters or numbers

            #assignments = [Channel_Dict[105], Channel_Dict[106], Channel_Dict[107], Channel_Dict[108], Channel_Dict[109], Channel_Dict[110]]
            #assignments = ['TC1 - L', 'TC3 - H', 'TC4 - I', 'TC5 - J', 'TC6 - K', 'TC2 - G']
            #assignments = ['GHI1', 'GHI2', 'GHI3', 'TC1 - G', 'TC2 - H', 'TC3 - I', 'TC4 - J', 'TC5 - K', 'TC6 - L']
            assignments = ['DNI', 'GHI1', 'GHI2', 'TC1 - G', 'TC2 - H', 'TC3 - I', 'TC4 - J', 'TC5 - K', 'TC6 - L']

            count = 0
            for m in re.finditer(pattern, readings1): # need to iterate because we need to read multiple channels
                res = m.group(0)
                out = assignments[count] + ": " + res.removesuffix(',')
                print(out) # remove the last comma of each line if there is one
                count +=1
                file_object.write(out) # write out to file
                file_object.write("\n")
            time.sleep(2)
        
        
        print("\n Finished requested reading")

        """
        # ALARM
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
        input("\nDone - Press Enter to Exit")


if __name__ == "__main__":
    main()
