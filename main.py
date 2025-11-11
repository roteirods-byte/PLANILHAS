# main.py
import logging, traceback
from sheets_client import Sheets
from config import SHEETS_SPREADSHEET_ID, TAB_LOG, TZINFO, COINS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def run_job():
    if not SHEETS_SPREADSHEET_ID:
        raise RuntimeError("Defina a variável SHEETS_SPREADSHEET_ID.")

    sh = Sheets(SHEETS_SPREADSHEET_ID)
    sh.append_log("JOB INICIADO")

    # ===== PIPELINE (placeholder) =====
    # 1) coletar preços (Binance/Bybit) -> exchanges.py
    # 2) cálculos (8 fórmulas oficiais) -> calc.py (próximo passo)
    # 3) escrever nas abas (SAÍDA 1/SAÍDA 2) -> sheets_client.py
    # ==================================

    sh.append_log("JOB OK")
    logging.info("Execução finalizada com sucesso.")

if __name__ == "__main__":
    try:
        run_job()
    except Exception as e:
        try:
            # tenta registrar erro no LOG se possível
            sh = Sheets(SHEETS_SPREADSHEET_ID) if SHEETS_SPREADSHEET_ID else None
            if sh:
                sh.append_log(f"JOB ERRO: {e.__class__.__name__}: {e}")
        finally:
            logging.error("Falha na execução:\n%s", traceback.format_exc())
            raise
