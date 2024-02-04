import asyncio
import ssl
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup
from pdfkit import from_file

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

BASE_URL = "https://www.cifraclub.com"

async def fetch(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    async with session.get(url, ssl=ssl_context) as response:
        if response.status == 200:
            html = await response.text()
            return html
        else:
            print(f"Failed to fetch {url}")
            return None

async def scrape_song_details(session: aiohttp.ClientSession, song_url: str):
    html = await fetch(session, song_url)
    if html:
        song_soup = BeautifulSoup(html, "html.parser")
        folhas = song_soup.find_all("div", class_=lambda x: x and x.startswith("folha"))

        return "".join(str(folha) for folha in folhas)

def sanitize_song_link(song_url: str) -> str:
    if song_url.endswith(".html"):
        song_url = song_url[:-5]
    if not song_url.endswith('/'):
        song_url += "/"
    song_url += "imprimir.html#columns=true"

    return song_url


async def get_songs_links_in_list(session: aiohttp.ClientSession, list_url: str):
    html = await fetch(session, list_url)
    if not html:
        return
    soup = BeautifulSoup(html, "html.parser")
    song_list = soup.find("ol", class_="list-links list-musics")
    song_links = song_list.find_all("li")
    songs_links_to_return: list[str] = []
    for link in song_links:
        song_url = BASE_URL + sanitize_song_link(link.find('a')['href'])
        songs_links_to_return.append(song_url)
    return songs_links_to_return

def get_as_html(song_details: list[str]) -> str:
    return f'<div>{"".join(song_details)}</div>'

def add_css_styles(html_string: str, css_file_path: str) -> str:
    with open(css_file_path, 'r') as f:
        css_content = f.read()

    soup = BeautifulSoup(html_string, "html.parser")

    style_tag = soup.new_tag("style")
    style_tag.string = css_content

    head_tag = soup.find("head")
    if head_tag is None:
        head_tag = soup.new_tag("head")
        if soup.find("html") is None:
            html_tag = soup.new_tag("html")
            soup.append(html_tag)
        soup.html.insert(0, head_tag)

    head_tag.append(style_tag)

    return str(soup)

def write_to_file(filename: str, song_details: list[str]) -> None:
    html = get_as_html(list(map(str, song_details)))
    html = add_css_styles(html, "style.css")

    with open(filename, "w") as file:
        file.write(html)

async def scrape_songs(list_url: str) -> None:
    async with aiohttp.ClientSession() as session:
        songs_links = await get_songs_links_in_list(session, list_url)
        tasks = [scrape_song_details(session, song_url) for song_url in songs_links]

        song_details = await asyncio.gather(*tasks)
        write_to_file("songs.html", song_details)



if __name__ == "__main__":
    list_url = input("Enter the list url: ")
    asyncio.run(scrape_songs(list_url))
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        "enable-local-file-access": True,
        "disable-external-links": True
    }
    try:
        from_file("songs.html", "songs.pdf", options=options)
    except OSError:
        # I don't really know why this exception happens, i think it's something
        # about external links, but i really don't care that much, it generates
        # the file anyway
        pass
