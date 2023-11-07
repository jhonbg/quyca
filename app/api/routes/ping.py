from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def read_root():
    """Ping the API."""
    return {"ping": "pong"}