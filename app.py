import streamlit as st
import pandas as pd
import datetime
import storage # Módulo para comunicação com o PostgreSQL
import os # Para ler variáveis de ambiente, se necessário

# --- CONFIGURAÇÃO INICIAL E VERIFICAÇÃO ---

# 1. Tenta inicializar o banco de dados (cria as tabelas se não existirem)
storage.initialize_database()

# 2. Configuração da página
st.set_page_config(layout="wide", page_title="Autotrader Dashboard")

# --- CSS CUSTOMIZADO (Seu padrão visual - Nível Profissional) ---
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
        /* Aplicar cor de fundo escura nas células para o contraste */
        color: #e7edf3;
    }
</style>
""", unsafe_allow_html=True)


# --- FUNÇÃO PARA COLORIR SINAIS NAS TABELAS ---
def colorir_sinal(val):
    """Aplica cores para as palavras LONG/SHORT e Ganho/Perda."""
    color = 'white'
    # Sinal (LONG/SHORT)
    if val == 'LONG':
        color = 'lightgreen'
    elif val == 'SHORT':
        color = 'lightcoral'
        
    # PNL (Ganho/Perda) - Assume que a coluna tem valores numéricos
    try:
        if isinstance(val, (int, float)):
            if val > 0:
                color = 'lightgreen'
            elif val < 0:
                color = 'lightcoral'
    except:
        pass # Ignora se não for número

    return f'color: {color}'

# --- CRIAÇÃO DOS PAINÉIS (ABAS) ---
tab_email, tab_moedas, tab_entrada, tab_saida = st.tabs([
    "E-MAIL", "MOEDAS", "ENTRADA", "SAÍDA"
])

# --- PAINEL E-MAIL ---
with tab_email:
    st.header("Configuração de E-mail")
    # Lógica simplificada: usa variáveis de ambiente para o Render

    col1, col2, col3, col4 = st.columns([2.6, 2.6, 2.6, 2.6])

    # Valores iniciais lidos das variáveis de ambiente (se existirem)
    mail_user_default = os.environ.get("MAIL_USER", "usuario@exemplo.com")
    mail_pass_default = os.environ.get("MAIL_PASS", "senha_app_secreta")
    mail_to_default = os.environ.get("MAIL_TO", "destinatario@exemplo.com")

    with col1:
        # Nota: O valor aqui é um placeholder. No Render, as variáveis são lidas de forma segura.
        st.text_input("Principal (remetente):", value=mail_user_default, key="mail_user")
    with col2:
        st.text_input("Senha (App Password):", value=mail_pass_default, type="password", key="mail_pass")
    with col3:
        st.text_input("Envio (destinatário):", value=mail_to_default, key="mail_to")

    btn_col, status_col = st.columns([2.6, 5.2])
    with btn_col:
        if st.button("TESTAR/SALVAR"):
            # Lógica de teste de e-mail e salvamento no DB virá aqui
            st.success("Configuração salva e e-mail de teste enviado (Simulação) ✅")

# --- PAINEL MOEDAS ---
with tab_moedas:
    st.header("Painel de Moedas")

    # Adição de novas moedas
    col1, col2 = st.columns([3, 1])
    with col1:
        new_symbols = st.text_input("Nova(s) moeda(s) (ex: BTC/USDT, ETH/USDT):", placeholder="Adicione símbolos separados por vírgula ou espaço")

    with col2:
        st.write("") 
        st.write("") 
        if st.button("Adicionar Moedas"):
            if new_symbols:
                # Lógica para adicionar moedas no banco de dados (storage) virá aqui
                st.success(f"Moedas {new_symbols} adicionadas para monitoramento.")
            else:
                st.warning("Nenhuma moeda informada.")


    # Dados de moedas lidos do banco de dados (storage.py)
    moedas_df = storage.load_data_for_panel('moedas', limit=100)
    
    # Valida se o DataFrame não está vazio
    if moedas_df.empty:
        st.info("Nenhuma moeda encontrada no banco de dados. Adicione moedas para monitorar.")
    else:
        # Edição e exibição da tabela de moedas
        st.write("Moedas Monitoradas")
        # data_editor permite marcar/desmarcar a coluna 'ativo'
        edited_df = st.data_editor(
            moedas_df, 
            use_container_width=True, 
            hide_index=True,
            column_order=('simbolo', 'ativo', 'observacao', 'created_at')
        ) 
        # Lógica para salvar mudanças no edited_df no DB virá aqui
        
        st.info(f"Total: {len(moedas_df)} pares (ordem por adição)")


# --- PAINEL ENTRADA ---
with tab_entrada:
    st.header("Painel Monitoramento de Entrada")

    # Dados lidos do banco de dados (tabela 'entradas')
    df_entradas = storage.load_data_for_panel('entradas', limit=100)

    if df_entradas.empty:
        st.info("Nenhum sinal de entrada registrado no banco de dados pelo Worker.")
    else:
        # Simplificação do seu modelo: usamos apenas uma tabela, mas separamos visualmente
        # Esta separação pode ser feita com filtros se o DB tiver uma coluna 'modo' (Swing/Posicional)

        # Filtro de exemplo: Simula as duas planilhas do seu print
        df_swing = df_entradas[df_entradas['modo'] == 'AUTO'].head(10)
        df_posicional = df_entradas[df_entradas['modo'] == ' MANUAL'].head(10)
        
        # Função para colorir LONG/SHORT
        def color_by_side(val):
            return [colorir_sinal(v) for v in val]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Entrada 4H - SWING")
            st.dataframe(
                df_swing.style.apply(color_by_side, subset=['side']).applymap(colorir_sinal, subset=['preco_entrada']),
                use_container_width=True, 
                hide_index=True
            )
        with col2:
            st.subheader("Entrada 1H - POSICIONAL")
            st.dataframe(
                df_posicional.style.apply(color_by_side, subset=['side']).applymap(colorir_sinal, subset=['preco_entrada']),
                use_container_width=True, 
                hide_index=True
            )

# --- PAINEL SAÍDA ---
with tab_saida:
    st.header("Painel Monitoramento de Saída")

    st.write("---") 

    # Controles de entrada manual de nova operação
    st.subheader("Adicionar Nova Operação (Manual)")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    # Simplificado para Modos do seu print
    MODOS = ["Swing", "Posicional"] 
    
    with c1:
        st.selectbox("Par", storage.get_active_symbols() or ["BTC/USDT", "ETH/USDT"], index=0)
    with c2:
        st.selectbox("Side", ["LONG", "SHORT"])
    with c3:
        st.selectbox("Modo", MODOS)
    with c4:
        st.number_input("Entrada", value=1.000, format="%.4f")
    with c5:
        st.number_input("Alav.", value=1, min_value=1)
    with c6:
        st.write("")
        st.write("")
        if st.button("Adicionar Operação"):
            st.success("Operação manual adicionada (Lógica de salvamento será implementada aqui)")

    st.write("---") 

    # Tabela de monitoramento
    st.subheader("Monitoramento da Operação")
    
    # Dados lidos do banco de dados (tabela 'saidas')
    df_saidas = storage.load_data_for_panel('saidas', limit=100)

    if df_saidas.empty:
        st.info("Nenhuma operação de saída ou ativa encontrada no banco de dados.")
    else:
        # Aplica a cor LONG/SHORT e PNL%
        st.dataframe(
            df_saidas.style.applymap(colorir_sinal, subset=['side']).applymap(colorir_sinal, subset=['pnl_percent']),
            use_container_width=True, 
            hide_index=True
        )
    st.toggle("Auto-refresh ligado", value=True)
