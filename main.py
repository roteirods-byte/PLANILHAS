# main.py
import os
from sheets_client import ler_moedas, append_log

def main():
    sid = os.getenv("SHEETS_SPREADSHEET_ID", "").strip()
    if not sid:
        print("ID ausente")
        return
    append_log(sid, "JOB INICIADO")
    try:
        moedas = ler_moedas(sid)
        prev = ", ".join(moedas[:10])
        append_log(sid, f"MOEDAS LIDAS ({len(moedas)}): {prev}")
        print("OK:", len(moedas), "moedas")
    except Exception as e:
        append_log(sid, f"JOB ERRO: {e}")
        raise

if __name__ == "__main__":
    main()
