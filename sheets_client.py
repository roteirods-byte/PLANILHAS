# sheets_client.py
import os
from datetime import datetime
from typing import List
from google.oauth2 import service_account
from googleapiclient.discovery import build
import config

SERVICE_ACCOUNT_FILE = os.path.expanduser('~/autotrader_job/chave-automacao.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def _service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds).spreadsheets()


def _read_column(sheet_name: str, col: str, start_row: int = 2) -> List[str]:
    """
    Lê uma coluna de forma SEGURA. Ex.: 'MOEDAS', 'A', 2 -> 'MOEDAS!A2:A'
    (evita o erro 'Unable to parse range')
    """
    rng = f"{sheet_name}!{col}{start_row}:{col}"
    resp = _service().values().get(
        spreadsheetId=config.SHEET_ID,
        range=rng,
        majorDimension='COLUMNS'
    ).execute()

    vals = resp.get('values', [])
    if not vals:
        return []

    # limpa vazios e normaliza
    out = []
    for v in vals[0]:
        s = str(v).strip().upper()
        if s:
            out.append(s)
    return out


def get_moedas() -> List[str]:
    """Lê a lista de moedas na aba MOEDAS (coluna A, a partir da linha 2)."""
    return _read_column(config.TABS['MOEDAS'], 'A', 2)


def append_log(status: str):
    """Escreve uma linha em LOG: DATA | HORA | STATUS"""
    now = datetime.now()
    row = [[now.strftime('%Y-%m-%d'), now.strftime('%H:%M'), status]]
    rng = f"{config.TABS['LOG']}!A:C"
    _service().values().append(
        spreadsheetId=config.SHEET_ID,
        range=rng,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={'values': row},
    ).execute()
