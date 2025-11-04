# ARQUIVO: storage.py

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

# 1. FUNÇÃO DE CONEXÃO AO BANCO DE DADOS
# A URL do DB é lida de uma variável de ambiente (DATABASE_URL) que o Render fornece.
def get_db_engine():
    """Cria e retorna o motor de conexão ao PostgreSQL."""
    # Garante que a variável DATABASE_URL esteja definida
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERRO: Variável DATABASE_URL não encontrada.")
        # Retorna None para falhar o processo de forma segura
        return None
    
    # Cria o motor (engine) de conexão ao banco de dados
    # O comando "pool_pre_ping=True" ajuda a manter a conexão estável na nuvem
    return create_engine(db_url, pool_pre_ping=True)

# 2. FUNÇÃO DE CRIAÇÃO DAS TABELAS
# Garante que o banco de dados tem as tabelas 'moedas', 'entradas' e 'saidas'
def initialize_database():
    """Cria as tabelas SQL se elas não existirem."""
    engine = get_db_engine()
    if engine is None:
        return False

    try:
        with engine.connect() as connection:
            # Comando SQL para criar a tabela 'moedas' (conforme seu Prompt Mestre)
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS moedas (
                    id SERIAL PRIMARY KEY,
                    simbolo TEXT UNIQUE NOT NULL,
                    ativo BOOLEAN NOT NULL DEFAULT TRUE,
                    observacao TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            # Comando SQL para criar a tabela 'entradas' (conforme seu Prompt Mestre)
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS entradas (
                    id SERIAL PRIMARY KEY,
                    simbolo TEXT NOT NULL,
                    side TEXT CHECK (side IN ('LONG','SHORT')) NOT NULL,
                    preco_entrada NUMERIC (18,8) NOT NULL,
                    alvo NUMERIC(18,8),
                    modo TEXT CHECK (modo IN ('AUTO',' MANUAL')) DEFAULT 'AUTO',
                    assunto TEXT, mensagem TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            # Comando SQL para criar a tabela 'saidas' (conforme seu Prompt Mestre)
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS saidas (
                    id SERIAL PRIMARY KEY,
                    entrada_id INT REFERENCES entradas(id) ON DELETE CASCADE,
                    preco_saida NUMERIC (18,8) NOT NULL,
                    status TEXT, -- 'gain' | 'stop' | 'manual' etc.
                    assunto TEXT, mensagem TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            connection.commit()
        print("Tabelas do banco de dados verificadas/criadas com sucesso.")
        return True
    except SQLAlchemyError as e:
        print(f"ERRO ao inicializar o banco de dados: {e}")
        return False

# 3. FUNÇÃO PARA LER OS DADOS QUE SERÃO MOSTRADOS NO PAINEL
def load_data_for_panel(table_name, limit=500):
    """Carrega dados de uma tabela SQL e retorna um DataFrame do Pandas."""
    engine = get_db_engine()
    if engine is None:
        return pd.DataFrame() # Retorna uma tabela vazia em caso de erro

    try:
        # Comando SQL simples para ler os dados mais recentes
        query = f"SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT {limit}"
        
        # O Pandas é ótimo em ler diretamente do banco de dados (por isso é profissional)
        df = pd.read_sql(query, engine)
        return df
    except SQLAlchemyError as e:
        print(f"ERRO ao carregar dados da tabela '{table_name}': {e}")
        return pd.DataFrame()
        
# 4. FUNÇÃO PARA OBTER AS MOEDAS ATIVAS
def get_active_symbols():
    """Retorna uma lista de moedas ativas para o Worker."""
    engine = get_db_engine()
    if engine is None:
        return []

    try:
        # Busca apenas os símbolos que estão marcados como 'ativo'
        query = "SELECT simbolo FROM moedas WHERE ativo = TRUE ORDER BY simbolo ASC"
        with engine.connect() as connection:
            result = connection.execute(text(query)).fetchall()
            # Transforma o resultado em uma lista simples (ex: ['BTC', 'ETH'])
            return [row[0] for row in result]
    except SQLAlchemyError as e:
        print(f"ERRO ao obter moedas ativas: {e}")
        return []

# Opcional: Adicionar funções para salvar entradas/saídas e moedas ativas aqui.
