from config.config import Setting
from fastapi import APIRouter,Request,Form,HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routers.login import get_current_user_from_token, get_current_user_from_cookie
from routers.login import login
TEMPLATES = Jinja2Templates(directory="templates")
from dotenv import load_dotenv
load_dotenv()


app = APIRouter()
TEMPLATES = Jinja2Templates(directory="templates")
from pydantic import BaseModel

client = Setting.client
db = client["SCMXpert"]
DeviceData = db["Devicedatastream"]


@app.get("/devicedata",response_class = HTMLResponse)
def shipment_get(request:Request, user: login = Depends(get_current_user_from_token)):
   try:

      streaming_data = []
      all_shipments = DeviceData.find({},{"_id":0})
      for data in all_shipments:
         streaming_data.append(data)
      context = {
         "user": user,
         "request": request,
         "streaming_data":streaming_data
      }
      return TEMPLATES.TemplateResponse("devicedata.html", context)
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))