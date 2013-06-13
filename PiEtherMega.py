#! /usr/bin/python3
#coding=utf-8
import serial
import binascii
import PiEtherMegaShield as shield
import numpy as np
#ignore


#declare variables
numEvent=0

##necessary switch function
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False
## Main loop function

def loopFunc():
    NextState=1
    while True:
        State=NextState
        for case in switch(State):
            if case(1):
                print ("going to Shieldinit")
                shield.ShieldInit()
                NextState=2
                break
            if case(2):
                if shield.CollectPosition():
                    shield.SendMsg(setTIM2_On)
                    NextState=3
                break
            if case(3):
                if shield.EventFound():
                    numEvent+=1
                    NextState=4
                break
            #case 4-6 crypto stuff

loopFunc()
