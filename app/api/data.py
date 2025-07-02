from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect
import pandas as pd
import psycopg
from psycopg import OperationalError
from fastapi.responses import JSONResponse
from app.dependencies import get_current_user, encrypt_password
from app.models.user_connection import UserConnection
from app.models.user import User
from app.database import get_db
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from urllib.parse import quote_plus

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard/data", response_class=HTMLResponse)
async def data_tab(
    request: Request,
    message: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse("dashboard/data_tab.html", {
        "request": request,
        "message": message
    })



@router.post("/dashboard/data", response_class=HTMLResponse)
async def handle_postgres_connection(
    request: Request,
    host: str = Form(...),
    port: int = Form(...),
    database: str = Form(...),
    user: str = Form(...),
    password: str = Form(...),
    sslmode: str = Form(...),
    db_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Try to connect to PostgreSQL
        conn = psycopg.connect(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password,
            sslmode=sslmode,
            connect_timeout=20
        )
        conn.close()

        # Check for existing connection
        existing_conn = db.query(UserConnection).filter_by(
            user_id=current_user.id,
            db_type=db_type,
            host=host,
            port=port,
            database=database,
            username=user
        ).first()

        if existing_conn:
            message = "🔄 Connection successful but already exists."
        else:
            new_conn = UserConnection(
                user_id=current_user.id,
                db_type=db_type,
                host=host,
                port=port,
                database=database,
                username=user,
                encrypted_password=encrypt_password(password),
                sslmode=sslmode
            )
            db.add(new_conn)
            db.commit()
            message = "✅ Connection successful!"

    except OperationalError as e:
        message = f"❌ Connection failed: {str(e)}"

    # Redirect with message in query string
    params = urlencode({"message": message})
    return RedirectResponse(f"/dashboard/data?{params}", status_code=303)


from fastapi.responses import HTMLResponse

@router.get("/dashboard/data/previews", response_class=HTMLResponse)
async def get_data_previews(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    previews_by_db = []
    connections = db.query(UserConnection).filter_by(user_id=current_user.id).all()

    for conn in connections:
        try:
            # Encode credentials to handle special characters like @, /, :, etc.
            username = quote_plus(conn.username)
            password = quote_plus(conn.get_decrypted_password())
            host = conn.host
            port = conn.port
            database = conn.database
            sslmode = conn.sslmode

            # Construct the engine URL safely
            engine_url = f"postgresql://{username}:{password}@{host}:{port}/{database}?sslmode={sslmode}"
            engine = create_engine(engine_url)

            inspector = inspect(engine)
            tables = inspector.get_table_names()
            table_previews = []

            for table in tables:
                try:
                    df = pd.read_sql(f"SELECT * FROM {table} LIMIT 5", engine)
                    table_previews.append({
                        "name": table,
                        "html": df.to_html(classes="table table-sm table-bordered", index=False)
                    })
                except Exception as e:
                    table_previews.append({
                        "name": table,
                        "html": f"<p>Error previewing table {table}: {e}</p>"
                    })

            previews_by_db.append({
                "db_name": conn.database,
                "tables": table_previews
            })

        except Exception as e:
            previews_by_db.append({
                "db_name": conn.database,
                "tables": [{"name": "Error", "html": f"<p>Connection failed: {e}</p>"}]
            })

    return templates.TemplateResponse("dashboard/data_tab_content.html", {
        "request": request,
        "previews_by_db": previews_by_db
    })
