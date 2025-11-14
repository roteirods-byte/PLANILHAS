# main.py — lê a aba MOEDAS e registra no LOG (BRT)

from datetime import datetime, timezone, timedelta
from sheets_client import read_col, append_rows

# ======= CONFIGURE AQUI =======
SPREADSHEET_ID = "COLE_AQUI_O_ID"   # ID da sua planilha AUTOTRADER
TAB_MOEDAS     = "MOEDAS"           # nome exato da aba
TAB_LOG        = "LOG"              # nome exato da aba
# ==============================

BRT = timezone(timedelta(hours=-3))

def now_brt():
    dt = datetime.now(BRT)
    return dt.date().isoformat(), dt.strftime("%H:%M")

def log_status(msg: str):
    data, hora = now_brt()
    append_rows(SPREADSHEET_ID, f"{TAB_LOG}!A:C", [[data, hora, msg]])

def ler_moedas() -> list[str]:
    # Lê a coluna A a partir da linha 2 (pula cabeçalho): A2:A
    moedas = read_col(SPREADSHEET_ID, TAB_MOEDAS, "A", start_row=2)
    # Normaliza (sem 'USDT' conforme seu padrão; remova se quiser listar tudo)
    norm = []
    for m in moedas:
        t = m.strip().upper()
        if t.endswith("USDT"):
            t = t[:-4]  # remove sufixo USDT
        if t:
            norm.append(t)
    # Ordenação alfabética (se desejar visualizar já ordenado)
    norm.sort()
    return norm

def main():
    log_status("JOB INICIADO")
    try:
        moedas = ler_moedas()
        if not moedas:
            log_status("AVISO: MOEDAS vazia")
        else:
            # Mostra só as 10 primeiras no LOG para não poluir
            preview = ", ".join(moedas[:10]) + ("..." if len(moedas) > 10 else "")
            log_status(f"MOEDAS lidas: {len(moedas)} → {preview}")
    except Exception as e:
        log_status(f"JOB ERRO: {e}")
        raise
    else:
        log_status("JOB OK")

if __name__ == "__main__":
    main()
