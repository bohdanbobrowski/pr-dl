#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import json
import re
import sys
import pycurl
import urllib2

class PobierzStrone:
    def __init__(self):
        self.contents = ''
    def body_callback(self, buf):
        self.contents = self.contents + buf

def get_resource_path(rel_path):
    dir_of_py_file = os.path.dirname(__file__)
    rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
    abs_path_to_resource = os.path.abspath(rel_path_to_resource)
    return abs_path_to_resource

if len(sys.argv) > 1:
    for arg in sys.argv:
        if(arg.find("http://www.polskieradio.pl")==0):
            print arg
            www = PobierzStrone()
            c = pycurl.Curl()
            c.setopt(c.URL, arg)
            c.setopt(c.WRITEFUNCTION, www.body_callback)
            c.perform()
            c.close()
            # 2.1. Szukamy w stary sposób
            # onclick="javascript:playFile('1083019','ee169737-54bb-40e0-b7be-eb4a69b7d4b8','','1057','/80/1007/Artykul/1141701,Musi-sie-udac-Joanna-Boguslawska','0','0');
            # http://static.polskieradio.pl/ee169737-54bb-40e0-b7be-eb4a69b7d4b8.mp3            
            links = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', www.contents)
            titles = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', www.contents)
            filenames = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'[^\']*\',\'[^\']*\',\'[^\']*\',\'([^\']*)\',\'1\',\'[^\']*\'\);', www.contents)
            # 2.2. Szukamy w nowy sposób
            # iSpeaker" data-media='{"id":874754,"file":"http://static.polskieradio.pl/4a9904eb-246e-4d7c-829d-32ac6ad05f9a.mp3","provider":"audio","uid":"4a9904eb-246e-4d7c-829d-32ac6ad05f9a","length":1800,"autostart":true,"link":"/39/0/Artykul/863703,Ronald-Reagan-czyli-jak-aktor-filmowy-zostal-prezydentem","title":"Ronald%20Reagan%2C%20czyli%20jak%20aktor%20filmowy%20zosta%C5%82%20prezydentem"
            links = links + re.findall('iSpeaker" data-media=\'{"id":[0-9]*,"file":"[^"]*","provider":"audio","uid":"([^"]*)","length":[0-9]*,"autostart":true,"link":"[^"]*","title":"[^"]*"', www.contents)
            titles = titles + re.findall('iSpeaker" data-media=\'{"id":[0-9]*,"file":"[^"]*","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":true,"link":"[^"]*","title":"([^"]*)"', www.contents)
            filenames = filenames + re.findall('iSpeaker" data-media=\'{"id":[0-9]*,"file":"[^"]*","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":true,"link":"([^"]*)","title":"[^"]*"', www.contents)
            if(len(links) == len(titles) and len(links) == len(filenames) and len(links) > 0):
                a = 0
                while a < len(links):
                    url = 'http://static.polskieradio.pl/'+links[a]+'.mp3'
                    print (str(a) + ". " + url)
                    title = titles[a]
                    title = urllib2.unquote(title)
                    title = title.replace(':','_')
                    title = title.replace(' ','_')
                    title = title.replace('/','_')
                    title = title.replace('&quot;','')
                    title = title.replace('"','')
                    title = title.replace('_-_','-')
                    title = title.replace('_-_','-')
                    title = title.replace('_-_','-')
                    print 'Tytuł: '+title
                    if(title != ''):
                        file_name = title+'.mp3'
                    else:
                        file_name = links[a]+'.mp3'
                    u = urllib2.urlopen(url)
                    f = open(file_name, 'wb')
                    meta = u.info()
                    file_size = int(meta.getheaders("Content-Length")[0])
                    print("Pobieranie: {0} Rozmiar: {1}".format(url, file_size))            
                    file_size_dl = 0
                    block_sz = 8192
                    while True:
                        buffer = u.read(block_sz)
                        if not buffer:
                            break
                        file_size_dl += len(buffer)
                        f.write(buffer)
                        p = float(file_size_dl) / file_size
                        status = r"{0}  [{1:.2%}]".format(file_size_dl, p)
                        status = status + chr(8)*(len(status)+1)                
                        sys.stdout.write(status)
                    f.close()
                    a += 1

