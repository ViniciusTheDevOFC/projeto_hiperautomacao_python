import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Meu Dashboard Dinâmico", layout="wide")

# --- INICIALIZAÇÃO DA MEMÓRIA (SESSION STATE) ---
if 'num_blocos' not in st.session_state:
    st.session_state.num_blocos = 1
if 'modo_impressao' not in st.session_state:
    st.session_state.modo_impressao = False
if 'imprimindo' not in st.session_state:
    st.session_state.imprimindo = False
if 'figuras' not in st.session_state:
    st.session_state.figuras = {}
if 'blocos_para_imprimir' not in st.session_state:
    st.session_state.blocos_para_imprimir = []

# 2. Função inteligente para carregar dados
@st.cache_data
def carregar_dados(arquivo):
    nome_arquivo = arquivo.name
    if nome_arquivo.endswith('.csv'):
        return pd.read_csv(arquivo, sep=None, engine='python')
    elif nome_arquivo.endswith(('.xls', '.xlsx')):
        return pd.read_excel(arquivo)
    return None

# 3. Criação dos Blocos Individuais de Gráfico
def criar_bloco_grafico(df, numero_do_bloco):
    st.subheader(f"Visão {numero_do_bloco}")
    
    with st.expander(f"⚙️ Configurar Gráfico {numero_do_bloco}", expanded=not st.session_state.modo_impressao):
        colunas = df.columns.tolist()
        
        tipo_grafico = st.selectbox("Tipo", options=["Gráfico de Barras", "Gráfico de Linhas", "Gráfico de Dispersão", "Gráfico de Pizza"], index=None, placeholder="Escolha o Tipo de Gráfico...", label_visibility="collapsed", key=f"tipo_{numero_do_bloco}")
        eixo_x = st.selectbox("Eixo X", options=colunas, index=None, placeholder="Escolha a coluna para o Eixo X...", label_visibility="collapsed", key=f"x_{numero_do_bloco}")
        eixo_y = st.selectbox("Eixo Y", options=colunas, index=None, placeholder="Escolha a coluna para o Eixo Y...", label_visibility="collapsed", key=f"y_{numero_do_bloco}")

    grafico_pronto = bool(tipo_grafico and eixo_x and eixo_y)

    if grafico_pronto:
        try:
            if tipo_grafico == "Gráfico de Barras":
                fig = px.bar(df, x=eixo_x, y=eixo_y, title=f"{eixo_y} por {eixo_x}")
            elif tipo_grafico == "Gráfico de Linhas":
                fig = px.line(df, x=eixo_x, y=eixo_y, title=f"Evolução de {eixo_y} ao longo de {eixo_x}")
            elif tipo_grafico == "Gráfico de Dispersão":
                fig = px.scatter(df, x=eixo_x, y=eixo_y, title=f"Dispersão: {eixo_x} vs {eixo_y}")
            elif tipo_grafico == "Gráfico de Pizza":
                if pd.api.types.is_numeric_dtype(df[eixo_y]):
                    fig = px.pie(df, names=eixo_x, values=eixo_y, title=f"Distribuição de {eixo_y} por {eixo_x}")
                else:
                    contagem = df[eixo_x].value_counts().reset_index()
                    contagem.columns = [eixo_x, 'Quantidade']
                    fig = px.pie(contagem, names=eixo_x, values='Quantidade', title=f"Quantidade de registros por {eixo_x}")
            
            st.plotly_chart(fig, use_container_width=True)
            st.session_state.figuras[numero_do_bloco] = fig
            
        except Exception as e:
            st.error("Ajuste os eixos para gerar este gráfico corretamente.")
            grafico_pronto = False
    else:
        st.info("👆 Selecione as opções acima para gerar este gráfico.")
        if numero_do_bloco in st.session_state.figuras:
            del st.session_state.figuras[numero_do_bloco]

    if st.session_state.modo_impressao:
        st.checkbox(f"🖨️ Selecionar Visão {numero_do_bloco} para impressão", key=f"print_{numero_do_bloco}", disabled=not grafico_pronto)


# ==========================================
# LÓGICA PRINCIPAL DA TELA
# ==========================================

if st.session_state.imprimindo:
    
    st.markdown("""
        <style>
        @media print {
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stButton {display: none;}
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🖨️ Relatório de Impressão")
    
    # --- A CORREÇÃO FOI FEITA AQUI ---
    if st.button("⬅️ Voltar ao Dashboard"):
        st.session_state.imprimindo = False
        st.session_state.modo_impressao = False # <--- Desliga o botão de impressão!
        st.session_state.blocos_para_imprimir = [] # <--- Limpa os "X" que foram marcados
        st.rerun()
        
    st.markdown("---")
    
    for i in st.session_state.blocos_para_imprimir:
        st.subheader(f"Visão {i}")
        st.plotly_chart(st.session_state.figuras[i], use_container_width=True)
        st.markdown("---")

    st.components.v1.html("<script>setTimeout(function() { window.parent.print(); }, 1000);</script>", height=0)

else:
    st.title("📊 Gerador de Dashboard Dinâmico - Otimizado")
    arquivo_carregado = st.file_uploader("Suba sua base de dados (CSV ou Excel) para começar", type=["csv", "xlsx", "xls"])

    if arquivo_carregado is not None:
        df = carregar_dados(arquivo_carregado)
        
        if df is not None:
            with st.expander("Ver todos os dados carregados"):
                st.dataframe(df)

            st.markdown("---")
            
            col_btn_add, col_btn_rem, col_btn_print, _ = st.columns([2, 2, 2, 2]) 
            
            with col_btn_add:
                if st.button("➕ Novo Bloco", use_container_width=True):
                    st.session_state.num_blocos += 1
                    st.rerun()
                    
            with col_btn_rem:
                if st.session_state.num_blocos > 1:
                    if st.button("➖ Remover Último", use_container_width=True):
                        st.session_state.num_blocos -= 1
                        st.rerun()
            
            with col_btn_print:
                # O botão agora reflete o estado correto da memória
                texto_botao_print = "❌ Cancelar Impressão" if st.session_state.modo_impressao else "🖨️ Modo Impressão"
                if st.button(texto_botao_print, use_container_width=True):
                    st.session_state.modo_impressao = not st.session_state.modo_impressao
                    st.rerun()

            if st.session_state.modo_impressao:
                st.info("Marque o 'X' embaixo dos gráficos que deseja e clique no botão abaixo para gerar o relatório.")
                
                # O botão de confirmar impressão!
                if st.button("✅ Confirmar e Abrir Impressão do Windows", type="primary"):
                    selecionados = []
                    for i in range(1, st.session_state.num_blocos + 1):
                        if st.session_state.get(f"print_{i}", False):
                            selecionados.append(i)
                            
                    if selecionados:
                        st.session_state.blocos_para_imprimir = selecionados
                        st.session_state.imprimindo = True
                        st.rerun()
                    else:
                        st.warning("Você precisa marcar o 'X' em pelo menos um gráfico pronto para poder imprimir!")

            st.markdown("---")
            
            for i in range(1, st.session_state.num_blocos + 1, 2):
                col1, col2 = st.columns(2)
                with col1:
                    criar_bloco_grafico(df, i)
                if i + 1 <= st.session_state.num_blocos:
                    with col2:
                        criar_bloco_grafico(df, i + 1)

    else:
        st.info("Aguardando o upload da sua planilha...")