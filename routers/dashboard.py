from config.config import Setting
from fastapi import APIRouter,Request,Form,HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routers.login import get_current_user_from_token, get_current_user_from_cookie
from routers.login import login

app = APIRouter()
TEMPLATES = Jinja2Templates(directory="templates")
from pydantic import BaseModel



@app.get("/dashboard",response_class = HTMLResponse)
def dashboard_get(request:Request, user: login = Depends(get_current_user_from_token)):
   print("User Role:::",user["Role"])
   try:
     #    dat =  Setting.User.find_one({"Role":"User-Viewer"})
        context = {
            "user": user,
            "request": request
        }
        return TEMPLATES.TemplateResponse("dashboard.html", context)
   except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
