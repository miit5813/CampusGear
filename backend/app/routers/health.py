from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["Служебные"])


@router.get("", summary="Проверка работы API")
def health_check():
    return {
        "status": "ok",
        "service": "campusgear-api",
        "time": datetime.now(timezone.utc).isoformat(),
    }
