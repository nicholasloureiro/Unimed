# app.py
# Painel de Resultados Laboratoriais – Unimed (com gráficos de barras mostrando últimos 5 caracteres e top 10 pacientes)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import unicodedata
import os, sys

# Garantir UTF‑8
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Adicionar Log para debug
# ---------------------------------------------------------------------------
def debug_log(message):
    st.sidebar.write(f"DEBUG: {message}")

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Painel Unimed", layout="wide")
st.title("📊 Painel de Resultados Laboratoriais – Unimed")

# ---------------------------------------------------------------------------
# Barra lateral – upload do CSV
# ---------------------------------------------------------------------------
st.sidebar.header("Configurações")

uploaded_file = st.sidebar.file_uploader("📁 Carregar arquivo CSV", type="csv")
if uploaded_file is None:
    st.info("Envie o CSV no painel lateral para começar.")
    st.stop()

# ---------------------------------------------------------------------------
# Debugging
# ---------------------------------------------------------------------------
st.sidebar.header("Debugging")
show_debug = st.sidebar.checkbox("Mostrar informações de debug")

# ---------------------------------------------------------------------------
# Leitura dos dados
# ---------------------------------------------------------------------------
df = pd.read_csv(uploaded_file)
st.success(f"{len(df):,} registros carregados com sucesso.")

if show_debug:
    debug_log(f"Colunas no DataFrame: {df.columns.tolist()}")
    debug_log(f"Tipos das colunas: {df.dtypes.to_dict()}")

# Detectar colunas de data
date_cols = []
for col in df.columns:
    if isinstance(df[col].dtype, pd.api.types.CategoricalDtype) or df[col].dtype == object:
        try:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="raise")
            date_cols.append(col)
            if show_debug:
                debug_log(f"Convertida coluna {col} para data")
        except Exception as e:
            if show_debug:
                debug_log(f"Falha ao converter {col} para data: {str(e)}")
            pass

