from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.weather import router as weather_router


app = FastAPI(
    title="Real-Time Weather Dashboard API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(weather_router)


@app.get("/")
def health_check():
    return {
        "status": "ok"
    }