# DynamicVolumeAdjust
Dynamically lower the volume of the music you are listening/master sound of your computer whenever someone is talking next to you

## How it works
It is actually a very simple script. It uses the system mic to detect sound around your pc over a short interval of time.
If the average volume during that interval exceed the defined threshold, the system volume will be lowered to the defined min volume in this interval of time linearly. It will continue to check the average volume, and if the detected volume during a interval reduced to below the threshold, the system volume will be increased back to normal level gradually.

## Dependencies
### For Windows

`pip install https://github.com/AndreMiras/pycaw/archive/develop.zip`

### For Mac

`sudo easy_install appscript`

### Common
`pip install numpy`

`pip install sounddevice `

## config
For now, please change the value of the following variables manually in the source code to customize it

```
duration = 10*3600  # run duration in seconds
th = 2.5        # volume threshold, if the volume is above this value, 
                # the system volume will be automatically lowered 
                # to allow you to hear the other's talking
                # this value is likely device dependent.
                # if your mic is very sentitive you may need to set it to 25 or more
                
interval = 0.666    # update interval and also the fate in/out time
                    # every interval of time, the average volume your mic detected during 
                    # this interval of time will be used to test against the threshold
                    # if the volume is greater than threshold, the system volume will be lowered linearly 
                    # for this interval of time to min volume
                    # then the average volume will be test again

if _platform == "linux" or _platform == "linux2":
    # linux
    pass
elif _platform == "darwin":
    minVolume = 0.5
    maxVolume = 3
elif _platform == "win32" or _platform == "win64":
    minVolume = -35.0   # min volume, when mic detected audio sign greater than threshold, 
                        # it will gradually lower the volume to min volume
    maxVolume = -20.0   # max volume, this is the desired system volume when no one is talking
```
