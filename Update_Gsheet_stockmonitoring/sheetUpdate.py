import os
import json
import csv
from datetime import datetime,timedelta
from src.aws import Aws
from src.utilization import General
from src.gsheet import GoogleSheetReader
from src.gdrive import Gdrive

gx=General()
aw=Aws()
gx.load_env()
secret_data = json.loads(aw.get_secret(gx.env('AWS_SECRET_NAME')))

def Downloadcsv():
    aw.download_file(gx.env('S3_BUCKET'), gx.env('OUTPUTFILE').split('/')[-1], file_name=gx.env('OUTPUTFILE'))
    if os.path.exists(gx.env('OUTPUTFILE')) :
        print(f"✅  Download file {gx.env('OUTPUTFILE').split('/')[-1]} success")
    else :
        print(f"❌  Download file {gx.env('OUTPUTFILE').split('/')[-1]} failed")


def UpdateSheet():
    Downloadcsv()
    gs=GoogleSheetReader(secret_data)
    gs.csv_to_google_sheets_no_pandas(gx.env('OUTPUTFILE'), gx.env('SPREADSHEET_ID'), gx.env('SHEET_NAME'))
