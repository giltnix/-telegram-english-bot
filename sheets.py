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
            raise RuntimeError("GOOGLE_CREDS_STRING not found in env variables")

        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, scope
        )

        client = gspread.authorize(creds)
        self.sheet = client.open(sheet_name).sheet1

    def get_exercises(self):
        rows = self.sheet.get_all_records()

        exams = {"oge": {}, "ege": {}}

        for row in rows:
            exam = row["exam"].strip().lower()
            task = row["task"].strip()
            question = row["question"].strip()
            options = [
                row["a"].strip(),
                row["b"].strip(),
                row["c"].strip(),
                row["d"].strip(),
            ]
            correct = row["correct"].strip().lower()

            exams.setdefault(exam, {}).setdefault(task, []).append({
                "question": question,
                "options": options,
                "correct": correct
            })

        return exams
