#!/usr/bin/env python
# -*- coding: utf-8 -*-
import eyed3
from eyed3.id3 import ID3_V2_4
import hashlib
import json
import os
from os.path import expanduser
from slugify import slugify
import pycurl
import re
import sys
import urllib
import urllib2
import json
import itertools

home = expanduser("~")
directory = './'

SAVE_ALL = 0
FORCED_SEARCH = False

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

def DownloadPodcastFile(url,title,description='',current=0,total=0):    
    print url
    url_hash = hashlib.md5()
    url_hash.update(url)
    url_hash = str(url_hash.hexdigest()[0:20])
    target_dir = './'
    # http://www.frazpc.pl/b/280820 - bo z tą literka Ł to jakis wałek
    file_name = slugify(title.replace('ł','l').replace('Ł','L').decode('utf-8'))
    if len(file_name) > 100:
        file_name = file_name[0:97] + "..."
    if len(file_name) == 0:
        file_name = url_hash + ".mp3"
    file_name = file_name + ".mp3"
    print '[' + str(current) + '/' + str(total) + ']'
    print 'Tytuł: ' + title
    print 'Link: ' + url
    print 'Plik: ' + file_name
    if(os.path.isfile(file_name)):
        print '[!] Plik o tej nazwie istnieje w katalogu docelowym'
    else:
        if(Klawisz(SAVE_ALL) == 1):
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
                if(os.path.isfile(file_name)):
                    try:
                        audiofile = eyed3.load(file_name)
                        if audiofile.tag is None:
                            audiofile.tag = eyed3.id3.Tag()
                            audiofile.tag.file_info = eyed3.id3.FileInfo(file_name)
                        comments = u"Url pliku mp3: "+unicode(url)+"\n\n"
                        audiofile.tag.comments.set(comments+u"Pobrane przy pomocy skryptu https://github.com/bohdanbobrowski/pr-dl")
                        audiofile.tag.artist = u"Polskie Radio"
                        audiofile.tag.album = u"polskieradio.pl"
                        audiofile.tag.genre = u"Speech"
                        audiofile.tag.title = unicode(title.decode('utf-8'))
                        audiofile.tag.audio_file_url = url
                        audiofile.tag.track_num = a
                        audiofile.tag.save(version=ID3_V2_4,encoding='utf-8')
                    except:
                        print 'Nie udalo się otagować pliku mp3...'
            except urllib2.HTTPError as e:
                print(e.code)
                print(e.read())

# Parametry podstawowe:
if '-t' in sys.argv or '-T' in sys.argv:
    SAVE_ALL = 1
