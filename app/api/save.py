from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.dashboards import Dashboard
from app.dependencies import get_current_user
import json

router = APIRouter()

@router.post("/dashboard/save")
async def save_dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        user = get_current_user(request, db)
    except HTTPException:
        return JSONResponse(content={"detail": "Not authenticated"}, status_code=401)

    payload = await request.json()

    name = payload.get("name")
    widgets = payload.get("widgets")
    canvas_size = payload.get("canvasSize")

    if not name or widgets is None or canvas_size is None:
        return JSONResponse(content={"detail": "Name, widgets, and canvasSize are required."}, status_code=400)

    full_data = {
        "widgets": widgets,
        "canvasSize": canvas_size
    }

    dashboard = Dashboard(
        user_id=user.id,
        name=name,
        data=json.dumps(full_data)
    )
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)

    return {"message": "Dashboard saved successfully", "dashboard_id": dashboard.id}
