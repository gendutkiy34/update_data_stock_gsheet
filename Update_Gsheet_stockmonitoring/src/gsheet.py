import os
import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build
#import pandas as pd
from src.utilization import General

gx=General()

gx.load_env()


class GoogleSheetReader:
    
    def __init__(self,credentials_file):
        """Initialize the Google Sheets API service"""
        self.creds = None
        self.service = None
        scope=['https://www.googleapis.com/auth/spreadsheets']
        try:
            if isinstance(credentials_file, str) and credentials_file.endswith('.json'):
                self.creds = service_account.Credentials.from_service_account_file(
                    credentials_file,
                    scopes=scope
                    #scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                )
                print(f"✓ Loaded credentials from file: {credentials_file}")
            elif isinstance(credentials_file, dict):
                self.creds = service_account.Credentials.from_service_account_info(
                    credentials_file,
                    scopes=scope
                )
                print("✓ Loaded credentials from dictionary")
            else:
                raise ValueError(f"credentials_file must be string or dict, got {type(credentials_file)}")
            
            # Build service for both cases
            self.service = build('sheets', 'v4', credentials=self.creds)
            print("✓ Google Sheets API service initialized successfully")
            
        except Exception as e:
            print(f"✗ Error initializing Google Drive service: {e}")
            raise

    def _clean_value_simple(self, value):
        """Simple value cleaning using pandas"""
        return '' if pd.isna(value) else value

    def _clean_data_simple(self, data):
        """Simple data cleaning that handles all cases"""
        if isinstance(data, pd.DataFrame):
            # Fill NaN/None with empty strings and convert to list
            return data.fillna('').values.tolist()
        elif isinstance(data, list):
            cleaned_data = []
            for row in data:
                if isinstance(row, list):
                    cleaned_row = ['' if pd.isna(cell) else cell for cell in row]
                    cleaned_data.append(cleaned_row)
                else:
                    cleaned_data.append(['' if pd.isna(row) else row])
            return cleaned_data
        else:
            raise ValueError("Data must be DataFrame or list")
                
            return cleaned_data

    def read_sheet(self, range_name='A:Z',SPREADSHEET_ID=None):
        """Read data from the specified range in the Google Sheet"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        values = result.get('values', [])
        
        if not values:
            print("No data found.")
            return pd.DataFrame()  # Return empty DataFrame
        
        dataraw = []
        for i, row in enumerate(values):
            if i == 0:
                cols = row
            else:
                dataraw.append(row)
        return dataraw

    def append_to_sheet(self, SPREADSHEET_ID=None, range_name='Sheet1!A:Z', values=None):
        """Append data to the sheet"""
        #cleaned_values = self._clean_data_for_sheets(values)
        try:
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            print(f"✓ Appended {result.get('updates', {}).get('updatedCells', 0)} cells")
            return result
        except Exception as e:
        # Append to Google S
            print(f"✗ Error appending to sheet: {e}")
            raise
    
    def list_worksheets(self, SPREADSHEET_ID):
        """
        List all worksheets in the spreadsheet with their properties
        
        Returns:
            list: List of worksheet information dictionaries
        """
        if not SPREADSHEET_ID:
            raise ValueError("SPREADSHEET_ID must be provided")
            
        try:
            # Get spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=SPREADSHEET_ID
            ).execute()
            
            worksheets = []
            for sheet in spreadsheet.get('sheets', []):
                props = sheet.get('properties', {})
                worksheet_info = {
                    'sheet_id': props.get('sheetId'),
                    'title': props.get('title'),
                    'index': props.get('index'),
                    'sheet_type': props.get('sheetType'),
                    'grid_properties': props.get('gridProperties', {})
                }
                worksheets.append(worksheet_info)
            
            print(f"✓ Found {len(worksheets)} worksheets in spreadsheet")
            return worksheets
            
        except Exception as e:
            print(f"✗ Error listing worksheets: {e}")
            raise

    def csv_to_google_sheets_no_pandas(self,csv_file_path, spreadsheet_id, sheet_name):
        # Read CSV with built-in csv module
        try :
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                newval = list(csv_reader)
            print(f"✅  Read file {csv_file_path.split('/')[-1]} success")
        except Exception as error:
            print(f"❌ Read file {csv_file_path.split('/')[-1]} Error: {error}")
            exit(1)

        # Append to Google Sheets
        try:
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=sheet_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': newval[1:]}
            ).execute()
            
            print(f"✅ Successfully appended {len(values)} rows")
            return True
            
        except Exception as error:
            print(f"❌ Error: {error}")
            return False