import logging
import azure.functions as func
import auth

import requests
import pandas as pd
from io import BytesIO

import helper


def OrroTasksHttp(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        validation_token = req.params.get('validationToken')
        if validation_token:
            logging.info(f"Validation token received: {validation_token}")
            return func.HttpResponse(validation_token, status_code=200)
        
        body = req.get_json()
        logging.info(f"Received body: {body}")
        
        notifications = body.get('value', [])
        if not notifications:
            return func.HttpResponse("No notifications found", status_code=400)

        access_token = auth.get_access_token()
        drive_id = auth.get_drive_id()
        file_ids = helper.get_changes()  # Ensure this returns a dictionary with file names and IDs
        logging.info(f"File IDs to process: {file_ids}")

        helper.process_files(file_ids, drive_id, access_token)

        return func.HttpResponse("Processing completed", status_code=200)

    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return func.HttpResponse("Invalid request: Could not parse JSON.", status_code=400)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return func.HttpResponse(f"An error occurred: {e}", status_code=500)





