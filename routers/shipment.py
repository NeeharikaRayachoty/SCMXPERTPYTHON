from config.config import Setting
from fastapi import APIRouter,Request,Form,HTTPException,Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routers.login import get_current_user_from_token, get_current_user_from_cookie
from routers.login import login

app = APIRouter()
TEMPLATES = Jinja2Templates(directory="templates")
from pydantic import BaseModel

class shipment(BaseModel):
    Invoice_Number : str
    PO_Number : int
    Container_Number : int
    Delivery_Number : int
    Expected_Delivery_Date : str
    NDC_Number : int
    Route_Details : str
    Batch_ID : int
    Goods_Type : str
    Serial_number : int
    Select_Device : str
    Shipment_Description : str

@app.get("/shipment",response_class = HTMLResponse)
def shipment_get(request:Request, user: login = Depends(get_current_user_from_token)):
   # return TEMPLATES.TemplateResponse("shipment.html",{"request":request})
   try:
      context = {
         "user": user,
         "request": request
      }
      return TEMPLATES.TemplateResponse("shipment.html", context)
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
@app.post("/shipment",response_class = HTMLResponse)
def shipment_post(request:Request, invoice:str=Form(...),poNum:int=Form(...),containernumber:int=Form(...),deliverynumber:int=Form(...),deliverydate:str=Form(...),ndcnumber:int=Form(...),route:str=Form(...),batch:int=Form(...),goods:str=Form(...),serialnumber:int=Form(...),device:str=Form(...),description:str=Form(...)):
   shipment_data = shipment(Invoice_Number=invoice,PO_Number=poNum,Container_Number=containernumber,Delivery_Number=deliverynumber,Expected_Delivery_Date=deliverydate,NDC_Number=ndcnumber,Route_Details=route,Batch_ID=batch,Goods_Type=goods,Serial_number=serialnumber,Select_Device=device,Shipment_Description=description)
   Invoice = Setting.Shipments.find_one({"Invoice_Number":invoice})
   try:
      if not Invoice:
            collection = Setting.Shipments.insert_one(shipment_data.dict())
            return TEMPLATES.TemplateResponse("shipment.html",{"request":request, "Shipmentcreated":"Shipment created Successfully"})
      return TEMPLATES.TemplateResponse("shipment.html", {"request":request, "Invoice":"Invoice Number Existed"})
   except Exception as exc: 
      raise HTTPException(status_code=500, detail="Internal Server Error") from exc
