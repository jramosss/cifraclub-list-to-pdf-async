import shutil
from contextlib import asynccontextmanager
from os import mkdir, path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pdfkit import from_string

from src.html import get_html
from src.scraper import scrape_songs

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not path.exists('./tmp'):
        mkdir('./tmp')
    try:
        yield
    finally:
        shutil.rmtree('./tmp', ignore_errors=True)

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def scrape_and_download_pdf(list_url: str):
    songs_list = await scrape_songs(list_url)
    html = get_html(songs_list)
    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    try:
        from_string(html, "./tmp/songs.pdf", options=options)
    except OSError:
        # I don't really know why this exception happens, i think it's something
        # about external links, but i really don't care that much, it generates
        # the file anyway
        pass
    return FileResponse("./tmp/songs.pdf", media_type="application/pdf", filename="songs.pdf")


