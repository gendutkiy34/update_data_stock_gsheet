import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from src.utilization import General


gx=General()



import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

class Gdrive:

    def __init__(self, credentials_file):
        """Initialize the Google Drive API service"""
        self.creds = None
        self.service = None
        try:
            if isinstance(credentials_file, str) and credentials_file.endswith('.json'):
                self.creds = service_account.Credentials.from_service_account_file(
                    credentials_file,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                print(f"✓ Loaded credentials from file: {credentials_file}")
            elif isinstance(credentials_file, dict):
                self.creds = service_account.Credentials.from_service_account_info(
                    credentials_file,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                print("✓ Loaded credentials from dictionary")
            else:
                raise ValueError(f"credentials_file must be string or dict, got {type(credentials_file)}")
            
            # Build service for both cases
            self.service = build('drive', 'v3', credentials=self.creds)
            print("✓ Google Drive service initialized successfully")
            
        except Exception as e:
            print(f"✗ Error initializing Google Drive service: {e}")
            raise

    def list_files(self, folder_id=None, page_size=100):
        """List files in Google Drive or a specific folder"""
        try:
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, size, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            print(f"✓ Found {len(files)} files")
            return files
            
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def search_files(self, filename=None, mime_type=None):
        """
        Search for files by name or type
        """
        try:
            query_parts = ["trashed=false"]
            
            if filename:
                query_parts.append(f"name contains '{filename}'")
            if mime_type:
                query_parts.append(f"mimeType='{mime_type}'")
            
            query = " and ".join(query_parts)
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, size)"
            ).execute()
            
            files = results.get('files', [])
            print(f"✓ Found {len(files)} files matching search criteria")
            return files
            
        except Exception as e:
            print(f"Error searching files: {e}")
            return []

    def download_file(self, file_id, destination_path):
        """
        Download a file from Google Drive
        Args:
            file_id: Google Drive file ID
            destination_path: Local path to save the file
        """
        try:
            # Get file metadata first
            file_metadata = self.service.files().get(
                fileId=file_id, 
                fields='name, mimeType'
            ).execute()
            
            print(f"⬇️ Downloading: {file_metadata['name']}")
            
            # Download the file
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"Download progress: {int(status.progress() * 100)}%")
            
            # Save to file
            with open(destination_path, 'wb') as f:
                f.write(fh.getvalue())
            
            print(f"✅ Downloaded: {file_metadata['name']} -> {destination_path}")
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False

    def download_file_by_name(self, filename, destination_path, folder_id=None):
        """
        Download a file by its name
        """
        try:
            query_parts = ["trashed=false", f"name='{filename}'"]
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            
            query = " and ".join(query_parts)
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType)"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                print(f"❌ File '{filename}' not found")
                return False
                
            if len(files) > 1:
                print(f"⚠️ Multiple files found with name '{filename}'. Using first one.")
                for file in files:
                    print(f"   - {file['name']} (ID: {file['id']})")
            
            return self.download_file(files[0]['id'], destination_path)
            
        except Exception as e:
            print(f"❌ Download by name failed: {e}")
            return False

    def upload_file(self, local_path, folder_id=None, new_name=None):
        """
        Upload a file to Google Drive
        Args:
            local_path: Path to local file
            folder_id: Folder ID to upload to (None for root)
            new_name: New name for the file in Drive (None to keep original)
        """
        try:
            if not os.path.exists(local_path):
                print(f"❌ Local file not found: {local_path}")
                return None
            
            filename = new_name or os.path.basename(local_path)
            
            # File metadata
            file_metadata = {'name': filename}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Media upload
            media = MediaFileUpload(
                local_path,
                resumable=True
            )
            
            print(f"⬆️ Uploading: {local_path} -> {filename}")
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            print(f"✅ Uploaded successfully!")
            print(f"   File ID: {file['id']}")
            print(f"   Name: {file['name']}")
            if 'webViewLink' in file:
                print(f"   URL: {file['webViewLink']}")
            
            return file
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None


    def is_initialized(self):
        """Check if service was initialized successfully"""
        return self.service is not None