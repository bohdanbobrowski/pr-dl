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

save_all = 0

def getin():
    if os.name == 'nt':
        from msvcrt import getch
        ch = getch()
    else:
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def Separator(sign='-'):
    rows, columns = os.popen('stty size', 'r').read().split()
    columns = int(columns)
    separator = ''
    for x in range(0, columns):
        separator = separator + sign
    print separator

def Klawisz(answer):
    if(answer == 1):
        return 1
    else:
        print "Czy zapisać podcast? ([t]ak / [n]ie / [z]akoncz)"
        key = getin()
        if key == 'z' or key == 'Z':
            Separator('#')
            exit()
        if key == 't' or key == 'T':
            return 1
        else:
            return 0

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

# Parametry podstawowe:
if len(sys.argv) > 2:
    if sys.argv[2] == '-T':
        save_all = 1
    else:
        home = sys.argv[2]
if len(sys.argv) > 3 and sys.argv[3] == '-T':
    save_all = 1

if len(sys.argv) > 1:
    if(sys.argv[1].find("http://www.polskieradio.pl")==0):

        Separator('#')
        print "Analizowany url: "+sys.argv[1]
        www = PobierzStrone()
        c = pycurl.Curl()
        c.setopt(c.URL, sys.argv[1])
        c.setopt(c.WRITEFUNCTION, www.body_callback)
        c.perform()
        c.close()
        
        """
        [TO-DO]:
        Część treści - jeżeli pojawia sie 'paginacja' - doładowywana jest przez AJAX'a

        link:
        <a id="ctl00_nextAnchor" onclick="LoadTab(10281, 35378, 0, 9, 396, 4, &quot;&quot;, 445, &quot;stid=9&amp;pid=7422&amp;cttype=4&amp;ctid=396&quot;, &quot;Poprzednie audycje&quot;, &quot;True&quot;, 9, 700, 5);">Następna strona&nbsp;»</a>
        url:
        http://www.polskieradio.pl/CMS/DocumentsListsManagement/DocumentsListTabContent.aspx/GetTabContent
        post:
        {tabId : 35378, boxInstanceId : 10281, sectionId : 9, categoryId : 396, categoryType : 4, subjectIds : '', tagIndexId : 445, queryString : 'stid=9&pid=7422&cttype=4&ctid=396', name : 'Poprzednie audycje', pageNumber : 2, pagerMode : 1, openArticlesInParentTemplate : 'True', idSectionFromUrl : 9, maxDocumentAge : 700 }
        {tabId : 35378, boxInstanceId : 10281, sectionId : 9, categoryId : 396, categoryType : 4, subjectIds : '', tagIndexId : 445, queryString : 'stid=9&pid=7422&cttype=4&ctid=396', name : 'Poprzednie audycje', pageNumber : 4, pagerMode : 1, openArticlesInParentTemplate : 'True', idSectionFromUrl : 9, maxDocumentAge : 700 }
        """
        
        # 2.1. Szukamy w stary sposób
        links = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', www.contents)
        titles = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', www.contents)
        
        # 2.2. Szukamy w nowy sposób
        links = links + re.findall('"file":"([^"]*)","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"[^"]*"', www.contents)
        titles = titles + re.findall('"file":"[^"]*","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"([^"]*)"', www.contents)
        
        print titles

        # 2.3. Jeżeli te dwa sposoby nie przyniosły skutku, szukamy raz jeszcze inaczej:
        if(len(links)==0):
            links = re.findall('"file":"([^"]*)"',www.contents)
            titles = re.findall('"title":"([^"]*)"',www.contents)

        print 'Znaleziono:'
        print str(len(links)) + ' linków'
        print str(len(titles)) + ' tytułów'
        Separator()
        
        print 'Rozpoczynamy pobieranie:'
        if(len(links) == len(titles) and len(links) > 0):
            a = 0
            while a < len(links):
                url = links[a]
                target_dir = home+'/'
                if url.find('static.polskieradio.pl') == -1:
                    url = 'http://static.polskieradio.pl/'+url+'.mp3'
                print "[" + str(a+1) + "/" + str(len(links)) + "] " + url
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
                if(Klawisz(save_all) == 1):
                    if(title != ''):
                        file_name = target_dir + title+'.mp3'
                    else:
                        file_name = target_dir + links[a]+'.mp3'
                    try:
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
                    except urllib2.HTTPError as e:
                        print(e.code)
                        print(e.read())
                Separator()
                a += 1
        Separator('#')
