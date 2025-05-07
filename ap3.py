# app.py — Painel de Resultados Laboratoriais Unimed (Corrigido e Completo)
import os
import sys
from datetime import datetime
import unicodedata
from typing import List, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

try:
    from pandasai import SmartDataframe
    from pandasai.llm.openai import OpenAI as OpenAILLM
except ImportError:
    st.error("❌ pandasai não encontrado. Instale com `pip install pandasai openai`. ")
    st.stop()

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.chains import ConversationalRetrievalChain
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
    from langchain.schema import HumanMessage, AIMessage
except ImportError:
    st.error("❌ LangChain ou ChromaDB não encontrados. Instale com `pip install chromadb langchain-core langchain-community langchain-openai`. ")
    st.stop()

os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def debug_log(message: str):
    if st.session_state.get("show_debug"):
        st.sidebar.write(f"DEBUG: {message}")

st.set_page_config(page_title="Painel Unimed", layout="wide")
st.title("📊 Painel de Resultados Laboratoriais – Unimed")

st.sidebar.header("Configurações")
uploaded_file = st.sidebar.file_uploader("📁 Carregar arquivo CSV", type="csv")
st.sidebar.header("Debugging")
st.sidebar.checkbox("Mostrar informações de debug", key="show_debug")
api_key_input = st.sidebar.text_input("🔑 OpenAI API Key (opcional)", type="password", placeholder="sk-...", value=os.getenv("OPENAI_API_KEY", ""))
if api_key_input:
    os.environ["OPENAI_API_KEY"] = api_key_input.strip()
    debug_log("API Key definida pelo usuário")
if uploaded_file is None:
    st.info("Envie o CSV no painel lateral para começar.")
    st.stop()

df = pd.read_csv(uploaded_file)
st.success(f"{len(df):,} registros carregados.")
debug_log(f"Colunas: {df.columns.tolist()}")

_date_cols: List[str] = []
for col in df.columns:
    if df[col].dtype == object:
        try:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="raise")
            _date_cols.append(col)
            debug_log(f"Coluna {col} convertida para datetime")
        except Exception:
            pass
if "data_nascimento" in df.columns and pd.api.types.is_datetime64_any_dtype(df["data_nascimento"]):
    df["idade"] = ((pd.Timestamp.today() - df["data_nascimento"]).dt.days // 365).astype("Int64")
    debug_log("Idade calculada")

def get_sdf():
    if "sdf" not in st.session_state:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("Informe a OpenAI API Key para usar o chat com os dados.")
            return None
        llm = OpenAILLM(api_token=api_key, model_name="gpt-4o-mini", temperature=0)
        st.session_state.sdf = SmartDataframe(df, config={"llm": llm, "conversational": True})
        debug_log("SmartDataframe criado")
    return st.session_state.sdf

def _build_creative_prompt():
    system_template = (
        "Você é um consultor de precificação de planos de saúde com vasta experiência. "
        "Utilize de maneira criativa os dados laboratoriais de pacientes (fornecidos como contexto) "
        "para fundamentar seus argumentos, identificar riscos, tendências de custo e oportunidades de gestão médica. "
        "Seja convincente, estruture sua resposta em tópicos claros, cite números relevantes quando possível e escreva sempre em português brasileiro.\n\n"
        "Se a pergunta não puder ser respondida com base no contexto, explique brevemente e responda de forma geral."
    )
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("Pergunta: {question}"),
        HumanMessagePromptTemplate.from_template("Contexto:\n{context}"),
    ])

def get_rag_chain():
    if "rag_chain" in st.session_state:
        return st.session_state.rag_chain
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("Informe a OpenAI API Key para usar o chat com inteligência.")
        return None
    sample_df = df.head(5000)
    docs = sample_df.astype(str).apply(lambda row: "; ".join(f"{col}: {row[col]}" for col in sample_df.columns), axis=1).tolist()
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=api_key)
    debug_log("Gerando embeddings e criando o vetor store (ChromaDB)…")
    vectorstore = Chroma.from_texts(docs, embedding=embeddings, collection_name="unimed_lab")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 12})
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.3, openai_api_key=api_key)
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": _build_creative_prompt()},
        return_source_documents=False,
        verbose=False,
    )
    st.session_state.rag_chain = chain
    st.session_state.rag_history: List[Tuple[str, str]] = []
    debug_log("RAG chain criado")
    return chain

