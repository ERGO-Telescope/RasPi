import urllib.parse
import urllib.request
import binascii
url='http://www.seti.net/php/setEvent.php'
values={'pixel_ID':439,
        'latitude':32.99,
        'longitude':-89.5,
        'analog':123,
        'wnR':12,
        'towMsR':123,
        'towSubMsR':1234}
data=urllib.parse.urlencode(values)
print (data)
#data=data.encode('utf-8')
full_url=url+'?'+data
print (full_url
       )
response= urllib.request.urlopen(full_url)
the_page= response.read()
print(the_page)
print(response.close())

