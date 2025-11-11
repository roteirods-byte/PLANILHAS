# main.py
import logging, traceback, datetime
from sheets_client import Sheets
from exchanges import Exchanges
from calc import pipeline_sinal
from config import SHEETS_SPREADSHEET_ID, TZINFO, COINS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SAIDA2_RANGE = "SAÍDA 2!A:Z"   # range amplo para append sem travar no nº de colunas

def _agora_brt():
    now = datetime.datetime.now(TZINFO)
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

def _ler_moedas(sh: Sheets):
    try:
        vals = sh.read("MOEDAS!A:A")
        lst = [str(r[0]).strip().upper() for r in vals if r and str(r[0]).strip()]
        return lst if lst else COINS
    except Exception:
        return COINS

def _append_saida2(sh: Sheets, row):
    # row esperado: [PAR, SIDE, MODO, ENTRADA, ATUAL, ALVO, PNL %, SITUAÇÃO, DATA, HORA, ALAV]
    sh.append(SAIDA2_RANGE, [row])

def run_job():
    if not SHEETS_SPREADSHEET_ID:
        raise RuntimeError("Defina a variável SHEETS_SPREADSHEET_ID.")

    sh = Sheets(SHEETS_SPREADSHEET_ID)
    sh.append_log("JOB INICIADO")

    coins = _ler_moedas(sh)
    ex = Exchanges()
    data, hora = _agora_brt()

    for coin in coins:
        try:
            # preço atual (com fallback de corretora)
            preco_atual, fonte = ex.get_price(coin)

            for modo, tf in [("SWING", "4h"), ("POSICIONAL", "1d")]:
                try:
                    ohlcv = ex.fetch_ohlcv(coin, timeframe=tf, limit=400)
                    res = pipeline_sinal(ohlcv, modo=modo)  # usa calc.py

                    linha = [
                        coin,                        # PAR
                        res["SIDE"],                # SIDE (LONG/SHORT/NÃO ENTRAR)
                        modo,                       # MODO
                        res["ENTRADA"],             # ENTRADA
                        preco_atual,                # ATUAL
                        res["ALVO"],                # ALVO
                        res["PNL_PCT"],             # PNL %
                        res["SITUACAO"],            # SITUAÇÃO
                        data,                       # DATA (AAAA-MM-DD)
                        hora,                       # HORA (HH:MM)
                        ""                          # ALAV (preencher se necessário)
                    ]
                    _append_saida2(sh, linha)

                except Exception as e_inner:
                    sh.append_log(f"ERRO {coin} {modo}: {e_inner.__class__.__name__}")
                    continue

        except Exception as e_coin:
            sh.append_log(f"ERRO {coin}: {e_coin.__class__.__name__}")
            continue

    sh.append_log("JOB OK")
    logging.info("Execução finalizada com sucesso.")

if __name__ == "__main__":
    try:
        run_job()
    except Exception as e:
        try:
            sh = Sheets(SHEETS_SPREADSHEET_ID) if SHEETS_SPREADSHEET_ID else None
            if sh:
                sh.append_log(f"JOB ERRO: {e.__class__.__name__}: {e}")
        finally:
            logging.error("Falha na execução:\n%s", traceback.format_exc())
            raise
