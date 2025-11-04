import streamlit as st
import pandas as pd
import datetime
import os
os.makedirs("data", exist_ok=True)

# Configuração da página
st.set_page_config(layout="wide", page_title="Autotrader Dashboard")

# --- CSS CUSTOMIZADO ---
# (Copiado do PROMPT-MESTRE e adaptado)
st.markdown("""
<style>
    /* Fundo principal e texto */
    .stApp {
        background-color: #0b2533;
        color: #e7edf3;
    }

    /* Cor dos títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #ff7b1b !important;
    }

    /* --- ESTILO DAS ABAS (TABS) --- */
    /* Cor do texto da aba selecionada e não selecionada */
    .stTabs [data-baseweb="tab-list"] button p {
        color: #e7edf3 !important; /* Cor do texto das abas normais */
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
        color: #ff7b1b !important; /* Cor Laranja para aba ATIVA */
        font-weight: bold;
    }
    /* Borda inferior da aba selecionada */
    .stTabs [data-baseweb="tab-list"] .st-emotion-cache-12fmjuu {
        background-color: #ff7b1b !important; /* Cor da linha/borda da aba ATIVA */
    }

    /* Estilo dos inputs e botões para replicar o modelo */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        width: 260px !important;
        height: 40px;
    }
    .stButton button {
        width: 260px !important;
        height: 40px;
        background-color: #007bff; /* Cor do botão Testar/Salvar */
        color: white;
    }

    /* Estilo para as tabelas (DataFrames) */
    .stDataFrame {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# --- CRIAÇÃO DOS PAINÉIS (ABAS) ---
tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs([
    "E-MAIL", "MOEDAS", "ENTRADA", "SAÍDA"
])

# --- PAINEL E-MAIL ---
with tab_email:
    st.header("Configuração de E-mail")

    # Layout com colunas para alinhar os campos
    col1, col2, col3, col4 = st.columns([2.6, 2.6, 2.6, 2.6]) # Proporções para espaçamento

    with col1:
        st.text_input("Principal (remetente):", value="roteiro.ds@gmail.com", key="mail_user")
    with col2:
        st.text_input("Senha (App Password):", value="••••••••••••••••", type="password", key="mail_pass")
    with col3:
        st.text_input("Envio (destinatário):", value="jtiroch@hotmail.com", key="mail_to")

    # Botão e status na mesma linha
    btn_col, status_col = st.columns([2.6, 5.2]) # Botão ocupa menos espaço que o status
    with btn_col:
        if st.button("TESTAR/SALVAR"):
            # Lógica de teste virá aqui
            st.success("Configuração salva e e-mail de teste enviado ✅")
            # st.error("Falha ao enviar e-mail: [detalhe do erro]")

# --- PAINEL MOEDAS ---
with tab_moedas:
    st.header("Painel de Moedas")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Nova(s) moeda(s) (ex: BTC, ETH, SOL):", placeholder="Adicione símbolos separados por vírgula ou espaço")

    with col2:
        st.write("") # Espaçamento
        st.write("") # Espaçamento
        st.button("Adicionar")

    # Dados de exemplo para a tabela de moedas
    moedas_data = {
        'Símbolo': ['AAVE', 'ADA', 'APT', 'ARB', 'ATOM', 'AVAX', 'AXS', 'BCH'],
        'Ativo': [True, True, False, True, True, False, True, True],
        'Observação': ['DeFi', 'Layer 1', 'Layer 1', 'Layer 2', 'Cosmos Hub', 'Layer 1', 'Gaming', 'Fork do BTC']
    }
    moedas_df = pd.DataFrame(moedas_data)

    st.write("Moedas Monitoradas")
    st.data_editor(moedas_df, use_container_width=True, hide_index=True) # data_editor permite edição
    st.info("Total: 8 pares (ordem alfabética)")


# --- PAINEL ENTRADA ---
with tab_entrada:
    st.header("Painel Monitoramento de Entrada")

    # Dados de exemplo
    data_entrada_swing = {
        "PAR": ["AAVE", "ADA", "ARB", "ATOM", "AVAX"],
        "SINAL": ["NÃO ENTRAR", "NÃO ENTRAR", "SHORT", "SHORT", "SHORT"],
        "PREÇO": [81.767, 123.105, 86.613, 20.741, 91.193],
        "ALVO": [0.0, 125.784, 80.412, 19.685, 85.944],
        "GANHO%": [0.00, 2.18, -7.16, -5.09, -5.76],
        "ASSERT%": [58.00, 62.00, 58.00, 61.00, 61.00],
        "DATA": ["2025-10-06"] * 5,
        "HORA": ["05:04:09"] * 5
    }
    df_entrada_swing = pd.DataFrame(data_entrada_swing)

    data_entrada_posicional = {
        "PAR": ["AAVE", "ADA", "ARB", "ATOM", "AVAX"],
        "SINAL": ["NÃO ENTRAR", "NÃO ENTRAR", "SHORT", "SHORT", "SHORT"],
        "PREÇO": [62.434, 61.062, 76.573, 55.862, 172.125],
        "ALVO": [0.0, 62.391, 71.092, 53.019, 162.218],
        "GANHO%": [0.00, 2.18, -7.16, -5.09, -5.76],
        "ASSERT%": [58.00, 62.00, 58.00, 61.00, 61.00],
        "DATA": ["2025-10-06"] * 5,
        "HORA": ["05:04:10"] * 5
    }
    df_entrada_posicional = pd.DataFrame(data_entrada_posicional)

    # Função para colorir
    def colorir_sinal(val):
        color = 'white'
        if val == 'LONG':
            color = 'lightgreen'
        elif val == 'SHORT':
            color = 'lightcoral'
        return f'color: {color}'

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Entrada 4H - SWING")
        st.dataframe(df_entrada_swing.style.applymap(colorir_sinal, subset=['SINAL']), use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Entrada 1H - POSICIONAL")
        st.dataframe(df_entrada_posicional.style.applymap(colorir_sinal, subset=['SINAL']), use_container_width=True, hide_index=True)

# --- PAINEL SAÍDA ---
with tab_saida:
    st.header("Painel Monitoramento de Saída")

    st.write("---") # Linha divisória

    # Controles de entrada de nova operação
    st.subheader("Adicionar Nova Operação")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.selectbox("Par", ["BTC", "ETH", "SOL"], index=0)
    with c2:
        st.selectbox("Side", ["LONG", "SHORT"])
    with c3:
        st.selectbox("Modo", ["Swing-friendly", "Posicional"])
    with c4:
        st.number_input("Entrada", value=1.220, format="%.3f")
    with c5:
        st.number_input("Alav.", value=5)
    with c6:
        st.write("")
        st.write("")
        st.button("Adicionar Operação")

    st.write("---") # Linha divisória

    # Tabela de monitoramento
    st.subheader("Monitoramento da Operação")
    data_saida = {
        "PAR": ["BTC", "FET"],
        "SIDE": ["SHORT", "LONG"],
        "MODO": ["Swing-friendly", "Posicional"],
        "ENTRADA": [1.220, 4.202],
        "PREÇO ATUAL": [1.215, 4.250],
        "ALVO": [1.100, 4.500],
        "PNL%": [-0.41, 1.14],
        "SITUAÇÃO": ["Aberta", "Aberta"],
        "DATA": ["2025-09-26", "2025-09-26"],
        "HORA": ["09:03:43", "09:04:05"],
        "ALAV": [50, 125],
    }
    df_saida = pd.DataFrame(data_saida)
    st.dataframe(df_saida.style.applymap(colorir_sinal, subset=['SIDE']), use_container_width=True, hide_index=True)
    st.toggle("Auto-refresh ligado", value=True)
