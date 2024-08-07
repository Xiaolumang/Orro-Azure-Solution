import logging
import azure.functions as func
import auth

import requests
import pandas as pd
from io import BytesIO

import helper
import datetime

ngrok = 'https://darling-virtually-redfish.ngrok-free.app'
notification_url = f'{ngrok}/api/HttpExample'
folder_path = 'Orro'
drive_id = auth.get_drive_id()

baseURI  = 'https://graph.microsoft.com/v1.0'
def delete_subscription(sub_id):
    access_token = auth.get_access_token()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    url = baseURI + f'/subscriptions/{sub_id}'
    response = requests.delete(url,headers=headers)

def get_all_subscriptions():
    access_token = auth.get_access_token()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    url = baseURI + f'/subscriptions'
    response = requests.get(url,headers=headers)
    sub_ids = []
    for item in response.json().get("value",[]):
        if drive_id in item.get("resource",""):
            sub_ids.append(item.get("id",""))
    logging.info(f'found subscription {sub_ids}')
    return sub_ids

def delete_all_subscriptions():
    ids = get_all_subscriptions()
    for id in ids:
        if id:
            logging.info(f'trying to delete subscription {id}')
            delete_subscription(id)


def create_subscription():
    access_token = auth.get_access_token()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "changeType": "updated",
        "notificationUrl": notification_url,
        "resource": f"/drives/{drive_id}/root",
        "expirationDateTime": (datetime.datetime.utcnow() + datetime.timedelta(days=3)).isoformat() + 'Z',  # Set expiration 3 days from now
        "clientState": "secretClientValue"
    }
    url = baseURI + '/subscriptions'
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def Subscribe4SharePointMonitor(myTimer: func.TimerRequest) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger!! function executed.')
    delete_all_subscriptions()
    create_subscription()