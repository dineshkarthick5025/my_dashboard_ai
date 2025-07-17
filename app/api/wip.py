from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/wip", response_class=HTMLResponse)
async def work_in_progress(request: Request):
    return templates.TemplateResponse("dashboard/wip.html", {"request": request, "active_page": "wip"})
