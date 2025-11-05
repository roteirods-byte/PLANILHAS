import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

DB_URL = os.getenv("DATABASE_URL") or os.getenv("URL_DO_BANCO_DE_DADOS")
if not DB_URL:
    raise RuntimeError("Defina DATABASE_URL (ou URL_DO_BANCO_DE_DADOS)")

engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    poolclass=QueuePool,
    pool_recycle=300,
)

def initialize_database():
    ddl = """
    CREATE TABLE IF NOT EXISTS moedas(
        id SERIAL PRIMARY KEY,
        simbolo TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS entradas(
        id SERIAL PRIMARY KEY,
        par TEXT NOT NULL,
        sinal TEXT,
        preco NUMERIC(18,6),
        alvo NUMERIC(18,6),
        ganho NUMERIC(9,2),
        assertividade NUMERIC(9,2),
        data DATE,
        hora TIME
    );

    CREATE TABLE IF NOT EXISTS saidas(
        id SERIAL PRIMARY KEY,
        par TEXT NOT NULL,
        lado TEXT NOT NULL,
        modo TEXT NOT NULL,
        entrada NUMERIC(18,6) NOT NULL,
        alav INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))

def list_moedas():
    with engine.begin() as c:
        rows = c.execute(text("SELECT simbolo FROM moedas ORDER BY simbolo")).fetchall()
    return [r[0] for r in rows]

def add_moedas_str(s: str) -> int:
    # aceita “BTC/USDT, ETH/USDT” etc
    itens = [x.strip().upper() for x in (s or "").replace(";", ",").split(",")]
    itens = [x for x in itens if x]
    if not itens:
        return 0
    with engine.begin() as c:
        for simb in itens:
            c.execute(
                text("INSERT INTO moedas(simbolo) VALUES (:s) ON CONFLICT (simbolo) DO NOTHING"),
                {"s": simb},
            )
    return len(itens)

def add_saida(par, lado, modo, entrada, alav):
    with engine.begin() as c:
        c.execute(
            text("""INSERT INTO saidas (par, lado, modo, entrada, alav)
                    VALUES (:par,:lado,:modo,:entrada,:alav)"""),
            {"par": par, "lado": lado, "modo": modo, "entrada": float(entrada), "alav": int(alav)},
        )

def list_saidas():
    with engine.begin() as c:
        return c.execute(
            text("""SELECT par,lado,modo,entrada,alav,created_at
                    FROM saidas ORDER BY id DESC LIMIT 100""")
        ).fetchall()
