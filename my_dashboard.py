import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================================================================
# BLOCK 1: CONFIGURATION AND MEMORY (SESSION STATE)
# ==============================================================================

# Configura a página do Streamlit para ocupar toda a largura da tela e define o título da aba
st.set_page_config(page_title="Meu Dashboard Dinâmico", layout="wide")

# O 'session_state' funciona como a memória interna do aplicativo para evitar que as variáveis 
# sejam reiniciadas toda vez que a tela sofrer uma nova renderização (atualização).
if 'num_blocos' not in st.session_state:
    st.session_state.num_blocos = 1  # Controla quantos blocos de gráficos estão abertos na tela

if 'modo_impressao' not in st.session_state:
    st.session_state.modo_impressao = False  # Controla se as caixas de seleção de impressão aparecem

if 'imprimindo' not in st.session_state:
    st.session_state.imprimindo = False  # Define se o usuário está visualizando a tela de impressão limpa

if 'figuras' not in st.session_state:
    st.session_state.figuras = {}  # Um dicionário Python que armazena os objetos de gráficos gerados

if 'blocos_para_imprimir' not in st.session_state:
    st.session_state.blocos_para_imprimir = []  # Lista com os IDs dos gráficos escolhidos para o PDF


# ==============================================================================
# BLOCK 2: INTELLIGENT DATA INGESTION
# ==============================================================================

# O '@st.cache_data' memoriza o processamento do arquivo. Se o usuário mexer nos gráficos,
# o Streamlit não precisará reler a planilha inteira do zero, poupando processamento.
@st.cache_data
def carregar_dados(arquivo):
    """
    Identifica dinamicamente a extensão do arquivo enviado (CSV ou Excel)
    e faz o tratamento correto utilizando o Pandas.
    """
    nome_arquivo = arquivo.name
    
    # Se for CSV, detecta o separador de forma automática (vírgula, ponto e vírgula, etc.)
    if nome_arquivo.endswith('.csv'):
        return pd.read_csv(arquivo, sep=None, engine='python')
    
    # Se for Excel, lê utilizando as estruturas tradicionais de planilhas
    elif nome_arquivo.endswith(('.xls', '.xlsx')):
        return pd.read_excel(arquivo)
        
    return None


# ==============================================================================
# BLOCK 3: DYNAMIC GRAPH COMPONENT
# ==============================================================================

def criar_bloco_grafico(df, numero_do_bloco):
    """
    Função modularizada que constrói de forma independente a interface de escolha,
    a lógica de plotagem e os tratamentos de erro de cada visão de gráfico.
    """
    st.subheader(f"Visão {numero_do_bloco}")
    
    # Se a tela estiver em modo de impressão, recolhe as opções de eixos para o design ficar limpo
    with st.expander(f"⚙️ Configurar Gráfico {numero_do_bloco}", expanded=not st.session_state.modo_impressao):
        colunas = df.columns.tolist() # Captura o nome das colunas da planilha carregada
        
        # Caixas de seleção individuais. O parâmetro 'key' garante que um elemento não anule o outro
        tipo_grafico = st.selectbox("Tipo", options=["Gráfico de Barras", "Gráfico de Linhas", "Gráfico de Dispersão", "Gráfico de Pizza"], index=None, placeholder="Escolha o Tipo de Gráfico...", label_visibility="collapsed", key=f"tipo_{numero_do_bloco}")
        eixo_x = st.selectbox("Eixo X", options=colunas, index=None, placeholder="Escolha a coluna para o Eixo X...", label_visibility="collapsed", key=f"x_{numero_do_bloco}")
        eixo_y = st.selectbox("Eixo Y", options=colunas, index=None, placeholder="Escolha a coluna para o Eixo Y...", label_visibility="collapsed", key=f"y_{numero_do_bloco}")

    # Variável booleana que confere se o usuário preencheu todas as informações do gráfico
    grafico_pronto = bool(tipo_grafico and eixo_x and eixo_y)

    if grafico_pronto:
        try:
            # Estrutura condicional para direcionar a biblioteca Plotly Express com base na escolha do usuário
            if tipo_grafico == "Gráfico de Barras":
                fig = px.bar(df, x=eixo_x, y=eixo_y, title=f"{eixo_y} por {eixo_x}")
            elif tipo_grafico == "Gráfico de Linhas":
                fig = px.line(df, x=eixo_x, y=eixo_y, title=f"Evolução de {eixo_y} ao longo de {eixo_x}")
            elif tipo_grafico == "Gráfico de Dispersão":
                fig = px.scatter(df, x=eixo_x, y=eixo_y, title=f"Dispersão: {eixo_x} vs {eixo_y}")
            elif tipo_grafico == "Gráfico de Pizza":
                # Lógica Inteligente para Gráfico de Pizza:
                # Se o eixo Y selecionado for numérico, faz a divisão proporcional tradicional
                if pd.api.types.is_numeric_dtype(df[eixo_y]):
                    fig = px.pie(df, names=eixo_x, values=eixo_y, title=f"Distribuição de {eixo_y} por {eixo_x}")
                # Se não for numérico (ex: texto), faz a contagem de repetições automática antes de plotar
                else:
                    contagem = df[eixo_x].value_counts().reset_index()
                    contagem.columns = [eixo_x, 'Quantidade']
                    fig = px.pie(contagem, names=eixo_x, values='Quantidade', title=f"Quantidade de registros por {eixo_x}")
            
            # Renderiza o gráfico do Plotly na tela ajustando ao tamanho da coluna
            st.plotly_chart(fig, use_container_width=True)
            
            # Salva o objeto gráfico na memória global para uso posterior na tela de impressão
            st.session_state.figuras[numero_do_bloco] = fig
            
        except Exception as e:
            # Tratamento preventivo caso o usuário cruze tipos de dados incompatíveis (ex: texto com texto no gráfico de linha)
            st.error("Ajuste os eixos para gerar este gráfico corretamente.")
            grafico_pronto = False
    else:
        # Exibe um aviso amigável enquanto o usuário não seleciona os filtros
        st.info("👆 Selecione as opções acima para gerar este gráfico.")
        if numero_do_bloco in st.session_state.figuras:
            del st.session_state.figuras[numero_do_bloco]

    # Se o modo de impressão estiver ligado, exibe uma caixinha de marcar logo abaixo do gráfico
    if st.session_state.modo_impressao:
        st.checkbox(f"🖨️ Selecionar Visão {numero_do_bloco} para impressão", key=f"print_{numero_do_bloco}", disabled=not grafico_pronto)


