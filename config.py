# config.py
import os
from zoneinfo import ZoneInfo

# === Ambiente ===
SHEETS_SPREADSHEET_ID = os.getenv("SHEETS_SPREADSHEET_ID", "").strip()

# === Timezone/Data/Hora ===
TZ = "America/Sao_Paulo"
TZINFO = ZoneInfo(TZ)

# === Abas/alcances A1 (ajuste conforme sua planilha) ===
TAB_LOG = "LOG!A:C"          # (DATA, HORA, STATUS)
TAB_SAIDA2 = "SAÍDA 2!A:N"   # estrutura oficial já confirmada
TAB_SAIDA1 = "SAÍDA 1!A:F"
TAB_MOEDAS = "MOEDAS!A:A"
TAB_EMAIL  = "EMAIL!A:C"

# === Formatação padrão ===
PRICE_DECIMALS = 3
PCT_DECIMALS = 2

# === Universo fixo de 39 moedas (ordem alfabética; sem 'USDT') ===
COINS = [
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC","DOGE","DOT","ETH",
    "FET","FIL","FLUX","ICP","INJ","LDO","LINK","LTC","NEAR","OP","PEPE","POL","RATS",
    "RENDER","RUNE","SEI","SHIB","SOL","SUI","TIA","TNSR","TON","TRX","UNI","WIF","XRP"
]
