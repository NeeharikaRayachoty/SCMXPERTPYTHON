import os
import pymongo
from dotenv import load_dotenv
load_dotenv()
class settings:
    client = pymongo.MongoClient(os.getenv("mongouri"))
    db = client["SCMXpert"]
    Admin=db["Admin"]
    DeviceData = db["Devicedatastream"]
    Shipments = db["Shipment"]
    User = db["User"]
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 5 # in mins
    COOKIE_NAME = "access_token"
    SECRET_KEY: str = "secret-key"
Setting = settings()
