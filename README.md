# thermode-control
## Functions to control QST.Lab thermodes (TCS) via serial connection

The thermodes by QST.Lab (see [their page](https://www.qst-lab.eu/tcs-technical-description)) have 5 stimulation zones that can be set to different temperatures. We used Python to control the thermode via a serial connection and read out the recorded temperatures of each zone. I implemented the normal stimulation mode (setting all parameters to a specific constant, then starting the stimulation) as well as the point to point mode (allows for more advanced stimulation protocols like ramps).
The functionality of the thermode encompasses a bit more, for example we never used the patient button, but following the code it should be straightforward to implement.

#### Minimal example:

```
import TcsControl_python3 as TCS

baselineTemp    = 31.0                  # baseline/neutral temperature (for all 5 zones equally)
durations       = [5.0] * 5             # stimulation durations in s for the 5 zones
ramp_speed      = [75, 75, 75, 75, 75]  # ramp up speed in °C/s for the 5 zones
return_speed    = [100.0] * 5           # ramp down speed in °C/s for the 5 zones
temperatures    = [46.0, 46.5, 47.0, 47.5, 48.0]  # target temperatures in °C for the 5 zones

thermode = TCS.TcsDevice(port='/dev/ttyACM0')
thermode.set_quiet()
thermode.set_baseline(baselineTemp)
thermode.set_durations(durations)
thermode.set_ramp_speed(ramp_speed)
thermode.set_return_speed(return_speed)
thermode.set_temperatures(temperatures)

thermode.stimulate()
thermode.close()

```

A more advanced example with temperature recording is given in the file Tcs_example.py

If you have suggestions for improvement, hit me a message!
