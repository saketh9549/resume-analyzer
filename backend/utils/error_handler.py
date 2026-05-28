from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger("backend.error_handler")

async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error on {request.url.path}: {exc.detail} (status {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "code": exc.status_code
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = "; ".join([f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in errors])
    logger.error(f"Validation error on {request.url.path}: {error_msg}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": f"Validation Error: {error_msg}",
            "code": 400
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"Internal Server Error: {str(exc)}",
            "code": 500
        }
    )

def register_error_handlers(app):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
