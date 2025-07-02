from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.dashboards import Dashboard

router = APIRouter()

@router.post("/dashboard/delete")
async def delete_dashboard(payload: dict, db: Session = Depends(get_db)):
    dashboard_id = payload.get("id")
    if not dashboard_id:
        raise HTTPException(status_code=400, detail="Dashboard ID required")

    db.query(Dashboard).filter(Dashboard.id == dashboard_id).delete()
    db.commit()
    return {"message": "Dashboard deleted"}
