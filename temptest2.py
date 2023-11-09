#!/usr/bin/env python3.10
# This driver is only supported by python 3.10 and I have python 3.11 installed as well so force ./filename to be run with this interpreter

# Thalia Koutsougeras
# Agilent 34972A datalogger python script for gathering temperatures from thermocoupless

import numpy as np # For keysight_ktdaq970 arrays
#import sys
# caution: path[0] is reserved for script path (or '' in REPL)
#sys.path.insert(1, r'C:\Users\Thalia\AppData\Local\Programs\Python\Python310\Lib\site-packages\keysight_ktdaq970')
import keysight_ktdaq970 
import pyvisa as visa


def main():
    rm = visa.ResourceManager() # VISA Resource Manager keeps track of instruments and creates sessions to them as requested
    addr = 'USB0::0x0957::0x2007::MY49016664::0::INSTR' # Grabbed from Keysight Connection Expert

    try:
        print("\n  keysight_ktdaq970 Python\n")

        logger = rm.open_resource(addr) # Open session for the datalogger with resource manager

        #logger.timeout =  10000
        logger.write('*RST') # Resets the instrument

        # requirement for configure
        logger.write(':FORMat:READing:CHANnel %d' % (1))
        logger.write(':FORMat:READing:ALARm %d' % (1))
        logger.write(':FORMat:READing:UNIT %d' % (1))
        logger.write(':FORMat:READing:TIME:TYPE %s' % ('REL'))

        #logger.write(':SENSe:TEMPerature:TRANsducer:TCouple:CHECk %d,(%s)' % (1, '101')) # just to check to see if everything is working with the thermocouple
        #logger.write(':CONFigure:TEMPerature %s,%s,(%s)' % ('TCouple', 'K', '101, 102')) # Requests a temperature measurement (probe, type, channel)
        logger.write(':CONFigure:FRESistance (%s)' % ('102'))
        print("\n Requested reading")

        # TODO: Check instrument for errors

    except Exception as e:
        print("\n  Exception:", e.__class__.__name__, e.args)

    finally:
        logger.close()
        rm.close()
        input("\nDone - Press Enter to Exit")


if __name__ == "__main__":
    main()