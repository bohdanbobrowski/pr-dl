import hashlib
import json
import logging
import os
import pathlib
import re
import urllib
import urllib.request

import eyed3  # type: ignore
import requests
import validators
from clint.textui import colored, puts  # type: ignore
from dlbar import DownloadBar  # type: ignore
from eyed3.id3.frames import ImageFrame  # type: ignore
from lxml import etree
from PIL import Image
from slugify import slugify

from prdl.kbhit import KBHit

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(name)s] - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


class LoggingClass:
    def __init__(self):
        self.logger = logger


class PrDlPodcast(LoggingClass):
    def __init__(
        self,
        article_url: str,
        description: str,
        file_name: str,
        thumb: str,
        title: str,
        uid: str,
        url: str,
        track_number=None,
    ):
        super().__init__()
        self.url: str = str(url)
        self.uid: str = uid
        self.article_url: str = article_url
        self.title: str = title
        self.description: str = description
        self.file_name = self.get_filename()
        self.file_size = 0
        self.thumbnail_url = thumb
        self.thumbnail_delete_after = False
        self.thumbnail_default_fn = self.get_default_thumbnail()
        self.thumbnail_file_name = ""
        self.thumbnail_mime = "image/jpg"
        self.set_thumbnail_file_name()
        self.track_number = track_number
        super().__init__()

    @property
    def url_hash(self) -> str:
        return hashlib.md5(self.url.encode()).hexdigest()

    def __hash__(self):
        return hash(self.url_hash)

    def __eq__(self, other):
        return self.url_hash == other.url_hash

    def __str__(self):
        return self.url

    def get_filename(self, file_name: str = "", suffix=""):
        if file_name == "":
            file_name = slugify(self.title.replace("ł", "l").replace("Ł", "L"))
        if len(file_name) > 100:
            file_name = file_name[0:100]
        if len(file_name) == 0:
            file_name = self.url_hash
        if suffix:
            file_name = file_name + "_" + str(suffix)
        if not file_name.endswith(".mp3"):
            file_name = file_name + ".mp3"
        return file_name

    def set_thumbnail_file_name(self):
        if self.thumbnail_url:
            expr = self.thumbnail_url.split(".")[-1]
            if expr.find("?"):
                expr = expr.split("?")[0]
            if expr == "file":
                expr = "jpg"
            self.thumbnail_delete_after = True
            self.thumbnail_file_name = self.url_hash + "." + expr
        else:
            self.thumbnail_delete_after = False
            self.thumbnail_file_name = self.thumbnail_default_fn

    @staticmethod
    def get_default_thumbnail() -> str:
        return os.path.join(pathlib.Path(__file__).parent.resolve(), "prdl_logo.jpg")

    def download_thumbnail(self):
        fpath = os.getcwd() + "/" + str(self.thumbnail_file_name).strip()
        if os.path.isfile(fpath):
            os.remove(fpath)
        if self.thumbnail_url:
            urllib.request.urlretrieve(self.thumbnail_url, fpath)
            size = (500, 500)
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


class PrDl(LoggingClass):
    def __init__(self, phrase: str = "", forced_search: bool = False, save_all: bool = False):
        super().__init__()
        self.phrase: str = phrase
        self.forced_search: bool = forced_search
        self.save_all: bool = save_all

    def confirm_save(self) -> bool:
        kb = KBHit()
        puts(colored.red("Save? ([y]es / [n]o / [q]uit)"))
        key = kb.getch()
        if key == "q":
            self.logger.info("Good bye.")
            exit()
        if key in ["y"]:
            return True
        return False

    @staticmethod
    def get_resource_path(rel_path):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), rel_path))

    def download_podcast(self, podcast: PrDlPodcast, current=0, total=0):
        self.logger.debug(f"Podcast found [{current}/{podcast}]: {podcast}")
        puts(colored.blue("[" + str(current) + "/" + str(total) + "]"))
        puts(colored.white(f"Title: {podcast.title}", bold=True))
        puts(colored.white(f"Url: {podcast.url} ({podcast.__hash__()})"))
        puts(colored.white(f"File: {podcast.file_name}"))
        if podcast.thumbnail_url:
            puts(colored.white("Thubnail: " + podcast.thumbnail_url))
        x = 1
        while os.path.isfile(podcast.file_name):
            podcast.file_name = podcast.get_filename(suffix=str(x))
            x += 1
        else:
            if self.save_all or self.confirm_save():
                download_bar = DownloadBar()
                download_bar.download(url=podcast.url, dest=podcast.file_name, title=f"Downloading {podcast.file_name}")
                podcast.id3tag()
                podcast.download_thumbnail()
                podcast.add_thumbnail()

    @staticmethod
    def get_web_page_content(url):
        response = requests.get(url)
        return response.text


