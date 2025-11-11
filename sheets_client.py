# sheets_client.py
from __future__ import annotations
import datetime
from typing import List, Any
import google.auth
from googleapiclient.discovery import build
from config import TAB_LOG, TZINFO

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class Sheets:
    def __init__(self, spreadsheet_id: str):
        creds, _ = google.auth.default(scopes=SCOPES)  # usa GOOGLE_APPLICATION_CREDENTIALS no Cloud Run Jobs
        self.service = build("sheets", "v4", credentials=creds, cache_discovery=False)
        self.spreadsheet_id = spreadsheet_id

    # ==== utilidades genéricas ====
    def read(self, range_a1: str) -> List[List[Any]]:
        resp = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_a1
        ).execute()
        return resp.get("values", [])

    def write(self, range_a1: str, values: List[List[Any]]):
        body = {"values": values}
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range=range_a1,
            valueInputOption="RAW", body=body
        ).execute()

    def append(self, range_a1: str, values: List[List[Any]]):
        body = {"values": values}
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id, range=range_a1,
            valueInputOption="RAW", body=body
        ).execute()

    # ==== LOG padrão (DATA, HORA, STATUS) ====
    def append_log(self, status: str):
        now = datetime.datetime.now(TZINFO)
        values = [[now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), status]]
        self.append(TAB_LOG, values)
