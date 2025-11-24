import json
from sheetUpdate import UpdateSheet

def lambda_handler(event, context):
    UpdateSheet()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
