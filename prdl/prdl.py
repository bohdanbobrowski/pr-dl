#!/usr/bin/env python
# -*- coding: utf-8 -*-

import eyed3
from eyed3.id3 import ID3_V2_4
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import hashlib
import os
from slugify import slugify
import pycurl
import re
import sys
import urllib
import urllib2
import json
import traceback
from clint.textui import puts, colored
from PIL import Image


class PrDlPodcast(object):
    def __init__(self, url, title, description='', track_number = 0, thumbnail_url=False):
        self.url = url
        self.title = title
        self.url_hash = self.getUrlHash()
        self.description = description
        self.file_name = self.getFileName()
        self.file_size = 0
        self.thumbnail_url = thumbnail_url
        self.thumbnail_delete_after = False
        self.setThumbnailFileName()
        self.track_number = track_number


    def getUrlHash(self):
        url_hash = hashlib.md5()
        url_hash.update(self.url)
        return str(url_hash.hexdigest()[0:20])

    def getFileName(self):
        file_name = slugify(self.title.replace('ł', 'l').replace('Ł', 'L').decode('utf-8'))
        if len(file_name) > 100:
            file_name = file_name[0:97] + "..."
        if len(file_name) == 0:
            file_name = self.url_hash + ".mp3"
        file_name = file_name + ".mp3"
        return file_name

    def setThumbnailFileName(self):
        if self.thumbnail_url:
            expr = self.thumbnail_url.split(".")[-1]
            self.thumbnail_mime = 'image/jpeg'
            self.thumbnail_delete_after = True
            self.thumbnail_file_name = self.url_hash + "." + expr
        else:
            self.thumbnail_mime = 'image/png'

            self.thumbnail_file_name = os.path.realpath(__file__).replace('prdl-cli.py', 'polskieradio_logo_cover.png')

    def downloadThumbnail(self):
        print self.thumbnail_url
        print self.thumbnail_file_name
        fpath = os.path.realpath(__file__).replace('prdl-cli.py', self.thumbnail_file_name)
        print fpath
        if (os.path.isfile(fpath)):
            os.remove(fpath)
        urllib.urlretrieve(self.thumbnail_url, fpath)
        print os.path.isfile(fpath)
        image = Image.open(fpath)
        image = image.crop((82, 0, 282, 200))
        image.save(self.thumbnail_file_name)

    def addThumbnail(self):
        if (os.path.isfile(self.file_name)):
            audio = MP3(self.file_name, ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass
            if (os.path.isfile(self.thumbnail_file_name)):
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime=self.thumbnail_mime,
                        type=3,
                        desc=u'Cover',
                        data=open(self.thumbnail_file_name).read()
                    )
                )
                audio.save()
                if self.thumbnail_delete_after:
                    os.remove(self.thumbnail_file_name)

    def download(self):
        try:
            remote = urllib2.urlopen(self.url)
            file = open(self.file_name, 'wb')
            meta = remote.info()
            self.file_size = int(meta.getheaders("Content-Length")[0])
            print("Pobieranie: {0} Rozmiar: {1}".format(self.url, self.file_size))
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = remote.read(block_sz)
                if not buffer:
                    break
                file_size_dl += len(buffer)
                file.write(buffer)
                p = float(file_size_dl) / self.file_size
                status = r"{0}  [{1:.2%}]".format(file_size_dl, p)
                status = status + chr(8) * (len(status) + 1)
                sys.stdout.write(status)
            file.close()
            return True
        except urllib2.HTTPError as error:
            print(error.code)
            print(error.read())
            return False

    def id3tag(self):
        if (os.path.isfile(self.file_name)):
            try:
                audiofile = eyed3.load(self.file_name)
                if audiofile.tag is None:
                    audiofile.tag = eyed3.id3.Tag()
                    audiofile.tag.file_info = eyed3.id3.FileInfo(self.file_name)
                comments = self.description +"\n\n"
                comments += u"Url pliku mp3: " + unicode(self.url) + "\n\n"
                audiofile.tag.comments.set(
                    comments + u"Pobrane przy pomocy skryptu https://github.com/bohdanbobrowski/pr-dl")
                audiofile.tag.artist = u"Polskie Radio"
                audiofile.tag.album = u"polskieradio.pl"
                audiofile.tag.genre = u"Speech"
                audiofile.tag.title = unicode(self.title.decode('utf-8'))
                audiofile.tag.audio_file_url = self.url
                audiofile.tag.track_num = self.track_number
                audiofile.tag.save(version=ID3_V2_4, encoding='utf-8')
            except Exception as error:
                print 'Nie udalo się otagować pliku mp3...'
            traceback.print_exc()