aba_dash, aba_chat, aba_rag = st.tabs(["📈 Visão Geral", "💬 Chat com os Dados", "🧠 Chat com Inteligência"])

with aba_dash:
    st.subheader("Indicadores‑chave")
    m1, m2, m3, m4 = st.columns(4)
    total_pacientes = df["cpf"].nunique() if "cpf" in df.columns else df.shape[0]
    m1.metric("Total de Pacientes", total_pacientes)
    total_exames = int(df.get("quantidade_exames", pd.Series([df.shape[0]])).sum())
    m2.metric("Total de Exames", total_exames)
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
        for c in _date_cols:
            df_disp[c] = df_disp[c].dt.strftime("%Y-%m-%d")
        gb = GridOptionsBuilder.from_dataframe(df_disp)
        gb.configure_default_column(filterable=True, sortable=True, resizable=True, flex=1, minWidth=120)
        gb.configure_grid_options(domLayout="normal", quickFilter=True)
        for col in df_disp.columns:
            if pd.api.types.is_numeric_dtype(df_disp[col]):
                gb.configure_column(col, filter="agNumberColumnFilter")
            elif col in _date_cols:
                gb.configure_column(col, filter="agDateColumnFilter", filterParams={"browserDatePicker": True})
            else:
                gb.configure_column(col, filter="agTextColumnFilter")
        grid = gb.build()
        grid["localeText"] = {"noRowsToShow": "Sem registros"}
        AgGrid(df_disp, gridOptions=grid, update_mode=GridUpdateMode.NO_UPDATE, height=500)
    except Exception as e:
        st.error(f"AgGrid falhou: {e}")
        st.dataframe(df)

with aba_chat:
    st.subheader("💬 Converse em português com seus dados (PandasAI)")
    sdf = get_sdf()
    if sdf is None:
        st.stop()
    if "messages" not in st.session_state:
        st.session_state.messages: List[dict] = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                if isinstance(msg["content"], pd.DataFrame):
                    st.dataframe(msg["content"])
                elif hasattr(msg["content"], "__class__") and msg["content"].__class__.__name__ in ["Figure", "AxesSubplot"]:
                    st.pyplot(msg["content"])
                else:
                    st.markdown(str(msg["content"]))
    user_prompt = st.chat_input("Pergunte algo, ex.: 'Pacientes com hemoglobina < 13'…")
    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        with st.spinner("Consultando…"):
            try:
                full_prompt = "Responda sempre em português brasileiro. Caso retorne dados tabulares, mostre DataFrame ordenado e limite a 50 linhas. Pergunta: " + user_prompt
                response = sdf.chat(full_prompt)
            except Exception as e:
                response = f"❌ Erro: {e}"
        with st.chat_message("assistant"):
            if isinstance(response, pd.DataFrame):
                st.dataframe(response)
            elif hasattr(response, "__class__") and response.__class__.__name__ in ["Figure", "AxesSubplot"]:
                st.pyplot(response)
            else:
                st.markdown(str(response))
        st.session_state.messages.append({"role": "assistant", "content": response})
    st.info("Dica: tente 'Listar top 5 pacientes com maior glicose'.")

with aba_rag:
    st.subheader("🧠 Converse em português com IA (RAG + ChromaDB)")
    chain = get_rag_chain()
    if chain is None:
        st.stop()
    if "rag_history" not in st.session_state:
        st.session_state.rag_history: List[Tuple[str, str]] = []
    for human, ai in st.session_state.rag_history:
        with st.chat_message("user"):
            st.markdown(human)
        with st.chat_message("assistant"):
            st.markdown(ai)
    rag_prompt = st.chat_input("Faça sua pergunta inteligente, ex.: 'Quais argumentos posso utilizar para aumentar o preço dos planos de saúde?'…", key="rag_input")
    if rag_prompt:
        formatted_history = []
        for human, ai in st.session_state.rag_history:
            formatted_history.append(HumanMessage(content=human))
            formatted_history.append(AIMessage(content=ai))
        with st.chat_message("user"):
            st.markdown(rag_prompt)
        with st.spinner("Pensando…"):
            result = chain.invoke({"question": rag_prompt, "chat_history": formatted_history})
            answer = result["answer"]
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.rag_history.append((rag_prompt, answer))
    st.info("Dica: combine filtros clínicos e estratégicos, ex.: 'Liste pacientes diabéticos acima de 60 anos com hemoglobina glicada alta e explique o impacto financeiro'.")
