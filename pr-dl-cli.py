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

def Separator():
    rows, columns = os.popen('stty size', 'r').read().split()
    columns = int(columns)
    separator = ''
    for x in range(0, columns):
        separator = separator + '-'
    print separator

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
            # 2.2. Szukamy w nowy sposób
            links = links + re.findall('data-media={"id":[0-9],"file":"([^"]*)","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"[^"]*"', www.contents)
            titles = titles + re.findall('data-media={"id":[0-9],"file":"[^"]*","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"([^"]*)"', www.contents)
            Separator()
            print 'Znaleziono:'
            print str(len(links)) + ' linków'
            print str(len(titles)) + ' tytułów'
            Separator()
            print 'Linki:'
            print links
            Separator()
            print 'Tytuły:'
            print titles
            Separator()
            print 'Rozpoczynamy pobieranie:'
            if(len(links)==0):
                links = re.findall('"file":"([^"]*)"',www.contents)
                titles = re.findall('"title":"([^"]*)"',www.contents)
            if(len(links) == len(titles) and len(links) > 0):
                a = 0
                while a < len(links):
                    url = links[a]
                    target_dir = home+'/'
                    if url.find('static.polskieradio.pl') == -1:
                        url = 'http://static.polskieradio.pl/'+url+'.mp3'
                    print (str(a) + ". " + url)
                    title = titles[a]
                    title = urllib2.unquote(title)
                    title = title.replace('?','')
                    title = title.replace('(','')
                    title = title.replace(')','')
                    title = title.replace(':','_')
                    title = title.replace(' ','_')
                    title = title.replace('/','_')
                    title = title.replace('&quot;','')
                    title = title.replace('"','')
                    title = title.replace('_-_','-')
                    title = title.replace('_-_','-')
                    title = title.replace('_-_','-')
                    print 'Tytuł: '+title
                    print 'Link: '+url
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
                    else:
                        print '[!] Plik o tej nazwie istnieje w katalogu docelowym'
                    a += 1

