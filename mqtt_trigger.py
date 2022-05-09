import paho.mqtt.client as mqtt
import time 
import json
from datetime import datetime
import requests
import cv2
import numpy as np

api_key = #MERAKI API KEY
MV_Camera_SN = #SERIAL NUMBER
base_url = f"https://api.meraki.com/api/v1/devices/{MV_Camera_SN}/camera/generateSnapshot"
aws_api_url = #AWS API GATEWAY URL
broker_address = #MQTT BROKER IP ADDRESS

def get_rtspurl(cam_serial):
    """
    Get RTSP URL from camera
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": api_key
    }

    try:
        r_rtspurl = requests.request('GET', f"https://api.meraki.com/api/v1/devices/{MV_Camera_SN}/camera/video/settings", headers=headers)
        r_rtspurl_json = r_rtspurl.json()
        print(r_rtspurl_json)
        return r_rtspurl_json["rtspUrl"]
    except Exception as e:
        return print(f"Error when getting image URL: {e}")
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+ str(rc))
    print("\n")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/merakimv/Q2GV-ZPNL-HFC7/0")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    payload = msg.payload.decode("utf-8")

    payload_dict= json.loads(payload)

    if msg.topic == "/merakimv/Q2GV-ZPNL-HFC7/0":
        if payload_dict['counts']['person'] > 0:
            print(f"Qty of people detected: {payload_dict['counts']['person']}")
            print("Found a person!!")

            #Waits for two seconds it grabs a better picture of the person in front of the camera
            time.sleep(2)
            headers = {
            'X-Cisco-Meraki-API-Key' : api_key,
            "timestamp": datetime.now().isoformat()
            } 

            image_url = requests.post(url= base_url, headers=headers).json()["url"]

            payload = {
                "image_url": image_url
            }
            
            print("Waiting for image to be renderized")
            time.sleep(6)

            # TRIGGER LAMBDA FUNCTION
            print("FUNCTION TRIGGERED!")
            print(payload)
            req=requests.post(url= aws_api_url, data=json.dumps(payload)).json()
            print(req)
            time.sleep(60)

        else:
            #print(f"Qty of people detected: {payload_dict['counts']['person']}")
            #print(str(time.ctime(payload_dict['ts']/1000)))
            dt = datetime.utcfromtimestamp(payload_dict['ts']/1000)
            iso_format = dt.isoformat() + 'Z'
            #print(iso_format)

        #print("----------------------------------------------")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)
client.loop_forever()
'''

video_capture = cv2.VideoCapture(get_rtspurl(MV_Camera_SN))

while True:

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_address, 1883, 60)
    
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]
    # Display the resulting image
    frame = cv2.resize(frame, (960, 540))
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


video_capture.release()
cv2.destroyAllWindows()
'''
