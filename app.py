# app.py
# Streamlit + Railway Postgres (funcional, sem simulação)

import os
from datetime import datetime
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

# -----------------------------------------------------------------------------
# DB: URL e Engine
# -----------------------------------------------------------------------------
DB_URL = os.getenv("DATABASE_URL") or os.getenv("URL_DO_BANCO_DE_DADOS")
if not DB_URL:
    raise RuntimeError(
        "Defina a variável de ambiente DATABASE_URL (ou URL_DO_BANCO_DE_DADOS) "
        "no serviço 'web' da Railway com a connection string do Postgres."
    )

# Ex.: postgresql+psycopg2://postgres:SEU_TOKEN@postgres.railway.internal:5432/railway
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    poolclass=QueuePool,
    pool_recycle=300,
)

# -----------------------------------------------------------------------------
# DDL (criação das tabelas)
# -----------------------------------------------------------------------------
DDL = """
CREATE TABLE IF NOT EXISTS email_config (
    id          SMALLINT PRIMARY KEY DEFAULT 1,
    remetente   TEXT,
    senha       TEXT,
    destino     TEXT,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS moedas (
    id       SERIAL PRIMARY KEY,
    simbolo  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS entradas (
    id             SERIAL PRIMARY KEY,
    par            TEXT NOT NULL,
    sinal          TEXT,
    preco          NUMERIC(18,6),
    alvo           NUMERIC(18,6),
    ganho          NUMERIC(9,2),
    assertividade  NUMERIC(9,2),
    data_evento    DATE,
    hora_evento    TIME,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS saidas (
    id         SERIAL PRIMARY KEY,
    par        TEXT NOT NULL,
    lado       TEXT NOT NULL,
    modo       TEXT NOT NULL,
    entrada    NUMERIC(18,6) NOT NULL,
    alav       INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""
with engine.begin() as conn:
    conn.execute(text(DDL))

# -----------------------------------------------------------------------------
# DAO helpers
# -----------------------------------------------------------------------------
def get_email_config():
    with engine.begin() as c:
        row = c.execute(text("SELECT remetente, senha, destino FROM email_config WHERE id=1")).fetchone()
    if row:
        return {"remetente": row[0] or "", "senha": row[1] or "", "destino": row[2] or ""}
    return {"remetente": "", "senha": "", "destino": ""}

def save_email_config(remetente: str, senha: str, destino: str):
    with engine.begin() as c:
        c.execute(
            text("""
                INSERT INTO email_config (id, remetente, senha, destino, updated_at)
                VALUES (1, :r, :s, :d, NOW())
                ON CONFLICT (id) DO UPDATE
                SET remetente=:r, senha=:s, destino=:d, updated_at=NOW()
            """),
            {"r": remetente.strip(), "s": senha.strip(), "d": destino.strip()},
        )

def list_moedas():
    with engine.begin() as c:
        rows = c.execute(text("SELECT simbolo FROM moedas ORDER BY simbolo")).fetchall()
    return [r[0] for r in rows]

def add_moedas_str(raw: str) -> int:
    itens = [x.strip().upper() for x in (raw or "").replace(";", ",").split(",")]
    itens = [x for x in itens if x]
    if not itens:
        return 0
    with engine.begin() as c:
        for s in itens:
            c.execute(
                text("INSERT INTO moedas(simbolo) VALUES (:s) ON CONFLICT (simbolo) DO NOTHING"),
                {"s": s},
            )
    return len(itens)

def add_saida(par: str, lado: str, modo: str, entrada: float, alav: int):
    with engine.begin() as c:
        c.execute(
            text("""
                INSERT INTO saidas (par, lado, modo, entrada, alav)
                VALUES (:par, :lado, :modo, :entrada, :alav)
            """),
            {"par": par, "lado": lado, "modo": modo, "entrada": float(entrada), "alav": int(alav)},
        )

def list_saidas():
    with engine.begin() as c:
        rows = c.execute(
            text("""
                SELECT par, lado, modo, entrada, alav, created_at
                FROM saidas
                ORDER BY id DESC
                LIMIT 200
            """)
        ).fetchall()
    cols = ["PAR", "LADO", "MODO", "ENTRADA", "ALAV", "CRIADA_EM"]
    return pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)

def list_entradas():
    with engine.begin() as c:
        rows = c.execute(
            text("""
                SELECT par, sinal, preco, alvo, ganho, assertividade, data_evento, hora_evento, created_at
                FROM entradas
                ORDER BY id DESC
                LIMIT 200
            """)
        ).fetchall()
    cols = ["PAR","SINAL","PRECO","ALVO","GANHO","ASSERT","DATA","HORA","CRIADA_EM"]
    return pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)

# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Autotrader Dashboard", layout="wide")
st.markdown(
    """
    <style>
    .main {background-color:#0b2a35;}
    h1, h2, h3, .stTabs [data-baseweb="tab"] p {color:#ff7a00 !important;}
    .stButton>button {background:#1677ff; color:white;}
    .success-box {background:#123d2a;padding:10px;border-radius:6px;color:#aaf3c3;}
    .warn-box {background:#2b1f00;padding:10px;border-radius:6px;color:#ffd479;}
    .info-box {background:#0f2747;padding:10px;border-radius:6px;color:#b9d5ff;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Painel do Autotrader")

tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs(["E-MAIL", "MOEDAS", "ENTRADA", "SAÍDA"])

# ------------------------ E-MAIL ------------------------
with tab_email:
    st.header("Configuração de E-mail")
    cfg = get_email_config()
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        remetente = st.text_input("Principal (remetente):", value=cfg["remetente"], placeholder="usuario@exemplo.com")
    with col2:
        senha = st.text_input("Senha (Senha do aplicativo):", value=cfg["senha"], type="password")
    with col3:
        destino = st.text_input("Envio (destinatário):", value=cfg["destino"], placeholder="destinatario@exemplo.com")

    if st.button("TESTAR/SALVAR", type="primary"):
        try:
            save_email_config(remetente, senha, destino)
            st.success("Configuração salva.")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

# ------------------------ MOEDAS ------------------------
with tab_moedas:
    st.header("Painel de Moedas")
    moedas_input = st.text_input("Moeda(s) da Nova (ex: BTC/USDT, ETH/USDT):")
    if st.button("Adicionar Moedas"):
        try:
            qt = add_moedas_str(moedas_input)
            st.success(f"{qt} moeda(s) adicionada(s).")
        except Exception as e:
            st.error(f"Erro ao adicionar moedas: {e}")

    lista = list_moedas()
    if not lista:
        st.info("Nenhuma moeda encontrada no banco de dados. Adicione moedas para monitorar.")
    else:
        st.write(", ".join(lista))

# ------------------------ ENTRADA ------------------------
with tab_entrada:
    st.header("Painel Monitoramento de Entrada")
    df_in = list_entradas()
    if df_in.empty:
        st.info("Nenhum sinal de entrada registrado no banco de dados pelo Worker.")
    else:
        st.dataframe(df_in, use_container_width=True)

# ------------------------ SAÍDA ------------------------
with tab_saida:
    st.header("Painel Monitoramento de Saída")

    with st.form("form_saida", clear_on_submit=False):
        col1, col2, col3, col4, col5 = st.columns([1.2,1,1,1,0.8])

        # Opções de PAR: lista do banco ou fallback
        opcoes_par = list_moedas() or ["BTC/USDT", "ETH/USDT"]
        par = col1.selectbox("Par", options=opcoes_par, index=0)

        lado = col2.selectbox("Lado", options=["LONGO", "SHORT"], index=0)
        modo = col3.selectbox("Modo", options=["Balanço", "Tendência"], index=0)
        entrada_val = col4.number_input("Entrada", value=1.0000, step=0.0001, format="%.4f")
        alav = col5.number_input("Alav.", value=1, min_value=1, max_value=125, step=1)

        submitted = st.form_submit_button("adicionar operação")
        if submitted:
            try:
                add_saida(par, lado, modo, entrada_val, alav)
                st.success("Operação manual adicionada e salva.")
            except Exception as e:
                st.error(f"Erro ao salvar operação: {e}")

    st.subheader("Monitoramento da")
    df = list_saidas()
    if df.empty:
        st.info("Nenhuma operação de saída ou ativa encontrada no banco de dados.")
    else:
        # Formatações rápidas
        if "ENTRADA" in df.columns:
            df["ENTRADA"] = df["ENTRADA"].map(lambda x: f"{float(x):,.3f}")
        st.dataframe(df, use_container_width=True)

    # (Opcional) Auto-refresh leve
    auto = st.toggle("Atualização automática ligada", value=False)
    if auto:
        st.experimental_rerun()
