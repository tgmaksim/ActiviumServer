from fastapi import FastAPI

from fastapi.exceptions import RequestValidationError

from ..api.base_api_exception import BaseApiException

from .stable import StableMiddleware
from .http_404 import http_404_handler
from .logging import LoggingMiddleware
from .monitoring import MonitoringMiddleware
from .api_exception import api_exception_handler
from .validation_exception import validation_exception_handler


__all__ = ['setup_exception_handlers']



def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(BaseApiException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(404, http_404_handler)

    app.add_middleware(MonitoringMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(StableMiddleware)
