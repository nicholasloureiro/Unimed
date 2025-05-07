# app.py
# Painel de Resultados Laboratoriais – Unimed (inclui chat com PandasAI)

"""
Versão atualizada
-----------------
* Corrige renderização do histórico do chat – eliminando a impressão do objeto `DeltaGenerator`.
* Uso explícito de blocos `with st.chat_message(...)` para cada mensagem.
* Mensagens agora armazenam apenas `role` e `content` (DataFrame, figura ou texto) – não há mais o papel artificial "data".
* Exibição consolidada dentro do mesmo bloco da mensagem do assistente, suportando textos, DataFrames e figuras.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import unicodedata
import os, sys

# ---------------------------------------------------------------------------
# Integração com PandasAI
# ---------------------------------------------------------------------------
try:
    from pandasai import SmartDataframe
    from pandasai.llm.openai import OpenAI as OpenAILLM
except ImportError:
    st.error("❌ pandasai não encontrado. Instale com `pip install pandasai openai`. ")
    st.stop()

# ---------------------------------------------------------------------------
# Garantir UTF‑8
# ---------------------------------------------------------------------------
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Função de Log
# ---------------------------------------------------------------------------
def debug_log(message: str):
    if st.session_state.get("show_debug"):
        st.sidebar.write(f"DEBUG: {message}")

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Painel Unimed", layout="wide")
st.title("📊 Painel de Resultados Laboratoriais – Unimed")

# ---------------------------------------------------------------------------
# Barra lateral – upload do CSV & Configurações
# ---------------------------------------------------------------------------
st.sidebar.header("Configurações")
uploaded_file = st.sidebar.file_uploader("📁 Carregar arquivo CSV", type="csv")

# Opção para exibir logs de Debug
st.sidebar.header("Debugging")
show_debug = st.sidebar.checkbox("Mostrar informações de debug", key="show_debug")

# Campo para informar a OpenAI API Key (opcional se já estiver em env)
api_key_input = st.sidebar.text_input(
    "🔑 OpenAI API Key (opcional)",
    type="password",
    placeholder="sk-...",
    value=os.getenv("OPENAI_API_KEY", ""),
)
if api_key_input:
    os.environ["OPENAI_API_KEY"] = api_key_input.strip()
    debug_log("API Key definida pelo usuário")

if uploaded_file is None:
    st.info("Envie o CSV no painel lateral para começar.")
    st.stop()

# ---------------------------------------------------------------------------
# Leitura dos dados
# ---------------------------------------------------------------------------
df = pd.read_csv(uploaded_file)
st.success(f"{len(df):,} registros carregados.")
debug_log(f"Colunas: {df.columns.tolist()}")

# Detectar datas
date_cols = []
for col in df.columns:
    if df[col].dtype == object:
        try:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="raise")
            date_cols.append(col)
            debug_log(f"Coluna {col} convertida para datetime")
        except Exception:
            pass

# Calcular idade
if "data_nascimento" in df.columns and pd.api.types.is_datetime64_any_dtype(df["data_nascimento"]):
    df["idade"] = ((pd.Timestamp.today() - df["data_nascimento"]).dt.days // 365).astype("Int64")
    debug_log("Idade calculada")

# ---------------------------------------------------------------------------
# Utilitário
# ---------------------------------------------------------------------------

def normalize_text(s: str) -> str:
    s = str(s).replace("–", "-").replace("—", "-")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").strip()

# ---------------------------------------------------------------------------
# SmartDataframe (lazy)
# ---------------------------------------------------------------------------

def get_sdf() -> "SmartDataframe | None":
    if "sdf" not in st.session_state:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("Informe a OpenAI API Key para usar o chat.")
            return None
        llm = OpenAILLM(api_token=api_key, model_name="gpt-4o-mini", temperature=0)
        st.session_state.sdf = SmartDataframe(df, config={"llm": llm, "conversational": True})
        debug_log("SmartDataframe criado")
    return st.session_state.sdf

# ---------------------------------------------------------------------------
# Layout (abas)
# ---------------------------------------------------------------------------
aba_dash, aba_chat = st.tabs(["📈 Visão Geral", "💬 Chat com os Dados"])

# ---------------------------------------------------------------------------
# VISÃO GERAL
# ---------------------------------------------------------------------------
with aba_dash:
    st.subheader("Indicadores‑chave")
    m1, m2, m3, m4 = st.columns(4)

    # Total de pacientes
    if "cpf" in df.columns:
        total_pacientes = df["cpf"].nunique()
    else:
        total_pacientes = df.shape[0]
    m1.metric("Total de Pacientes", total_pacientes)

    # Total de exames
    total_exames = int(df.get("quantidade_exames", pd.Series([df.shape[0]])).sum())
    m2.metric("Total de Exames", total_exames)

    # Idade média
    idade_media = f"{df['idade'].mean():.1f} anos" if "idade" in df.columns else "–"
    m3.metric("Idade Média", idade_media)

    m4.metric("Atualizado em", datetime.now().strftime("%d/%m/%Y %H:%M"))

    st.divider()
    st.subheader("Exploração Gráfica")

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:
        sel_cols = st.multiselect("Colunas numéricas", numeric_cols, default=numeric_cols[: min(3, len(numeric_cols))])

        if sel_cols:
            if "cpf" in df.columns:
                df["paciente_id"] = df["cpf"].astype(str).str[-5:]
            elif "nome" in df.columns:
                df["paciente_id"] = df["nome"].astype(str).str[-5:]
            else:
                df["paciente_id"] = df.index.astype(str)
            hover = {k: True for k in (set(["nome", "idade"]) & set(df.columns))}
            for col in sel_cols:
                fig = px.bar(df.nlargest(10, col), x="paciente_id", y=col, title=f"Top 10 Pacientes – {col}", hover_data=hover)
                st.plotly_chart(fig, use_container_width=True)
            if len(sel_cols) >= 2:
                st.plotly_chart(px.imshow(df[sel_cols].corr(), text_auto=True, aspect="auto", title="Matriz de Correlação"), use_container_width=True)
    else:
        st.info("Nenhuma coluna numérica.")

    st.divider()
    st.subheader("🔎 Tabela completa")
    try:
        df_disp = df.copy()
        for c in date_cols:
            df_disp[c] = df_disp[c].dt.strftime("%Y-%m-%d")
        gb = GridOptionsBuilder.from_dataframe(df_disp)
        gb.configure_default_column(filterable=True, sortable=True, resizable=True, flex=1, minWidth=120)
        gb.configure_grid_options(domLayout="normal", quickFilter=True)
        for col in df_disp.columns:
            if pd.api.types.is_numeric_dtype(df_disp[col]):
                gb.configure_column(col, filter="agNumberColumnFilter")
            elif col in date_cols:
                gb.configure_column(col, filter="agDateColumnFilter", filterParams={"browserDatePicker": True})
            else:
                gb.configure_column(col, filter="agTextColumnFilter")
        grid = gb.build()
        grid["localeText"] = {"noRowsToShow": "Sem registros"}
        AgGrid(df_disp, gridOptions=grid, update_mode=GridUpdateMode.NO_UPDATE, height=500)
    except Exception as e:
        st.error(f"AgGrid falhou: {e}")
        st.dataframe(df)

# ---------------------------------------------------------------------------
# CHAT
# ---------------------------------------------------------------------------
with aba_chat:
    st.subheader("💬 Converse em português com seus dados")

    sdf = get_sdf()
    if sdf is None:
        st.stop()

    # Inicializar histórico
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Renderizar histórico
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:  # assistant
            with st.chat_message("assistant"):
                if isinstance(msg["content"], pd.DataFrame):
                    st.dataframe(msg["content"])
                elif hasattr(msg["content"], "__class__") and msg["content"].__class__.__name__ in ["Figure", "AxesSubplot"]:
                    st.pyplot(msg["content"])
                else:
                    st.markdown(msg["content"])

    # Entrada do usuário
    user_prompt = st.chat_input("Pergunte algo, ex.: 'Pacientes com hemoglobina < 13'…")
    if user_prompt:
        # Armazenar & mostrar a pergunta
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Consultar PandasAI
        with st.spinner("Consultando…"):
            try:
                full_prompt = (
                    "Responda sempre em português brasileiro. Caso retorne dados tabulares, mostre DataFrame ordenado e limite a 50 linhas. Pergunta: "
                    + user_prompt
                )
                response = sdf.chat(full_prompt)
            except Exception as e:
                response = f"❌ Erro: {e}"

        # Mostrar & armazenar resposta
        with st.chat_message("assistant"):
            if isinstance(response, pd.DataFrame):
                st.dataframe(response)
            elif hasattr(response, "__class__") and response.__class__.__name__ in ["Figure", "AxesSubplot"]:
                st.pyplot(response)
            else:
                st.markdown(str(response))
        st.session_state.messages.append({"role": "assistant", "content": response})

    st.info("Dica: tente 'Listar top 5 pacientes com maior glicose'.")
