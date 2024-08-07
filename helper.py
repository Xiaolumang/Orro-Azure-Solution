import requests
import auth
import Process_Files.comm as comm
import logging
from io import BytesIO
import pandas as pd
import time

import Process_Files.orro_summarise_helper as orro_summarise_helper
import Process_Files.excel_helper as excel_helper
import Process_Files.orro_compare_helper as orro_compare_helper

sheet_name = 'Bill Charge Detail'
drive_id = auth.get_drive_id()
folder_id = auth.get_folder_id('Orro')
#drive_id = auth.get_drive_id()


def is_locked(item_id):
    access_token = auth.get_access_token()
    url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    item = response.json()
    return 'lock' in item

def wait_until_unlocked(item_id, max_retries=5):
    retries = 0
    while retries < max_retries:
        if not is_locked(item_id ):
            return True
        logging.warning(f"Item is locked, retrying in {2 ** retries} seconds...")
        time.sleep(2 ** retries)
        retries += 1
    return False

def upload_file(file_name, file_content, folder_id):
    logging.info(f'Uploading {file_name}')
    if not wait_until_unlocked(folder_id):
        raise Exception("Max retries reached. Folder is still locked.")
    access_token = auth.get_access_token()
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}:/{file_name}:/content"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    } 
    response = requests.put(url, headers=headers, data=file_content)
    response.raise_for_status()
    return response.json()


def process_file_summarise(file_content):
    df = pd.read_excel(BytesIO(file_content),sheet_name)
    # Add your processing logic here
    output = BytesIO()
    df = orro_summarise_helper.summarise_by_cost_center(df)
    df.to_excel(output, index=False)
    output.seek(0)
    output = excel_helper.highlight_excel(output)
    return output.getvalue()

def process_file_compare(file_content):
    df = pd.read_excel(BytesIO(file_content),sheet_name)
    # Add your processing logic here
    output = BytesIO()
    df = orro_compare_helper.compare_charge_with_expected(df)
    df.to_excel(output, index=False)
    output.seek(0)
    return output.getvalue()


def process_files(file_ids, drive_id, access_token):
    orro_folder_id = auth.get_folder_id('Orro')
    orro2_folder_id = auth.get_folder_id('Orro2')

    # Get old files in 'Orro' folder
    logging.info(' ing old files from Orro folder...')
    orro_files = get_orro_files()

    for file_name, old_file_id in orro_files.items():
        # Download, delete, and upload with the same name
        if old_file_id in file_ids:
            logging.info(f'Downloading and deleting old file: {file_name}')
            file_content = download_file(old_file_id) 
            delete_file(old_file_id)

        # Process and upload new file with the same name
        
            logging.info(f'Processing and uploading new file: {file_name}')
       
            processed_content = process_file_summarise(file_content)
            upload_file("summarise_task.xlsx", processed_content, orro2_folder_id)

            processed_content = process_file_compare(file_content)
            upload_file("compare_task.xlsx", processed_content, orro2_folder_id)


def download_file(file_id):
    access_token = auth.get_access_token()
    url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/content'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.content



def get_orro_files():

    folder_id = auth.get_folder_id('Orro')
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children"
    access_token = auth.get_access_token()
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    items = response.json().get('value', [])
    return {item['name']: item['id'] for item in items if item['file']}

def file_id_2_df(file_id,sheet_name):
    file_content = download_file(file_id)
    if sheet_name:
        df = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name)
    else:
        df = pd.read_excel(BytesIO(file_content))
    return df

def get_file_id_by_name(fname):
    name_id_pairs = get_orro_files()
    return name_id_pairs[fname]

def delete_file(item_id):
    access_token = auth.get_access_token()
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    logging.info(f"Deleted file with ID: {item_id}")

def get_changes():
    drive_id = auth.get_drive_id()
   # url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{resource_id}/delta'
    
    url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/delta'
    access_token = auth.get_access_token()
    headers = {'Authorization': f'Bearer {access_token}'}
    
    new_file_ids = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Filter for newly created files and extract their IDs
        changes = data.get('value', [])
        for change in changes:
            if (
                change.get('deleted') is None and 
                change.get('file') is not None and 
                change.get('@odata.type') == "#microsoft.graph.driveItem" and 
                change.get('name') != comm.file_reiew_expected_template
            ):
                new_file_ids.append(change['id'])
        
        # Check if there's another page of results
        url = data.get('@odata.nextLink')
    
    return new_file_ids
