# sheets.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class SheetsLoader:
    def __init__(self, creds_json, sheet_name):
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(sheet_name).sheet1

    def get_exercises(self):
        # возвращает структуру {exam: {task: [exercise_dict, ...]}}
        data = self.sheet.get_all_records()
        result = {}
        for row in data:
            exam = row["exam"].strip().lower()
            task = row["task"].strip().lower()
            exercise = row["exercise"].strip()
            options = row.get("options", "")
            answer = row.get("answer", "").strip()

            ex_dict = {
                "exercise": exercise,
                "options": options.split(";") if options else [],
                "answer": answer
            }

            if exam not in result:
                result[exam] = {}
            if task not in result[exam]:
                result[exam][task] = []
            result[exam][task].append(ex_dict)
        return result
