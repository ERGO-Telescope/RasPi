// File: ERGOEtherMega2.ino  As of 2013-05-22
#define Unit 1 // This is the pixel unit number (unit 1 is a test unit) 

#include <MemoryFree.h>
#include <SPI.h>
#include <Ethernet.h>

#define MeasuredValue 555 // This simply creates "555" for the Analog field on the server
#define UBX_MAX_SIZE 60 

PROGMEM prog_uchar setPRT1[] = {0xB5, 0x62,0x06 ,0x00, 0x14 ,0x00 ,0x01, 0x00, 0x00 ,0x00, 0xD0, 0x08, 0x00, 0x00, 0x00, 0xC2, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00 ,0x00, 0x00, 0x00, 0x00, 0xB8, 0x42};
PROGMEM prog_uchar setPRT2[] = {0xB5, 0x62,0x06 ,0x00, 0x14 ,0x00 ,0x01, 0x00, 0x00 ,0x00, 0xC0, 0x08, 0x00, 0x00, 0x00, 0xC2, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00 ,0x00, 0x00, 0x00, 0x00, 0xA8, 0x42};

PROGMEM prog_uchar setTIM2_On[] ={0xB5, 0x62,0x06,0x01, 0x08,0x00,0x0D,0x03, 0x00,  0x01,  0x00,  0x00,  0x00,  0x00, 0x20, 0x25} ; 
PROGMEM prog_uchar setTIM2_Off[] ={0xB5, 0x62,0x06,0x01, 0x08,0x00,0x0D,0x03, 0x00,  0x00,  0x00,  0x00,  0x00,  0x00, 0x1F, 0x20} ; 
PROGMEM prog_uchar setNavPOSLHH_Off[] ={0xB5, 0x62,0x06,0x01, 0x08,0x00,0x01,0x02, 0x00,  0x00,  0x00,  0x00,  0x00,  0x00, 0x12, 0xB9 } ; // Turn UART1 off for NAV-POSLHH
PROGMEM prog_uchar setNavPOSLHH_On[] ={0xB5, 0x62,0x06,0x01, 0x08,0x00,0x01,0x02, 0x00,  0x01,  0x00,  0x00,  0x00,  0x00, 0x13, 0xBE } ;  // Turn UAER2 on for NAV-POSLHH
PROGMEM prog_uchar setNavSol_On[] ={0xB5, 0x62,0x06,0x01, 0x08,0x00,0x01,0x06, 0x00,  0x01,  0x00,  0x00,  0x00,  0x00, 0x17, 0xDA } ;
PROGMEM prog_uchar setNavSol_Off[] ={0xB5, 0x62,0x06,0x01, 0x08,0x00,0x01,0x06, 0x00,  0x00,  0x00,  0x00,  0x00,  0x00, 0x16, 0xD5 } ;
PROGMEM prog_uchar setRATE_1000[] ={0xB5, 0x62,0x06,0x08, 0x06,0x00,0xE8,0x03, 0x01, 0x00,  0x01,  0x00,  0x01,  0x39  } ;
PROGMEM prog_uchar setRATE_200[] = {0xB5, 0x62,0x06,0x08, 0x06,0x00,0xC8,0x00, 0x01, 0x00,  0x01,  0x00,   0xDE, 0x6A, } ;

byte mac[] = {  0x90, 0xA2, 0xda, 0x00, 0x90, 0x61 };// Enter a MAC address for Ethernet controller .
char serverName[] = "shell.cent.betaforce.com";// Works...

boolean Fix3D;
long wnR;
uint8_t NumSats; 
long UBX_ecefVZ;
long iTOW;
long lon;
long lat;
long height;
long hMSL;
long towMsR;
long towSubMsR;

char * Key = "derp";

uint8_t derpKey1[]={0x64,0x65,0x72,0x70 }; // 4 char key which is "derp"
int i;
int State = 99 ;
int NextState = 99;

String ClearPostData;
byte * CryptoPostData;
int numEvent;
EthernetClient client;
int loops = 0;
void setup()
{
	Serial.begin(115200);
	Serial1.begin(9600);// Start at the default baud rate 
	Serial.println (" -- ERGO Ether Mega 2  2013-05-22 --");

	numEvent = 0;
	//	Serial.println("check mac"); 
	if(Ethernet.begin(mac) == 0)
	{
		Serial.println("...Error getting IP address via DHCP...");
		while(true);
	}

	Serial.print(" freeMem = ");// Report initial memory usage
	Serial.println(freeMemory());

	NextState = 1;
}