if '-f' in sys.argv or '-F' in sys.argv:
    FORCED_SEARCH = True

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
        html = www.contents
        
        # 2.1. Ładujemy podstrony:        
        # 2.1.1. Analizujemy linki do podstron
        try:
            tabId =         int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[\s]*([0-9]*),[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', html).group(1))
            boxInstanceId = int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([\s]*([0-9]*),[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', html).group(1))
            sectionId =     int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[\s]*([0-9]*),[0-9\s]*,[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', html).group(1))
            categoryId =    int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[\s]*([0-9]*),[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', html).group(1))
            categoryType =  int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[\s]*([0-9]*), [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', html).group(1))
            queryString =   str(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[\s]*[0-9]*, &quot;&quot;, [0-9]*, &quot;([a-z0-9&;=]*)&quot;', html).group(1)).replace('&amp;','&')
            tagIndexId =    int(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*, &quot;&quot;, ([0-9]*)[a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\)', html).group(1))
            name = str(re.search('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[\s]*[0-9]*, &quot;&quot;, [0-9]*, &quot;[a-z0-9&;=]*&quot;, &quot;([a-zA-Z0-9\s]*)', html).group(1))
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
        except (IndexError,AttributeError):
            analizuj_podstrony = 0

        pages = [] + re.findall('<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\);" class="">[\s]*([0-9]*)', html)        

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

                Podejrzewam że coś z ciastkami albo naglowkami jest nie teges.
                """

        c.close()

        # 2.2. Szukamy pokastów:
        links = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', html)
        titles = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', html)
        descriptions = [] + re.findall('onclick="javascript:playFile\(\'[^\']*\',\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);', html)
        links = links + re.findall('"file":"([^"]*)","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"[^"]*"', html)
        titles = titles + re.findall('"file":"[^"]*","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"([^"]*)"', html)
        descriptions = descriptions + re.findall('"file":"[^"]*","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"[^"]*","desc":"([^"]*)"', html)

        # 2.3. Jeżeli te dwa sposoby nie przyniosły skutku, szukamy raz jeszcze inaczej:
        if(len(links)==0):
            links = re.findall('"file":"([^"]*)"',html)
            titles = re.findall('"title":"([^"]*)"',html)

        # 3. Budujemy listę unikalnych linków:
        download_list = []
        added_links = []
        if(len(links) == len(titles) and len(links) > 0):
            for (x,y) in enumerate(links):
                if links[x] not in added_links:
                    url = links[x]
                    added_links.append(url)
                    if url.find('//static') > -1 and url.find('http://') == -1:
                        url = 'http:'+url
                    if url.find('http://static') == -1:
                        url = 'http://static.polskieradio.pl/'+url+'.mp3'
                    title = titles[x]
                    description = descriptions[x]
                    # Jeżeli tytuł jest pusty szukamy tytułu w źródle raz jeszcze:
                    if title == '':
                        podcast_id = str(url.replace('http://static.polskieradio.pl/','').replace('.mp3',''))
                        if re.search("playFile\('[0-9]*','"+podcast_id+"','','[0-9]*','[0-9a-zA-Z\/]*\,([^']*)",html):
                            podcast_title = re.search("playFile\('[0-9]*','"+podcast_id+"','','[0-9]*','[0-9a-zA-Z\/]*\,([^']*)",html).group(1)
                            title = podcast_title
                        else:
                            title = re.search("<title>([^<^>]*)</title>",html).group(1)
                            title = title.strip() + " " + podcast_id
                    title = urllib2.unquote(title)
                    if title.find('.mp3') > -1:
                        title = urllib2.unquote(description);
                    fname = title
                    title = title.replace('&quot;','"')
                    title = title.replace('""','"')
                    fname = fname.replace('&quot;','')
                    fname = fname.replace('?','')
                    fname = fname.replace('(','')
                    fname = fname.replace(')','')
                    fname = fname.replace(':','_')
                    fname = fname.replace(' ','_')
                    fname = fname.replace('/','_')
                    fname = fname.replace('"','')
                    fname = fname.replace('_-_','-')
                    fname = fname.replace('_-_','-')
                    fname = fname.replace('_-_','-')
                    d_l = {'url':url,'title':title,'description':description,'fname':fname}
                    download_list.append(d_l)

        # 4. Pobieranie:
        print 'Rozpoczynamy pobieranie:'
        Separator()
        a = 1
        for d in download_list:
            if len(d['title']) == 0:
                d['title'] = d['url'].replace('.mp3','')
            DownloadPodcastFile(d['url'],d['title'],d['description'],a,len(download_list))
            Separator()
            a += 1 
        Separator('#')

    else:
        # Jeżeli nie podano bezpośredniego linku staramy się wyszukać słowo kluczowe
        search_params = urllib.quote('offset=0&limit=500&query='+sys.argv[1])
        search_url = 'http://api.polskieradio.pl/netsprint.search?type=radio&params='+search_params        
        wynik = urllib.urlopen(search_url)
        wynik = wynik.read()
        wynik = json.loads(wynik)
        pliki_dodane = []
        pliki = []
        """
        {u'audiolength': u'970', u'description': u'Proces Melchiora Wa\u0144kowicza - komentarz historyka prof. Rafa\u0142a Habielskiego', u'path': u'http://www.polskieradio.pl/ec8014c5-5307-4306-ac85-91814a353fc8.file', u'type': u'Plik d\u017awi\u0119kowy', u'id': 793279, u'name': u'proces melchiora wa\u0144kowicza.mp3'}
        """
        if 'response' in wynik and 'results' in wynik['response'] and len(wynik['response']['results'])>0:
            Separator('#')
            # Najpierw szukam w wynikach plików dźwiekowych
            for w in wynik['response']['results']:
                if 'files' in w:
                    for file in w['files']:
                        if file['name'] not in pliki_dodane and file['type'] == u'Plik dźwiękowy':                            
                            pliki.append(file)

            # "Wzmocnione" szukanie - akceptuj tylko pliki dźwiekowe które w tytule mają szukaną frazę
            if FORCED_SEARCH:
                pliki_sprawdzone = []
                for p in pliki:
                    p['description'] = p['description']
                    if len(p['description']) == 0:
                        p['description'] = p['name'].replace('.mp3','')
                    print p['description']
                    if p['description'].upper().find(sys.argv[1].upper()) > -1:
                        pliki_sprawdzone.append(p)
                pliki = pliki_sprawdzone

            # Zabieram się za Pobieranie
            a = 1
            for p in pliki:
                p['description'] = p['description'].encode('utf-8')
                if len(p['description']) == 0:
                    p['description'] = p['name'].replace('.mp3','').encode('utf-8')
                DownloadPodcastFile(p['path'],p['description'],'',a,len(pliki))
                Separator()
                a += 1 
                                
