#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=== Authors ===
Dr. Ulrike Horn: uhorn@cbs.mpg.de
Max Planck Institute for Human Cognitive and Neuroscience
Research group Pain Perception
Date: 8th of May 2026
"""

import serial
import numpy as np
import warnings

class TcsDevice:
    # Constants for parameter ranges
    BASELINE_MIN = 20.0
    BASELINE_MAX = 40.0
    TEMPERATURE_MIN = 0.1
    TEMPERATURE_MAX = 60.0
    DURATION_MIN = 0.001
    DURATION_MAX = 99.999
    SPEED_MIN = 0.1
    SPEED_MAX = 300.0

    def __init__(self, port='/dev/ttyACM0'):
        # Open serial port
        self.s_port = serial.Serial(port, 115200, timeout = 2)
        self.s_port.flushInput();
        self.s_port.write(bytes(b'H'))
        self.s_port.flushOutput()
        firmware_msg = self.s_port.read(30)
        print(firmware_msg)
        self.s_port.flushInput()
        id_msg = self.s_port.read(30)
        print(id_msg)
        self.s_port.flushInput()
        # read the rest
        rest = self.s_port.read(10000)
        self.s_port.flushInput()
        #print(rest)
        
        self.s_port.write(bytes(b'B'))
        self.s_port.flushOutput()
        battery = self.s_port.read(14)
        print(battery)

    def _validate_numeric_value(self, value, min_val, max_val, name):
        """Helper to validate a single numeric value within range."""
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a numeric value.")
        if value < min_val or value > max_val:
            raise ValueError(f"{name} must be between {min_val} and {max_val}.")

    def _validate_numeric_list(self, values, min_val, max_val, name):
        """Helper to validate a list of 5 numeric values within range."""
        if not isinstance(values, (list, tuple)) or len(values) != 5:
            raise ValueError(f"{name} must be an array of exactly 5 elements.")
        for val in values:
            if not isinstance(val, (int, float)):
                raise ValueError(f"All {name} must be numeric values.")
            if val < min_val or val > max_val:
                raise ValueError(f"All {name} must be between {min_val} and {max_val}.")

    def set_quiet(self):
        """
        sets thermode to quiet mode
        otherwise TCS sends regularly temperature data
        (@1Hz if no stimulation, @100Hz during stimulation)
        and that can corrupt dialog between PC and TCS
        """
        self.s_port.write(bytes(b'F'))
        self.s_port.flushOutput()
    
    
    def set_filter(self, level):
        """
        sets MR filter setting
        :param level: string 'high', 'medium' or 'low' to set filter strength
        """
        if level=='high':
            command = b'Of3'
        elif level=='medium':
            command = b'Of2'
        elif level=='low':
            command = b'Of1'
        else:
            print('Enter a valid filter strength (high, medium, low)')
            return
        self.s_port.write(bytes(command))
        self.s_port.flushOutput()
    
    def set_baseline(self, baselineTemp):
        """
        sets baseline temperature in °C (also called neutral temperature)
        :param baselineTemp: 1 float value (min 20°C, max 40°C)
        """
        self._validate_numeric_value(baselineTemp, self.BASELINE_MIN, self.BASELINE_MAX, "Baseline temperature")
        command = b'N%03d' % (baselineTemp*10)
        self.s_port.write(bytes(command))
        self.s_port.flushOutput()
    
    
    def set_durations(self, stimDurations):
        """
        sets stimulus durations in s for all 5 zones
        :param stimDurations: array of 5 values (min 0.001s, max 99.999s)
        """
        self._validate_numeric_list(stimDurations, self.DURATION_MIN, self.DURATION_MAX, "stimulus durations")
        # check if speeds are equal
        if stimDurations.count(stimDurations[0]) == len(stimDurations):
            # yes: send all speeds in one command
            command = b'D0%05d' % (stimDurations[1]*1000)
            self.s_port.write(bytes(command))
            self.s_port.flushOutput()
        else:       
            # no: send speeds in separate commands
            for i in range(5):
                command = b'D%d%05d' % ((i+1) , (stimDurations[i]*1000))
                self.s_port.write(bytes(command))
                self.s_port.flushOutput()
    
    
    def set_ramp_speed(self, rampSpeeds):
        """
        sets ramp up speeds in °C/s for all 5 zones
        :param rampSpeeds: array of 5 values (min 0.1°C/s, max 300°C/s)
        """
        self._validate_numeric_list(rampSpeeds, self.SPEED_MIN, self.SPEED_MAX, "ramp speeds")
        
        # check if speeds are equal
        if rampSpeeds.count(rampSpeeds[0]) == len(rampSpeeds):
            # yes: send all speeds in one command
            command = b'V0%04d' % (rampSpeeds[1]*10)
            self.s_port.write(bytes(command))
            self.s_port.flushOutput()
        else:        
            # no: send speeds in separate commands
            for i in range(5):
                command = b'V%d%04d' % ((i+1), (rampSpeeds[i]*10))
                self.s_port.write(bytes(command))
                self.s_port.flushOutput()
    
    def set_return_speed(self, returnSpeeds):
        """
        sets ramp down/ return speeds in °C/s for all 5 zones
        :param returnSpeeds: array of 5 values (min 0.1°C/s, max 300°C/s)
        """
        self._validate_numeric_list(returnSpeeds, self.SPEED_MIN, self.SPEED_MAX, "return speeds")
        
        # check if speeds are equal
        if returnSpeeds.count(returnSpeeds[0]) == len(returnSpeeds):
            # yes: send all speeds in one command
            command = b'R0%04d' % (returnSpeeds[1]*10)
            self.s_port.write(bytes(command))
            self.s_port.flushOutput()
        else:        
            # no: send speeds in separate commands
            for i in range(5):
                command = b'R%d%04d' % ((i+1), (returnSpeeds[i]*10))
                self.s_port.write(bytes(command))
                self.s_port.flushOutput()
    
    
    def set_temperatures(self, temperatures):
        """
        sets target temperatures in °C for all 5 zones
        :param temperatures: array of 5 values (min 0.1°C, max 60°C)
        """
        self._validate_numeric_list(temperatures, self.TEMPERATURE_MIN, self.TEMPERATURE_MAX, "temperatures")
        
        # check if temperatures are equal
        if temperatures.count(temperatures[0]) == len(temperatures):
            # yes: send all speeds in one command
            command = b'C0%03d' % (temperatures[1]*10)
            self.s_port.write(bytes(command))
            self.s_port.flushOutput()
        else:        
            # no: send speeds in separate commands
            for i in range(5):
                command = b'C%d%03d' % ((i+1), (temperatures[i]*10))
                self.s_port.write(bytes(command))
                self.s_port.flushOutput()
    
    
    def stimulate(self):
        """
        starts the stimulation protocol with the parameters that have been set
        """
        self.s_port.write(bytes(b'L'))
    

    def stop(self):
        """
        stops the stimulation protocol
        """
        self.s_port.write(bytes(b'A'))
        self.s_port.flushOutput()
    

    def get_temperatures(self):
        """
        get current temperatures of zone 1 to 5 in °C
        :return: returns an array of five temperatures or empty array if 
            there is an error
        """
        self.s_port.flushInput()
        self.s_port.write(bytes(b'E'))
        self.s_port.flushOutput()
        # this is the format of the data sent by TCS when reading temperatures:
        # '/r' + 'xxx?xxx?xxx?xxx?xxx?xxx' with '?' = sign '+' ou '-'
        # neutral + t1 to t5
        datatemps = self.s_port.read(24)
        temperatures = []
        if len(datatemps) >= 24:
            for i in range(5):
                start = 5 + i * 4  # Positions: 5-7, 9-11, 13-15, 17-19, 21-23
                try:
                    temp = float(datatemps[start:start+3].decode(errors='ignore')) / 10
                except (ValueError, UnicodeDecodeError):
                    print(f"Temperature data cannot be decoded for zone {i+1}. Received data: {datatemps[start:start+3]}")
                    temp = -1.0
                temperatures.append(temp)
        else:
            warnings.warn("Received temperature data is incomplete or corrupted.")
            temperatures = [-1.0] * 5

        return temperatures, datatemps
    
    
    def enable_point_to_point(self, enabled_zones):
        """
        enable/disable point to point stimulation for each zone
        :param enabled_zones:   array of 5 integers to choose zones 
                                to be enabled (1) or disabled (0)
        """
        if not isinstance(enabled_zones, (list, tuple)) or len(enabled_zones) != 5:
            raise ValueError("enabled_zones must be an array of exactly 5 elements.")
        for zone in enabled_zones:
            if not isinstance(zone, int) or zone not in (0, 1):
                raise ValueError("Each element in enabled_zones must be 0 or 1.")
        zonestr = ''.join(str(e) for e in enabled_zones)
        command = b'Ue'+zonestr.encode('UTF-8')
        self.s_port.write(bytes(command))
        self.s_port.flushOutput()
    
    
    def set_point_to_point(self, zones, timevec, temperature):
        """
        set point to point stimulation curve
        :param zones: array of 5 integers (0 or 1) to choose zones to be set
        :param timevec: array of time in seconds (column vector with length n,
                                               first point 0)
        :param temperature: array of temperature in °C (column vector with 
                                                        same length n, 
                                                        first point neutral temp)
        """
        # Validate zones
        if not isinstance(zones, (list, tuple)) or len(zones) != 5:
            raise ValueError("zones must be an array of exactly 5 elements.")
        for zone in zones:
            if zone not in (0, 1):
                raise ValueError("Each element in zones must be 0 or 1.")
        
        # Convert to numpy arrays and validate
        try:
            timevec = np.array(timevec, dtype=float)
            temperature = np.array(temperature, dtype=float)
        except (ValueError, TypeError):
            raise ValueError("timevec and temperature must contain numeric values.")
        
        # Check shapes and dimensions
        if np.shape(timevec) != np.shape(temperature):
            raise ValueError("timevec and temperature arrays must have the same length.")
        if (np.ndim(timevec) != 1) or (np.ndim(temperature) != 1):
            raise ValueError("timevec and temperature must be 1-dimensional arrays.")
        if len(timevec) > 999:
            raise ValueError("Length of timevec and temperature arrays must be less than 1000.")
        if len(timevec) < 2:
            raise ValueError("timevec and temperature must have at least 2 points.")
        if timevec[0] != 0:
            raise ValueError("The first time point must be 0.")
        if not np.all(np.diff(timevec) > 0):
            raise ValueError("Time values must be strictly increasing.")
        
        # Check temperature range
        if np.any(temperature < 0.1) or np.any(temperature > 60):
            raise ValueError("Temperature values must be between 0.1°C and 60°C.")
        
        # round time to 10 ms
        timevec = np.round(timevec*100)/100
        
        # compute time intervals between points
        deg = np.array(temperature[1:])
        delta = timevec[1:] - timevec[0:-1] # time intervals in s
        
        # intervals must be less or equal to 9.99s (9990 ms)
        # so this loop generates intermediate points if necessary
        sup9990ms = True
        while sup9990ms:
            sup9990ms = False
            for i in range(len(delta)):
                if delta[i] > 9.99:
                    sup9990ms = True
                    if i==0:
                        # add point at beginning
                        delta = np.concatenate(([delta[0]/2.0], [delta[0]/2.0], delta[1:]))
                        deg = np.insert(deg, 0, (temperature[0] + deg[0])/2.0)
                    elif i==(len(delta)-1):
                        # add point at the end
                        delta = np.concatenate((delta[0:i], [delta[i]/2.0, delta[i]/2.0]))
                        deg = np.concatenate((deg[0:i], [(deg[i-1]+deg[i])/2.0], [deg[i]]))
                    else:
                        # add intermediate point
                        delta = np.concatenate((delta[0:i], [delta[i]/2.0, delta[i]/2.0], delta[i+1:]))
                        deg = np.concatenate((deg[0:i], [(deg[i-1]+deg[i])/2.0], deg[i:]))
                    break
        
        # send array of points to thermode
        combined_str = ''.join(str(e) for e in zones) + '%03d' % (len(delta))
        command = b'Uw' + combined_str.encode('UTF-8')
        self.s_port.write(bytes(command))
        self.s_port.flushOutput()
        
        for i in range(len(delta)):
            command = b'%03d%03d' % ((round(delta[i]*100)), (round(deg[i]*10)))
            self.s_port.write(bytes(command))
            self.s_port.flushOutput()
    
    
    def enable_zones(self, enabled_zones):
        """
        enable/disable each zone
        :param enabled_zones:   array of 5 integers to choose zones 
                                to be enabled (1) or disabled (0)
        """
        zonestr = ''.join(str(e) for e in enabled_zones)
        command = b'S'+zonestr.encode('UTF-8')
        self.s_port.write(bytes(command))
        self.s_port.flushOutput()
    

    def close(self):
        """ 
        closes the serial port connection to the TCS device
        """
        self.s_port.close()
    