#! /usr/bin/python3
#coding=utf-8
import serial
import binascii
import time
import numpy as np
import struct
## Declare messages to be sent to Ublox
setRate_200 = "B5 62 06 08 06 00 C8 00 01 00 01 00 DE 6A"
setRate_1000 = "B5 62 06 08 06 00 E8 03 01 00 01 00 01 39"
setNavSol_Off = "B5 62 06 01 08 00 01 06 00 00 00 00 00 00 16 D5"
setNavSol_On = "B5 62 06 01 08 00 01 06 00 01 00 00 00 00 17 DA"
setNavPOSLHH_Off = "B5 62 06 01 08 00 01 02 00 00 00 00 00 12 B9" # Turn UART1 off
setNavPOSLHH_On = "B5 62 06 01 08 00 01 02 00 01 00 00 00 00 13 BE" # Turn UAER2 on
setTIM2_On = "B5 62 06 01 08 00 0D 03 00 01 00 00 00 00 20 25"
setTIM2_Off = "B5 62 06 01 08 00 0D 03 00 00 00 00 00 00 1F 20"

setPRT = "B5 62 06 00 14 00 01 00 00 00 D0 08 00 00 00 C2 01 00 01 00 01 00 00 00 00 00 B8 42"
setPRT2 = "B5 62 06 00 14 00 01 00 00 00 C0 08 00 00 00 C2 01 00 01 00 01 00 00 00 00 00 A8 42"
##list or commands to be sent
CmdList=[setPRT,setNavPOSLHH_Off, setNavSol_Off, setTIM2_Off, setRate_1000, setNavSol_On]
##declare variables
ck_a=0
ck_b=0
step= int
UBX_Class=np.uint8
UBX_ID=np.uint8
UBX_length_hi=np.uint8
UBX_length_lo=np.uint8
UBX_counter=np.uint8
UBX_MAX_SIZE=60
UBX_buffer=[None]*60
UBX_ck_a=np.uint8
UBX_ck_b=np.uint8
msTime=int #ms Time of week
ch=int
flags=int
checksum=int
GPSTimer=int
lon=int
lat=int
height=int
hMSL=int
towMsR=int
towSubMsR=int
Fix3D=bool
UBX_ecefVZ=int
NumSats= int
Speed3D=int
GroundSpeed=int
GroundCourse=int
wnR=int
UBX_ecefVZ=int
Buffer=[]
NewMessage=False

## Initialize UART Port
Port = serial.Serial()
Port.baudrate = 38400
Port.port = '/dev/ttyAMA0'


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
## Function that sends Message to Ublox
def SendMsg(command):
    Port.write(bytes.fromhex(command))
    
    return print ("command " +str(command)+" sent")
def ShieldInit():
    Port.open()
    for cmd in CmdList:
        SendMsg(cmd)
        time.sleep(5)
def CollectPosition():
    global NewMessage
    ret=bool
    ret=False
    SatCount=int
    MessageRecieved()
    print ('back in Collect position, turning port on')
    
    if NewMessage==True:
        print (NewMessage)
        time.sleep(.1)
        Port.open()
        if UBX_ID==b'06' and Fix3D:
            SendMsg(setNavSol_Off)
            Sendmsg(setNavPOSLHH_On)
        if UBX_ID==b'02':
            SendMsg(setNavPOSLHH_Off)
            ret=True
        else:
            ret=False
        return ret
def EventFound():
    global NewMessage
    ret=bool
    ret=False
    print('in EventFound')
    if NewMessage ==True:
        if UBX_Class ==b'0d' and UBX_ID==b'03':
            ret=True
    return ret
def MessageRecieved():
    print("in Message Recieved")
    global Buffer, NewMessage
    count=0
    step=0
    NewMessage=False
    Port.open()
    while Port.isOpen():
        #print("port is open")
        count+=1
        data= binascii.hexlify(Port.read(1))
        
        for case in switch(step):
            print (data)
            if case(0):
                if data==b'b5':
                    print("case 0")
                    step+=1
                break
            if case(1):
                print ("case 1")
                if data==b'62':
                    step+=1
                    
                else:
                    step=0
                break
            if case(2):
                print ("case 2")
                global UBX_Class
                UBX_Class=data
                Buffer.append(data)
                #Ubx_CheckSum(UBX_Class)
                step+=1
                break
            if case(3):
                print ('case 3')
                global UBX_ID
                UBX_ID=data
                Buffer.append(data)
                #Ubx_CheckSum(UBX_ID)
                step+=1
                break
            if case(4):
                print("case4")
                global UBX_length_hi
                UBX_length_hi=data
                Buffer.append(data)
                #Ubx_CheckSum(UBX_length_hi)
                step+=1
                print(int(UBX_length_hi,16), UBX_MAX_SIZE)
                if int(UBX_length_hi,16)>=UBX_MAX_SIZE:
                    print (int(UBX_length_hi,16), 'case 4 tech')
                    step=0
                    ck_a=0
                    ck_b=0
                break
            if case(5):
                print('case 5')
                global UBX_length_lo, UBX_counter
                UBX_length_lo=data
                Buffer.append(data)
                #Ubx_CheckSum(UBX_length_lo)
                step+=1
                UBX_counter=0
                break
            if case(6):
                global UBX_counter, UBX_length_hi, UBX_buffer
                if UBX_counter<int(UBX_length_hi,16):
                    
                    UBX_buffer[UBX_counter]=data
                    Buffer.append(data)
                    #Ubx_CheckSum(data)
                    UBX_counter+=1
                    if UBX_counter==int(UBX_length_hi,16):
                        step+=1
                break
            if case(7):
                global UBX_ck_a
                UBX_ck_a=struct.unpack('B',binascii.unhexlify(data))[0]
                UBX_buffer[UBX_counter]=data
                #UBX_ck_a=int(data,16)
                print("case 7",UBX_ck_a)
                step+=1
                break
            if case(8):
                global UBX_ck_b, UBX_ck_a, ck_a, ck_b
                UBX_ck_b=struct.unpack('B',binascii.unhexlify(data))[0]
                UBX_buffer[UBX_counter+1]=data
                #UBX_ck_b=int(data,16)
                Ubx_CheckSum(Buffer)
                
                print("case 8",'UBX_ck_b=',UBX_ck_b,'UBX_ck_a=',UBX_ck_a, ck_b, ck_a)
                     
                if (ck_a== UBX_ck_a) and (ck_b== UBX_ck_b):
                    print('reseting')
                    step=0
                    ck_a=0
                    ck_b=0
                    ParseMessage()
                    print ('back in message recieved')
                    Port.close()
                    break
                else:
                    
                    step=0
                    ck_a=0
                    ck_b=0
                    print ('reseting 2',ck_a, ck_b)
                    break
                
                break
            
    #End of Message Recieved
