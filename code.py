import time
from array import *
import board

import touchio
import pulseio
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull

import usb_midi
import adafruit_midi
from adafruit_midi.midi_message     import note_parser
from adafruit_midi.note_on          import NoteOn
from adafruit_midi.note_off         import NoteOff
from adafruit_midi.control_change   import ControlChange
from adafruit_midi.pitch_bend       import PitchBend

#DefineTouch Thresholds

buttonLedDelay = 0.2


#####INPUTS

#init touch buttons
pads = [board.A0,board.A1,board.A2,board.A3,board.A4,board.A5]
touchpads = [touchio.TouchIn(pad) for pad in pads]
touchThresholds = [3000,3000,3000,3000,3000,3600]
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
ledR = pulseio.PWMOut(board.D14, frequency=5000, duty_cycle=0)
ledG = pulseio.PWMOut(board.D15, frequency=5000, duty_cycle=0)
ledB = pulseio.PWMOut(board.D16, frequency=5000, duty_cycle=0)


time.sleep(1)

#### MIDI

midi_channel = 1
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=midi_channel-1)
midi_in = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], in_channel=midi_channel-1)


velocity = 127

midiNotes = [[1,2,3,4,5,6],#TouchBtns
             [7,8,9,10],#TactileBtns
             [11,12,13,14],#Fader
             [15,16,17,18],#FaderReset
             [19,20,21]]#LogoRGB Feedback

#midiNotes = [[y-128 for y in x] for x in midiNotes]
print(midiNotes)

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

    msg = midi_in.receive()
    if isinstance(msg, NoteOn) or isinstance(msg, NoteOff):
        print(str(msg.note)+" "+str(msg.velocity))

        index = index_2d(midiNotes,msg.note)
        print(index)

        if(index[0]==0):#touch
            touchLeds[index[1]].value = not int(msg.velocity/127)
        elif(index[0]==1):#Btn
            btnLeds[index[1]].value = not int(msg.velocity/127)
        #elif(index[0]==2):#Fader
        elif(index[0]==4):#Logo
            if index[1]==0:
                ledR.duty_cycle = int((msg.velocity) * 65535 / 127)
            elif index[1]==1:
                ledG.duty_cycle = int((msg.velocity) * 65535 / 127)
            elif index[1]==2:
                ledB.duty_cycle = int((msg.velocity) * 65535 / 127)



    for idx, touchpad in enumerate(touchpads):
        if touchpad.value != keydownTouch[idx]:
            keydownTouch[idx] = touchpad.value
            if keydownTouch[idx]:
                midi.send(NoteOn(midiNotes[0][idx], velocity))
            else:
                midi.send(NoteOn(midiNotes[0][idx], 0))  # Using note on 0 for off

    for idx, btn in enumerate(btns):
        if btn.value != keydownBtn[idx]:
            keydownBtn[idx] = btn.value
            if not keydownBtn[idx]:
                midi.send(NoteOn(midiNotes[1][idx], velocity))
            else:
                midi.send(NoteOn(midiNotes[1][idx], 0))  # Using note on 0 for off
    
    for idx, fader in enumerate(faders):
        faderVal = int(fader.value/512)
        if faderVal != FaderLast[idx] and abs(FaderLastRaw[idx]-fader.value)>255:
            FaderLast[idx] = faderVal
            FaderLastRaw[idx] = fader.value
            if faderVal>1:
                midi.send(NoteOn(midiNotes[2][idx], faderVal))
                if not FaderOverride:
                    FaderOverride[idx] = False
                    midi.send(NoteOn(midiNotes[3][idx], 0)) #set Fader override                

            else:
                FaderOverride[idx] = False
                midi.send(NoteOn(midiNotes[2][idx], 0))
                midi.send(NoteOn(midiNotes[3][idx], velocity)) #reset Fader override


    #Read Faders


    if faderLogo:
        ledR.duty_cycle = clamp(faders[0].value-64,0,65535)
        ledG.duty_cycle = clamp(faders[1].value-64,0,65535)
        ledB.duty_cycle = clamp(faders[2].value-64,0,65535)
