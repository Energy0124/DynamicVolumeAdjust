# dependency
# For Windows
# ----
# pip install https://github.com/AndreMiras/pycaw/archive/develop.zip
# ----
# For Mac
# ----
# sudo easy_install appscript
#
# ----
# Common
# ----
# pip install numpy
# pip install sounddevice
# ----
import os
import platform
import sounddevice as sd
import numpy as np
import time as timer
import sys
import re
from subprocess import Popen, PIPE, STDOUT, call

from sys import platform as _platform


def log(msg):
    if verbose:
        print msg


def get_speaker_output_volume():
    if _platform == "linux" or _platform == "linux2":
        pass
    elif _platform == "darwin":
        cmd = "osascript -e 'get volume settings'"
        proc = Popen(cmd, shell=True, stdout=PIPE, )
        output = proc.communicate()[0]
        pattern = re.compile(r"output volume:(\d+), input volume:(\d+), "
                             r"alert volume:(\d+), output muted:(true|false)")
        output, _, _, muted = pattern.match(output).groups()

        volume = int(output)
        muted = (muted == 'true')
        return 0 if muted else volume
    elif _platform == "win32" or _platform == "win64":
        return 0


if _platform == "linux" or _platform == "linux2":
    # linux
    pass
elif _platform == "darwin":
    from osax import *
    sa = OSAX()
elif _platform == "win32" or _platform == "win64":
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

# config
verbose = False
duration = 10*3600  # run duration in seconds
th = 2.666  # threshold
interval = 0.333  # update interval and also the fate in/out time
cd = 2


if _platform == "linux" or _platform == "linux2":
    # linux
    pass
elif _platform == "darwin":
    minVolume = 0.5
    maxVolume = get_speaker_output_volume() / 10
elif _platform == "win32" or _platform == "win64":
    minVolume = -35.0  # update minVolume
    maxVolume = -20.0  # update minVolume


t1 = timer.time()
t2 = timer.time()
dt = t2 - t1
deltaFade = 0
fState = 0
pState = fState
avgVolume = 0
frameCount = 0
cdTimer = 0


def print_sound(indata, outdata, frames, time, status):
    global t1, t2, dt, fState, pState, frameCount, avgVolume, cdTimer
    global th, interval, minVolume, maxVolume, cd

    volume_norm = np.linalg.norm(indata)*10
    log("|" * int(volume_norm))
    log("avgVolume: " + str(avgVolume))
    log("cdTimer: " + str(cdTimer))

    ct = timer.time()
    t2 = ct
    dft = t2 - t1
    dt += t2 - t1
    log("dt: " + str(dt))

    t1 = t2

    if avgVolume > th and dt > interval and cdTimer <= 0:
        pState = fState
        fState = -1
        dt = 0
        frameCount = 1
        avgVolume = volume_norm
        cdTimer = cd
    elif avgVolume <= th and dt > interval and cdTimer <= 0:
        pState = fState
        fState = 1
        dt = 0
        frameCount = 1
        avgVolume = volume_norm
        cdTimer = cd
    elif dt > interval and cdTimer > 0:
        pState = fState
        dt = 0
        frameCount = 1
        avgVolume = volume_norm
    else:
        avgVolume = (avgVolume * frameCount + volume_norm) / (frameCount + 1)
        frameCount += 1
        normalizedDeltaVolume = dt/interval * (maxVolume - minVolume)
        log("normalizedDeltaVolume: " + str(normalizedDeltaVolume))
        if cdTimer > 0:
            cdTimer -= dft
        if _platform == "linux" or _platform == "linux2":
            # linux
            pass
        elif _platform == "darwin":
            if fState < 0 and pState != fState:
                sa.set_volume(maxVolume - normalizedDeltaVolume)
            if fState > 0 and pState != fState:
                sa.set_volume(minVolume + normalizedDeltaVolume)
        elif _platform == "win32" or _platform == "win64":
            if fState < 0 and pState != fState:
                log("current volume: "+str(maxVolume - normalizedDeltaVolume))
                volume.SetMasterVolumeLevel(
                    maxVolume - normalizedDeltaVolume, None)
            if fState > 0 and pState != fState:
                log("current volume: "+str(minVolume + normalizedDeltaVolume))
                volume.SetMasterVolumeLevel(
                    minVolume + normalizedDeltaVolume, None)


if not verbose:
    print("Verbose mode is turned off. No log will be printed.")

with sd.Stream(callback=print_sound):
    sd.sleep(duration * 1000)
