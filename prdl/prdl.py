#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from download import download
import eyed3
from eyed3.id3 import ID3_V2_4
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import hashlib
import os
from slugify import slugify
import pycurl
import requests
import re
import urllib
import urllib.request
import json
from clint.textui import puts, colored
from PIL import Image
from bs4 import BeautifulSoup
from lxml.html.soupparser import fromstring


class PrDlPodcast(object):
    def __init__(self, url, title, description='', track_number = 0, thumbnail_url=False):
        self.url = url
        self.title = title
        self.url_hash = self.getUrlHash()
        self.description = BeautifulSoup(description).get_text()
        self.file_name = self.getFileName()
        self.file_size = 0
        self.thumbnail_url = thumbnail_url
        self.thumbnail_delete_after = False
        self.thumbnail_default_fn = self.getDefaultThumbnail()
        self.setThumbnailFileName()
        self.track_number = track_number

    def getUrlHash(self):
        url_hash = hashlib.md5(self.url.encode("utf-8"))
        return str(url_hash.hexdigest()[0:20])

    def getFileName(self):
        file_name = slugify(self.title.replace('ł', 'l').replace('Ł', 'L'))
        if len(file_name) > 100:
            file_name = file_name[0:97] + "..."
        if len(file_name) == 0:
            file_name = self.url_hash + ".mp3"
        file_name = file_name + ".mp3"
        return file_name

    def setThumbnailFileName(self):
        if self.thumbnail_url:
            expr = self.thumbnail_url.split(".")[-1]
            if expr == 'file':
                expr = 'jpg'
            self.thumbnail_mime = 'image/jpeg'
            self.thumbnail_delete_after = True
            self.thumbnail_file_name = self.url_hash + "." + expr
        else:
            self.thumbnail_delete_after = False
            self.thumbnail_file_name = self.thumbnail_default_fn
        

    def getDefaultThumbnail(self):
        self.thumbnail_mime = 'image/jpg'
        tpath = os.path.realpath(__file__).split('/')
        tpath.pop()
        tpath.append('polskieradio_logo_cover.jpg')
        tpath = '/'.join(tpath)
        return tpath

    def downloadThumbnail(self):
        fpath = os.getcwd() + '/' + str(self.thumbnail_file_name).strip()
        if (os.path.isfile(fpath)):
            os.remove(fpath)
        if self.thumbnail_url:
            urllib.request.urlretrieve(self.thumbnail_url, fpath)
            size = (200, 200)
            image = Image.open(fpath)
            image.thumbnail(size, Image.ANTIALIAS)
            background = Image.open(self.thumbnail_default_fn)
            background.paste(
                image, (int((size[0] - image.size[0]) / 2), int((size[1] - image.size[1]) / 2))
            )
            background.save(self.thumbnail_file_name)

    def addThumbnail(self):
        if (os.path.isfile(self.file_name)):
            audio = MP3(self.file_name, ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass
            if (os.path.isfile(self.thumbnail_file_name)):
                thumbf = open(self.thumbnail_file_name, 'rb')
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime=self.thumbnail_mime,
                        type=3,
                        desc='Cover',
                        data=thumbf.read()
                    )
                )
                audio.save()
                if self.thumbnail_delete_after:
                    os.remove(self.thumbnail_file_name)

    def id3tag(self):
        if (os.path.isfile(self.file_name)):
            try:
                audiofile = eyed3.load(self.file_name)
                if audiofile.tag is None:
                    audiofile.tag = eyed3.id3.Tag()
                    audiofile.tag.file_info = eyed3.id3.FileInfo(self.file_name)
                comments = self.description +"\n\n"
                comments += "Url pliku mp3: " + self.url + "\n\n"
                audiofile.tag.comments.set(
                    comments + "Pobrane przy pomocy skryptu https://github.com/bohdanbobrowski/pr-dl")
                audiofile.tag.artist = "Polskie Radio"
                audiofile.tag.album = "polskieradio.pl"
                audiofile.tag.genre = "Speech"
                audiofile.tag.title = self.title
                audiofile.tag.audio_file_url = self.url
                audiofile.tag.track_num = self.track_number
                audiofile.tag.save(version=ID3_V2_4, encoding='utf-8')
            except Exception as error:
                print(error)