# Calcular idade se existir coluna de nascimento
if "data_nascimento" in df.columns and pd.api.types.is_datetime64_any_dtype(df["data_nascimento"]):
    nasc = df["data_nascimento"]
    df["idade"] = ((pd.Timestamp.today() - nasc).dt.days // 365).astype("Int64")
    if show_debug:
        debug_log("Idade calculada com sucesso")

# ---------------------------------------------------------------------------
# Funções utilitárias
# ---------------------------------------------------------------------------
def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ")
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    return s.strip()

# ---------------------------------------------------------------------------
# Layout de abas
# ---------------------------------------------------------------------------
aba_dashboard, = st.tabs(["📈 Visão Geral"])

# ---------------------------------------------------------------------------
# Aba 1 – Dashboard
# ---------------------------------------------------------------------------
with aba_dashboard:
    st.subheader("Indicadores‑chave")
    m1, m2, m3, m4 = st.columns(4)

    try:
        if "cpf" in df.columns:
            total_pacientes = len(pd.Series(df["cpf"]).drop_duplicates())
            if show_debug:
                debug_log("Calculado total_pacientes com drop_duplicates")
        else:
            total_pacientes = df.shape[0]
            if show_debug:
                debug_log("Coluna CPF não encontrada, usando shape[0]")
    except Exception as e:
        total_pacientes = df.shape[0]
        if show_debug:
            debug_log(f"Erro ao calcular total_pacientes: {str(e)}")

    m1.metric("Total de Pacientes", total_pacientes)

    try:
        total_exames = int(df.get("quantidade_exames", pd.Series([df.shape[0]])).sum())
        if show_debug:
            debug_log(f"Total de exames calculado: {total_exames}")
    except Exception as e:
        total_exames = df.shape[0]
        if show_debug:
            debug_log(f"Erro ao calcular total_exames: {str(e)}")
    
    m2.metric("Total de Exames", total_exames)

    try:
        if "idade" in df.columns and df["idade"].notna().any():
            idade_media = f"{df['idade'].mean():.1f} anos"
            if show_debug:
                debug_log(f"Idade média calculada: {idade_media}")
        else:
            idade_media = "–" 
            if show_debug:
                debug_log("Coluna idade não encontrada ou todos valores são NA")
    except Exception as e:
        idade_media = "–"
        if show_debug:
            debug_log(f"Erro ao calcular idade média: {str(e)}")
            
    m3.metric("Idade Média", idade_media)

    m4.metric("Atualizado em", datetime.now().strftime("%d/%m/%Y %H:%M"))

    st.divider()
    st.subheader("Exploração Gráfica")

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if show_debug:
        debug_log(f"Colunas numéricas: {numeric_cols}")
        
    if numeric_cols:
        sel_cols = st.multiselect("Colunas numéricas para visualizar (barras)", numeric_cols, default=numeric_cols[: min(3, len(numeric_cols))])

        if "cpf" in df.columns:
            df["paciente_id"] = df["cpf"].astype(str).str[-5:]
            group_col = "paciente_id"
        elif "nome" in df.columns:
            df["paciente_id"] = df["nome"].astype(str).str[-5:]
            group_col = "paciente_id"
        else:
            df["paciente_id"] = df.index.astype(str)
            group_col = "paciente_id"

        hover_data = {}
        if "nome" in df.columns:
            hover_data["nome"] = True
        if "idade" in df.columns:
            hover_data["idade"] = True

        for col in sel_cols:
            try:
                top_df = df.nlargest(10, col)
                fig = px.bar(
                    top_df,
                    x=group_col,
                    y=col,
                    title=f"Top 10 Pacientes - {col}",
                    hover_data=hover_data
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar gráfico de barras para {col}: {str(e)}")
                if show_debug:
                    debug_log(f"Detalhes do erro gráfico: {str(e)}")

        if len(sel_cols) >= 2:
            try:
                corr = df[sel_cols].corr()
                st.plotly_chart(px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale="viridis", title="Matriz de Correlação"), use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar matriz de correlação: {str(e)}")
                if show_debug:
                    debug_log(f"Detalhes do erro de correlação: {str(e)}")
    else:
        st.info("Nenhuma coluna numérica encontrada para gerar gráficos.")

    st.divider()
    st.subheader("🔎 Tabela completa – filtro e busca em tempo real")

    try:
        df_display = df.copy()
        for c in date_cols:
            df_display[c] = df_display[c].dt.strftime("%Y-%m-%d")

        gb = GridOptionsBuilder.from_dataframe(df_display)
        gb.configure_default_column(filterable=True, sortable=True, resizable=True, minWidth=120, flex=1)
        gb.configure_grid_options(domLayout="normal", quickFilter=True)

        for col in df_display.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                gb.configure_column(col, filter="agNumberColumnFilter")
            elif col in date_cols:
                gb.configure_column(col, filter="agDateColumnFilter", filterParams={"browserDatePicker": True})
            else:
                gb.configure_column(col, filter="agTextColumnFilter")

        grid_options = gb.build()
        grid_options["localeText"] = {
            "searchOoo": "Pesquisar…",
            "noRowsToShow": "Sem registros para exibir",
            "columns": "Colunas",
            "filters": "Filtros",
            "applyFilter": "Aplicar Filtro",
            "resetFilter": "Limpar Filtro",
            "equals": "Igual a",
            "notEqual": "Diferente de",
            "lessThan": "Menor que",
            "lessThanOrEqual": "Menor ou igual a",
            "greaterThan": "Maior que",
            "greaterThanOrEqual": "Maior ou igual a",
            "inRange": "Entre",
            "contains": "Contém",
            "notContains": "Não contém",
            "startsWith": "Começa com",
            "endsWith": "Termina com",
            "blank": "Em branco",
            "notBlank": "Não em branco",
            "between": "Entre",
        }

        AgGrid(df_display, gridOptions=grid_options, update_mode=GridUpdateMode.NO_UPDATE, enable_enterprise_modules=False, height=500, fit_columns_on_grid_load=False)
    except Exception as e:
        st.error(f"Erro ao renderizar AgGrid: {str(e)}")
        if show_debug:
            debug_log(f"Detalhes do erro AgGrid: {str(e)}")
        st.dataframe(df_display)