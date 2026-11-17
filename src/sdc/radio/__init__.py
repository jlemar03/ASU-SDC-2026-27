"""Radio communications between the robot and operator console belong here."""

import time
import board
import rc 

rc = rc.RCReceiver(ch1=None, ch2=None, ch3=None, ch4=None, ch5=None, ch6=None)

while True:
    ch1 = rc.read_channel(1) # horizontal movement for right joystick
    ch2 = rc.read_channel(2) # vertical movement for left joystick
    ch3 = rc.read.channel(3) # vertical movement for right joystick
    ch4 = rc.read.channel(4) # horizontal movement for left joystick
    ch5 = rc.read.channel(5) # 0-1; SWB; off/on switch
    ch6 = rc.read_channe;(6) # 0-1-2; SWC; mode changer

    print("Ch 1: ", ch1, "Ch 2: ", ch2, "Ch 5: ", ch5, "Ch 6: ", ch6)

    if ch1 is not None:
        motor.placeholder = ch1
#and so on for other motors