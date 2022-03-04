import time
from array import *
import board

import touchio
import pwmio
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull

import usb_midi
import adafruit_midi
from adafruit_midi.control_change   import ControlChange

#####INPUTS

#init touch buttons
pads = [board.A0,board.A1,board.A2,board.A3,board.A4,board.A5]
touchpads = [touchio.TouchIn(pad) for pad in pads]
touchThresholds = [3500,3500,3500,3500,3500,4000]
for idx, touchpad in enumerate(touchpads): touchpad.threshold = touchThresholds[idx]
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
for touchLed in touchLeds: touchLed.value = True # Turn Off
del touchLedPins

#init Btn Leds
btnLedPins = [board.D10,board.D11,board.D12,board.D13]
btnLeds = [initIO(btnLedPin,Direction.OUTPUT) for btnLedPin in btnLedPins]
for btnLed in btnLeds: btnLed.value = True # Turn Off
del btnLedPins

del initIO

#init Logo Leds
ledR = pwmio.PWMOut(board.D14, frequency=5000, duty_cycle=0)
ledG = pwmio.PWMOut(board.D15, frequency=5000, duty_cycle=0)
ledB = pwmio.PWMOut(board.D16, frequency=5000, duty_cycle=0)


time.sleep(1)

#### MIDI

midi_channel = 1
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=midi_channel-1)
midi_in = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], in_channel=midi_channel-1)


maxVal = 127

midiControls = [[0,1,2,3,4,5],#TouchBtns
             [6,7,8,9],#TactileBtns
             [10,11,12,13],#Fader
             [14,15,16,17],#FaderReset
             [18,19,20]]#LogoRGB Feedback

midi_channel_offset = 0

for i, m in enumerate(midiControls):
    for j, x in enumerate(m):
        midiControls[i][j] = x + midi_channel_offset

print(midiControls)

keydownTouch = [False] * len(touchpads)
keydownBtn = [False] * len(btns)
FaderLast = [0]*len(faders)
FaderLastRaw = [0]*len(faders)
FaderOverride = [0]*len(faders)

def LogoColor(r,g,b):
    #print(str(r)+","+str(g)+","+str(b))
    global faderLogo
    faderLogo = False
    
    ledR.duty_cycle = int((r) * 65535 / 255)
    ledG.duty_cycle = int((g) * 65535 / 255)
    ledB.duty_cycle = int((b) * 65535 / 255)

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def index_2d(myList, v):
    for i, x in enumerate(myList):
        if v in x:
            return [i, x.index(v)]


#def getLogoColor()

LogoColor(0,0,0)
time.sleep(0.2)
LogoColor(255,0,0)
time.sleep(0.2)
LogoColor(0,0,0)


print("starting...")

while True:

    msg = midi_in.receive()
    if isinstance(msg, ControlChange) and midi_channel_offset <=msg.control <= midi_channel_offset+20:
        print(str(msg.control)+" "+str(msg.value))

        index = index_2d(midiControls,msg.control)
        #print(index)

        if(index[0]==0):#touch
            touchLeds[index[1]].value = not int(msg.value/maxVal)
        elif(index[0]==1):#Btn
            btnLeds[index[1]].value = not int(msg.value/maxVal)
        #elif(index[0]==2):#Fader
        elif(index[0]==4):#Logo
            if index[1]==0:
                ledR.duty_cycle = int((msg.value) * 65535 / maxVal)
            elif index[1]==1:
                ledG.duty_cycle = int((msg.value) * 65535 / maxVal)
            elif index[1]==2:
                ledB.duty_cycle = int((msg.value) * 65535 / maxVal)



    for idx, touchpad in enumerate(touchpads):
        if touchpad.value != keydownTouch[idx]:
            keydownTouch[idx] = touchpad.value
            if keydownTouch[idx]:
                #print(touchpad.raw_value)
                midi.send(ControlChange(midiControls[0][idx], maxVal))
            else:
                midi.send(ControlChange(midiControls[0][idx], 0))

    for idx, btn in enumerate(btns):
        if btn.value != keydownBtn[idx]:
            keydownBtn[idx] = btn.value
            if not keydownBtn[idx]:
                midi.send(ControlChange(midiControls[1][idx], maxVal))
            else:
                midi.send(ControlChange(midiControls[1][idx], 0))
    
    for idx, fader in enumerate(faders):
        faderVal = int(fader.value/512)
        if faderVal != FaderLast[idx] and abs(FaderLastRaw[idx]-fader.value)>255:
            FaderLast[idx] = faderVal
            FaderLastRaw[idx] = fader.value
            midi.send(ControlChange(midiControls[2][idx], faderVal))
