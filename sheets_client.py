# sheets_client.py
from __future__ import annotations
import datetime
from typing import List, Any
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import TZINFO

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class Sheets:
    def __init__(self, spreadsheet_id: str):
        creds, _ = google.auth.default(scopes=SCOPES)
        self.service = build("sheets", "v4", credentials=creds, cache_discovery=False)
        self.spreadsheet_id = spreadsheet_id

    def _append(self, range_a1: str, values: List[List[Any]]):
        body = {"values": values}
        return self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id, range=range_a1,
            valueInputOption="RAW", body=body
        ).execute()

    def append_first(self, ranges: List[str], values: List[List[Any]]):
        last_err = None
        for r in ranges:
            try:
                return self._append(r, values)
            except HttpError as e:
                last_err = e
        raise last_err or RuntimeError("Falha ao gravar no Sheets.")

    def read_first(self, ranges: List[str]) -> List[List[Any]]:
        last_err = None
        for r in ranges:
            try:
                resp = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id, range=r
                ).execute()
                return resp.get("values", [])
            except HttpError as e:
                last_err = e
        if last_err:
            raise last_err
        return []

    def append_log(self, status: str):
        now = datetime.datetime.now(TZINFO)
        values = [[now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), status]]
        self.append_first(["LOG!A:C"], values)
