# This driver is only supported by python 3.10 and I have python 3.11 installed as well so force ./filename to be run with this interpreter
# I changed my environment variables to run python 3.10 automatically
# This code is fully working

# i dont know if i need this anymore !/usr/bin/env python3.10

# Thalia Koutsougeras
# Agilent 34972A datalogger python script for gathering temperatures from thermocouples

# Full descriptions of commands from the manual in the link below:
# http://instructor.physics.lsa.umich.edu/adv-labs/Tools_Resources/HP%2034970%20user's%20guide.pdf

import numpy as np # For keysight_ktdaq970 arrays
import pyvisa as visa
import re


def main():
    def remove_suffix(input_string, suffix):
        if suffix and input_string.endwith(suffix):
            return input_string[:-len(suffix)]
        return input_string
    
    rm = visa.ResourceManager('@py') # VISA Resource Manager keeps track of instruments and creates sessions to them as requested
    #addr = 'USB0::0x0957::0x2007::MY49016664::0::INSTR' # Grabbed from Keysight Connection Expert
    addr = 'USB0::2391::8199::MY49016664::0::INSTR' #from raspberry pi - same thing as windows but in decimal
    # USB[ board ]:: manufacturer ID :: model code :: serial number [:: USB interface number ][::INSTR]

    # Opening a file for writing to
    file_object = open("measurements.txt", "w")

    try:
        print("\n  keysight_ktdaq970 Python\n")
        print("\n available instruments: ", rm.list_resources()) # Print out list of available instruments
        logger = rm.open_resource(addr) # Open session for the datalogger with resource manager
        print("\n Manufacturer/Model/Serial/Firmware level: ", logger.query('*IDN?')) # Reads out manufacturer, model, serial number, firmware level and options in an ASCII response data element

        #logger.timeout =  10000
        #logger.write('*RST') # Resets the instrument

        """
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
        """

        # TEMPERATURE READINGS
        # SENSe - This checks that thermocouple is properly connected 
        logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:CHECk %d,(%s)' % (1, '@202'))
        # SENSe - This selects the thermocouple type to use
        logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:TYPE %s,(%s)' % ('K', '@202'))

        # CONFigure - These commands configure the channels for temperature measurements but do not initiate the scan.
        logger.write(':CONFigure:TEMPerature %s,%s,(%s)' % ('TCouple', 'K', '@202'))

        # ROUT - This command selects the channels to be included in the scan list. This command is used in conjunction with the CONFigure commands to set up an 
        #    automated scan. The specified channels supersede any channels previously defined to be part of the scan list. To start the scan, use the INITiate or 
        #    READ? command. 
        logger.write(':ROUTe:SCAN (%s)' % ('@202'))

        # READ? - This command changes the instrument's triggering system from the "idle" state to the "wait-for-trigger" state. Scanning will begin when the specified 
        #   trigger conditions are satisfied following the receipt of the READ? command. Readings are then sent immediately to reading memory and the instrument's 
        #   output buffer. On the 34970A, you must then receive the readings into your computer or the instrument will stop scanning when the output buffer becomes full.
        #   Readings are not stored in the instruments internal memory when using READ?. On the 34972A, the readings are always sent to memory and they will still be 
        #   available after READ? finishes.
        #   First 4 FORMat commands are required
        #readings = logger.query(':READ? (%s)' % ('@102'))
        # READ? is the same as INITiate and FETCh? below

        # INITiate - This command changes the state of the triggering system from the "idle" state to the "wait-for-trigger" state. Scanning will begin when the 
        #   specified trigger conditions are satisfied following the receipt of the INITiate command. Readings are stored in the instrument's internal reading memory. 
        #   Note that the INITiate command also clears the previous set of readings from memory.
        #   Needs scanning enabled
        logger.write(':INITiate')
        logger.write(':FORMat:READing:CHANnel %d' % (1))
        logger.write(':FORMat:READing:ALARm %d' % (1))
        logger.write(':FORMat:READing:UNIT %d' % (1))
        logger.write(':FORMat:READing:TIME:TYPE %s' % ('REL'))
        # FETCh? - This command transfers readings stored in non-volatile memory to the instrument's output buffer, where you can read them into your computer. The 
        #    readings stored in memory are not erased when you read them with FETCh?. The format of the readings can be changed using FORMat:READing commands.
        readings1 = logger.query(':FETCh?')
        print(readings1)

        # Here we use regex to find expressions starting with a + and also contains a second + until we reach the next group starting with a +
        # Format of 2 readings: example = "+1.46376840E+02 OHM,102,0,+9.90000000E+37 OHM,103,0"
        # Format of 1 reading: "+reading,channel,time"
        pattern = re.compile(r'[+].*?([+][0-9A-Z, ]+)') #regex
        for m in re.finditer(pattern, readings1): # need to iterate because we need to read multiple channels
            res = m.group(0)
            #print(res.removesuffix(',')) # remove the last comma of each line if there is one
            # removesuffix is a python 3.9+ command but im running 3.7
            print(remove_suffix(res, ','))
            #file_object.write(res.removesuffix(',')) # write out to file
            file_object.write(remove_suffix(res, ',')) # write out to file
            file_object.write("\n")

        
        print("\n Finished requested reading")

    except Exception as e:
        print("\n  Exception:", e.__class__.__name__, e.args)

    finally:
        logger.close() # close out this session
        rm.close() # close the resource manager
        file_object.close()
        input("\nDone - Press Enter to Exit")


if __name__ == "__main__":
    main()
