# ARQUIVO: worker.py

import datetime
import sys
import storage       # Nosso módulo de conexão com o banco de dados
import exchange      # Nosso módulo de busca de preços
# import signals     # Módulo para cálculos de sinais (será criado depois)

# --- CONFIGURAÇÃO ---
INTERVALO_CRON = "10 minutos"

# --- LÓGICA DE EXECUÇÃO DO WORKER ---

def worker_job():
    """
    Função principal que o Render executa como um Cron Job.
    """
    print(f"[{datetime.datetime.now()}] >>> Iniciando Worker Job ({INTERVALO_CRON}) <<<")
    
    # 1. Garante que as tabelas do banco de dados existem (Segurança)
    if not storage.initialize_database():
        print("FALHA CRÍTICA: Não foi possível conectar/inicializar o banco de dados.")
        return # Para o Worker se o DB não funcionar

    # 2. Carrega a lista de moedas que estão marcadas como ATIVAS
    active_symbols = storage.get_active_symbols()
    
    if not active_symbols:
        # Se não houver moedas no DB, monitora um padrão (BTC/USDT) para teste
        active_symbols = ["BTC/USDT"] 
        print("Alerta: Nenhuma moeda ativa encontrada no DB. Usando BTC/USDT para teste.")
    
    
    # 3. Itera sobre cada moeda ativa e executa a lógica
    for symbol in active_symbols:
        try:
            print(f"Processando símbolo: {symbol}")
            
            # 3a. COLETAR COTAÇÃO
            current_price = exchange.get_current_price(symbol)
            
            if current_price is None:
                print(f"Skipping {symbol}: Não foi possível obter o preço atual.")
                continue # Pula para a próxima moeda
            
            # 3b. (Próxima etapa) GERAR SINAIS
            # sinal = signals.evaluate(symbol, current_price, history_data)
            
            # 3c. (Próxima etapa) DECISÃO DE ENTRADA/SAÍDA
            # if sinal.entrada: storage.create_entry(...)
            
            print(f"Processamento de {symbol} concluído. Preço: {current_price}")
            
        except Exception as e:
            # Logar exceções específicas (para debugging no Render Logs)
            print(f"ERRO ao processar {symbol}: {e}", file=sys.stderr)
            
    
    print(f">>> Worker Job finalizado com sucesso. <<<")


if __name__ == "__main__":
    worker_job()

# Nota: O worker.py não tem lógica de 'retries' (tentativas de erro) ainda,
# mas isso pode ser adicionado em uma próxima etapa para maior resiliência.
