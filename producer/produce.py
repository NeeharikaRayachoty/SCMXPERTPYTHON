"""Importing code & the necessary libraries for the program to run."""

import socket
import os
from dotenv import load_dotenv
from kafka import KafkaProducer

load_dotenv()

socket_connection = socket.socket()
print("The Consumer team is currently occupied, please hold for their -----response.")
HOST = os.getenv("host")
PORT = os.getenv("port")
socket_connection.connect((HOST, int(PORT))) 
bootstrap_servers =os.getenv("bootstrap_servers") 

PRODUCER = KafkaProducer(bootstrap_servers=bootstrap_servers, retries=5)
# , api_version = (0,11,5)
TOPIC_NAME = os.getenv("topic_name") 

while True: 
    try:
         DATA = socket_connection.recv(70240)
     #     print("producer data", DATA)
         PRODUCER.send(TOPIC_NAME, DATA)
         
    except Exception as exception:
         print(exception) 
socket_connection.close()