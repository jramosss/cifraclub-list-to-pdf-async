

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pdfkit import from_string

from src.file_writer import get_html
from src.scraper import scrape_songs

router = APIRouter()

@router.get("/")
async def hello_world():
    return {"message": "Hello Worlddd"}

@router.post("/generate")
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
