import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class SheetsLoader:
    def __init__(self, sheet_name: str):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds_json = os.environ.get("GOOGLE_CREDS_STRING")
        if not creds_json:
            raise RuntimeError("GOOGLE_CREDS_STRING not found in environment")
        
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        try:
            self.sheet = client.open(sheet_name).sheet1
            print(f"✅ Таблица '{sheet_name}' успешно загружена")
        except Exception as e:
            print(f"❌ Ошибка загрузки таблицы: {e}")
            raise
    
    def get_raw_rows(self):
        """Для совместимости со старым кодом"""
        return self.sheet.get_all_records()
