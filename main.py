# main.py
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from sheets_client import get_moedas, append_log

TZ = ZoneInfo("America/Sao_Paulo")
SHEET_ID = os.environ.get("SHEETS_SPREADSHEET_ID", "").strip()
if not SHEET_ID:
    raise SystemExit("Defina SHEETS_SPREADSHEET_ID")

def agora():
    dt = datetime.now(TZ)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")

if __name__ == "__main__":
    data, hora = agora()
    try:
        append_log(SHEET_ID, data, hora, "JOB INICIADO")
        moedas = get_moedas(SHEET_ID)
        append_log(SHEET_ID, data, hora, f"MOEDAS LIDAS: {len(moedas)}")
        print("Primeiras moedas:", moedas[:10])
    except Exception as e:
        append_log(SHEET_ID, data, hora, f"JOB ERRO: {e}")
        raise