# ==============================================================================
# BLOCK 4: CORE SCREEN APPLICATION LOGIC
# ==============================================================================

# --- SUB-BLOCO A: TELA DE IMPRESSÃO LIMPA ---
if st.session_state.imprimindo:
    
    # Injeta CSS nativo na aplicação para ocultar os cabeçalhos, rodapés do Streamlit e botões na hora do papel/PDF
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
    
    # Botão para voltar à visualização padrão do sistema redefinindo as memórias do app
    if st.button("⬅️ Voltar ao Dashboard"):
        st.session_state.imprimindo = False
        st.session_state.modo_impressao = False 
        st.session_state.blocos_para_imprimir = [] 
        st.rerun() # Recarrega a tela imediatamente aplicando o reset
        
    st.markdown("---")
    
    # Laço de repetição que busca apenas os gráficos marcados pelo usuário e reconstrói na tela limpa
    for i in st.session_state.blocos_para_imprimir:
        st.subheader(f"Visão {i}")
        st.plotly_chart(st.session_state.figuras[i], use_container_width=True)
        st.markdown("---")

    # Injeta um script em JavaScript para acionar automaticamente a janela de impressão/salvar em PDF do Windows após 1 segundo
    st.components.v1.html("<script>setTimeout(function() { window.parent.print(); }, 1000);</script>", height=0)


# --- SUB-BLOCO B: TELA PRINCIPAL (DASHBOARD BUILDER) ---
else:
    st.title("📊 Gerador de Dashboard Dinâmico - Otimizado")
    
    # Componente visual para carregar o arquivo
    arquivo_carregado = st.file_uploader("Suba sua base de dados (CSV ou Excel) para começar", type=["csv", "xlsx", "xls"])

    if arquivo_carregado is not None:
        df = carregar_dados(arquivo_carregado)
        
        if df is not None:
            # Exibe uma tabela interativa opcional contendo os dados crus da planilha
            with st.expander("Ver todos os dados carregados"):
                st.dataframe(df)

            st.markdown("---")
            
            # Cria 4 colunas horizontais para organizar os botões de ação do painel administrativo
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
                # Modifica dinamicamente a cor e texto do botão dependendo do estado atual da ação
                texto_botao_print = "❌ Cancelar Impressão" if st.session_state.modo_impressao else "🖨️ Modo Impressão"
                if st.button(texto_botao_print, use_container_width=True):
                    st.session_state.modo_impressao = not st.session_state.modo_impressao
                    st.rerun()

            # Painel informativo e de validação final da impressão
            if st.session_state.modo_impressao:
                st.info("Marque o 'X' embaixo dos gráficos que deseja e clique no botão abaixo para gerar o relatório.")
                
                if st.button("✅ Confirmar e Abrir Impressão do Windows", type="primary"):
                    selecionados = []
                    # Varre todos os blocos verificando quais checkboxes foram marcados como True
                    for i in range(1, st.session_state.num_blocos + 1):
                        if st.session_state.get(f"print_{i}", False):
                            selecionados.append(i)
                            
                    if selecionados:
                        st.session_state.blocos_para_imprimir = selecionados
                        st.session_state.imprimindo = True # Ativa a mudança de tela para o Sub-bloco A
                        st.rerun()
                    else:
                        st.warning("Você precisa marcar o 'X' em pelo menos um gráfico pronto para poder imprimir!")

            st.markdown("---")
            
            # --- LÓGICA DE GRID EM DUAS COLUNAS ---
            # O laço de repetição avança de 2 em 2 (step=2) para criar pares de colunas na horizontal
            for i in range(1, st.session_state.num_blocos + 1, 2):
                col1, col2 = st.columns(2)
                with col1:
                    criar_bloco_grafico(df, i) # Renderiza o gráfico ímpar na esquerda
                if i + 1 <= st.session_state.num_blocos:
                    with col2:
                        criar_bloco_grafico(df, i + 1) # Se houver um par correspondente, joga na direita

    else:
        # Estado inicial do sistema enquanto a memória aguarda o upload do arquivo
        st.info("Aguardando o upload da sua planilha...")