import hashlib
import json
import logging
import os
import pathlib
import urllib
import urllib.request

import eyed3
import requests
import validators
from clint.textui import colored, puts
from download import download
from eyed3.id3.frames import ImageFrame
from lxml import etree
from PIL import Image
from slugify import slugify


class PrDlLoggingClass:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(name)s] - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        self.log.addHandler(ch)


class PrDlPodcast(PrDlLoggingClass):
    def __init__(self, podcast, track_number=None):
        self.url = podcast["url"]
        self.uid = podcast["uid"]
        self.article_url = podcast["article_url"]
        self.title = podcast["title"]
        self.url_hash = self._getUrlHash()
        self.description = podcast["description"]
        self.file_name = self.get_filename()
        self.file_size = 0
        self.thumbnail_url = podcast["thumb"]
        self.thumbnail_delete_after = False
        self.thumbnail_default_fn = self.get_default_thumbnail()
        self.set_thumbnail_file_name()
        self.track_number = track_number
        super().__init__()

    def _getUrlHash(self):
        url_hash = hashlib.md5(self.url.encode("utf-8")).hexdigest()
        return url_hash[0:20]

    def get_filename(self, suffix=""):
        file_name = slugify(self.title.replace("ł", "l").replace("Ł", "L"))
        if len(file_name) > 100:
            file_name = file_name[0:100]
        if len(file_name) == 0:
            file_name = self.url_hash
        if suffix:
            file_name = file_name + "_" + str(suffix)
        file_name = file_name + ".mp3"
        return file_name

    def set_thumbnail_file_name(self):
        if self.thumbnail_url:
            expr = self.thumbnail_url.split(".")[-1]
            if expr.find("?"):
                expr = expr.split("?")[0]
            if expr == "file":
                expr = "jpg"
            self.thumbnail_mime = "image/jpeg"
            self.thumbnail_delete_after = True
            self.thumbnail_file_name = self.url_hash + "." + expr
        else:
            self.thumbnail_delete_after = False
            self.thumbnail_file_name = self.thumbnail_default_fn

    def get_default_thumbnail(self):
        self.thumbnail_mime = "image/jpg"
        thumbnail_path = pathlib.Path(__file__).parent.resolve()
        return os.path.join(thumbnail_path, "polskieradio_logo_cover.jpg")

    def download_thumbnail(self):
        fpath = os.getcwd() + "/" + str(self.thumbnail_file_name).strip()
        if os.path.isfile(fpath):
            os.remove(fpath)
        if self.thumbnail_url:
            urllib.request.urlretrieve(self.thumbnail_url, fpath)
            size = (200, 200)
            image = Image.open(fpath)
            image.thumbnail(size, Image.LANCZOS)
            background = Image.open(self.thumbnail_default_fn)
            background.paste(
                image,
                (
                    int((size[0] - image.size[0]) / 2),
                    int((size[1] - image.size[1]) / 2),
                ),
            )
            background.save(self.thumbnail_file_name)

    def add_thumbnail(self):
        if os.path.isfile(self.file_name):
            if os.path.isfile(self.thumbnail_file_name):
                audio = eyed3.load(self.file_name)
                if audio.tag is None:
                    audio.initTag()

                audio.tag.images.set(
                    ImageFrame.FRONT_COVER,
                    open(self.thumbnail_file_name, "rb").read(),
                    self.thumbnail_mime,
                )
                audio.tag.save()

                if self.thumbnail_delete_after:
                    os.remove(self.thumbnail_file_name)

    def id3tag(self):
        if os.path.isfile(self.file_name):
            audiofile = eyed3.load(self.file_name)
            if audiofile:
                audiofile.tag = eyed3.id3.Tag()
                audiofile.tag.file_info = eyed3.id3.FileInfo(self.file_name)
                comments = f"{self.description}\nUrl artykułu: {self.article_url}\nUrl pliku mp3: {self.url}\n\nPobrane przy pomocy skryptu https://github.com/bohdanbobrowski/pr-dl"
                audiofile.tag.comments.set(comments)
                audiofile.tag.artist = "Polskie Radio"
                audiofile.tag.album = "polskieradio.pl"
                audiofile.tag.genre = "Speech"
                audiofile.tag.title = self.title
                audiofile.tag.audio_file_url = self.url
                if self.track_number:
                    audiofile.tag.track_num = self.track_number
                audiofile.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding="utf-8")
            else:
                if audiofile is None:
                    os.remove(self.file_name)
                    if os.path.isfile(self.thumbnail_file_name):
                        os.remove(self.thumbnail_file_name)


