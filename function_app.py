import azure.functions as func
import logging
import requests
import pandas as pd
from io import BytesIO
import auth

from http_function import OrroTasksHttp
from timer_function import Subscribe4SharePointMonitor

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="HttpExample")
def HttpExample(req: func.HttpRequest) -> func.HttpResponse:
    return OrroTasksHttp(req)


@app.timer_trigger(schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
@app.function_name(name="TimerTriggerExample")
def TimerTriggerExample(myTimer: func.TimerRequest) -> None:
    Subscribe4SharePointMonitor(myTimer)

