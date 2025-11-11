# config.py
import os
from zoneinfo import ZoneInfo

SHEETS_SPREADSHEET_ID = os.getenv("SHEETS_SPREADSHEET_ID", "").strip()

TZINFO = ZoneInfo("America/Sao_Paulo")

# Abas (aceita variações com/sem acento)
RANGE_LOG      = ["LOG!A:C"]
RANGE_MOEDAS = ["MOEDAS!A:A", "MOEDA!A:A", "Moedas!A:A", "Moeda!A:A"]
RANGE_SAIDA2   = ["SAÍDA 2!A:K", "SAIDA 2!A:K"]     # 11 colunas
RANGE_ENTRADA  = ["ENTRADA!A:I"]                    # 9 colunas
RANGE_EMAIL    = ["EMAIL!A:D"]                      # EMAIL | SENHA | EMAIL DESTINO | ENVIAR/TESTAR

PRICE_DECIMALS = 3
PCT_DECIMALS   = 2
