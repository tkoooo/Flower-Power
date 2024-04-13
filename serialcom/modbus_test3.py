# Thalia Koutsougeras
# Raspberry Pi RS 485 Communication with Solar Tracking System
# How to code serial: https://circuitdigest.com/microcontroller-projects/rs485-serial-communication-between-arduino-and-raspberry-pi 
# https://wiki.seeedstudio.com/RS-485_Shield_for_Raspberry_Pi/ 
# https://www.circuitstate.com/tutorials/what-is-rs-485-how-to-use-max485-with-arduino-for-reliable-long-distance-serial-communication/ 
# Raspbi is the "master", and tracking system is the "slave", adn MAX485 DIP is in between
# half-duplex bc 2 wires
# run every day at a certain time: https://www.codementor.io/@gergelykovcs/how-to-run-and-schedule-python-scripts-on-raspberry-pi-n2clhe3kp 


import numpy as np 
import time
import serial
import RPi.GPIO as GPIO
from time import sleep
import datetime

from pymodbus.client.sync import ModbusSerialClient


#import serial 
import serial.rs485 
#import time
#from time import sleep
#import RPi.GPIO as GPIO 


def main():
    
    # https://medium.com/raspberry-pi-and-rs485-modbus/modbus-rs485-raspberry-pi-5ccbc1996b7d 
    TXDEN_1=7 # transmit enable pin 
     
    GPIO.setwarnings(False) 
    GPIO.setmode(GPIO.BOARD) 
    GPIO.setup(TXDEN_1, GPIO.OUT, initial=GPIO.HIGH) 
     
    porty = '/dev/serial0' #'/dev/ttyS0'
    ser=serial.rs485.RS485(port=porty,baudrate=9600,timeout=3,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS) 
    ser.rs485_mode = serial.rs485.RS485Settings(rts_level_for_tx=False, rts_level_for_rx=False, delay_before_tx=0.0, delay_before_rx=-0.0) 
     
    SendFrameo =b'\x01\x03\x00\x02\x00\x01\x25\xCA' # data is in hex format in python since rs485 rtu uses hex encoded data
    SendFrame =b'\x06\x03\x9C\x46\x00\x01\x25\xCA' # data is in hex format in python since rs485 rtu uses hex encoded data
    # slave id 01, function code 03, addr of first register to read in 2 bytes = 00 01, num registers to read = 00 01, checksum 2 bytes = D5 CA,
    # 01 03 00 01 00 01 D5 CA
    # 00 01, 06 00, 00 06, 6 reg, 9C 46

     
     
    while True: 
        GPIO.output(TXDEN_1, GPIO.HIGH) #write enabled for sending data frame to read the register 
        ser.write(SendFrame) #sending data frame 
        GPIO.output(TXDEN_1, GPIO.LOW) #read enabled to get reply from pymodbus slave software 
        coming_data = ser.inWaiting() #checking buffer with data available 
        print("comming_data:",coming_data) # if no data is available comming data will be equal to 0 
        x=ser.read(ser.inWaiting()) #reading the actual data from pymodbus slave
        #x = ser.read(size=800) # didnt help
        print(repr(x))# printing in hex format 
        print("ok") 
        time.sleep(2)
        
        


    # OLD CODE WITH PYSERIAL
    """
    GPIO.setmode(GPIO.BOARD) #referring to the pins by the number of pin in the board
    GPIO.setup(7, GPIO.OUT, initial=GPIO.HIGH) #GPIO pin 4 (connected to DE & RE of RS-485)

    # initiate sreial class at pins GPIO14 and 15 - these are the serial connection ports
    send = serial.Serial(
        port='/dev/serial0',
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
    
    send.write(str(8)) # take off sun and return towards home position fully pointed away from the sun
    print("ERROR! cells exceeded 100C")
    sleep(5) # cool off for 30 seconds
    """
    
    """
    # code ive been testing

    # also industrialshields.com
    # basic starter code taken from https://stackoverflow.com/questions/70686813/how-to-access-particular-registers-using-pymodbus-rtu 
    client = ModbusSerialClient(
        #port='/dev/serial0',
        port = '/dev/ttyS0',
        startbit=1,
        databits=8,
        parity="N",
        stopbits=1,
        errorcheck="crc",
        baudrate=9600,
        method="RTU",
        timeout=3,
    )

    if client.connect():  # Trying for connect to Modbus slave
        # ONLINE CODE
        # Read holding register
        print("Connection Successful")
        addressi = int(0x40006)
        addressih=0x40006
        address3 = 40006
        slave_address = 0x06
        slave_address2 = 6
        res = client.read_holding_registers(address=address3, count=1, unit=slave_address)

        # Where "address" is register address
        # Where "count" is the number of registers to read
        # Where "unit" is the slave address, found in vendor documentation
        print(res)
        client.close()

        # -------------------------------------------------------------------------------
        # MY CODE
        # I will need to write to a register: function code 0x06
        # I want to write to register (integer value) not a coil (single bit on/off)
        # I think in the tracker manual, 40006.8 means register 40006 code 8
        # documentation from: https://readthedocs.org/projects/pymodbus/downloads/pdf/latest/ 
        
        write_register(address: int, value: int, slave: int = 0, **kwargs: Any) → T
        Write register (code 0x06).
        Parameters
        • address – Address to write to
        • value – Value to write
        • slave – (optional) Modbus slave ID
        • kwargs – (optional) Experimental parameters.
        Raises
        ModbusException –
        
        # new code - these expect integer values
        print("Connection Successful")
        address = int(0x40006) # this register from manual - may need a different one
        value = 8 # this code under this register
        slave = 6 #(number from 1-255) - i got this from the solar tracker
        res = client.write_register(address, value, slave)
        print(res)
        client.close()
    
        

    else:
        print("Failed to connect to Modbus device")
    """

    sleep(3)


if __name__ == "__main__":
    main()