#! /usr/bin/python3
#coding=utf-8
import serial
import binascii
import PixelRaspiShieldmod as shield
import numpy as np
from urllib.request import Request, urlopen
from urllib.error import  URLError
import urllib.parse
import urllib.request
import linecache
#ignore


#declare variables
numEvent=0
address='mac'

def Scale(value,factor):
    temp=str(value)
    print (temp)
    newVal=temp[:(len(temp)-factor)]+'.'+temp[-factor:]
    return float(newVal)
                

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
    global numEvent,lat,lon, wnR, towMsR,towSubMsR, address
    NextState=1
    while True:
        State=NextState
        for case in switch(State):
            if case(1):
                print ("going to Shieldinit")
                temp=(linecache.getline('cert.ini',9))
                address= (temp[6:])
                shield.ShieldInit()
                NextState=2
                break
            if case(2):
                if shield.CollectPosition():
                    
                    NextState=3
                break
            if case(3):
                if shield.CollectPosition():
                    shield.SendMsg(setTIM2_On)
                    NextState=4
                break
            if case(4):
                if shield.EventFound():
                    numEvent+=1
                    NextState=5
                break
            
            if case(5):
                NextState=6
                break
            if case(6):#make call to server
                print ('case 6')
                url= 'http://www.seti.net/php/setEvent.php'
##                try:
##                    print ('trying url')
##                    response=urlopen(url)
##                except URLError as e:
##                    print('in except')
##                    if hasattr(e,'reason'):
##                        print ('We failed to reach the server.')
##                        print ('Reason:',e.reason)
##                        NextState=1
##                    elif hasattr(e,'code'):
##                        print('The server couldn\'t fulfill the request')
##                        print ('Error code:', e.code)
##                        NextState=1
##                    else:
                print('in else')
                values={'mac': address}
                values2={'latitute': Scale(lat,7), #need two dictionaries so that mac field goes first in url
                        'longitude': Scale(lon,7),
                        'analog': analog,
                        'wnR': wnR,
                        'towMsR': towMsR,
                        'towSubMsR': towSubMsR}
                data=urllib.parse.urlencode(values)
                data=data[:-3]
                data2=urllib.parse.urlencode(values2)                
                full_url=url+'?'+data+'&'+data2
                response=urllib.request.urlopen(full_url)
                print (response.read().decode('utf-8'))
                NextState=6
                break
            if case(7):
                loop=0
                if response.code == 200:
                    NextState=3
                loop+=1
                if loop>1000:
                    response.close()
                    NextState=1
                break

loopFunc()
