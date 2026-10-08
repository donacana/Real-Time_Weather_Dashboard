from fastapi import APIRouter, HTTPException

from backend.app.services.weather_service import get_current_weather


router = APIRouter(
    prefix="/api/weather",
    tags=["Weather"],
)


@router.get("/current")
def current_weather():
    weather = get_current_weather()

    if weather is None:
        raise HTTPException(
            status_code=404,
            detail="저장된 날씨 데이터가 없습니다.",
        )

    return weather