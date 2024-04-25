# Thalia Koutsougeras
# Plotting code converted from Owen's Matlab program

import re
import numpy as np
import matplotlib.pyplot as plt


measurementsPerMinute = 30 #was 24
openArea = (16 * 14 * .002025) / 2.7 #m^2
dishArea = 2.7 # was 2.66
specificHeat = 4.184

filename = "measurements_042424_T1_test.txt"
file_object = open(filename, "r")


with open(filename, "r") as file:
    data = file.read()

# TIME EXTRACTION
timepat = r"time: (\d+):(\d+)"
times = [int(hour) * 60 + int(minute) for hour, minute in re.findall(timepat, data)]

# for plotting time series
t = np.arange(len(times)) / measurementsPerMinute

# FLOW EXTRACTION
flowpat = r"flow: ([+-]?\d+\.\d+E[+-]\d+)"
flow = [float(val) for val in re.findall(flowpat, data)]
flow = [(val - 3.7113) / 135.78 * 63.09 if val < 500 else 0 for val in flow]

# DNI extraction
dnipat = r"DNI: ([+-]?\d+\.\d+E[+-]\d+)"
DNI = [float(val) / 0.008 for val in re.findall(dnipat, data)]

# Data extraction for TC temps
gpat = r"G: ([+-]?\d+\.\d+E[+-]\d+)"
hpat = r"H: ([+-]?\d+\.\d+E[+-]\d+)"
ipat = r"I: ([+-]?\d+\.\d+E[+-]\d+)"
jpat = r"J: ([+-]?\d+\.\d+E[+-]\d+)"
kpat = r"K: ([+-]?\d+\.\d+E[+-]\d+)"
lpat = r"L: ([+-]?\d+\.\d+E[+-]\d+)"

G = [float(val) for val in re.findall(gpat, data)]
H = [float(val) for val in re.findall(hpat, data)]
I = [float(val) for val in re.findall(ipat, data)]
J = [float(val) for val in re.findall(jpat, data)]
K = [float(val) for val in re.findall(kpat, data)]
L = [float(val) for val in re.findall(lpat, data)]

# analysis
deltaT = np.array(L) - np.array(G)
massFlowRate = np.array(flow)
Wcoil = massFlowRate * specificHeat * deltaT
Wincident = openArea * np.array(DNI) * dishArea * 1000
efficiency = (Wcoil / Wincident) * 100

# plot of temps DNI over time
plt.figure()
plt.plot(t, G, color='#7E2F8E', linewidth=1.5)
#plt.plot(t, H, color='#0051ff', linewidth=1.5)
#plt.plot(t, I, color='#00ff04', linewidth=1.5)
#plt.plot(t, J, color='#e3ff00', linewidth=1.5)
#plt.plot(t, K, color='#ff8d00', linewidth=1.5)
#plt.plot(t, L, color='#ff1a00', linewidth=1.5)
#plt.ylim([25, 50])
plt.ylabel("Temperature (C)")
plt.gca().yaxis.set_label_coords(-0.06, 0.5)
plt.show()



plt.twinx()
plt.grid(True)
plt.plot(t, DNI, color='black', linestyle="-", linewidth=2)
plt.ylabel("Irradiance (kW/m^2)")
plt.gca().yaxis.set_label_coords(1.06, 0.5)
plt.xlabel("Time (min)")
plt.xlim([0, max(t)])
plt.title("SFR3 DNI & Coil Temps")
plt.legend(["TC1", "TC2", "TC3", "TC4", "TC5", "TC6", "DNI"], loc="best")
plt.show()

# plot of power DNI over time
plt.figure()
plt.plot(t, Wcoil)
plt.ylabel("Power Output (W)")
plt.twinx()
plt.grid(True)
plt.plot(t, DNI)
plt.xlim([0, max(t)])
plt.xlabel("Time (min)")
plt.ylabel("Irradiance (W/m^2)")
plt.legend(["Coil Output", "DNI"], loc="best")
plt.title("SFR3 DNI & Thermal Output")
plt.show()

# plot of power in power out over time
plt.figure()
plt.plot(t, Wcoil, linewidth=2)
plt.plot(t, Wincident, linewidth=2)
plt.xlim([0, max(t)])
plt.ylim([0, 1000])
plt.ylabel("Power (W)")
plt.twinx()
plt.grid(True)
plt.plot(t, efficiency, linewidth=2)
plt.ylim([0, 100])
plt.ylabel("Efficiency (%)")
plt.xlabel("Time (min)")
plt.legend(["Coil Output", "Sun Input", "Efficiency"], loc="best")
plt.title("SFR3 Thermal Efficiency")
plt.show()

# plot of eff. over time
plt.figure()
plt.plot(t, Wcoil)
plt.ylabel("Coil Output (Watts)")
plt.xlabel("Min")
plt.xlim([0, max(t)])
plt.show()

# plot of coil output and flow rate
plt.figure()
plt.plot(t, Wcoil, linewidth=2)
plt.xlim([0, max(t)])
plt.ylabel("Power (W)")
plt.twinx()
plt.grid(True)
plt.plot(t, massFlowRate, linewidth=2)
plt.ylabel("Flow Rate (gps)")
plt.xlabel("Time (min)")
plt.legend(["Coil Output", "Mass Flow Rate"], loc="best")
plt.title("SFR3 Coil Output and Flow Rate")
plt.show()

# plot of temps and flow rate over time
plt.figure()
plt.plot(t, G, color='#7E2F8E', linewidth=1.5)
plt.plot(t, H, color='#0051ff', linewidth=1.5)
plt.plot(t, I, color='#00ff04', linewidth=1.5)
plt.plot(t, J, color='#e3ff00', linewidth=1.5)
plt.plot(t, K, color='#ff8d00', linewidth=1.5)
plt.plot(t, L, color='#ff1a00', linewidth=1.5)
plt.ylim([25, 50])
plt.ylabel("Temperature (C)")
plt.gca().yaxis.set_label_coords(-0.06, 0.5)

plt.twinx()
plt.grid(True)
plt.plot(t, massFlowRate, color='black', linestyle="-", linewidth=2)
plt.ylabel("Mass Flow Rate (gps)")
plt.gca().yaxis.set_label_coords(1.06, 0.5)
plt.xlabel("Time (min)")
plt.xlim([0, max(t)])
plt

file_object.close()