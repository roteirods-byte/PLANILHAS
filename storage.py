# storage.py
import os
from typing import Iterable, Optional
from sqlalchemy import create_engine, text
import pandas as pd

# --- conexão -----------------------------------------------------------------
DB_URL = os.getenv("DATABASE_URL") or os.getenv("URL_DO_BANCO_DE_DADOS")
if not DB_URL:
    raise RuntimeError("DATABASE_URL/URL_DO_BANCO_DE_DADOS não definida")

engine = create_engine(DB_URL, pool_pre_ping=True, future=True)

# --- migração idempotente (ajusta o schema se precisar) ----------------------
def ensure_schema() -> None:
    ddl = """
    -- Tabela de moedas (precisa ter a coluna 'par')
    CREATE TABLE IF NOT EXISTS moedas (
        par TEXT PRIMARY KEY
    );

    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
             WHERE table_name = 'moedas' AND column_name = 'par'
        ) THEN
            ALTER TABLE moedas ADD COLUMN par TEXT;
        END IF;
    END $$;

    CREATE UNIQUE INDEX IF NOT EXISTS ix_moedas_par ON moedas(par);

    -- Entradas manuais (opcional para seus painéis)
    CREATE TABLE IF NOT EXISTS entradas (
        id SERIAL PRIMARY KEY,
        par TEXT NOT NULL,
        lado TEXT NOT NULL,           -- LONG | SHORT
        modo TEXT NOT NULL,           -- Balanço | etc
        entrada NUMERIC(18,6) NOT NULL,
        alav INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    -- Saídas / monitoramento
    CREATE TABLE IF NOT EXISTS saídas (
        id SERIAL PRIMARY KEY,
        par TEXT NOT NULL,
        lado TEXT NOT NULL,
        modo TEXT NOT NULL,
        entrada NUMERIC(18,6) NOT NULL,
        atual   NUMERIC(18,6),
        alvo    NUMERIC(18,6),
        pnl     NUMERIC(12,6),
        situacao TEXT,
        data DATE,
        hora TIME,
        alav INTEGER NOT NULL DEFAULT 1,
        ativo BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with engine.begin() as con:
        con.execute(text(ddl))

# --- funções usadas pelos painéis --------------------------------------------
def db_list_moedas(limit: Optional[int] = None) -> pd.DataFrame:
    sql = "SELECT par FROM moedas ORDER BY par ASC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    return pd.read_sql(sql, engine)

def db_add_moedas(pares: Iterable[str]) -> int:
    pares = [p.strip().upper() for p in pares if p.strip()]
    if not pares:
        return 0
    ins = text("INSERT INTO moedas(par) VALUES (:p) ON CONFLICT (par) DO NOTHING")
    with engine.begin() as con:
        for p in pares:
            con.execute(ins, {"p": p})
    return len(pares)

def db_add_saida_manual(par: str, lado: str, modo: str, entrada: float, alav: int) -> None:
    sql = text("""
        INSERT INTO saídas (par, lado, modo, entrada, alav, ativo)
        VALUES (:par, :lado, :modo, :entrada, :alav, TRUE)
    """)
    with engine.begin() as con:
        con.execute(sql, {"par": par.upper(), "lado": lado, "modo": modo, "entrada": float(entrada), "alav": int(alav)})

def db_list_saidas_ativas(limit: int = 100) -> pd.DataFrame:
    sql = """
        SELECT par, lado, modo, entrada, atual, alvo, pnl, situacao, data, hora, alav
          FROM saídas
         WHERE ativo = TRUE
         ORDER BY created_at DESC
         LIMIT :n
    """
    return pd.read_sql(text(sql), engine, params={"n": int(limit)})

# chamamos na importação
ensure_schema()
