# app.py  —  versão simplificada e robusta para Railway
import os
from datetime import datetime
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

# -----------------------------
# Config da página
# -----------------------------
st.set_page_config(page_title="Autotrader Dashboard", layout="wide")

PRIMARY_COLOR = "#ff7f00"  # laranja títulos
BG_DARK = "#0a2a33"        # azul escuro

st.markdown(
    f"""
    <style>
      .stApp {{ background-color: {BG_DARK}; color: #ffffff; }}
      .bigtitle {{ color: {PRIMARY_COLOR}; font-size: 32px; font-weight: 800; margin: 16px 0 8px 0; }}
      .section {{ border-top: 1px solid rgba(255,255,255,0.08); margin-top: 18px; padding-top: 18px; }}
      .ok     {{ background:#0f5132; padding:10px 12px; border-radius:8px; }}
      .warn   {{ background:#664d03; padding:10px 12px; border-radius:8px; }}
      .info   {{ background:#0b4f6c; padding:10px 12px; border-radius:8px; }}
      div[data-baseweb="select"] span {{ color:#ddd; }}
      .stTextInput>div>div>input, .stNumberInput input {{ color:#ddd; }}
      .stButton>button {{ border-radius:8px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Banco de dados
# -----------------------------
def _get_db_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        st.error("Variável DATABASE_URL não encontrada no ambiente.")
        st.stop()
    return url

@st.cache_resource
def get_engine():
    return create_engine(_get_db_url(), pool_pre_ping=True, pool_recycle=1800)

def init_db():
    engine = get_engine()
    with engine.begin() as con:
        con.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS email_config (
            id INTEGER PRIMARY KEY,
            sender_email TEXT NOT NULL,
            app_password TEXT NOT NULL,
            recipient_email TEXT NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        con.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS moedas (
            id SERIAL PRIMARY KEY,
            par TEXT UNIQUE NOT NULL
        );
        """)
        con.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS entradas (
            id SERIAL PRIMARY KEY,
            par TEXT NOT NULL,
            side TEXT NOT NULL,
            modo TEXT NOT NULL,
            preco NUMERIC NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        con.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS saidas (
            id SERIAL PRIMARY KEY,
            par TEXT NOT NULL,
            side TEXT NOT NULL,
            modo TEXT NOT NULL,
            entrada NUMERIC NOT NULL,
            alav INTEGER NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)

def run_safe(fn, ok_msg: str):
    try:
        fn()
        st.success(ok_msg)
    except Exception as e:
        st.error(f"Falha: {e}")

# -----------------------------
# Ações de dados
# -----------------------------
def db_save_email(sender, app_pw, recipient):
    engine = get_engine()
    with engine.begin() as con:
        con.execute(
            text("""INSERT INTO email_config (id, sender_email, app_password, recipient_email, updated_at)
                    VALUES (1, :s, :p, :r, NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        sender_email=EXCLUDED.sender_email,
                        app_password=EXCLUDED.app_password,
                        recipient_email=EXCLUDED.recipient_email,
                        updated_at=NOW();"""),
            {"s": sender, "p": app_pw, "r": recipient},
        )

def db_load_email():
    engine = get_engine()
    with engine.connect() as con:
        row = con.execute(text("SELECT sender_email, app_password, recipient_email FROM email_config WHERE id=1")).fetchone()
        if not row:
            return {"sender": "", "app_pw": "", "recipient": ""}
        return {"sender": row[0], "app_pw": row[1], "recipient": row[2]}

def db_add_moedas(moedas_list):
    engine = get_engine()
    with engine.begin() as con:
        for m in moedas_list:
            m = m.strip().upper()
            if not m:
                continue
            con.execute(text("INSERT INTO moedas(par) VALUES(:p) ON CONFLICT(par) DO NOTHING"), {"p": m})

def db_list_moedas():
    engine = get_engine()
    with engine.connect() as con:
        df = pd.read_sql(text("SELECT par FROM moedas ORDER BY par ASC"), con)
    return df

def db_add_saida(par, side, modo, entrada, alav):
    engine = get_engine()
    with engine.begin() as con:
        con.execute(
            text("""INSERT INTO saidas (par, side, modo, entrada, alav)
                    VALUES (:par, :side, :modo, :entrada, :alav)"""),
            {"par": par, "side": side, "modo": modo, "entrada": entrada, "alav": alav},
        )

def db_list_saidas(limit=200):
    engine = get_engine()
    with engine.connect() as con:
        df = pd.read_sql(
            text("""SELECT id, par, side, modo, entrada, alav, created_at
                    FROM saidas
                    ORDER BY id DESC
                    LIMIT :l"""),
            con,
            params={"l": limit},
        )
    return df

def load_data_for_panel(table: str, limit: int = 100) -> pd.DataFrame:
    """Compatibilidade com chamadas antigas."""
    engine = get_engine()
    with engine.connect() as con:
        return pd.read_sql(text(f"SELECT * FROM {table} ORDER BY 1 DESC LIMIT :l"), con, params={"l": limit})

# -----------------------------
# UI
# -----------------------------
init_db()

tabs = st.tabs(["E-MAIL", "MOEDAS", "ENTRADA", "SAÍDA"])

# ---------- E-MAIL ----------
with tabs[0]:
    st.markdown('<div class="bigtitle">Configuração de E-mail</div>', unsafe_allow_html=True)
    cfg = db_load_email()

    c1, c2, c3 = st.columns([1.1, 1, 1.1])
    sender = c1.text_input("Principal (remetente):", value=cfg["sender"], placeholder="usuario@exemplo.com")
    app_pw = c2.text_input("Senha (Senha do aplicativo):", value=cfg["app_pw"], type="password")
    recipient = c3.text_input("Envio (destinatário):", value=cfg["recipient"], placeholder="destinatario@exemplo.com")

    if st.button("TESTAR/SALVAR"):
        def _do():
            db_save_email(sender, app_pw, recipient)
            # Simulação de envio de teste — apenas valida conexão DB e gravação.
            _ = db_load_email()
        run_safe(_do, "Configuração salva e teste de conexão executado.")

# ---------- MOEDAS ----------
with tabs[1]:
    st.markdown('<div class="bigtitle">Painel de Moedas</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    nova = c1.text_input("Moeda(s) da Nova (ex: BTC/USDT, ETH/USDT):", value="")
    if c2.button("Adicionar Moedas"):
        moedas_list = [m.strip() for m in nova.replace(";", ",").split(",") if m.strip()]
        def _do():
            db_add_moedas(moedas_list)
        run_safe(_do, f"Moedas {', '.join(moedas_list)} adicionadas para monitoramento.")

    try:
        dfm = db_list_moedas()
        if dfm.empty:
            st.info("Nenhuma moeda encontrada no banco de dados. Adicione moedas para monitorar.")
        else:
            st.dataframe(dfm, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro ao carregar moedas: {e}")

# ---------- ENTRADA ----------
with tabs[2]:
    st.markdown('<div class="bigtitle">Painel Monitoramento de Entrada</div>', unsafe_allow_html=True)
    try:
        dfe = load_data_for_panel("entradas", limit=200)
        if dfe.empty:
            st.info("Nenhum sinal de entrada registrado no banco de dados pelo Worker.")
        else:
            st.dataframe(dfe, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar entradas: {e}")

# ---------- SAÍDA ----------
with tabs[3]:
    st.markdown('<div class="bigtitle">Painel Monitoramento de Saída</div>', unsafe_allow_html=True)

    st.markdown("**Adicionar Nova Operação (Manual)**")
    dfm = db_list_moedas()
    pares = dfm["par"].tolist() if not dfm.empty else ["BTC/USDT", "ETH/USDT"]

    c1, c2, c3, c4, c5 = st.columns([1.2, 1, 1, 1, 0.8])
    par = c1.selectbox("Par", options=pares, index=0)
    side = c2.selectbox("Lado", options=["LONGO", "SHORT"], index=0)
    modo = c3.selectbox("Modo", options=["Balanço", "Simulação"], index=0)
    entrada = c4.number_input("Entrada", min_value=0.0, step=0.001, format="%.4f", value=1.0000)
    alav = c5.number_input("Alav.", min_value=1, step=1, value=1)

    if st.button("adicionar operação"):
        def _do():
            db_add_saida(par, side, modo, entrada, int(alav))
        run_safe(_do, "Operação manual adicionada.")

    st.markdown('<div class="section"></div>', unsafe_allow_html=True)
    st.markdown("**Monitoramento da**")
    try:
        dfs = db_list_saidas(limit=300)
        if dfs.empty:
            st.info("Nenhuma operação de saída ou ativa encontrada no banco de dados.")
        else:
            # ajustes visuais simples
            dfs_ = dfs.copy()
            dfs_["created_at"] = pd.to_datetime(dfs_["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            st.dataframe(dfs_, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar saídas: {e}")
