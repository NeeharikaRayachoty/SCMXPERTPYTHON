from config.config import Setting
from fastapi import APIRouter,Request,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
app = APIRouter()
TEMPLATES = Jinja2Templates(directory="templates")


@app.get("/",response_class = HTMLResponse)
def home(request:Request):
   return TEMPLATES.TemplateResponse("index.html",{"request":request})