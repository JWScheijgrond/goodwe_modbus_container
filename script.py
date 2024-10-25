import asyncio
import goodwe
import requests
import schedule
import time
import os
from goodwe.exceptions import MaxRetriesException, PartialResponseException, RequestFailedException, RequestRejectedException
from goodwe.protocol import ProtocolCommand, UdpInverterProtocol
from datetime import datetime

# Replace with your PVOutput API key and system ID
API_KEY = os.environ.get("PVO_APIKEY", "PVOUTPUTAPIKEY")
SYSTEM_ID = os.environ.get("PVO_SYSTEMID", "1111111")
INVERTER_IP_ADDRESS = os.environ.get("INV_IP", "192.168.0.239")
FAMILY = os.environ.get("INV_FAM", "D-NS")
TZ = os.environ.get("TZ", "Europe/Amsterdam")

async def get_runtime_data():
    #Connect to the Inverter and retrieve the data
    inverter = await goodwe.connect(host=INVERTER_IP_ADDRESS, family=FAMILY )
    runtime_data = await inverter.read_runtime_data()

    data = {}
    for sensor in inverter.sensors():
        if sensor.id_ in runtime_data:
            data[sensor.id_] = runtime_data[sensor.id_]
            #print is added to check the values in the logging
            print("ID: %s value: %s" % (sensor.id_, data[sensor.id_]))
    return data

def upload_to_pvoutput(data):
    url = 'https://pvoutput.org/service/r2/addstatus.jsp'
    headers = {
        'X-Pvoutput-Apikey': API_KEY,
        'X-Pvoutput-SystemId': SYSTEM_ID
    }

    # Prepare the data to be uploaded
    payload = {
        'd': datetime.now().strftime('%Y%m%d'),             # Date in YYYYMMDD format
        't': datetime.now().strftime('%H:%M'),              # Time in HH:MM format
        'v1': data.get('e_day', 0)*1000,                    # Power Generation (Wh) Multiply by 1000 PVO expects Wh and the inverter sends kWh
        'v2': data.get('total_inverter_power', 0),          
        'v5': data.get('temperature', 0),                   
        'v6': data.get('vpv1', 0),                          
        'c1': 1                                             # cumulative energy
    }

    print(payload) #log wwhat is being sent

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        print('Data uploaded successfully')
    else:
        print(f'Failed to upload data: {response.status_code} - {response.text}')

async def main():
    data = await get_runtime_data()
    upload_to_pvoutput(data)

def run_main():
    try:
        print('Starting run')
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred in main: {e}")

def run_search_local():
    try:
        print('Starting search local')
        asyncio.run(search_inverterforAddress())
    except Exception as e:
        print(f"An error occurred in search local: {e}")

async def search_inverterforAddress() -> bytes:
    #The magic string to wake up the inverter. 
    #this is also part of the GOODWE library, but added here to call for a single IP to bypass the Error 13 when broadcasting in a linux environment.
    command = ProtocolCommand("WIFIKIT-214028-READ".encode("utf-8"), lambda r: True)
    try:
        result = await command.execute(UdpInverterProtocol(INVERTER_IP_ADDRESS, 48899, 2, 1)) #the broadcast is over UDP, but the connection is then made by modbus
        if result is not None:
            return result.response_data()
        else:
            raise Exception("No response received to broadcast request.")
    except Exception as e:
        print(f"An error occurred in discover: {e}")


def job():
    print("I'm working... at " + datetime.now().strftime('%H:%M'))

if __name__ == '__main__':
    print('Start MAIN')
    print(f"API_Key is {API_KEY}")
    print(f"SYSTEM_ID is {SYSTEM_ID}")
    print(f"INVERTER_IP_ADDRESS is {INVERTER_IP_ADDRESS}")
    print(f"FAMILY is {FAMILY}")
    print(f"TZ is {TZ}")
    schedule.every(10).minutes.do(run_search_local) #Search local every 10 minutes to enable the modbus if it has stopped
    schedule.every(1).minutes.do(run_main) #Check every minute for inverter information
    schedule.every(1).minutes.do(job) #Log that the script is working

    while 1:
        schedule.run_pending()
        time.sleep(30)