void loop()// Main Loop of the Pixel
{
	{if(NextState != State)// Report state change
	{
		Serial.print("Enter State: ");
		Serial.println(NextState);
	}
	State = NextState;
	switch (State)
	{
	case 0:
		NextState = 1;
		break;
	case 1:
		ShieldInit();
		//NextState = 0; // Debugg
		NextState = 2;	// Go wait for NAV-SOL to appear
		break;
	case 2:
		if (CollectPosition()) 
		{
			/*
			Serial.println(" Position data collected: ");
			Serial.print("SOL-Fix3d: ");if (Fix3D) Serial.println("true"); else Serial.println("false"); 
			Serial.print("SOL-NumSats: "); Serial.println(NumSats);
			Serial.print("SOL-Vertical Speed: "); Serial.println(UBX_ecefVZ );
			Serial.print("POSLLH-lon: "); Serial.println(lon);
			Serial.print("POSLLH-lat: "); Serial.println(lat);
			Serial.print("POSLLH-hMSL: "); Serial.println(hMSL);
			Serial.print("POSLLH-iTOW: "); Serial.println(iTOW);*/

			CFG( setTIM2_On,sizeof(setTIM2_On ));// Turn on the Events
			NextState =  3 ;// Go wait for TIM2 Events

		}
		break;
	case 3:
		if (EventFound())
		{ 
			numEvent++;
			/*Serial.println("Event data collected: ");
			Serial.print(" Event Number: "); Serial.println(numEvent );
			Serial.print(" TIM2-wnR: "); Serial.println( wnR ); 
			Serial.print(" TIM2-towMsR: "); Serial.println(towMsR);
			Serial.print(" TIM2-towSubMsR: "); Serial.println(towSubMsR);*/

			NextState =  4 ;// Go build Clear/Crypto and POST
			//NextState =  0 ;// DEBUG
		}
		break;
	case 4:
		ClearPostData = CreateClearPOST( Unit,MeasuredValue, lat,lon,hMSL,wnR, towMsR,towSubMsR  );
		//	Serial.print("ClearPostData: ");
		//	Serial.println(ClearPostData);
		// Uncomment the next line to send a known message to the server
		//ClearPostData  = "{  \"analog\":\"1\",     \"  latitude\":\"53.32\",\"   longitude\":\"78.82\",\"altitude\":\"50\",\"unixtime\":\"1349808179\",\"nanoseconds\":\"8239\"}";

		ClearPostData.replace(" ","");
		CryptoPostData = CreateCryptoPost(Key,ClearPostData ); 

		//	Serial.println( HashtoASCII(CryptoPostData));// This converts the byte hash to ascii for printing and to send to POST

		NextState =  5 ;// go POST it

		break;
	case 5:// Make call to server
		{// if you get a connection, report back via serial:
			Serial.println("connecting...");
			if (client.connect(serverName, 8000)) // Port for James Riley's server is 8000 
			{
				Serial.println("connected");
				client.println("POST /api/v1/event/ HTTP/1.1");	
				client.println("Content-Type: application/json");	
				String auth;
				//auth = "Authorization: 1:";
				auth = "Authorization: ";
				auth += Unit;// This is the pixel unit number (a constant)
				auth +=":";

				auth += HashtoASCII(CryptoPostData);
				client.println(auth);

				String strContentLength  =  "Content-Length: ";
				strContentLength += ClearPostData.length() ;
				strContentLength += "\r\n";
				client.println(strContentLength); 

				client.print(ClearPostData); 

				NextState =  6 ;// Then go wait for response to the post  
			} 
			else 
			{
				Serial.println("connection failed");
				NextState = 1;
			}
		}
		break;
	case 6:// Recover server response

		{
			int connectLoop = 0;
			while(client.connected())
			{
				while(client.available())
				{
					char c = client.read();
					Serial.print(c);
					connectLoop = 0;
				}

				delay(1);
				connectLoop++;
				if(connectLoop > 10000)
				{
					Serial.println();
					Serial.println(F("Timeout"));
					client.stop();
				}
			}
			Serial.println(F("disconnecting."));
			client.stop();

			Serial.print(" freeMem = ");
			Serial.println(freeMemory());
			NextState = 3;
		}
		break;
	}
	}

}