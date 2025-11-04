# AUTOTRADER – Painéis (patch completo)
# Rodar com: streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT

import os
from datetime import datetime
import streamlit as st
import pandas as pd

# ===================== CONFIG BÁSICA =====================
st.set_page_config(page_title="AUTOTRADER", layout="wide")
os.makedirs("data", exist_ok=True)

# Paleta do projeto
COR_FUNDO = "#0F2433"         # azul escuro
COR_TITULO = "#FF7F2A"        # laranja
COR_TEXTO = "#FFFFFF"         # branco
COR_LONG = "#00BF63"          # verde
COR_SHORT = "#FF4D4D"         # vermelho
COR_NEUTRO = "#BFBFBF"

# CSS global
st.markdown(f"""
<style>
body {{ background-color: {COR_FUNDO}; color: {COR_TEXTO}; }}
[data-testid="stAppViewContainer"] {{
    background-color: {COR_FUNDO};
}}
h1, h2, h3, h4, h5 {{
    color: {COR_TITULO} !important;
    font-weight: 800;
    letter-spacing: .5px;
}}
.block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
}}
/* botões */
.stButton > button {{
    background:#1377FF; color:white; border:0; border-radius:12px; padding:.6rem 1.2rem; font-weight:700;
}}
/* tabelas */
thead tr th {{
    color: {COR_TITULO} !important; font-weight:800;
}}
</style>
""", unsafe_allow_html=True)

# ===================== LISTA OFICIAL DE MOEDAS =====================
MOEDAS_OFICIAIS = sorted([
    "AAVE","ADA","APT","ARB","ATOM","AVAX","AXS","BCH","BNB","BTC","DOGE","DOT",
    "ETH","FET","FIL","FLUX","ICP","INJ","LDO","LINK","LTC","NEAR","OP","PEPE",
    "POL","RATS","RENDER","RUNE","SEI","SHIB","SOL","SUI","TIA","TNSR","TON",
    "TRX","UNI","WIF","XRP"
])

# ===================== HELPERS =====================
def agora_data_hora():
    dt = datetime.utcnow()  # manter simples e estável
    data = dt.date().isoformat()
    hora = dt.strftime("%H:%M")
    return data, hora

def fmt_preco(x):
    try:
        return f"{float(x):.3f}"
    except Exception:
        return x

def fmt_pct(x):
    try:
        return f"{float(x):.2f}%"
    except Exception:
        return x

def styler_entrada(df):
    s = df.style.format({
        "PREÇO": fmt_preco, "ALVO": fmt_preco, "GANHO%": fmt_pct, "ASSERT%": fmt_pct
    })
    if "SINAL" in df.columns:
        def cor_sinal(v):
            if str(v).upper() == "LONG":  return f"color:{COR_LONG}; font-weight:700;"
            if str(v).upper() == "SHORT": return f"color:{COR_SHORT}; font-weight:700;"
            return ""
        s = s.applymap(cor_sinal, subset=["SINAL"])
    return s

def styler_saida(df):
    s = df.style.format({
        "ENTRADA": fmt_preco, "PREÇO ATUAL": fmt_preco, "ALVO": fmt_preco, "PNL%": fmt_pct
    })
    if "SIDE" in df.columns:
        def cor_side(v):
            if str(v).upper() == "LONG":  return f"color:{COR_LONG}; font-weight:700;"
            if str(v).upper() == "SHORT": return f"color:{COR_SHORT}; font-weight:700;"
            if "NÃO" in str(v).upper():   return f"color:{COR_NEUTRO}; font-weight:700;"
            return ""
        s = s.applymap(cor_side, subset=["SIDE"])
    if "PNL%" in df.columns:
        def cor_pnl(v):
            try:
                vv = float(v)
                if vv > 0:  return f"color:{COR_LONG}; font-weight:700;"
                if vv < 0:  return f"color:{COR_SHORT}; font-weight:700;"
            except Exception:
                pass
            return ""
        s = s.applymap(cor_pnl, subset=["PNL%"])
    return s

# ===================== ESTADO INICIAL =====================
if "email_cfg" not in st.session_state:
    st.session_state.email_cfg = {"principal":"", "senha":"", "destino":""}

if "df_moedas" not in st.session_state:
    st.session_state.df_moedas = pd.DataFrame({
        "Símbolo": MOEDAS_OFICIAIS,
        "Ativo": [True]*len(MOEDAS_OFICIAIS),
        "Observação": ["" for _ in MOEDAS_OFICIAIS]
    })

if "entrada_swing" not in st.session_state:
    data, hora = agora_data_hora()
    st.session_state.entrada_swing = pd.DataFrame({
        "PAR": MOEDAS_OFICIAIS[:5],
        "SINAL": ["LONG","SHORT","SHORT","SHORT","SHORT"],
        "PREÇO": [81.767,123.105,86.613,20.741,91.193],
        "ALVO":  [0,125.784,80.412,19.685,85.944],
        "GANHO%":[0,2.18,-7.16,-5.09,-5.76],
        "ASSERT%":[58,62,58,61,61],
        "DATA":[data]*5,
        "HORA":[hora]*5
    })

if "entrada_pos" not in st.session_state:
    data, hora = agora_data_hora()
    st.session_state.entrada_pos = pd.DataFrame({
        "PAR": MOEDAS_OFICIAIS[:5],
        "SINAL": ["LONG","LONG","SHORT","SHORT","SHORT"],
        "PREÇO": [62.434,61.062,76.573,55.862,172.125],
        "ALVO":  [0,62.391,71.092,53.019,162.218],
        "GANHO%":[0,2.18,-7.16,-5.09,-5.76],
        "ASSERT%":[58,62,58,61,61],
        "DATA":[data]*5,
        "HORA":[hora]*5
    })

if "saida_ops" not in st.session_state:
    st.session_state.saida_ops = pd.DataFrame(columns=[
        "PAR","SIDE","MODO","ENTRADA","PREÇO ATUAL","ALVO","PNL%","SITUAÇÃO","DATA","HORA","ALAV"
    ])

# ===================== UI – TOPO =====================
st.markdown(f"<h1 style='text-align:center;'>AUTOTRADER</h1>", unsafe_allow_html=True)
aba = st.tabs(["E-MAIL", "MOEDAS", "ENTRADA", "SAÍDA"])

# ===================== ABA E-MAIL =====================
with aba[0]:
    st.markdown("### Configuração de E-mail")
    c1,c2,c3 = st.columns([1.2,1.2,1.2])
    with c1:
        principal = st.text_input("Principal (remetente):", value=st.session_state.email_cfg["principal"])
    with c2:
        senha = st.text_input("Senha (App Password):", value=st.session_state.email_cfg["senha"], type="password")
    with c3:
        destino = st.text_input("Envio (destinatário):", value=st.session_state.email_cfg["destino"])
    if st.button("TESTAR/SALVAR"):
        # Apenas salva no estado; envio real requer SMTP/AppPassword válido.
        st.session_state.email_cfg = {"principal":principal, "senha":senha, "destino":destino}
        st.success("Configurações salvas. (Envio de teste omitido neste ambiente)")

# ===================== ABA MOEDAS =====================
with aba[1]:
    st.markdown("### Painel de Moedas")
    novo = st.text_input("Adicione símbo_
