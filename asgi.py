import codecs

from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.applications import FastAPI
from fastapi.responses import JSONResponse

from core import log, get_min_version
from api.middleware import ExceptionHandlerMiddleware

from api.login import router as login
from api.dnevnik import router as dnevnik


app = FastAPI()
app.add_middleware(ExceptionHandlerMiddleware)

app.include_router(login)
app.include_router(dnevnik)


@app.get("/")
async def root(request: Request):
    with codecs.open('./index.html', 'r', encoding='utf-8') as file:
        html: str = file.read()

    await log(request, request.base_url.path, None, "200 OK")
    return Response(content=html, headers={"Content-Type": "text/html; charset=utf-8"})


@app.get("/v1/checkVersion")
async def check_version(request: Request):
    await log(request, request.base_url.path, None, "200 OK")
    return JSONResponse(await get_min_version())
