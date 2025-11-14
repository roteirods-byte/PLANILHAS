# sheets_client.py
import os
from typing import List, Tuple
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
RANGE_LOG = "LOG!A:C"
RANGES_MOEDAS = ["MOEDAS!A2:A", "MOEDAS!A:A", "MOEDA!A2:A", "Moedas!A2:A", "Moeda!A2:A"]

def _client():
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not key_path or not os.path.exists(key_path):
        raise RuntimeError(f"Credencial não encontrada em GOOGLE_APPLICATION_CREDENTIALS: {key_path}")
    creds = service_account.Credentials.from_service_account_file(key_path, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds).spreadsheets()

def _get_first_range(spreadsheet_id: str, ranges: List[str]) -> Tuple[str, list]:
    svc = _client()
    for r in ranges:
        try:
            resp = svc.values().get(spreadsheetId=spreadsheet_id, range=r, majorDimension="ROWS").execute()
            values = resp.get("values", [])
            if values is not None:
                return r, values
        except Exception:
            continue
    raise RuntimeError(f"Nenhum range válido: {ranges}")

def get_moedas(spreadsheet_id: str) -> List[str]:
    _, rows = _get_first_range(spreadsheet_id, RANGES_MOEDAS)
    out = []
    for row in rows:
        cel = (row[0] if row else "").strip()
        if not cel:
            continue
        t = cel.replace("/USDT", "").replace("-USDT", "").upper()
        out.append(t)
    return out

def append_log(spreadsheet_id: str, data: str, hora: str, status: str) -> None:
    svc = _client()
    body = {"values": [[data, hora, status]]}
    svc.values().append(
        spreadsheetId=spreadsheet_id,
        range=RANGE_LOG,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
