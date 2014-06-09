#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import os.path
import json
import re
import sys
import pycurl
import urllib2

from os.path import expanduser
home = expanduser("~")

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
            links = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', www.contents)
            titles = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', www.contents)
            # print www.contents
            # 2.2. Szukamy w nowy sposób
            # data-media={"id":1084883,"file":"http://static.polskieradio.pl/45b8b22e-2f2e-49c2-a99b-48fef8e4fa85.mp3","provider":"audio","uid":"45b8b22e-2f2e-49c2-a99b-48fef8e4fa85","length":873,"autostart":true,"link":"/39/0/Artykul/1145828,Kongres-Wiedenski-–-narodziny-nowoczesnej-dyplomacji","title":"Kongres%20Wiede%C5%84ski%20%E2%80%93%20narodziny%20nowoczesnej%20dyplomacji"
            links = links + re.findall('data-media={"id":[0-9],"file":"([^"]*)","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"[^"]*"', www.contents)
            titles = titles + re.findall('data-media={"id":[0-9],"file":"[^"]*","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"([^"]*)"', www.contents)
            if(len(links)==0):
                links = re.findall('"file":"([^"]*)"',www.contents)
                # print len(links)
                # print links
                titles = re.findall('"title":"([^"]*)"',www.contents)
                # print len(titles)
                # print titles            
            if(len(links) == len(titles) and len(links) > 0):
                a = 0
                while a < len(links):
                    url = links[a]
                    target_dir = home+'/'
                    if not url.find('static.polskieradio.pl'):
                        url = 'http://static.polskieradio.pl/'+url+'.mp3'
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
                        file_name = target_dir + title+'.mp3'
                    else:
                        file_name = target_dir + links[a]+'.mp3'
                    u = urllib2.urlopen(url)
                    if not os.path.isfile(file_name):
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