class PrDl(PrDlLoggingClass):
    def __init__(self):
        super().__init__()
        self.phrase: str = ""
        self.forced_search: bool = False
        self.save_all: bool = False

    @staticmethod
    def get_key():
        if os.name == "nt":
            from msvcrt import getch

            ch = getch()
        else:
            import sys
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def confirm_save(self) -> bool:
        puts(colored.red("Czy zapisać podcast? ([t]ak / [n]ie / [z]akoncz)"))
        key = self.get_key().decode()
        if key in ["z", "Z"]:
            self.log.info("Przerwano na polecenie użytkownika")
            exit()
        if key in ["t", "T", "y", "Y"]:
            return True
        else:
            return False

    @staticmethod
    def get_resource_path(rel_path):
        dir_of_py_file = os.path.dirname(__file__)
        rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
        abs_path_to_resource = os.path.abspath(rel_path_to_resource)
        return abs_path_to_resource

    def download_podcast(self, podcast, current=0, total=0):
        self.log.debug(f"Znaleziono podcast [{current}/{podcast}]: {podcast}")
        podcast = PrDlPodcast(podcast, track_number=current)
        puts(colored.blue("[" + str(current) + "/" + str(total) + "]"))
        puts(colored.white("Tytuł: " + podcast.title, bold=True))
        puts(colored.white("Link: " + podcast.url))
        puts(colored.white("Plik: " + podcast.file_name))
        if podcast.thumbnail_url:
            puts(colored.white("Miniaturka: " + podcast.thumbnail_url))
        x = 1
        while os.path.isfile(podcast.file_name):
            podcast.file_name = podcast.get_filename(x)
            x += 1
        else:
            if self.save_all or self.confirm_save():
                try:
                    download(podcast.url, "./" + podcast.file_name)
                    podcast.id3tag()
                    podcast.download_thumbnail()
                    podcast.add_thumbnail()
                except RuntimeError as e:
                    self.log.error(e)

    def get_web_page_content(self, url):
        response = requests.get(url)
        return response.text


class PrDlSearch(PrDl):
    def __init__(self, phrase, save_all=False, forced_search=False):
        super().__init__()
        self.phrase = phrase.lower()
        self.forced_search = forced_search
        self.save_all = save_all

    def get_files(self, results):
        # Najpierw szukam w responseach plików dźwiekowych
        files = {}
        for r in results:
            crawl = PrDlCrawl("https://www.polskieradio.pl{}".format(r["url"]), self.save_all)
            files_on_page = crawl.get_podcasts_list()
            if r["image"]:
                default_thumb = "https:{}".format(r["image"])
                for f in files_on_page:
                    if not files_on_page[f]["thumb"]:
                        files_on_page[f]["thumb"] = default_thumb
            for f in files_on_page:
                if not self.forced_search or self.phrase in files_on_page[f]["title"].lower():
                    files[f] = files_on_page[f]
        return files

    def _get_search_url(self, page=1):
        search_url = (
            "https://portalsearch.polskieradio.pl/api/search?pageSize=50&page="
            + str(page)
            + "&query=%"
            + urllib.parse.quote(self.phrase.replace(" ", "+"))
            + "%22"
        )
        self.log.info(f"Pobieram: {search_url}")
        return search_url

    def download_podcasts_list(self, podcasts):
        a = 1
        for k in podcasts:
            self.download_podcast(podcasts[k], a, len(podcasts))
            a += 1

    def start(self):
        response = json.loads(urllib.request.urlopen(self._get_search_url()).read())
        pages = round(int(response["count"]) / int(response["pageSize"]))
        podcasts = self.get_files(response["results"])
        self.download_podcasts_list(podcasts)
        if pages > 1:
            for p in range(2, pages):
                self.log.info(f"Strona {p} z {pages}:")
                response = json.loads(urllib.request.urlopen(self._get_search_url(p)).read())
                podcasts = self.get_files(response["results"])
                self.download_podcasts_list(podcasts)


