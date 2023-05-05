from passlib.context import CryptContext
from pydantic import BaseModel
from config.config import Setting
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
app = APIRouter()
TEMPLATES = Jinja2Templates(directory="templates")


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    """Function to change plain password to Hash"""
    return PWD_CONTEXT.hash(password)


def verify_password(password: str, hashed_password: str):
    """Function to verify hased password"""
    return PWD_CONTEXT.verify(password, hashed_password)


class signup(BaseModel):
    Username: str
    Email: str
    Role:str
    Password: str
    ConfirmPassword: str


@app.get("/signup", response_class=HTMLResponse)
def signup_get(request: Request):
    return TEMPLATES.TemplateResponse("signup.html", {"request": request})


@app.post("/signup", response_class=HTMLResponse)
def signup_post(request: Request, username: str = Form(...), email: str = Form(...),role: str =Form(...) ,password: str = Form(...), cnfpassword: str = Form(...)):

    hashed_password = hash_password(password)
    signup_data = signup(Username=username, Email=email,Role=role ,Password=hashed_password, ConfirmPassword=hashed_password)
    data = Setting.User.find_one({"Email": email})
    try:
            # if signup and signup["role"] in ["Super-Admin", "User-Viewer"]:
            
        if not data and (password == cnfpassword):
                Setting.User.insert_one(signup_data.dict())
                return HTMLResponse("<script>window.location.href ='/';</script>")
        return TEMPLATES.TemplateResponse("signup.html", {"request": request, "Email_Existed": "Email already exists"})

    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Internal Server Error") from exc
