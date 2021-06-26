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
import validators
from clint.textui import puts, colored
from PIL import Image
from lxml import etree
import logging


class PrDlLoggingClass(object):

    def __init__(self):
        self.log = logging.getLogger(__name__)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s [%(name)s] - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        self.log.debug("Logger zainicjowany")


class PrDlPodcast(PrDlLoggingClass):

    def __init__(self, podcast, track_number = None):
        self.url = podcast['url']
        self.uid = podcast['uid']
        self.article_url = podcast['article_url']
        self.title = podcast['title']
        self.url_hash = self._getUrlHash()
        self.description = podcast['description']
        self.file_name = self.getFileName()
        self.file_size = 0
        self.thumbnail_url = podcast['thumb']
        self.thumbnail_delete_after = False
        self.thumbnail_default_fn = self.getDefaultThumbnail()
        self.setThumbnailFileName()
        self.track_number = track_number
        super().__init__()

    def _getUrlHash(self):
        url_hash = hashlib.md5(self.url.encode("utf-8")).hexdigest()
        return str(url_hash[0:20])

    def getFileName(self, suffix=''):
        file_name = slugify(self.title.replace('ł', 'l').replace('Ł', 'L'))
        if len(file_name) > 100:
            file_name = file_name[0:100]
        if len(file_name) == 0:
            file_name = self.url_hash
        if suffix:
            file_name = file_name + "_" + str(suffix)
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
            try:
                audio = MP3(self.file_name, ID3=ID3)
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
            except Exception as e:                
                self.log.error(e)

    def id3tag(self):
        if (os.path.isfile(self.file_name)):
            audiofile = eyed3.load(self.file_name)
            if audiofile:
                audiofile.tag = eyed3.id3.Tag()
                audiofile.tag.file_info = eyed3.id3.FileInfo(self.file_name)
                comments = "{}\nUrl artykułu: {}\nUrl pliku mp3: {}\n\nPobrane przy pomocy skryptu https://github.com/bohdanbobrowski/pr-dl".format(
                    self.description,
                    self.article_url,
                    self.url
                )
                audiofile.tag.comments.set(comments)
                audiofile.tag.artist = "Polskie Radio"
                audiofile.tag.album = "polskieradio.pl"
                audiofile.tag.genre = "Speech"
                audiofile.tag.title = self.title
                audiofile.tag.audio_file_url = self.url
                if self.track_number:
                    audiofile.tag.track_num = self.track_number
                audiofile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION,encoding='utf-8')
            else:
                if audiofile is None:
                    os.remove(self.file_name)
                    if os.path.isfile(self.thumbnail_file_name):
                        os.remove(self.thumbnail_file_name)


class PrDl(PrDlLoggingClass):

    def __init__(self, phrase, save_all = False, forced_search = False):
        self.phrase = phrase.lower()
        self.forced_search = forced_search
        self.save_all = save_all
        super().__init__()

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

    def confirmSave(self, answer):
        if (answer == 1):
            return 1
        else:
            puts(colored.red("Czy zapisać podcast? ([t]ak / [n]ie / [z]akoncz)"))
            key = self.getKey()
            if key == 'z' or key == 'Z':
                self.log.info("Przerwano na polecenie użytkownika")
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

    def downloadPodcast(self, podcast, current=0, total=0):
        self.log.debug("Znaleziono podcast [{}/{}]: {}".format(current, podcast, podcast))
        podcast = PrDlPodcast(podcast, track_number=current)
        puts(colored.blue('[' + str(current) + '/' + str(total) + ']'))
        puts(colored.white('Tytuł: ' + podcast.title, bold=True))
        puts(colored.white('Link: ' + podcast.url))
        puts(colored.white('Plik: ' + podcast.file_name))
        if podcast.thumbnail_url:
            puts(colored.white('Miniaturka: ' + podcast.thumbnail_url))
        x = 1
        while os.path.isfile(podcast.file_name):
            podcast.file_name = podcast.getFileName(x)
            x += 1
        else:
            if (self.confirmSave(self.save_all) == 1):
                download(podcast.url, './' + podcast.file_name)
                podcast.id3tag()
                podcast.downloadThumbnail()
                podcast.addThumbnail()

    def getWebPageContent(self, url):
        response = requests.get(url)
        return response.text


