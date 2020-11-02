import time
import board

import touchio
import pulseio
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull

import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

import usb_midi
#import adafruit_lis3dh
import adafruit_midi
from adafruit_midi.note_on          import NoteOn
from adafruit_midi.control_change   import ControlChange
from adafruit_midi.pitch_bend       import PitchBend

#DefineTouch Thresholds
touchThresholds = [3000,3000,3000,3000,3000,3600]

buttonLedDelay = 0.2


#####INPUTS

#init touch buttons
pads = [board.A0,board.A1,board.A2,board.A3,board.A4,board.A5]
touchpads = [touchio.TouchIn(pad) for pad in pads]
del pads

#init Fader
faderPins = [board.A6,board.A7,board.A8,board.A9]
faders = [AnalogIn(faderPin) for faderPin in faderPins]
del faderPins


def initIO(pin,dir):
    io = DigitalInOut(pin)
    io.direction = dir
    return io

#init Buttons
btnPins =  [board.D6,board.D7,board.D8,board.D9]
btns = [initIO(btnPin,Direction.INPUT) for btnPin in btnPins]
del btnPins

#####LEDS
#init led lines
touchLedPins = [board.D0,board.D1,board.D2,board.D3,board.D4,board.D5]
touchLeds = [initIO(touchLedPin,Direction.OUTPUT) for touchLedPin in touchLedPins]
del touchLedPins

#init Btn Leds
btnLedPins = [board.D10,board.D11,board.D12,board.D13]
btnLeds = [initIO(btnLedPin,Direction.OUTPUT) for btnLedPin in btnLedPins]
del btnLedPins

del initIO

#init Logo Leds
ledR = pulseio.PWMOut(board.D14, frequency=5000, duty_cycle=0)
ledG = pulseio.PWMOut(board.D15, frequency=5000, duty_cycle=0)
ledB = pulseio.PWMOut(board.D16, frequency=5000, duty_cycle=0)


#uncomment these if keyboard library is installed. See top comment
time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems
cc = ConsumerControl(usb_hid.devices)

for btnLed in btnLeds: btnLed.value = True

def LogoColor(r,g,b):
    #print(str(r)+","+str(g)+","+str(b))
    global faderLogo
    faderLogo = False
    
    ledR.duty_cycle = int((r) * 65535 / 255)
    ledG.duty_cycle = int((g) * 65535 / 255)
    ledB.duty_cycle = int((b) * 65535 / 255)

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

#def getLogoColor()

LogoColor(0,0,0)
time.sleep(0.3)
LogoColor(255,0,0)
time.sleep(0.3)
LogoColor(0,255,0)
time.sleep(0.3)
LogoColor(0,0,255)
time.sleep(0.3)


print("starting...")
#important: LED is active when False!
#important: capacitive values might need adjustment depending on your procedural design

faderLogo = False

while True:
    if touchpads[0].raw_value > touchThresholds[0]:
        #print("1: "+str(touch1.raw_value))
        #cc.send(ConsumerControlCode.VOLUME_INCREMENT) #uncomment if keyboard library is installed
        touchLeds[0].value = False
        LogoColor(0,0,0)
        time.sleep(buttonLedDelay)

    else:
        touchLeds[0].value = True

    if touchpads[1].raw_value > touchThresholds[1]:
        #print("2: "+str(touch2.raw_value))
        #cc.send(ConsumerControlCode.VOLUME_DECREMENT)  #uncomment if keyboard library is installed
        touchLeds[1].value = False
        LogoColor(255,0,0)
        time.sleep(buttonLedDelay)

    else:
        touchLeds[1].value = True

    if touchpads[2].raw_value > touchThresholds[2]:
        #print("3: "+str(touch3.raw_value))
        #cc.send(ConsumerControlCode.MUTE)  #uncomment if keyboard library is installed
        touchLeds[2].value = False
        LogoColor(0,255,0)
        time.sleep(buttonLedDelay)

    else:
        touchLeds[2].value = True
        
    if touchpads[3].raw_value > touchThresholds[3]:
        #print("4: "+str(touch4.raw_value))
        #cc.send(ConsumerControlCode.MUTE)  #uncomment if keyboard library is installed
        touchLeds[3].value = False
        LogoColor(0,0,255)
        time.sleep(buttonLedDelay)
    else:
        touchLeds[3].value = True

    if touchpads[4].raw_value > touchThresholds[4]:
        #print("5: "+str(touch5.raw_value))
        #cc.send(ConsumerControlCode.MUTE)  #uncomment if keyboard library is installed
        touchLeds[4].value = False
        LogoColor(255,255,255)
        time.sleep(buttonLedDelay)
    else:
        touchLeds[4].value = True

    if touchpads[5].raw_value > touchThresholds[5]:
        #print("6: "+str(touch6.raw_value))
        #cc.send(ConsumerControlCode.MUTE)  #uncomment if keyboard library is installed
        touchLeds[5].value = False
        faderLogo = True
        time.sleep(buttonLedDelay)
    else:
        touchLeds[5].value = True

    #Read Faders


    if faderLogo:
        ledR.duty_cycle = clamp(faders[0].value-64,0,65535)
        ledG.duty_cycle = clamp(faders[1].value-64,0,65535)
        ledB.duty_cycle = clamp(faders[2].value-64,0,65535)


    #Read Buttons

    if not btns[0].value:
        btnLeds[0].value = False
        time.sleep(buttonLedDelay)
    else:
        btnLeds[0].value = True

    if not btns[1].value:
        btnLeds[1].value = False
        time.sleep(buttonLedDelay)
    else:
        btnLeds[1].value = True

    if not btns[2].value:
        btnLeds[2].value = False
        time.sleep(buttonLedDelay)
    else:
        btnLeds[2].value = True

    if not btns[3].value:
        btnLeds[3].value = False
        time.sleep(buttonLedDelay)
    else:
        btnLeds[3].value = True
