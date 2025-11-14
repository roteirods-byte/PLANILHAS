# sheets_client.py — cliente Google Sheets (range seguro A2:A)
from __future__ import annotations
from typing import List, Any, Optional
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = os.path.expanduser('~/autotrader_job/chave-automacao.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

def _svc():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds).spreadsheets()

def _a1_col(col: str, start_row: int = 2, end_row: Optional[int] = None) -> str:
    # Gera A2:A (nunca "A:")
    if end_row is None:
        return f"{col}{start_row}:{col}"
    return f"{col}{start_row}:{col}{end_row}"

def read_col(spreadsheet_id: str, tab: str, col: str, start_row: int = 2) -> List[str]:
    a1 = f"{tab}!{_a1_col(col, start_row)}"
    resp = _svc().values().get(
        spreadsheetId=spreadsheet_id,
        range=a1,
        majorDimension="COLUMNS",
    ).execute()
    vals = resp.get("values", [])
    return [v for v in (vals[0] if vals else []) if v]

def read_range(spreadsheet_id: str, a1: str) -> List[List[Any]]:
    return _svc().values().get(spreadsheetId=spreadsheet_id, range=a1).execute().get("values", [])

def append_rows(spreadsheet_id: str, a1: str, rows: List[List[Any]]):
    body = {"values": rows}
    return _svc().values().append(
        spreadsheetId=spreadsheet_id,
        range=a1,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()

def update_range(spreadsheet_id: str, a1: str, rows: List[List[Any]]):
    body = {"values": rows}
    return _svc().values().update(
        spreadsheetId=spreadsheet_id,
        range=a1,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()

def clear_range(spreadsheet_id: str, a1: str):
    return _svc().values().clear(spreadsheetId=spreadsheet_id, range=a1, body={}).execute()
