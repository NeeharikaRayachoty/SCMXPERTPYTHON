"""Importing code & the necessary libraries for the program to run."""

import os
import json
import sys
import pymongo
from kafka import KafkaConsumer
from dotenv import load_dotenv
load_dotenv()

client = pymongo.MongoClient(os.getenv("mongouri"))
db = client["SCMXpert"]
DeviceData = db["Devicedatastream"]

TOPIC_NAME = os.getenv("topic_name")
bootstrap_servers = os.getenv("bootstrap_servers") 

print("The production team is currently occupied, please hold for their -----response.")

try: 
    CONSUMER = KafkaConsumer(TOPIC_NAME, bootstrap_servers=bootstrap_servers,auto_offset_reset='latest')
#    , api_version=(0,11,5)
    for DATA in CONSUMER: 
        try: 
            # print("consumer data", DATA)
            DATA = json.loads(DATA.value) 
            mdata = DeviceData.insert_one(DATA) 
        
            # print(mdata)
        except json.decoder.JSONDecodeError:
            continue
        
except KeyboardInterrupt: 
        sys.exit()