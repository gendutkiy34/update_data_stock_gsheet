# update_data_stock_gsheet
Serverless AWS Lambda pipeline for automated stock data collection and analysis. Features dynamic stock lists, technical indicators, and Google Sheets integration.

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
stock-monitoring-pipeline/
├── lambda_functions/
│   ├── get_data_yfinance/           # Lambda Function 1
│   │   ├── src/ 
│   │   │   ├── __init__.py
│   │   │   ├── aws.py
│   │   │   ├── stock.py
│   │   │   └── utilization.py
│   │   ├── lambda_function.py
│   │   ├── getdata.py
│   │   ├── .env
│   │   └── requirements.txt
│   └── Update_Gsheet_stockmonitoring/ # Lambda Function 2
│       ├── src/ 
│       │   ├── __init__.py
│       │   ├── aws.py
│       │   ├── gdrive.py
│       │   ├── gsheet.py
│       │   └── utilization.py
│       ├── .env
│       ├── getdata.py
│       ├── lambda_function.py
│       └── requirements.txt
├── layers/                       # AWS Lambda Layer
│   └── requirements.txt
└── README.md
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

## 🛠️ Prerequisites
- AWS Account with appropriate permissions
- Google Service Account with Sheets API access
- Google Sheet created and shared with service account


# ⚙️ Setup Instructions
## 1. Google Sheets Setup
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
## 2. AWS Secrets Manager Setup
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

## 3. S3 Bucket Setup
1. Open AWS Management Console → S3
2. Click Create bucket
3. Bucket name: ishg-data-pipeline-yourname (must be unique)
4. Region: Choose your preferred region (e.g., us-east-1)
5. Uncheck "Block all public access" (or keep based on your security needs)
6. Click Create bucket

## 4. IAM Roles Setup
1. Create Lambda Execution Role
2. Open IAM Console → Roles → Create role
3. Trusted entity: AWS service
4. Use case: Lambda → Next
5. Add permissions policies:
  - AWSLambdaBasicExecutionRole
  - AmazonS3FullAccess (or create custom policy for specific buckets)
  - SecretsManagerReadWrite
6. Click Next
7. Role name: ishg-lambda-execution-role
8. Click Create role

## 5. Lambda Function 1: Data Collector
### Create Function
1. Open AWS Console → Lambda → Create function
2. Choose Author from scratch
3. Function name: get_data_yfinance
4. Runtime: Python 3.10 (or your preferred version)
5. Architecture: x86_64
6. Execution role: Use existing role → select ishg-lambda-execution-role
7. Click Create function
### Configure Function
1. In Configuration tab → Environment variables → Edit
2. Add variables:
   - AWS_SECRET_NAME = aws secretname
   - AWS_SECRET_REGION = aws region
   - STOCK_CODE = ISHG.JK
   - OUTPUTFILE = /tmp/outputfile.csv
   - S3_BUCKET = bucket-name
6. Click Save
### Upload Code
1. In Code tab, upload your Python code as a .zip file or paste in the editor
2. Click Deploy

## 6. Lambda Function 2: Sheet Updater
### Create Function
1. Open AWS Console → Lambda → Create function
2. Choose Author from scratch
3. Function name: Update_Gsheet_stockmonitoring
4. Runtime: Python 3.10 (or your preferred version)
5. Architecture: x86_64
6. Execution role: Use existing role → select ishg-lambda-execution-role
7. Click Create function
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
### Upload Code
1. In Code tab, upload your Python code as a .zip file or paste in the editor
2. Click Deploy

## 7. EventBridge Scheduler Setup
1. Open EventBridge Console → Schedules → Create schedule
2. Schedule name: ishg-daily-update
3. Schedule pattern: Recurring schedule
4. Schedule type: Rate expression
5. Rate expression: 1 Day or use Cron expression: 30 20 ? * MON-FRI * (4:30 PM ET)
6. Click Next
7. Target type: AWS service
8. Select target: Lambda function
9. Function: ishg-data-collector
10. Click Next → Next → Create schedule

# 🔄 Workflow
1. 4:30 PM ET Daily: EventBridge triggers Lambda Function 1
2. Data Collection: Function 1 fetches ISHG data from Yahoo Finance
3. Indicator Calculation: RSI, EMA, MACD, and volatility are calculated
4. CSV Export: Data is saved as CSV and uploaded to S3
5. Sheet Update: Lambda Function 2 is triggered, downloads CSV, and updates Google Sheets
6. Completion: Google Sheet is updated with latest data

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
| Category | Issue | Solution |
|----------|-------|----------|
| **AWS Permissions** | Secret access denied | Check IAM role has `secretsmanager:GetSecretValue` permission |
| **AWS Resources** | S3 bucket not found | Verify bucket `jkstockdata` exists in `ap-southeast-1` region |
| **Google API** | Google Sheet not found | Check `SPREADSHEET_ID` and ensure sheet is shared with service account |
| **External APIs** | Yahoo Finance timeout | Increase Lambda timeout to 3-5 minutes |
| **Dependencies** | Module import errors | Verify Lambda layer is properly attached to function |
| **Performance** | Lambda timeout | Reduce number of stocks or increase timeout/memory |

