from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .routers.auth import auth_router
from .routers.referral import ref_router

app = FastAPI(
    title="Referral System API",
    description="RESTful API для реферальной системы.",
)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Referral System API!"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


app.include_router(auth_router)
app.include_router(ref_router)
