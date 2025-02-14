from fastapi import FastAPI
from .routers.auth import auth_router
from .routers.referral import ref_router

app = FastAPI(
    title="Referral System API",
    description="RESTful API для реферальной системы.",
)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Referral System API!"}


app.include_router(auth_router)
app.include_router(ref_router)
