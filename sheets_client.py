# sheets_client.py
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS_FILE = "/content/drive/MyDrive/chave-automacao.json"  # BLOCO 1A oficial

def _svc():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds).spreadsheets().values()

def a1_range(sheet_title: str, col_from="A", col_to="A", first_row=None, last_row=None) -> str:
    # protege o título e evita ranges inválidos
    title = sheet_title.replace("'", "''")
    if first_row and last_row:
        return f"'{title}'!{col_from}{first_row}:{col_to}{last_row}"
    if first_row:
        return f"'{title}'!{col_from}{first_row}:{col_to}"
    if last_row:
        return f"'{title}'!{col_from}:{col_to}{last_row}"
    return f"'{title}'!{col_from}:{col_to}"

def read_column(spreadsheet_id: str, sheet_title: str, col="A", skip_header=True):
    rng = a1_range(sheet_title, col, col)
    resp = _svc().get(
        spreadsheetId=spreadsheet_id,
        range=rng,
        majorDimension="COLUMNS"
    ).execute()
    vals = resp.get("values", [[]])
    col_vals = vals[0] if vals else []
    return [v.strip() for v in col_vals[1:]] if (skip_header and col_vals) else col_vals

def write_rows(spreadsheet_id: str, sheet_title: str, start_cell: str, rows):
    rng = f"'{sheet_title.replace(\"'\",\"''\")}'!{start_cell}"
    body = {"values": rows}
    return _svc().update(
        spreadsheetId=spreadsheet_id,
        range=rng,
        valueInputOption="RAW",
        body=body
    ).execute()
