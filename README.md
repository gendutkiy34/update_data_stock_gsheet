# Stock Monitoring Data Pipeline

A serverless AWS Lambda pipeline that automatically collects Indonesian stock data from Yahoo Finance, calculates technical indicators, and updates Google Sheets daily after market close.

![AWS](https://img.shields.io/badge/AWS-Lambda-orange)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 📊 Architecture

```mermaid
flowchart TD
    A[🕒 EventBridge Scheduler<br>cron0 15 ? * MON-FRI *] --> B[λ Data Collector<br>get_data_yfinance]
    
    B --> C[📈 Yahoo Finance API<br>Dynamic Stock List]
    B --> D[🧮 Calculate Indicators<br>RSI, EMA, MACD, Volatility]
    B --> E[📄 Create CSV File]
    B --> F[☁️ S3 Bucket Upload]
    
    B --> G[🚀 Direct Lambda Invocation]
    G --> H[λ Sheet Updater<br>Update_Gsheet_stockmonitoring]
    
    H --> I[🔐 AWS Secrets Manager]
    H --> J[📥 Download CSV from S3]
    H --> K[📊 Google Sheets API]
    
    K --> L[✅ Google Sheet Updated]
    
    style A fill:#4CAF50,color:#ffffff
    style B fill:#2196F3,color:#ffffff
    style H fill:#2196F3,color:#ffffff
    style F fill:#FF9800,color:#ffffff
    style L fill:#4CAF50,color:#ffffff
```

## 🎯 Features
- Multi-Stock Monitoring: Track multiple Indonesian stocks simultaneously
- Dynamic Stock Management: Easily add/remove stocks via environment variables
- Automated Daily Updates: Runs automatically after market close (10 PM WIB)
- Technical Indicators: Calculates RSI(14), EMA12, EMA26, MACD, Signal, and 7-day Volatility
- Secure Architecture: Uses AWS Secrets Manager for credentials and S3 for data storage
- Cost Effective: Serverless design with optimized resource allocation

## Repository Structure
```
📦 stock-monitoring-pipeline
├── 📂 lambda_functions
│   ├── 📂 get_data_yfinance           # 🚀 Lambda Function 1
│   │   ├── 📂 src 
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 aws.py
│   │   │   ├── 📄 stock.py
│   │   │   └── 📄 utilization.py
│   │   ├── 📄 lambda_function.py
│   │   ├── 📄 getdata.py
│   │   ├── 🔧 .env
│   │   └── 📋 requirements.txt
│   └── 📂 Update_Gsheet_stockmonitoring # 📊 Lambda Function 2
│       ├── 📂 src 
│       │   ├── 📄 __init__.py
│       │   ├── 📄 aws.py
│       │   ├── 📄 gdrive.py
│       │   ├── 📄 gsheet.py
│       │   └── 📄 utilization.py
│       ├── 🔧 .env
│       ├── 📄 sheetUpdate.py
│       ├── 📄 lambda_function.py
│       └── 📋 requirements.txt
├── 📂 layers
│   └── 📋 requirements.txt
└── 📄 README.md
```

## Function 1: Data Collector (get_data_yfinance)
- lambda_function.py - Main handler function
- src/aws.py - AWS services operations (S3, Secrets Manager)
- src/stock.py - Yahoo Finance data fetching and technical calculations
- src/utilization.py - Utility functions and helpers
- getdata.py - Data processing logic
- .env - Local environment variables (for development)

## Function 2: Sheet Updater (Update_Gsheet_stockmonitoring)
- lambda_function.py - Main handler function
- src/aws.py - AWS services operations
- src/gdrive.py - Google Drive API interactions
- src/gsheet.py - Google Sheets operations
- src/utilization.py - Utility functions and helpers
- getdata.py - Data retrieval and processing
- .env - Local environment variables (for development)


# ⚙️ Setup Instructions
## 🛠️ Prerequisites
- AWS Account with appropriate permissions
- Google Service Account with Sheets API access
- Google Sheet created and shared with service account
- Python 3.10 installed locall

## Step 1: Prepare Dependencies for AWS Lambda Layer
- Create Requirements File
- Create layers/requirements.txt:
```
yfinance>=0.2.18
pandas>=1.5.0
numpy>=1.21.0
google-auth>=2.17.0
google-api-python-client>=2.80.0
```
### Build Lambda Layer
1. Create directory structure:
```
mkdir -p python/src
```
2. Copy shared source code and install dependencies:
```cp -r src/* python/src/
pip install -r layers/requirements.txt -t python/
```
3. Create layer ZIP:
```
zip -r dependencies_layer.zip python/
```

## Step 2: Create AWS Lambda Layer via GUI
1. Open AWS Console → Lambda → Layers
2. Click Create layer
3. Layer name: stock-monitoring-dependencies
4. Upload your dependencies_layer.zip file
5. Compatible runtimes: Python 3.10
6. Click Create

## Step 3: Google Sheets Setup
### Create Service Account
1. Go to Google Cloud Console
2. Click "Select Project" → "New Project" or choose existing
3. Navigate to APIs & Services → Library
4. Search for "Google Sheets API" and click Enable
5. Go to APIs & Services → Credentials
6. Click + CREATE CREDENTIALS → Service Account
7. Fill in service account details and click Create
8. Download the JSON key file by clicking the service account → Keys → Add Key → JSON
9. Open your Google Sheet and share it with the service account email (e.g., your-service-account@project.iam.gserviceaccount.com) with Editor permissions
### Prepare Google Sheet
Create a sheet with the following headers in the first row:
```
Date, Close, High, Low, Open, Volume, RSI(14), EMA12, EMA26, MACD, Signal, Volatilitas(7d)
```
## Step 4: AWS Secrets Manager Setup
1. Open AWS Management Console → Secrets Manager
2. Click Store a new secret
3. Select Other type of secret
4. Click Plaintext and paste your Google service account JSON:
```
aws secretsmanager create-secret \
    --name "google/sheets/credentials" \
    --secret-string '{
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR-PRIVATE-KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
    }'
```
5. Click Next
6. Secret name: google/sheets/credentials
7. Click Next → Next → Store

## Step 5: S3 Bucket Setup
1. Open AWS Management Console → S3
2. Click Create bucket
3. Bucket name: ishg-data-pipeline-yourname (must be unique)
4. Region: Choose your preferred region (e.g., us-east-1)
5. Uncheck "Block all public access" (or keep based on your security needs)
6. Click Create bucket

## Step 6: IAM Roles Setup
1. Create Lambda Execution Role
2. Open IAM Console → Roles → Create role
3. Trusted entity: AWS service
4. Use case: Lambda → Next
5. Add permissions policies:
  - AWSLambdaBasicExecutionRole
  - AmazonS3FullAccess (or create custom policy for specific buckets)
  - SecretsManagerReadWrite
6. Click Next
7. Role name: stock-monitoring-lambda-role
8. Click Create role

## Step 7: Lambda Function 1 - Data Collector
### Create Function
1. Open AWS Console → Lambda → Create function
2. Choose Author from scratch
3. Function name: get_data_yfinance
4. Runtime: Python 3.10 (or your preferred version)
5. Architecture: x86_64
6. Execution role: Use existing role → select ishg-lambda-execution-role
7. Click Create function
### Add Layer
1. In your function, scroll to Layers section
2. Click Add a layer
3. Choose Custom layers
4. Select stock-monitoring-dependencies
5. Version: 1
6. Click Add
### Configure Function
1. In Configuration tab → Environment variables → Edit
2. Add variables:
   - AWS_SECRET_NAME = aws secretname
   - AWS_SECRET_REGION = aws region
   - STOCK_CODE = ISHG.JK
   - OUTPUTFILE = /tmp/outputfile.csv
   - S3_BUCKET = bucket-name
6. Click Save
### Configure Basic Settings
1. In Configuration → General configuration → Edit
2. Memory: 200 MB
3. Timeout: 5 minutes
4. Click Save
### Upload Code
1. Package your code:
```
cd get_data_yfinance
zip -r function1.zip lambda_function.py getdata.py src/ -x "*.env"
```
2. Upload function1.zip via AWS Console

## Step 8: Lambda Function 2 - Sheet Updater
### Create Function
1. Open AWS Console → Lambda → Create function
2. Choose Author from scratch
3. Function name: Update_Gsheet_stockmonitoring
4. Runtime: Python 3.10 (or your preferred version)
5. Architecture: x86_64
6. Execution role: Use existing role → select ishg-lambda-execution-role
7. Click Create function
### Add Layer
1. In your function, scroll to Layers section
2. Click Add a layer
3. Choose Custom layers
4. Select stock-monitoring-dependencies
5. Version: 1
6. Click Add
### Configure Function
1. In Configuration tab → Environment variables → Edit
2. Add variables:
   - AWS_SECRET_NAME = aws secretname
   - AWS_SECRET_REGION = aws region
   - SPREADSHEET_ID = ISHG.JK
   - INPUTFILE = /tmp/outputfile.csv
   - S3_BUCKET = bucket-name
   - SHEET_NAME = sheet-name
6. Click Save
### Configure Basic Settings
1. In Configuration → General configuration → Edit
2. Memory: 256 MB
3. Timeout: 5 minutes
4. Click Save
### Upload Code
1. Package your code:
```
cd Update_Gsheet_stockmonitoring
zip -r function1.zip lambda_function.py sheetUpdate.py src/ -x "*.env"
```
2. Upload function1.zip via AWS Console

## Step 9: Add Lambda Invocation Permission
1. Go to Function 1 → Configuration → Permissions
2. Click on the execution role name
3. In IAM console, click Add permissions → Create inline policy
4. JSON tab, paste:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["lambda:InvokeFunction"],
            "Resource": "arn:aws:lambda:ap-southeast-1:*:function:Update_Gsheet_stockmonitoring"
        }
    ]
}
```
5. Click Review policy → Create policy

## Step 10: EventBridge Scheduler Setup
1. Open EventBridge Console → Schedules → Create schedule
2. Schedule name: stock-daily-update
3. Schedule pattern: Recurring schedule
4. Schedule type: Rate expression
5. Rate expression: 1 Day or use Cron expression: 30 20 ? * MON-FRI * (4:30 PM ET)
6. Click Next
7. Target type: AWS service
8. Select target: Lambda function
9. Function: get_data_yfinance
10. Click Next → Next → Create schedule


# 🔄 Workflow
1. Daily Trigger: EventBridge triggers Function 1 at 10 PM WIB
2. Data Collection: Fetches current stock data from Yahoo Finance
3. Indicator Calculation: Computes RSI, EMA, MACD, and volatility
4. CSV Export: Creates/overwrites CSV with today's data only
5. S3 Upload: Saves CSV to specified bucket
6. Function Invocation: Function 1 directly calls Function 2
7. Sheet Update: Function 2 downloads CSV and appends data to Google Sheets
8. Completion: Data available for analysis


# 🧪 Testing
## Test Lambda Functions
1. Go to Lambda Console → Select your function
2. Click Test tab
3. Create new test event with:
```
json
{
  "test": true,
  "manual_run": true
}
```
4. Click Test


# 📊 Monitoring
## View Logs
- CloudWatch → Log groups:
  - /aws/lambda/stock-data-collector
  - /aws/lambda/stock-sheet-updater
## Check Files
- S3 Console → jkstockdata bucket → verify dailystockmonitor.csv


# ❗ Troubleshooting
| Issue | Solution |
|-------|----------|
| Secret access denied | Check IAM role has Secrets Manager permissions |
| S3 bucket not found | Verify bucket exists in correct region |
| Google Sheet not found | Check SPREADSHEET_ID and sharing permissions |
| Yahoo Finance timeout | Increase Lambda timeout to 3-5 minutes |
| Module import errors | Verify Lambda layer is properly attached |
| Lambda timeout | Reduce number of stocks or increase timeout |

# 🔧 Performance Configuration
1. Function 1: 200 MB RAM, 5 min timeout (data collection)
2. Function 2: 256 MB RAM, 5 min timeout (sheets operations)
3. CloudWatch: 5-day log retention for cost optimization
4. CSV Strategy: Replace (not append) for clean data transfer

#  Cost Estimation
## Monthly Cost Breakdown (Estimated)
| Service | Usage | Cost | Notes |
|---------|-------|------|-------|
| **AWS Lambda** | 2 functions × 30 days × 5 min/day | ~$0.10 - $0.20 | 200MB & 256MB memory, 5 min timeout |
| **EventBridge Scheduler** | 1 schedule × 20 invocations/month | ~$0.10 | Based on 20 trading days |
| **AWS Secrets Manager** | 1 secret stored | ~$0.40 | Fixed monthly cost |
| **S3 Storage** | ~1MB CSV × 30 days + API calls | ~$0.01 - $0.05 | Minimal storage needs |
| **CloudWatch Logs** | 5 days retention, ~10MB/month | ~$0.02 - $0.05 | Ingest + storage |
| **Data Transfer** | Minimal inter-service traffic | ~$0.01 | Within same region |

**Total Estimated Monthly Cost: ~$0.65 - $0.85 USD**
