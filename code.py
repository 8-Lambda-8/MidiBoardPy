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
touchThreshold1 = 3000
touchThreshold2 = 3000
touchThreshold3 = 3000
touchThreshold4 = 3000
touchThreshold5 = 3000
touchThreshold6 = 3600

buttonLedDelay = 0.2


#####INPUTS

#init touch buttons
touch1 = touchio.TouchIn(board.A0)
touch2 = touchio.TouchIn(board.A1)
touch3 = touchio.TouchIn(board.A2)
touch4 = touchio.TouchIn(board.A3)
touch5 = touchio.TouchIn(board.A4)
touch6 = touchio.TouchIn(board.A5)

#init Fader
Fader1 = AnalogIn(board.A6)
Fader2 = AnalogIn(board.A7)
Fader3 = AnalogIn(board.A8)
Fader4 = AnalogIn(board.A9)


#init Buttons
Btn1 = DigitalInOut(board.D6)
Btn1.direction = Direction.INPUT
Btn2 = DigitalInOut(board.D7)
Btn2.direction = Direction.INPUT
Btn3 = DigitalInOut(board.D8)
Btn3.direction = Direction.INPUT
Btn4 = DigitalInOut(board.D9)
Btn4.direction = Direction.INPUT


#####LEDS
#init led lines
Led1 = DigitalInOut(board.D0)
Led1.direction = Direction.OUTPUT
Led2 = DigitalInOut(board.D1)
Led2.direction = Direction.OUTPUT
Led3 = DigitalInOut(board.D2)
Led3.direction = Direction.OUTPUT
Led4 = DigitalInOut(board.D3)
Led4.direction = Direction.OUTPUT
Led5 = DigitalInOut(board.D4)
Led5.direction = Direction.OUTPUT
Led6 = DigitalInOut(board.D5)
Led6.direction = Direction.OUTPUT

#init Btn Leds
LedBtn1 = DigitalInOut(board.D10)
LedBtn1.direction = Direction.OUTPUT
LedBtn2 = DigitalInOut(board.D11)
LedBtn2.direction = Direction.OUTPUT
LedBtn3 = DigitalInOut(board.D12)
LedBtn3.direction = Direction.OUTPUT
LedBtn4 = DigitalInOut(board.D13)
LedBtn4.direction = Direction.OUTPUT

#init Logo Leds
ledR = pulseio.PWMOut(board.D14, frequency=5000, duty_cycle=0)
ledG = pulseio.PWMOut(board.D15, frequency=5000, duty_cycle=0)
ledB = pulseio.PWMOut(board.D16, frequency=5000, duty_cycle=0)


#uncomment these if keyboard library is installed. See top comment
time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems
cc = ConsumerControl(usb_hid.devices)

LedBtn1.value = True #Turn off
LedBtn2.value = True
LedBtn3.value = True
LedBtn4.value = True

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

FaderLastVal1 = 0
FaderLastVal2 = 0
FaderLastVal3 = 0
FaderLastVal4 = 0

faderLogo = False

while True:
    if touch1.raw_value > touchThreshold1:
        #print("1: "+str(touch1.raw_value))
        #cc.send(ConsumerControlCode.VOLUME_INCREMENT) #uncomment if keyboard library is installed
        Led1.value = False
        LogoColor(0,0,0)
        time.sleep(buttonLedDelay)

    else:
        Led1.value = True

    if touch2.raw_value > touchThreshold2:
        #print("2: "+str(touch2.raw_value))
        #cc.send(ConsumerControlCode.VOLUME_DECREMENT)  #uncomment if keyboard library is installed
        Led2.value = False
        LogoColor(255,0,0)
        time.sleep(buttonLedDelay)

    else:
        Led2.value = True

    if touch3.raw_value > touchThreshold3:
        #print("3: "+str(touch3.raw_value))
        #cc.send(ConsumerControlCode.MUTE)  #uncomment if keyboard library is installed
        Led3.value = False
        LogoColor(0,255,0)
        time.sleep(buttonLedDelay)

    else:
        Led3.value = True
        
    if touch4.raw_value > touchThreshold4:
        #print("4: "+str(touch4.raw_value))
        #cc.send(ConsumerControlCode.MUTE)  #uncomment if keyboard library is installed
        Led4.value = False
        LogoColor(0,0,255)
        time.sleep(buttonLedDelay)
    else:
        Led4.value = True

    if touch5.raw_value > touchThreshold5:
        #print("5: "+str(touch5.raw_value))
        #cc.send(ConsumerControlCode.MUTE)  #uncomment if keyboard library is installed
        Led5.value = False
        LogoColor(255,255,255)
        time.sleep(buttonLedDelay)
    else:
        Led5.value = True

    if touch6.raw_value > touchThreshold6:
        #print("6: "+str(touch6.raw_value))
        #cc.send(ConsumerControlCode.MUTE)  #uncomment if keyboard library is installed
        Led6.value = False
        faderLogo = True
        time.sleep(buttonLedDelay)
    else:
        Led6.value = True

    #Read Faders

    if Fader1.value != FaderLastVal1:
        FaderLastVal1 = Fader1.value
        #print(FaderLastVal1)
    
    if Fader2.value != FaderLastVal2:
        FaderLastVal2 = Fader2.value
        #print(FaderLastVal2)

    if Fader3.value != FaderLastVal3:
        FaderLastVal3 = Fader3.value
        #print(FaderLastVal3)

    if Fader4.value != FaderLastVal4:
        FaderLastVal4 = Fader4.value
        #print(FaderLastVal4)

    if faderLogo:
        ledR.duty_cycle = clamp(Fader1.value-64,0,65535)
        ledG.duty_cycle = clamp(Fader2.value-64,0,65535)
        ledB.duty_cycle = clamp(Fader3.value-64,0,65535)


    #Read Buttons

    if not Btn1.value:
        LedBtn1.value = False
        time.sleep(buttonLedDelay)
    else:
        LedBtn1.value = True

    if not Btn2.value:
        LedBtn2.value = False
        time.sleep(buttonLedDelay)
    else:
        LedBtn2.value = True

    if not Btn3.value:
        LedBtn3.value = False
        time.sleep(buttonLedDelay)
    else:
        LedBtn3.value = True

    if not Btn4.value:
        LedBtn4.value = False
        time.sleep(buttonLedDelay)
    else:
        LedBtn4.value = True
