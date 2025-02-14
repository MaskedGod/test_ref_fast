from fastapi import FastAPI

app = FastAPI(
    title="Referral System API",
    description="RESTful API для реферальной системы.",
)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Referral System API!"}
