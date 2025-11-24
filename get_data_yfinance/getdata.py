import os
import json
import boto3
from datetime import datetime, timedelta, timezone
from src.utilization import General
from src.stock import Stock
from src.aws import Aws


gx=General()
gx.load_env()
aw=Aws()

def GetStockData():
    custom_tz = timezone(timedelta(hours=7))
    dtnow = datetime.now(custom_tz)
    days_back=7
    if dtnow.strftime('%a') == 'mon' :
        enddate = dtnow - timedelta(days=3)
    elif dtnow.strftime('%a') == 'su' :
        enddate = dtnow - timedelta(days=2)
    else :
        enddate = dtnow - timedelta(days=1)
    print(f"✅  get data {datetime.strftime(dtnow,'%Y-%m-%d')}")
    startdate = enddate - timedelta(days=days_back * 2)
    st=Stock(gx.env('STOCK_CODE'))
    print(f"✅  load stock code success, total : {len(st.ListStock())}")
    dfdata=st.GetYesterday(startdate,dtnow)
    print(f"✅  Get Data Stock successfull, total : {len(dfdata.index)}")
    dfdata.to_csv(gx.env('OUTPUTFILE'), index=False)
    print("✅ Export to csv successfull")


def UploadtoS3():
    try :
        GetStockData()
        aw.upload_file(gx.env('OUTPUTFILE'), gx.env('S3_BUCKET'), object_name=gx.env('OUTPUTFILE').split('/')[-1])
        print("✅ Upload to S3 successful")
        os.remove(gx.env('OUTPUTFILE'))
        print(f"✅ delete {gx.env('OUTPUTFILE')} successful")
    except Exception as e:
        print("❌ Upload to S3 failed")
        print(e)