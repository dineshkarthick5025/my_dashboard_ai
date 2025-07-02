import app.models.user as User
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models.dashboards import Dashboard

router = APIRouter()
templates = Jinja2Templates(directory="templates")



@router.post("/dashboard/thumbnail")
async def save_dashboard_thumbnail(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    print(f"📦 Received thumbnail payload: {payload}")

    dashboard_id = payload.get("dashboard_id")
    image_data = payload.get("image_data")

    if not dashboard_id or not image_data:
        print("⚠️ Missing dashboard_id or image_data in payload.")
        raise HTTPException(status_code=400, detail="dashboard_id and image_data are required")

    print(f"🔍 Looking for dashboard with ID {dashboard_id} belonging to user ID {current_user.id}")

    dashboard = db.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        Dashboard.user_id == current_user.id
    ).first()

    if not dashboard:
        print(f"❌ Dashboard with ID {dashboard_id} not found or unauthorized.")
        raise HTTPException(status_code=404, detail="Dashboard not found")

    print(f"✅ Dashboard found. Updating thumbnail...")
    dashboard.thumbnail = image_data

    db.commit()
    print(f"💾 Thumbnail for dashboard ID {dashboard_id} updated successfully.")

    return {"message": "Thumbnail updated"}