class PrDlSearch(PrDl):

    def getFiles(self, results):
        # Najpierw szukam w responseach plików dźwiekowych
        files = {}
        for r in results:
            crawl = PrDlCrawl("https://www.polskieradio.pl{}".format(r['url']), self.save_all)
            files_on_page = crawl.getPodcastsList()
            if r['image']:
                default_thumb = "https:{}".format(r['image'])
                for f in files_on_page:
                    if not files_on_page[f]['thumb']:
                        files_on_page[f]['thumb'] = default_thumb
            for f in files_on_page:
                if not self.forced_search or self.phrase in files_on_page[f]['title'].lower():
                    files[f] = files_on_page[f]
        return files

    def _get_search_url(self, page =1):
        search_url = 'https://portalsearch.polskieradio.pl/api/search?pageSize=50&page=' + str(page) + '&query=%' + urllib.parse.quote(self.phrase.replace(" ", "+")) + '%22'
        self.log.info("Pobieram: {}".format(search_url))
        return search_url

    def downloadPodcastsList(self, podcasts):
        a = 1
        for k in podcasts:
            self.downloadPodcast(podcasts[k], a, len(podcasts))
            a += 1

    def start(self):
        response = json.loads(urllib.request.urlopen(self._get_search_url()).read())
        pages = round(int(response['count']) / int(response['pageSize']))
        podcasts = self.getFiles(response['results'])
        self.downloadPodcastsList(podcasts)
        if pages > 1:
            for p in range(2, pages):
                self.log.info("Strona {} z {}:".format(p, pages))
                response = json.loads(urllib.request.urlopen(self._get_search_url(p)).read())
                podcasts = self.getFiles(response['results'])
                self.downloadPodcastsList(podcasts)


class PrDlCrawl(PrDl):

    def __init__(self, url, save_all = False):
        self.url =  url
        self.save_all = save_all
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.DEBUG)

    def getFilename(self, title):
        fname = title
        title = title.replace('&quot;', '"')
        title = title.replace('""', '"')
        for x in ['&quot;','„','”','…','?','(',')']:
            fname = fname.replace(x, '')
        for y in [':',' ','/','"','.',',']:
            fname = fname.replace(y, '_')
        while '__' in fname:
            fname = fname.replace('__', '_')
        while '_-_' in fname:
            fname = fname.replace('_-_', '-')
        fname = fname.strip('_')
        return fname

    def getArticles(self, html_dom):
        """ Get articles - web page parts, with attached podcasts
        """
        articles = html_dom.xpath("//article")
        articles += html_dom.xpath("//div[contains(@class, 'atarticle')]")
        return articles

    def getThumb(self, html_dom, art):
        thumb = None
        try:
            thumb = "https:"+art.xpath(".//img[contains(@class, 'NoRightBtn')]")[0].get("src")
        except Exception:
            pass
        if thumb is None:
            try:
                thumb = html_dom.xpath(".//span[contains(@class, 'img')]")[0].get("style")
                thumb = thumb.replace('background-image:url(', 'https:')
                thumb = thumb.replace(');', '')
            except Exception:
                pass        
        if thumb and validators.url(thumb):
            return thumb
        else:
            return None

    def getPodcasts(self, html_dom, article_url = ''):                
        result = {}
        html_title = html_dom.xpath("//title")[0].text.strip()
        for art in self.getArticles(html_dom):
            podcast = art.xpath(".//*[@data-media]")
            thumb = self.getThumb(html_dom, art)
            for p in podcast:
                try:
                    pdata_media = json.loads(p.attrib.get('data-media'))
                    uid = hashlib.md5(pdata_media['file'].encode('utf-8')).hexdigest()
                    try:
                        title = art.xpath(".//h1[contains(@class, 'title')]")[0].text.strip()
                        if not title:
                            title = art.xpath(".//h1[contains(@class, 'title')]/a")[0].text.strip()
                    except Exception:
                        title = html_title + " - " + urllib.parse.unquote(pdata_media['title']).strip()                        
                    try:
                        description = urllib.parse.unquote(pdata_media['desc']).strip()
                    except Exception:
                        description = title
                    result[uid] = {
                        'url': "https:" + pdata_media['file'],
                        'uid': uid,
                        'article_url': article_url,
                        'title': title,
                        'description': description,
                        'fname': self.getFilename(title),
                        'thumb': thumb
                    }
                except Exception as e:                    
                    self.log.error(e)        
        return result

    def getPodcastsList(self):
        self.log.info("Analizowany url: {}".format(self.url))
        downloads_list = []
        try:
            html = self.getWebPageContent(self.url)
            downloads_list = self.getPodcasts(etree.HTML(html), self.url)
        except Exception as e:
            self.log.error(e)
        return downloads_list

    def start(self):
        podcasts_list = self.getPodcastsList()
        a = 1
        for k in podcasts_list:
            self.downloadPodcast(podcasts_list[k], a, len(podcasts_list))
            a += 1