class PrDl(object):
    def __init__(self, phrase, save_all = False, forced_search = False):
        self.phrase = phrase.lower()
        self.forced_search = forced_search
        self.save_all = save_all
        self.headers = None

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
        print(separator)

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
        if thumb:
            puts(colored.white('Miniaturka: ' + thumb))
        if (os.path.isfile(podcast.file_name)):
            print("[!] Plik o tej nazwie istnieje w katalogu docelowym")
        else:
            if (self.confirmSave(self.save_all) == 1):
                download(url, './' + podcast.file_name)
                podcast.id3tag()
                podcast.downloadThumbnail()
                podcast.addThumbnail()

    def downloadPodcast(self, podcast, counter=None, length=None):
        if len(podcast['title']) == 0:
            podcast['title'] = podcast['url'].replace('.mp3', '')
        podcast['url'] = podcast['url'].replace('.mp3.mp3', '.mp3')
        self.downloadPodcastFile(podcast['url'], podcast['title'], podcast['description'], counter, length, podcast['thumb'])
        self.drawSeparator()

    def getWebPageContent(self, url):
        response = requests.get(url)
        return response.text


class PrDlSearch(PrDl):

    def getFiles(self, results):
        # Najpierw szukam w responseach plików dźwiekowych
        files = []
        for r in results:
            crawl = PrDlCrawl("https://www.polskieradio.pl{}".format(r['url']), self.save_all)
            files_on_page = crawl.getPodcastsList()
            if r['image']:
                default_thumb = "https:{}".format(r['image'])
                i = 0
                while i < len(files_on_page):
                    if not files_on_page[i]['thumb']:
                        files_on_page[i]['thumb'] = default_thumb
                    i += 1
            if self.forced_search:
                files_after_forced_search = []
                for f in files_on_page:
                    if f['title'].lower() in self.phrase:
                        files_after_forced_search.append(f)
                files = files + files_after_forced_search
            else:
                files = files + files_on_page
        return files

    def _get_search_url(self, page =1):
        search_url = 'https://portalsearch.polskieradio.pl/api/search?pageSize=50&page=' + str(page) + '&query=%' + urllib.parse.quote(self.phrase) + '%22'
        print("Pobieram: {}".format(search_url))
        return search_url

    def downloadPodcastsList(self, podcasts):
        a = 1
        for p in podcasts:
            self.downloadPodcast(p, a, len(podcasts))
            a += 1

    def start(self):
        response = json.loads(urllib.request.urlopen(self._get_search_url()).read())
        pages = round(int(response['count']) / int(response['pageSize']))
        podcasts = self.getFiles(response['results'])
        self.downloadPodcastsList(podcasts)
        if pages > 1:
            for p in range(2, pages):
                print("Strona {} z {}:".format(p, pages))
                response = json.loads(urllib.request.urlopen(self._get_search_url(p)).read())
                podcasts = self.getFiles(response['results'])
                self.downloadPodcastsList(podcasts)


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

    def getThumbnails(self, html_tree):
        thumbs = html_tree.xpath("//img[@id='imgArticleMain']")
        result = []
        for t in thumbs:
            result.append('https:'+t.attrib.get('src'))
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

    def getFilename(self, title):
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
        return fname

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
                    title = urllib.parse.unquote(title)
                    if title.find('.mp3') > -1:
                        title = urllib.parse.unquote(description)
                    fname = self.getFilename(title)
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

    def getPodcasts(self, html_dom):
        podcast = html_dom.xpath("//span[@class='play pr-media-play']")
        result = []
        for p in podcast:
            pdata_media= json.loads(p.attrib.get('data-media'))
            title = urllib.parse.unquote(pdata_media['desc'])
            row = {
                'url': "https:"+pdata_media['file'],
                'title': title,
                'description': title,
                'fname': self.getFilename(title),
                'thumb': None
            }
            result.append(row)
        return result

    def getPodcastsList(self):
        print("Analizowany url: {}".format(self.url))
        html = self.getWebPageContent(self.url)
        html_dom = fromstring(html)
        links = self.getLinks(html)
        titles = self.getTitles(html)
        descriptions = self.getDescriptions(html)
        if (len(links) == 0):
            links = re.findall('"file":"([^"]*)"', html)
            titles = re.findall('"title":"([^"]*)"', html)
        thumbnails = self.getThumbnails(html_dom)
        downloads_list = self.getDownloadsList(links, titles, thumbnails, descriptions, html) + self.getPodcasts(html_dom)
        return downloads_list

    def start(self):
        podcasts_list = self.getPodcastsList()
        a = 1
        for podcast in podcasts_list:
            self.downloadPodcast(podcast, a, len(podcasts_list))
            a += 1
        self.drawSeparator('#')