class PrDlSearch(PrDl):
    def __init__(self, phrase, save_all=False, forced_search=False):
        super().__init__()
        self.phrase = phrase.lower()
        self.forced_search = forced_search
        self.save_all = save_all

    def get_files(self, results) -> list[PrDlPodcast]:
        files = []
        for r in results:
            self.logger.info(f"Analyzing: {r['url']}")
            crawler = PrDlCrawl(
                url=f"https://www.polskieradio.pl{r['url']}",
                save_all=self.save_all,
            )
            for f in crawler.get_podcasts_list():
                if r["image"]:
                    default_thumb = f"https:{r['image']}"
                    if not f.thumbnail_file_name:
                        f.thumbnail_file_name = default_thumb
                if not self.forced_search or self.phrase in f.title.lower():
                    files.append(f)
        return list(set(files))

    def _get_search_url(self, page=1):
        search_url = (
            "https://portalsearch.polskieradio.pl/api/search?pageSize=50&page="
            + str(page)
            + "&query=%"
            + urllib.parse.quote(self.phrase.replace(" ", "+"))
            + "%22"
        )
        self.logger.info(f"Downloading: {search_url}")
        return search_url

    def download_podcasts_list(self, podcasts: list[PrDlPodcast]):
        a = 1
        for p in podcasts:
            self.download_podcast(p, a, len(podcasts))
            a += 1

    def start(self):
        response = json.loads(urllib.request.urlopen(self._get_search_url()).read())
        pages = round(int(response["count"]) / int(response["pageSize"]))
        podcasts_list = self.get_files(response["results"])
        self.download_podcasts_list(podcasts_list)
        if pages > 1:
            for p in range(2, pages):
                self.logger.info(f"Page {p}/{pages}:")
                response = json.loads(urllib.request.urlopen(self._get_search_url(p)).read())
                podcasts = self.get_files(response["results"])
                self.download_podcasts_list(podcasts)


class PrDlCrawl(PrDl):
    def __init__(self, url: str, save_all: bool):
        super().__init__()
        self.url = url
        self.save_all = save_all
        self.logger.setLevel(logging.DEBUG)

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

    @staticmethod
    def get_occurrences(pattern: str, data) -> list[int]:
        return [match.start() for match in re.finditer(pattern, data)]

    @staticmethod
    def get_podcasts_v2(page_data: str, url: str = "") -> list[PrDlPodcast]:
        data = None
        podcasts_list = []
        for keyword in ["podcasts", "podcastEpisodes"]:
            for page_data_part in page_data.split(f'\\"{keyword}\\":')[1:]:
                page_data_part = page_data_part.replace('\\"', '"')
                page_data_part = page_data_part.replace('\\\\"', "")
                page_data_part = page_data_part.replace(":null,", ':"",')
                for position in PrDlCrawl.get_occurrences("]", page_data_part):
                    data_json = page_data_part[: position + 1]
                    try:
                        data_part = json.loads(data_json)
                        if data is None:
                            data = data_part
                        else:
                            data = data + data_part
                        break
                    except json.decoder.JSONDecodeError:
                        pass
        if data is None and page_data.find('{"props":{"pageProps":{"data":') > -1:
            page_data_part = page_data.split('{"props":')[1]
            for position in PrDlCrawl.get_occurrences("}", page_data_part):
                data_json = page_data_part[: position + 1]
                try:
                    data_part = json.loads(data_json)
                    podcast_dict = {
                        "article_url": url,
                        "title": data_part.get("pageProps", {}).get("data", {}).get("articleData", {}).get("title", []),
                        "file_name": data_part.get("pageProps", {})
                        .get("data", {})
                        .get("articleData", {})
                        .get("title", []),
                    }
                    for attachment in (
                        data_part.get("pageProps", {}).get("data", {}).get("articleData", {}).get("attachments", [])
                    ):
                        if attachment.get("fileType") == "Audio":
                            podcast_dict["url"] = attachment.get("file")
                            podcast_dict["uid"] = attachment.get("fileUid")
                            podcast_dict["description"] = attachment.get("description")
                        if attachment.get("fileType") == "Image":
                            podcast_dict["thumb"] = attachment.get("file")
                    try:
                        podcasts_list.append(PrDlPodcast(**podcast_dict))
                    except TypeError:
                        pass
                except json.decoder.JSONDecodeError:
                    pass
        track_number = 0
        if data:
            for podcast in data:
                podcasts_list.append(
                    PrDlPodcast(
                        article_url=url,
                        description=podcast.get("description", ""),
                        file_name=podcast.get("title"),
                        thumb=podcast.get("coverUrl", podcast.get("imageUrl")),
                        title=podcast.get("title"),
                        uid=podcast.get("id"),
                        url=podcast.get("url"),
                        track_number=track_number,
                    )
                )
                track_number += 1
        return podcasts_list

    def get_podcasts(self, html_dom, article_url="") -> list[PrDlPodcast]:
        podcasts_list = []
        html_title = html_dom.xpath("//title")[0].text.strip()
        for art in self.get_articles(html_dom):
            podcast = art.xpath(".//*[@data-media]")
            thumb = self.get_thumb(html_dom, art)
            for p in podcast:
                try:
                    pdata_media = json.loads(p.attrib.get("data-media"))
                    uid = hashlib.md5(pdata_media["file"].encode()).hexdigest()
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
                        "file_name": self.get_filename(title),
                        "thumb": thumb,
                    }
                    podcasts_list.append(PrDlPodcast(**podcast))
                except Exception as e:
                    self.logger.error(e)
        return podcasts_list

    def get_podcasts_list(self) -> list[PrDlPodcast]:
        html = self.get_web_page_content(self.url)
        downloads_list = self.get_podcasts_v2(html, self.url)
        if not downloads_list:
            downloads_list = self.get_podcasts(etree.HTML(html), self.url)
        return list(set(downloads_list))

    def start(self):
        podcasts_list = self.get_podcasts_list()
        self.logger.info(len(podcasts_list))
        podcasts_list = list(set(podcasts_list))
        self.logger.info(len(podcasts_list))
        a = 1
        for podcast_episode in podcasts_list:
            self.download_podcast(podcast_episode, a, len(podcasts_list))
            a += 1
