import os
import boto3
import json
from botocore.exceptions import ClientError
from src.utilization import General 

gx=General()
gx.load_env()

class Aws:
    
    def __init__(self):
        """Initialize AWS Secrets Manager client"""
        self.session = boto3.session.Session()
        self.client = self.session.client(
            service_name='secretsmanager', 
            region_name=gx.env('AWS_SECRET_REGION')
        )
        self.s3 = boto3.client('s3')

    def get_secret(self, secret_name):
        """Retrieve secret from AWS Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response['SecretString']
            return secret_string
        except Exception as e:
            print(f"Error retrieving secret: {e}")
            return None

    def upload_file(self, file_name, bucket, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_name)
        try:
            self.s3.upload_file(file_name, bucket, object_name)
            print(f"File {file_name} uploaded to {bucket}/{object_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"The object {object_name} does not exist in bucket {bucket}.")
            elif error_code == 'NoSuchBucket':
                print(f"The bucket {bucket} does not exist.")
            elif error_code in ('AccessDenied', '403'):
                print(f"Access denied to bucket {bucket} or object {object_name}.")
            else:
                print(f"Error uploading file s3//{bucket}/{file_name}: {error_code}")
            return False

    def download_file(self, bucket, object_name, file_name=None):
        if file_name is None:
            file_name = os.path.basename(object_name)
        try:
            self.s3.download_file(bucket, object_name, file_name)
            print(f"File {object_name} downloaded from {bucket} to {file_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"The object {object_name} does not exist in bucket {bucket}.")
            elif error_code == 'NoSuchBucket':
                print(f"The bucket {bucket} does not exist.")
            elif error_code in ('AccessDenied', '403'):
                print(f"Access denied to bucket {bucket} or object {object_name}.")
            else:
                print(f"Error downloading file: {e}")
            return False
        except FileNotFoundError:
            print(f"The file {file_name} was not found.")
            return False