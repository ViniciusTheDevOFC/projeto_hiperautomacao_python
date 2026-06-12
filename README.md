# 📊 Gerador de Dashboard Dinâmico Otimizado

Uma aplicação interativa desenvolvida em Python com **Streamlit** que permite a qualquer usuário realizar o upload de bases de dados (CSV ou Excel) e construir, de forma 100% visual, múltiplos blocos de gráficos personalizados. Além disso, conta com um sistema inteligente de fechamento e preparação de relatórios prontos para impressão.

---

## 🚀 Funcionalidades da Aplicação

Com base no código estruturado do ecossistema, o projeto entrega:
* **Leitura Inteligente Multiformato:** Suporte nativo para detecção de separadores em arquivos `.csv` e leitura de planilhas `.xls` e `.xlsx`.
* **Visualização da Base:** Aba expansível integrada para conferência dos dados brutos carregados via dataframe.
* **Múltiplos Blocos de Gráficos:** Botões dinâmicos para **Adicionar (`➕ Novo Bloco`)** ou **Remover (`➖ Remover Último`)** visões em tempo real organizadas em Grid (duas colunas).
* **Variedade de Plotagem (Plotly):** Suporte interativo para:
  * Gráfico de Barras
  * Gráfico de Linhas
  * Gráfico de Dispersão
  * Gráfico de Pizza (com contagem automatizada de strings ou soma de valores numéricos).
* **Modo Impressão Exclusivo:** Ativação de caixas de seleção para escolher especificamente quais gráficos gerados farão parte do relatório final, acionando o print nativo do sistema operacional de forma limpa (escondendo botões e menus do Streamlit).

---

## 🛠️ Tecnologias e Dependências

As versões exatas utilizadas para o funcionamento estável desta aplicação são:
* **Python 3.8+**
* **Streamlit** (v1.24.1) - Interface do usuário e reatividade.
* **Pandas** (v2.2.2) - Tratamento e manipulação de matrizes de dados.
* **Plotly** (v5.17.0) - Renderização de gráficos dinâmicos de alta performance.
* **Openpyxl** (v3.1.28) - Engine indispensável para leitura de arquivos Excel modernos.

---

## 📦 Como Rodar a Aplicação em Qualquer Dispositivo

Siga os passos abaixo no terminal para configurar o ambiente e executar o projeto na sua máquina:

### 1. Clonar ou Acessar a Pasta do Projeto
Abra o seu terminal (CMD, PowerShell ou Terminal do Mac/Linux) e navegue até a pasta onde os arquivos estão localizados:
```bash
cd "Caminho/Ate/A/Sua/Pasta/Projeto 5 periodo em python"
2. Configurar o Ambiente Virtual (Recomendado)
Para garantir que as dependências não entrem em conflito com outros projetos, configure a pasta virtual do Python:

No Windows:

Bash
  python -m venv venv
  venv\Scripts\activate
No Linux/Mac:

Bash
  python3 -m venv venv
  source venv/bin/activate