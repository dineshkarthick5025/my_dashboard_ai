from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.models.user import User
from app.dependencies import get_current_user
from app.database import get_db
from passlib.context import CryptContext

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)


# GET: Settings page
@router.get("/dashboard/settings", response_class=HTMLResponse)
def settings_page(
    request: Request,
    user: User = Depends(get_current_user)
):
    return templates.TemplateResponse("dashboard/settings_tab.html", {
        "request": request,
        "user_data": {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        },
        "active_page": "settings"
    })


# POST: Handle settings form submission
@router.post("/dashboard/settings/update")
async def update_settings(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    password: str = Form(None),
    confirm_password: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        # Validate password match if provided
        if password and password != confirm_password:
            return JSONResponse({
                "status": "error",
                "message": "Passwords do not match"
            }, status_code=400)

        # Update fields only if changed
        updated = False
        if user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if user.last_name != last_name:
            user.last_name = last_name
            updated = True
        if password:
            user.hashed_password = hash_password(password)
            updated = True

        if updated:
            db.add(user)
            db.commit()
            db.refresh(user)

        return JSONResponse({
            "status": "success",
            "message": "Settings updated successfully"
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Failed to update settings: {str(e)}"
        }, status_code=500)
