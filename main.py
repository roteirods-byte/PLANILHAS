# main.py
import logging, traceback, datetime
from sheets_client import Sheets
from exchanges import Exchanges
from calc import pipeline_sinal
from config import (
    SHEETS_SPREADSHEET_ID, TZINFO, PRICE_DECIMALS, PCT_DECIMALS,
    RANGE_LOG, RANGE_MOEDAS, RANGE_SAIDA2, RANGE_ENTRADA
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def _agora_brt():
    now = datetime.datetime.now(TZINFO)
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

def _ler_moedas(sh: Sheets):
    vals = sh.read_first(RANGE_MOEDAS)
    lst = [str(r[0]).strip().upper() for r in vals if r and str(r[0]).strip()]
    return lst

def _append_saida2(sh: Sheets, row):
    sh.append_first(RANGE_SAIDA2, [row])

def _append_entrada_if_apto(sh: Sheets, coin, modo, preco_atual, res, data, hora):
    if res.get("SITUACAO") != "Apto":
        return
    # ENTRADA: MOEDA | SIDE | MODO | ATUAL | ALVO | GANHO % | ARSSE. % | DATA | HORA
    linha = [
        coin,
        res["SIDE"],
        modo,
        round(float(preco_atual), PRICE_DECIMALS),
        round(float(res["ALVO"]), PRICE_DECIMALS),
        round(float(res["PNL_PCT"]), PCT_DECIMALS),
        round(float(res["ASSERTIVIDADE_PCT"]), PCT_DECIMALS),
        data,
        hora,
    ]
    sh.append_first(RANGE_ENTRADA, [linha])

def run_job():
    if not SHEETS_SPREADSHEET_ID:
        raise RuntimeError("Defina SHEETS_SPREADSHEET_ID.")

    sh = Sheets(SHEETS_SPREADSHEET_ID)
    sh.append_log("JOB INICIADO")

    coins = _ler_moedas(sh)
    ex = Exchanges()
    data, hora = _agora_brt()

    for coin in coins:
        try:
            preco_atual, _src = ex.get_price(coin)

            for modo, tf in [("SWING", "4h"), ("POSICIONAL", "1d")]:
                try:
                    ohlcv = ex.fetch_ohlcv(coin, timeframe=tf, limit=400)
                    res = pipeline_sinal(ohlcv, modo=modo)

                    # SAÍDA 2: PAR | SIDE | MODO | ENTRADA | ATUAL | ALVO | PNL % | SITUAÇÃO | DATA | HORA | ALAV
                    linha_saida2 = [
                        coin,
                        res["SIDE"],
                        modo,
                        round(float(res["ENTRADA"]), PRICE_DECIMALS),
                        round(float(preco_atual), PRICE_DECIMALS),
                        round(float(res["ALVO"]), PRICE_DECIMALS),
                        round(float(res["PNL_PCT"]), PCT_DECIMALS),
                        res["SITUACAO"],
                        data,
                        hora,
                        ""
                    ]
                    _append_saida2(sh, linha_saida2)
                    _append_entrada_if_apto(sh, coin, modo, preco_atual, res, data, hora)

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
