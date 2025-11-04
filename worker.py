# ARQUIVO: worker.py (CORREÇÃO FINAL DE SINTAXE)

import datetime
import sys
import os
import storage       
import exchange     

# --- CONFIGURAÇÃO ---
INTERVALO_CRON = "10 minutos"

# --- LÓGICA DE EXECUÇÃO DO WORKER ---

def worker_job():
    """
    Função principal que o Render executa como um Cron Job a cada 10 minutos.
    """
    try:
        print(f"[{datetime.datetime.now()}] >>> Iniciando Worker Job ({INTERVALO_CRON}) <<<")
        
        # 1. Garante que as tabelas do banco de dados existem
        if not storage.initialize_database():
            print("FALHA CRÍTICA: Não foi possível conectar/inicializar o banco de dados. Parando Worker.")
            # Sai com código 1 para que o Render saiba que falhou
            sys.exit(1) 

        # 2. Carrega a lista de moedas que estão marcadas como ATIVAS
        active_symbols = storage.get_active_symbols()
        
        if not active_symbols:
            active_symbols = ["BTC/USDT"] 
            print("Alerta: Nenhuma moeda ativa encontrada no DB. Usando BTC/USDT para teste.")
        
        
        # 3. Itera sobre cada moeda ativa
        for symbol in active_symbols:
            print(f"Processando símbolo: {symbol}")
            current_price = exchange.get_current_price(symbol)
            
            if current_price is None:
                print(f"Pulando {symbol}: Não foi possível obter o preço atual.")
                continue 
            
            # Lógica de sinais e trading será executada aqui
            print(f"Processamento de {symbol} concluído. Preço: {current_price}")
            
        print(f">>> Worker Job finalizado com sucesso. <<<")
        
    except Exception as e:
        # Loga a falha de forma clara no Render Logs
        print(f"ERRO CRÍTICO no Worker: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    worker_job()
