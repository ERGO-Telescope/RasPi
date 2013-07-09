import urllib.parse
import urllib.request
import binascii
import linecache

temp=linecache.getline('cert.ini',9)
address= (temp[6:])
print (address,'working')


url='http://www.seti.net/php/setEvent.php?'
values={}
values2={}
values['mac']=address
values2['latitude']= 32.99
values2['towMsR']=123
values2['longitude']=-89.5
values2['analog']=123
values2['wnR']=12
values2['towSubMsR']=1234
data=urllib.parse.urlencode(values)
data=data[:-3]
data2=urllib.parse.urlencode(values2)


print (data,data2)
full_url=url+data+'&'+data2#'?mac='+address+'&latitude=32.99&longitude=-89.5&analog=123&wnR=12&towMsR=123&towSubMsR=1234'
print (full_url)
response= urllib.request.urlopen(full_url)
the_page= response.read().decode('utf-8')
print(the_page)
##print(response.close())

