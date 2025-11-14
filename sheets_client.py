# sheets_client.py
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopo para Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TZ = ZoneInfo("America/Sao_Paulo")

def _build_service():
    json_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "chave-automacao.json")
    creds = service_account.Credentials.from_service_account_file(json_path, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)

def append_log(spreadsheet_id: str, texto: str):
    svc = _build_service()
    agora = datetime.now(TZ)
    valores = [[agora.strftime("%Y-%m-%d"), agora.strftime("%H:%M"), texto]]
    body = {"values": valores}
    svc.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="LOG!A:C",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()

def ler_moedas(spreadsheet_id: str):
    """Lê a coluna de moedas com tolerância a nomes/acentos."""
    svc = _build_service()
    candidatos = ["MOEDAS!A2:A", "MOEDAS!A:A", "Moedas!A2:A", "MOEDA!A2:A", "Moeda!A2:A"]
    ultima = None
    for rg in candidatos:
        try:
            resp = svc.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=rg
            ).execute()
            rows = resp.get("values", [])
            # Normaliza a coluna A
            col = [r[0] for r in rows if r]
            # Limpeza
            out = []
            for s in col:
                t = s.strip().upper()
                if not t or t in ("PAR", "MOEDAS", "MOEDA"):
                    continue
                t = t.replace("USDT", "").strip()
                out.append(t)
            if out:
                return out
        except HttpError as e:
            ultima = e
            continue
    if ultima:
        raise ultima
    return []
