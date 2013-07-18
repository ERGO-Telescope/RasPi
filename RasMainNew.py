#! /usr/bin/python3
#coding=utf-8
import serial
import binascii
import RasShieldNew as shield
import numpy as np
from urllib.request import Request, urlopen
from urllib.error import  URLError
import urllib.parse
import urllib.request
import linecache
import glob
#ignore


#declare variables
numEvent=0
address='mac'
setTIM2_On = "B5 62 06 01 08 00 0D 03 00 01 00 00 00 00 20 25"
setTIM2_Off = "B5 62 06 01 08 00 0D 03 00 00 00 00 00 00 1F 20"
setNavSol_Off = "B5 62 06 01 08 00 01 06 00 00 00 00 00 00 16 D5"
setNavSol_On = "B5 62 06 01 08 00 01 06 00 01 00 00 00 00 17 DA"

def Scale(value,factor):
    temp=str(value)
    print (temp)
    newVal=temp[:(len(temp)-factor)]+'.'+temp[-factor:]
    return float(newVal)

def restart():
    command= "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process= subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output=process.communicate()[0]
    print (output)

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
    NextState=0
    while True:
        State=NextState
        for case in switch(State):
            if case(0):
                print ("going to Shieldinit")
                files=glob.glob('*.ini')
                if 'cert.ini' not in files:
                    print ('Add PixelBirthday file')
                    restart()
                else:
                    temp=(linecache.getline('cert.ini',9))#10 for new birth certificate                
                    address= (temp[6:])
                print (address)
                shield.ShieldInit()
                NextState=1
                break
            if case(1):
                print ('case 1 of Main')
                if shield.NAV_SOL_Received():
                    #shield.SendMsg(setNavSol_Off)
                    NextState=2
                break
            if case(2):
                print ("in case 2 of Main")
                if shield.NAV_POSLHH_Received():                    
                    NextState=3
                break
            if case(3):
                print ("in case 3 of Main")
                if shield.EventFound():
                    print ('EventFound')
                    numEvent+=1
                    NextState=4
                break
            
            if case(4):
                print ("in case 4 of Main")
                NextState=5
                break
            if case(5):#make call to server
                print ('Posting data')
                url= 'http://www.seti.net/php/setEvent2.php'
                try:
                    print ('trying url')
                    response=urlopen(url)
                except URLError as e:
                    print('in except')
                    if hasattr(e,'reason'):
                        print ('We failed to reach the server.')
                        print ('Reason:',e.reason)
                        NextState=1
                    elif hasattr(e,'code'):
                        print('The server couldn\'t fulfill the request')
                        print ('Error code:', e.code)
                        NextState=1
                    
                
                print(shield.lat, shield.lon)
                #need two dictionaries so that mac field goes first in url
                values={'mac': address
                        }
                values2={'analog': 555,
                        'lat':shield.lat,
                        'lon':shield.lon,
                        'hMSL':shield.hMSL,
                        'wnR': shield.wnR,
                        'towMsR': shield.towMsR,
                        'towSubMsR': shield.towSubMsR}
                ###########################
                print(values2)
                data=urllib.parse.urlencode(values)
                data=data[:-3]
                data2=urllib.parse.urlencode(values2)                
                full_url=url+'?'+data+'&'+data2
                print (full_url)
                response=urllib.request.urlopen(full_url)
                print (response.read().decode('utf-8'))
                NextState=6
                break
            if case(6):
                loop=0
                if response.code == 200:
                    #shield.SendMsg(setNavSol_On)
                    NextState=1
                loop+=1
                if loop>1000:
                    response.close()
                    NextState=1
                break

loopFunc()
