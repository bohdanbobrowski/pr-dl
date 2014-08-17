#!/usr/bin/env python
#-*- coding: utf-8 -*-
import json
import os
from os.path import expanduser
import pycurl
import re
import sys
import urllib
import urllib2

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
        headers = ['Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language: pl,en-us;q=0.7,en;q=0.3','Accept-Charset: ISO-8859-2,utf-8;q=0.7,*;q=0.7','Content-Type: application/x-www-form-urlencoded']#,'Content-Length: 65']
        c.setopt(c.HEADER, 1);
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.USERAGENT,'Mozilla/5.0 (X11; U; Linux i686; pl; rv:1.8.0.3) Gecko/20060426 Firefox/1.5.0.3')
        c.setopt(c.REFERER, sys.argv[1])        
        c.setopt(c.COOKIEFILE, '')
        c.perform()
        
        # 2.1. Ładujemy podstrony:        
        # 2.1.1. Analizujemy linki do podstron
        try:
            tabId =         int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[\s]*([0-9]*),[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', www.contents).group(1))
            boxInstanceId = int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([\s]*([0-9]*),[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', www.contents).group(1))
            sectionId =     int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[\s]*([0-9]*),[0-9\s]*,[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', www.contents).group(1))
            categoryId =    int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[\s]*([0-9]*),[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', www.contents).group(1))
            categoryType =  int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[\s]*([0-9]*), [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', www.contents).group(1))
            queryString =   str(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[\s]*[0-9]*, &quot;&quot;, [0-9]*, &quot;([a-z0-9&;=]*)&quot;', www.contents).group(1)).replace('&amp;','&')
            tagIndexId =    int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*, &quot;&quot;, ([0-9]*)[a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', www.contents).group(1))
            name = str(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[\s]*[0-9]*, &quot;&quot;, [0-9]*, &quot;[a-z0-9&;=]*&quot;, &quot;([a-zA-Z0-9\s]*)', www.contents).group(1))
            pagerMode = '0'
            openArticlesInParentTemplate = 'True'
            idSectionFromUrl = sectionId
            maxDocumentAge = '-1'
            showCategoryForArticle = 'False'
            post = {
                'tabId' : tabId,
                'boxInstanceId' : boxInstanceId,
                'sectionId' : sectionId,
                'categoryId' : categoryId,
                'categoryType' : categoryType,
                'subjectIds' : "",
                'tagIndexId' : tagIndexId,
                'queryString' : queryString,
                'name' : name,
                'pagerMode' : 0,
                'openArticlesInParentTemplate' : "True",
                'idSectionFromUrl' : sectionId,
                'maxDocumentAge' : 1000,
                # 'showCategoryForArticle' : "False"
            }
            analizuj_podstrony = 1
        except IndexError:
            analizuj_podstrony = 0

        pages = [] + re.findall('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\);" class="">[\s]*([0-9]*)', www.contents)        

        # Niestety ustawiam na 0 by nie tracić czasu na niedziałającą paginację (szczegóły niżej):
        analizuj_podstrony = 0

        if(analizuj_podstrony == 1 and len(pages)>0):
            print "Znaleziono "+str(pages[-1])+" podstron."
            p = 2
            while p <= int(pages[-1]):
                post['pageNumber'] = p
                post_data = json.dumps(post)
                print post_data
                www2 = PobierzStrone()
                c.setopt(c.URL, 'http://www.polskieradio.pl/CMS/DocumentsListsManagement/DocumentsListTabContent.aspx/GetTabContent')
                c.setopt(c.POST, 1)
                c.setopt(c.POSTFIELDS, post_data)
                c.setopt(c.WRITEFUNCTION, www2.body_callback)
                headers = ['Accept: application/json, text/javascript, */*; q=0.01','Accept-Language: pl,en-US;q=0.8,en;q=0.6,ru;q=0.4','Content-Type: application/json; charset=UTF-8']#,'Content-Length: 65']
                c.setopt(c.HEADER, 0);
                c.setopt(c.HTTPHEADER, headers)
                c.setopt(c.FOLLOWLOCATION, 1)
                c.setopt(c.USERAGENT,'Mozilla/5.0 (X11; U; Linux i686; pl; rv:1.8.0.3) Gecko/20060426 Firefox/1.5.0.3')
                c.setopt(c.REFERER, sys.argv[1])        
                c.perform()
                print www2.contents
                print "- pobieram "+str(p)+" podstronę"
                p = p+1 
                """
                Próbuje ogarnąć ta paginacje ale ciągle wywala błąd:
                at System.Linq.Enumerable.First[TSource](IEnumerable`1 source)
                at Billennium.PR.Business.Logic.Components.DocumentsListsLogic.<>c__DisplayClass52.<GetTab>b__51(IDbConnection conn)
                at Billennium.PR.Business.Persistence.MsSqlServer.DbConnectionProvider.UsingConnection(Action`1 codeBlock, Action`2 finallyBlock)
                at Billennium.PR.Business.Logic.Components.DocumentsListsLogic.GetTab(Int32 tabId)
                at Billennium.PR.Web.Portal.CMS.DocumentsListsManagement.DocumentsListTabContent.GetTabContent(Int32 tabId, Int32 boxInstanceId, Int32 sectionId, Int32 categoryId, Int32 categoryType, String subjectIds, Int32 tagIndexId, String queryString, String name, Int32 pageNumber, Int32 pagerMode, String openArticlesInParentTemplate, Int32 idSectionFromUrl, Int32 maxDocumentAge)

                specyfikacja funkcji GetTabContent:
                GetTabContent(
                    Int32 tabId,
                    Int32 boxInstanceId,
                    Int32 sectionId,
                    Int32 categoryId,
                    Int32 categoryType,
                    String subjectIds,
                    Int32 tagIndexId,
                    String queryString,
                    String name,
                    Int32 pageNumber,
                    Int32 pagerMode,
                    String openArticlesInParentTemplate,
                    Int32 idSectionFromUrl,
                    Int32 maxDocumentAge
                )

                moje query:
                {
                    "tabId": 5677,
                    "boxInstanceId": 16115,
                    "sectionId": 8,
                    "showCategoryForArticle": "False",
                    "queryString": "stid=8&pid=7298&cttype=4&ctid=405",
                    "subjectIds": "",
                    "openArticlesInParentTemplate": "True",
                    "pagerMode": 0,
                    "name": "Poprzednie audycje",
                    "idSectionFromUrl": 8,
                    "tagIndexId": 444,
                    "pageNumber": 3,
                    "maxDocumentAge": -1,
                    "categoryType": 4,
                    "categoryId": 405
                }

                Podejżewam że coś z ciastkami albo naglowkami jest nie teges.
                """

        c.close()

        # 2.2. Szukamy pokastów:
        links = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', www.contents)
        titles = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', www.contents)
        links = links + re.findall('"file":"([^"]*)","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"[^"]*"', www.contents)
        titles = titles + re.findall('"file":"[^"]*","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"([^"]*)"', www.contents)

        # 2.3. Jeżeli te dwa sposoby nie przyniosły skutku, szukamy raz jeszcze inaczej:
        if(len(links)==0):
            links = re.findall('"file":"([^"]*)"',www.contents)
            titles = re.findall('"title":"([^"]*)"',www.contents)

        # 3. Budujemy listę unikalnych linków:
        do_pobrania = {}
        if(len(links) == len(titles) and len(links) > 0):
            a = 0
            while a < len(links):
                url = links[a]
                if url.find('static.polskieradio.pl') == -1:
                    url = 'http://static.polskieradio.pl/'+url+'.mp3'
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
                try:
                    do_pobrania[url]
                except KeyError:
                    do_pobrania[url] = title
                a = a+1
        print 'Znaleziono: '+ str(len(do_pobrania)) + ' podkastów.'

        # 4. Pobieranie:
        print 'Rozpoczynamy pobieranie:'
        Separator()
        if(len(do_pobrania) > 0):
            a = 0
            for url in do_pobrania:
                title = do_pobrania[url]
                target_dir = home+'/'
                file_name = target_dir + title+'.mp3'
                print 'Tytuł: '+title
                print 'Link: '+url
                if(os.path.isfile(file_name)):
                    print '[!] Plik o tej nazwie istnieje w katalogu docelowym'
                else:
                    if(Klawisz(save_all) == 1):
                        try:
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
                        except urllib2.HTTPError as e:
                            print(e.code)
                            print(e.read())
                Separator()
                a += 1
        Separator('#')
