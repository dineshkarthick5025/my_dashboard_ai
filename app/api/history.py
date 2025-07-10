from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models.user import User
import sqlalchemy as sa

router = APIRouter()
templates = Jinja2Templates(directory="templates")



@router.get("/dashboard/history", response_class=HTMLResponse)
async def history_tab(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    history = db.execute(
        sa.text("""
            SELECT id, prompt, generated_query, status, llm_config::text, created_at
            FROM query_history
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """), {"user_id": current_user.id}
    ).fetchall()

    return templates.TemplateResponse("dashboard/history_tab.html", {"request": request, "history": history, "active_page": "history"})

