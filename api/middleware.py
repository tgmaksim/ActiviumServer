import traceback

from fastapi.requests import Request
from fastapi.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith('/v0'):
            return JSONResponse({"api": False})

        try:
            return await call_next(request)
        except Exception as e:
            print(''.join(traceback.format_exception(e)))
            raise HTTPException(status_code=500, detail="Internal Server Error")