class PrDlCrawl(PrDl):
    def __init__(self, url: str, save_all: bool):
        super().__init__()
        self.url = url
        self.save_all = save_all
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.DEBUG)

    @staticmethod
    def get_filename(title):
        for x in ["&quot;", "„", "”", "…", "?", "(", ")"]:
            title = title.replace(x, "")
        for y in [":", " ", "/", '"', ".", ","]:
            title = title.replace(y, "_")
        while "__" in title:
            title = title.replace("__", "_")
        while "_-_" in title:
            title = title.replace("_-_", "-")
        title = title.strip("_")
        return title

    @staticmethod
    def get_articles(html_dom):
        """Get articles - web page parts, with attached podcasts"""
        articles = html_dom.xpath("//article")
        articles += html_dom.xpath("//div[contains(@class, 'atarticle')]")
        return articles

    @staticmethod
    def get_thumb(html_dom, art):
        thumb = None
        try:
            thumb = "https:" + art.xpath(".//img[contains(@class, 'NoRightBtn')]")[0].get("src")
        except IndexError:
            pass
        if thumb is None:
            try:
                thumb = html_dom.xpath(".//span[contains(@class, 'img')]")[0].get("style")
                thumb = thumb.replace("background-image:url(", "https:")
                thumb = thumb.replace(");", "")
            except (IndexError, AttributeError):
                pass
        if thumb and validators.url(thumb):
            thumb = thumb.removesuffix("?format=500")
            return thumb
        else:
            return None

    def get_podcasts(self, html_dom, article_url=""):
        result = {}
        html_title = html_dom.xpath("//title")[0].text.strip()
        for art in self.get_articles(html_dom):
            podcast = art.xpath(".//*[@data-media]")
            thumb = self.get_thumb(html_dom, art)
            for p in podcast:
                try:
                    pdata_media = json.loads(p.attrib.get("data-media"))
                    uid = hashlib.md5(pdata_media["file"].encode("utf-8")).hexdigest()
                    try:
                        title = art.xpath(".//h1[contains(@class, 'title')]")[0].text.strip()
                        if not title:
                            title = art.xpath(".//h1[contains(@class, 'title')]/a")[0].text.strip()
                    except IndexError:
                        title = html_title + " - " + urllib.parse.unquote(pdata_media["title"]).strip()
                    try:
                        description = urllib.parse.unquote(pdata_media["desc"]).strip()
                    except IndexError:
                        description = title
                    podcast = {
                        "url": "https:" + pdata_media["file"],
                        "uid": uid,
                        "article_url": article_url,
                        "title": title,
                        "description": description,
                        "fname": self.get_filename(title),
                        "thumb": thumb,
                    }
                    if uid not in result:
                        result[uid] = podcast
                except Exception as e:
                    self.log.error(e)
        return result

    def get_podcasts_list(self):
        self.log.info(f"Analizowany url: {self.url}")
        html = self.get_web_page_content(self.url)
        downloads_list = self.get_podcasts(etree.HTML(html), self.url)
        return downloads_list

    def start(self):
        podcasts_list = self.get_podcasts_list()
        a = 1
        for k in podcasts_list:
            self.download_podcast(podcasts_list[k], a, len(podcasts_list))
            a += 1
