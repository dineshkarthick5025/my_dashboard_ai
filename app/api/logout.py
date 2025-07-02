from app.session_manager import delete_session
from fastapi import Request, HTTPException
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/logout")
def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)

    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session_id")
    return response