class PrDl(object):
    def getKey(self):
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

    def drawSeparator(self, sign='-'):
        rows, columns = os.popen('stty size', 'r').read().split()
        columns = int(columns)
        separator = ''
        for x in range(0, columns):
            separator = separator + sign
        print separator

    def confirmSave(self, answer):
        if (answer == 1):
            return 1
        else:
            puts(colored.red("Czy zapisać podcast? ([t]ak / [n]ie / [z]akoncz)"))
            key = self.getKey()
            if key == 'z' or key == 'Z':
                self.drawSeparator('#')
                exit()
            if key == 't' or key == 'T':
                return 1
            else:
                return 0

    def get_resource_path(self, rel_path):
        dir_of_py_file = os.path.dirname(__file__)
        rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
        abs_path_to_resource = os.path.abspath(rel_path_to_resource)
        return abs_path_to_resource

    def downloadPodcastFile(self, url, title, description='', current=0, total=0, thumb=""):
        podcast = PrDlPodcast(url, title, description='', track_number=current, thumbnail_url=thumb)
        puts(colored.blue('[' + str(current) + '/' + str(total) + ']'))
        puts(colored.white('Tytuł: ' + title, bold=True))
        puts(colored.white('Link: ' + url))
        puts(colored.white('Plik: ' + podcast.file_name))
        if thumb != "":
            puts(colored.white('Miniaturka: ' + thumb))
        if (os.path.isfile(podcast.file_name)):
            print '[!] Plik o tej nazwie istnieje w katalogu docelowym'
        else:
            if (self.confirmSave(self.save_all) == 1):
                podcast.download()
                podcast.id3tag()
                podcast.downloadThumbnail()
                podcast.addThumbnail()

    def getWebPageContent(self, url):
        www = PageDownloader()
        c = pycurl.Curl()
        c.setopt(c.URL, sys.argv[1])
        c.setopt(c.WRITEFUNCTION, www.body_callback)
        c.setopt(c.HEADER, 1);
        c.setopt(c.HTTPHEADER, self.headers)
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.USERAGENT, 'Mozilla/5.0 (X11; U; Linux i686; pl; rv:1.8.0.3) Gecko/20060426 Firefox/1.5.0.3')
        c.setopt(c.REFERER, sys.argv[1])
        c.setopt(c.COOKIEFILE, '')
        c.perform()
        c.close()
        return www.contents


class PrDlSearch(PrDl):
    def __init__(self, phrase, save_all = False, forced_search = False):
        self.phrase = phrase
        self.search_str = unicode(phrase.decode('utf-8').upper())
        self.forced_search = forced_search
        self.save_all = save_all

    def getFiles(self, response):
        files = []
        files_dodane = []
        # Najpierw szukam w responseach plików dźwiekowych
        for w in response['response']['results']:
            if 'files' in w:
                for file in w['files']:
                    if file['name'] not in files_dodane and file['type'] == u'Plik dźwiękowy':
                        files.append(file)
        # "Wzmocnione" szukanie - akceptuj tylko files dźwiekowe które w tytule mają szukaną frazę
        if self.forced_search:
            files_checked = []
            for p in files:
                p['description'] = p['description']
                if len(p['description']) == 0:
                    p['description'] = p['name'].replace('.mp3', '')
                description = unicode(p['description'].upper())
                if description.find(self.search_str) > -1:
                    files_checked.append(p)
            files = files_checked
        return files

    def start(self):
        search_url = 'http://apipr.polskieradio.pl/api/elasticArticles?sort_by=date&sort_order=desc&offset=0&limit=500&query=' + urllib.quote(self.phrase)
        response = urllib.urlopen(search_url)
        response = response.read()
        response = json.loads(response)
        if 'response' in response and 'results' in response['response'] and len(response['response']['results']) > 0:
            self.drawSeparator('#')
            files = self.getFiles(response)
            a = 1
            for p in files:
                p['description'] = p['description'].encode('utf-8').strip()
                if len(p['description']) == 0:
                    p['description'] = p['name'].replace('.mp3', '').encode('utf-8')
                p['path'] = p['path'].replace('.mp3.mp3', '.mp3')
                self.downloadPodcastFile(p['path'], p['description'], '', a, len(files))
                self.drawSeparator()
                a += 1

