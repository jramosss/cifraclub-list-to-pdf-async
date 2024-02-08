import shutil
from contextlib import asynccontextmanager
from os import mkdir, path

from fastapi import FastAPI

from src.routes.home import router as HomeRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startup")
    if not path.exists('./tmp'):
        mkdir('./tmp')
    try:
        yield
    finally:
        shutil.rmtree('./tmp', ignore_errors=True)
        print("shutdown")

app = FastAPI(lifespan=lifespan)

app.include_router(HomeRouter)

@app.get("/")
async def root():
    return {"message": "Hello World"}



