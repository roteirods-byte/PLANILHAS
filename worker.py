# ARQUIVO: worker.py

import datetime
import sys
import os
import storage       # Módulo de conexão com o banco de dados (SQLAlchemy)
import exchange      # Módulo de busca de preços (CCXT)
# import signals     # Módulo para cálculos de sinais (Adicionado em passos anteriores)

# --- CONFIGURAÇÃO ---
# Corrigida a sintaxe da constante de tempo que causava o erro
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
            return # Parar se o DB não funcionar

        # 2. Carrega a lista de moedas que estão marcadas como ATIVAS
        active_symbols = storage.get_active_symbols()
        
        if not active_symbols:
            # Moeda padrão para teste se o DB estiver vazio
            active_symbols = ["BTC/USDT"] 
            print("Alerta: Nenhuma moeda ativa encontrada no DB. Usando BTC/USDT para teste.")
        
        
        # 3. Itera sobre cada moeda ativa e executa a lógica
        for symbol in active_symbols:
            print(f"Processando símbolo: {symbol}")
            
            # 3a. COLETAR COTAÇÃO
            current_price = exchange.get_current_price(symbol)
            
            if current_price is None:
                print(f"Pulando {symbol}: Não foi possível obter o preço atual.")
                continue 
            
            # 3b. (Próxima etapa) GERAR SINAIS - Integração do signals.py
            # Exemplo: sinal = signals.evaluate_simple(history_data)
            
            # 3c. DECISÃO DE ENTRADA/SAÍDA - Se houver um sinal, a lógica de storage.py salva.
            
            print(f"Processamento de {symbol} concluído. Preço: {current_price}")
            
        
        # 4. (Falta implementar) Envio de E-mail de resumo
            
        print(f">>> Worker Job finalizado com sucesso. <<<")
        
    except Exception as e:
        # Logar exceções no Render Logs para debugging
        print(f"ERRO CRÍTICO no Worker: {e}", file=sys.stderr)
        # Retorna 1 para indicar falha ao Render
        sys.exit(1)


if __name__ == "__main__":
    worker_job()
