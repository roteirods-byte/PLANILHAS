# ARQUIVO: signals.py

import pandas as pd
import pandas_ta as ta

# 1. CLASSE SIMPLES PARA ORGANIZAR O RESULTADO DO SINAL
class Signal:
    """Estrutura para retornar o resultado da análise de sinal."""
    def __init__(self, entry: bool, exit: bool, side: str, message: str):
        self.entrada = entry  # Sinal para entrar em uma posição (LONG ou SHORT)
        self.saida = exit     # Sinal para fechar uma posição
        self.side = side      # LONG ou SHORT
        self.mensagem = message # Descrição do sinal (ex: "MA Crossover Buy")

# 2. FUNÇÃO DE ANÁLISE (MVP - Média Móvel Cruzada)
def evaluate(history_data: pd.DataFrame) -> Signal:
    """
    Avalia a lógica de trade para um determinado conjunto de dados históricos.
    
    Lógica MVP: Média Móvel Curta (MA_S) cruza Média Móvel Longa (MA_L).
    """
    if history_data.empty or 'close' not in history_data.columns:
        return Signal(False, False, "", "Dados históricos insuficientes.")

    # Parâmetros: Média Rápida (10 períodos) e Média Lenta (30 períodos)
    MA_S_PERIOD = 10
    MA_L_PERIOD = 30

    # 1. Calcula as Médias Móveis usando Pandas-TA
    # Nota: Pandas-TA adiciona as novas colunas MA_S e MA_L ao DataFrame
    history_data.ta.sma(close='close', length=MA_S_PERIOD, append=True, col_names=(f'MA_S',))
    history_data.ta.sma(close='close', length=MA_L_PERIOD, append=True, col_names=(f'MA_L',))

    # Pegamos os dois últimos pontos de dados para ver o cruzamento (cross)
    # i = atual; i-1 = anterior
    last_i = history_data.iloc[-1]
    prev_i = history_data.iloc[-2]
    
    # Valores atuais
    ma_s_now = last_i['MA_S']
    ma_l_now = last_i['MA_L']
    
    # Valores anteriores
    ma_s_prev = prev_i['MA_S']
    ma_l_prev = prev_i['MA_L']

    # --- LÓGICA DE SINAL ---
    
    # SINAL DE COMPRA (LONG / ENTRADA): MA Rápida cruza ACIMA da MA Lenta
    if (ma_s_prev <= ma_l_prev) and (ma_s_now > ma_l_now):
        return Signal(True, False, "LONG", f"MA {MA_S_PERIOD} cruzou acima da MA {MA_L_PERIOD}")

    # SINAL DE VENDA (SHORT / ENTRADA): MA Rápida cruza ABAIXO da MA Lenta
    elif (ma_s_prev >= ma_l_prev) and (ma_s_now < ma_l_now):
        return Signal(True, False, "SHORT", f"MA {MA_S_PERIOD} cruzou abaixo da MA {MA_L_PERIOD}")
        
    # SINAL DE SAÍDA: Preço toca uma das médias (pode ser mais complexo, mas aqui é simples)
    elif last_i['close'] < ma_s_now * 0.99 or last_i['close'] > ma_s_now * 1.05:
        return Signal(False, True, "", "Sinal de Saída por preço atual.")
        
    # NENHUM SINAL ATIVO
    return Signal(False, False, "", "Aguardando cruzamento ou nova condição.")
