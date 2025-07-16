from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.generatefuncs import askai

router = APIRouter()


# Define the input model
class AIRequest(BaseModel):
    message: str

@router.post("/ask-ai")
async def handle_ask_ai(req: AIRequest):
    response_text = askai(req.message)
    return JSONResponse(content={"response": response_text})