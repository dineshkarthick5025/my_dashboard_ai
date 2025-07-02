from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard/settings", response_class=HTMLResponse)
async def settings_tab(request: Request):
    return templates.TemplateResponse("dashboard/settings_tab.html", {"request": request})