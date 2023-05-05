from config.config import Setting
from fastapi import APIRouter,Request,Form,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
app = APIRouter()
TEMPLATES = Jinja2Templates(directory="templates")
from pydantic import BaseModel
from passlib.context import CryptContext



PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str):
   """Function to change plain password to Hash"""
   return PWD_CONTEXT.hash(password)
def verify_password(password: str, hashed_password: str):
   """Function to verify hased password"""
   return PWD_CONTEXT.verify(password, hashed_password)

class forget(BaseModel):
   Email: str
   Password: str
   ConfirmPassword : str




@app.get("/forget",response_class = HTMLResponse)
def forget_get(request:Request):
   return TEMPLATES.TemplateResponse("forgetpass.html",{"request":request})
   
@app.post("/forget",response_class = HTMLResponse)
def forget_post(request:Request, email:str=Form(...),password:str=Form(...),cnfpassword:str=Form(...)):
   hashed_password = hash_password(password)
   forget_data = forget(Email=email,Password=hashed_password,ConfirmPassword=hashed_password)
   user = Setting.User.find_one({"Email":email})
   if not user:
      return TEMPLATES.TemplateResponse("forgetpass.html",{"request":request,"message1":"User Not Registred yet!"})
   else:
      if  (password == cnfpassword):
         forget_data = Setting.User.update_one({"Email":email},{"$set":{"Password":hashed_password,"ConfirmPassword":hashed_password}})
         return TEMPLATES.TemplateResponse("forgetpass.html",{"request":request,"success":"Password Changed Successfully"})
         # return HTMLResponse("<script>window.location.href = '/login';</script>")
   return TEMPLATES.TemplateResponse("forgetpass.html",{"request":request})
      
   
   





  