def ParseMessage():
    global UBX_Class, UBX_ID, UBX_buffer, lon, lat, height, hMSL, Fix3D, Speed3D
    global UBX_ecefVZ, NumSats, GroundSpeed, GroundCourse, ch, flags, wnR, towMsR
    global towSubMsR, checksum, NewMessage
    print("in ParseMessage")
    Position= int
    if UBX_Class== b'03':
        if UBX_ID==b'02': #I D N AV P O S L L H
            Position=0
            msTime= join4(UBX_buffer,Position)
            print("this is ms time",msTime)
            Position+=4
            lon= join4(UBX_buffer,Position)
            Position+=4
            lat= join4(UBX_buffer,Position)
            Position+=4
            height= join4(UBX_buffer,Position)
            Position+=4
            hMSL= join4(UBX_buffer,Position)
            NewMessage=True
        if UBX_ID==b'03':#I D N A V - S O L
            if UBX_buffer >=b'03' and (UBX_buffer[5]==b'01'):
                Fix3D=True  #Valid position
            else:
                Fix3D=False #Invalid position       
        if UBX_ID==b'06': #I D N A V S O L
            if UBX_buffer[10]>= b'03' and (UBX_buffer[11]==b'01'):
                Fix3D=True  #Valid position
            else:
                Fix3D=False #Invalid position
            UBX_ecefVZ=join4(UBX_buffer,36)
            NumSats=UBX_buffer[47]
            NewMessage= True
        if UBX_ID== b'12':  #I D N A V V E L N E D
            Position=16
            Speed3D=join4(UBX_buffer,Position) #cm/s
            print ("this is speed3d",Speed3D)
            Position+=4
            GroundSpeed=join4(UBX_buffer,Position) #cm/s
            Position+=4
            GroundCourse=join4(UBX_buffer,Position) #cm/s
            GroundCourse/=1000
            Position+=4
            NewMessage=True
    if UBX_Class== b'05':
        if UBX_ID==b'01':
            print()

        if UBX_ID==b'00':
            print()      

    if UBX_Class==b'0d': #TIM
        if UBX_ID==b'03':
            print(UBX_Class,UBX_ID)
            ch=doneByte(UBX_buffer,0)
            flags=doneByte(UBX_buffer,1)
            wnR=join2(UBX_buffer,4)
            towMsR=join4(UBX_buffer,8)
            towSubMsR=join4(UBX_buffer,12)
            checksum=join2(UBX_buffer,28)
            NewMessage=True
            print ('leaving', NewMessage)
    print ('end of parse message')
    
#end of Parse Message
        
def join4(buffer, position=int):
    toJoin=[]
    newPosition=position
    for i in range(position,position+4):
        #print(int(buffer[newPosition],16))
        intOfByte=int(buffer[newPosition],16)
        toJoin.append(intOfByte)
        newPosition+=1
    union=int.from_bytes(toJoin,byteorder='little',signed=True)  	
    return union

def join2(buffer, position=int):
    toJoin=[]
    newPosition=position
    for i in range(position,position+2):
        intOfByte=int(buffer[newPosition],16)
        toJoin.append(intOfByte)
        newPosition+=1
    union=int.from_bytes(toJoin,byteorder='little',signed=True)		
    return union

def doneByte(buffer,position=int):
    toJoin=[]
    newPosition=position
    intOfByte=int(buffer[newPosition],16)
    toJoin.append(intOfByte)
    union=int.from_bytes(toJoin,byteorder='little',signed=True)		
    return union

def Ubx_CheckSum(Buffer):
    global ck_a, ck_b
    
    
    for byte in Buffer:
        data=int(byte,16)
        ck_a=(ck_a+data)%256
        ck_b=(ck_b+ck_a)%256
