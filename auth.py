from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

tenant_id = os.getenv('TENANT_ID')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
site_name = os.getenv('SITE_NAME')
host_name = os.getenv('HOST_NAME')
site_path = os.getenv('SITE_PATH')

def get_access_token():
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json().get('access_token')

def get_site_id():
    access_token = get_access_token()
    url = f'https://graph.microsoft.com/v1.0/sites/{host_name}:/{site_path}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    site = response.json()
    if site:
        return site['id']
    else:
        raise Exception("Site not found")

def get_drive_id():
    access_token = get_access_token()
    site_id = get_site_id()
    url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    drives = response.json().get('value', [])
    if drives:
        for drive in drives:
            if drive['name'] == 'Documents':
                return drive['id']
        raise Exception("Drive not found")
    else:
        raise Exception("Drive not found")

def get_folder_id(folder_name):
    access_token = get_access_token()
    drive_id = get_drive_id()
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    items = response.json().get('value', [])
    
    for item in items:
        if item['name'] == folder_name and 'folder' in item:
            return item['id']
    
    raise ValueError(f"Folder named '{folder_name}' not found")