class PrDlCrawl(PrDl):
    def __init__(self, url, save_all = False):
        self.url =  url
        self.save_all = save_all
        self.headers = ['Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language: pl,en-us;q=0.7,en;q=0.3', 'Accept-Charset: ISO-8859-2,utf-8;q=0.7,*;q=0.7',
           'Content-Type: application/x-www-form-urlencoded']

    def getPages(self, html):
        return [] + re.findall(
            '<a[a-z\="\s]*onclick="[a-zA-Z\_]*LoadTab\([0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*,[0-9\s]*, [a-z0-9&;,=\s]*[\s]*[a-zA-z\s]*&quot;, &quot;True&quot;,[0-9\s]*,[0-9\s\-]*[\', &quot;False&quot;\']*,[0-9\s]*\);" class="">[\s]*([0-9]*)',
            html
        )

    def getLinks(self, html):
        links = [] + re.findall(
            'onclick="javascript:playFile\(\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);',
            html
        )
        links += re.findall(
            '"file":"([^"]*)","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"[^"]*"',
            html
        )
        return links

    def getTitles(self, html):
        titles = [] + re.findall(
            'onclick="javascript:playFile\(\'[^\']*\',\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);',
            html
        )
        titles += re.findall(
            '"file":"[^"]*","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"([^"]*)"',
            html
        )
        return titles

    def getDescriptions(self, html):
        descr = [] + re.findall(
            'onclick="javascript:playFile\(\'[^\']*\',\'[^\']*\',\'([^\']*)\',\'[^\']*\',\'[^\']*\',\'1\',\'[^\']*\'\);',
        html)
        descr += re.findall(
            '"file":"[^"]*","provider":"audio","uid":"[^"]*","length":[0-9]*,"autostart":[a-z]*,"link":"[^"]*","title":"[^"]*","desc":"([^"]*)"',
            html
        )
        return descr

    def getThumbnails(self, html):
        regex = 'id="imgArticleMain" src=.([^"\']*)'
        thumbs = re.findall(regex, html)
        result = []
        for thumb in thumbs:
            result.append('https:' + thumb)
        return result

    def fillEmptyTitle(self, title, url, html):
        if title == '':
            podcast_id = str(url.replace('http://static.polskieradio.pl/', '').replace('.mp3', ''))
            if re.search(
                    "playFile\('[0-9]*','" + podcast_id + "','','[0-9]*','[0-9a-zA-Z\/]*\,([^']*)",
                    html):
                title = re.search(
                    "playFile\('[0-9]*','" + podcast_id + "','','[0-9]*','[0-9a-zA-Z\/]*\,([^']*)",
                    html).group(1)
            else:
                title = re.search("<title>([^<^>]*)</title>", html).group(1)
                title = title.strip() + " " + podcast_id
        return title

    def getDownloadsList(self, links, titles, thumbnails, descriptions, html):
        downloads_list = []
        added_links = []
        if (len(links) == len(titles) and len(links) > 0):
            for (x, y) in enumerate(links):
                if links[x] not in added_links:
                    url = links[x]
                    added_links.append(url)
                    if url.find('//static') > -1 and url.find('http://') == -1:
                        url = 'http:' + url
                    if url.find('http://static') == -1:
                        url = 'http://static.polskieradio.pl/' + url + '.mp3'
                    title = titles[x]
                    description = descriptions[x]
                    title = self.fillEmptyTitle(title, url, html)
                    title = urllib2.unquote(title)
                    if title.find('.mp3') > -1:
                        title = urllib2.unquote(description);
                    fname = title
                    title = title.replace('&quot;', '"')
                    title = title.replace('""', '"')
                    fname = fname.replace('&quot;', '')
                    fname = fname.replace('?', '')
                    fname = fname.replace('(', '')
                    fname = fname.replace(')', '')
                    fname = fname.replace(':', '_')
                    fname = fname.replace(' ', '_')
                    fname = fname.replace('/', '_')
                    fname = fname.replace('"', '')
                    fname = fname.replace('_-_', '-')
                    fname = fname.replace('_-_', '-')
                    fname = fname.replace('_-_', '-')
                    row = {
                        'url': url,
                        'title': title,
                        'description': description,
                        'fname': fname
                    }
                    try:
                        row["thumb"] = thumbnails[(x/2)]
                    except Exception:
                        row["thumb"] = ""
                    downloads_list.append(row)
        return downloads_list

    def start(self):
        self.drawSeparator('#')
        print "Analizowany url: " + self.url
        html = self.getWebPageContent(self.url)
        links = self.getLinks(html)
        titles = self.getTitles(html)
        descriptions = self.getDescriptions(html)
        if (len(links) == 0):
            links = re.findall('"file":"([^"]*)"', html)
            titles = re.findall('"title":"([^"]*)"', html)
        thumbnails = self.getThumbnails(html)
        downloads_list = self.getDownloadsList(links, titles, thumbnails, descriptions, html)
        self.drawSeparator()
        a = 1
        for d in downloads_list:
            if len(d['title']) == 0:
                d['title'] = d['url'].replace('.mp3', '')
            d['url'] = d['url'].replace('.mp3.mp3', '.mp3')
            self.downloadPodcastFile(d['url'], d['title'], d['description'], a, len(downloads_list), d['thumb'])
            self.drawSeparator()
            a += 1
        self.drawSeparator('#')


class PageDownloader:
    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + buf
