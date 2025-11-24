import os
from datetime import datetime,timedelta
import json


class General:
    @staticmethod
    def load_json(filepath):
        """Load JSON data from a file"""
        with open(filepath, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_json(filepath, data):
        """Save JSON data to a file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def ReadTextFile(filepath):
        """Read text file and return content"""
        with open(filepath, 'r') as f:
            return f.read().strip() 
    
    @staticmethod
    def WriteTextFile(filepath, content):
        """Write content to text file"""
        with open(filepath, 'w') as f:
            f.write(content)

    @staticmethod
    def env(key, default=None):
        return os.getenv(key, default)

    @staticmethod
    def load_env():
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"').strip("'")
            print("✅ Environment loaded!")
        except FileNotFoundError:
            print("⚠️ No .env file found")