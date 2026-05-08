#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
=== Authors ===
Dr. Ulrike Horn: uhorn@cbs.mpg.de
Max Planck Institute for Human Cognitive and Neuroscience
Research group Pain Perception
Date: 8th of May 2026
"""

import pandas as pd
import time
import matplotlib.pyplot as plt
plt.interactive(True)
import TcsControl_python3 as TCS

# settings
baselineTemp    = 31.0                  # baseline/neutral temperature (for all 5 zones equally)
durations       = [5.0] * 5             # stimulation durations in s for the 5 zones
ramp_speed      = [75, 75, 75, 75, 75]  # ramp up speed in °C/s for the 5 zones
return_speed    = [100.0] * 5           # ramp down speed in °C/s for the 5 zones
temperatures    = [46.0, 46.5, 47.0, 47.5, 48.0]  # target temperatures in °C for the 5 zones

# create thermode object
thermode = TCS.TcsDevice(port='/dev/ttyACM0')

# Quiet mode
thermode.set_quiet()

# send all settings for the stimuli
thermode.set_baseline(baselineTemp)
thermode.set_durations(durations)
thermode.set_ramp_speed(ramp_speed)
thermode.set_return_speed(return_speed)
thermode.set_temperatures(temperatures)

# start stimulation
thermode.stimulate()    

# record stimulation temperatures
recordDuration = max(durations)+1.0;
recordDuration = 3.0;
cpt = 0
start_time = time.time()
column_names = ["temp_1", "temp_2", "temp_3", "temp_4", "temp_5"]
df = pd.DataFrame(columns = column_names)
while True:
    current_temperatures = thermode.get_temperatures()
    data = pd.DataFrame([current_temperatures], columns=column_names)
    df = df.append(data)
    current_time = time.time()
    cpt = cpt + 1;
    elapsed_time = current_time - start_time
    if elapsed_time > recordDuration:
        print("Finished iterating in: " + str(int(elapsed_time))  + " seconds")
        break

# plot it
plt.xlabel('time in samples')
plt.ylabel('temperature')
plt.plot(range(len(df)), df['temp_1'])
plt.plot(range(len(df)), df['temp_2'])
plt.plot(range(len(df)), df['temp_3'])
plt.plot(range(len(df)), df['temp_4'])
plt.plot(range(len(df)), df['temp_5'])
plt.show()

# close connection
thermode.close()
