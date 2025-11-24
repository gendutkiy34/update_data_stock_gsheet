import json
import boto3
from datetime import datetime, timedelta,timezone
from getdata import UploadtoS3

def GetNow():
    custom_tz = timezone(timedelta(hours=7))
    dtnow = datetime.now(custom_tz)
    return dtnow


def lambda_handler(event, context):
    try:
        UploadtoS3()
        print("✅ Get list stock sucesss")

        lambda_client = boto3.client('lambda')
        function_name = 'Update_Gsheet_stockmonitoring'
        
        payload = {
            'source': 'get_data_yfinance',
            'result': 'success', 
            'original_event': event,
            'timestamp': datetime.strftime(GetNow(), '%Y-%m-%d %H:%M:%S')
        }
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',  # Async execution
            Payload=json.dumps(payload)
        )
        
        # CRITICAL: Log the response details
        print(f"📨 Invoke Response StatusCode: {response['StatusCode']}")
        print(f"📨 Response Metadata: {response['ResponseMetadata']}")

        return {
        'statusCode': 200,
        'body': json.dumps('✅ Get Data Sucess !!')
        }
    except Exception as e:
        print(f"❌ Get list stock error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }