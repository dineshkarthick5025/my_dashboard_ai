from fastapi import APIRouter

router = APIRouter()

@router.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_metadata_stub():
    return {}
