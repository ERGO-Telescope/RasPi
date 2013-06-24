#! /usr/bin/python3
#coding=utf-8
import serial
import binascii
import PiEtherMegaShield as shield
import numpy as np
from urllib.request import Request, urlopen
from urllib.error import  URLError
import urllib.parse
import urllib.request
#ignore


#declare variables
numEvent=0

def Scale(value,factor):
    temp=str(value)
    print temp
    newVal=temp[:(len(temp)-factor)]+'.'+temp[-factor:]
    return int(newVal)
                

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
            if case(4):
                NextState=5
                break
            if case(5):#make call to server
                url= Request('http://www.seti.net/php/setEvent.php')
                try:
                    response=urlopen(url)
                except URLError as e:
                    if hasattr(e,'reason'):
                        print ('We failed to reach the server.')
                        print ('Reason:',e.reason)
                        NextState=1
                    elif hasattr(e,'code'):
                        print('The server couldn\'t fulfill the request')
                        print ('Error code:', e.code)
                        NextState=1
                    else:
                        values={'pixel_ID': 1,
                                'latitute': Scale(lat,7),
                                'longitude': Scale(lon,7),
                                'analog': 0;
                                'wnR': wnR,
                                'towMsR': towMsR,
                                'towSubMsR': towMsR}
                        data=urllib.parse.urlencode(values)
                        full_url=url+'?'+data
                        response=urllib.request.urlopen(full_url)
                        print (response.read())
                        NextState=6
                break
            if case(6):
                #some weird stuff
                NextState=3
                break

loopFunc()
