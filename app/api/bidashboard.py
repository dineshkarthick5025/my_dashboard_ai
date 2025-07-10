from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_current_user
from app.database import get_db
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
from app.models.dashboards import Dashboard

from app.models.user import User


router = APIRouter()
templates = Jinja2Templates(directory="templates")


from datetime import datetime

@router.get("/dashboard/bidashboard", response_class=HTMLResponse)
async def bihome_tab(request: Request, db: Session = Depends(get_db)):
    try:
        user = get_current_user(request, db)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    
    dashboards = db.query(Dashboard).filter(Dashboard.user_id == user.id).all()
    
    return templates.TemplateResponse(
        "dashboard/bidashboard_tab.html",
        {
            "request": request,
            "dashboards": dashboards,
            "cache_bust": datetime.utcnow().timestamp(),
            "active_page": "bidashboard"
        }
    )
