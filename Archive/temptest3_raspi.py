
import pyvisa as visa
rm = visa.ResourceManager('@py')
print(rm.list_resources())
