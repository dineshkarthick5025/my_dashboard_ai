from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.dashboards import Dashboard

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard/bihome", response_class=HTMLResponse)
async def bihome_tab(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Fetch recent 4 dashboards for the current user
    recent_dashboards = db.query(Dashboard).filter(
        Dashboard.user_id == current_user.id
    ).order_by(Dashboard.id.desc()).limit(4).all()

    return templates.TemplateResponse(
        "dashboard/bihome_tab.html",
        {
            "request": request,
            "first_name": current_user.first_name,
            "recent_dashboards": recent_dashboards,
            "active_page": "bihome"
        }
    )

