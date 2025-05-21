import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# import json # Not actively used, can be removed if not needed later
import collections
from datetime import datetime

from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_openai import ChatOpenAI
from ai_data_science_team import PandasDataAnalyst, DataWranglingAgent, DataVisualizationAgent

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Painel Inteligente Unimed",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🩺"
)

# --- STYLING ---
st.markdown("""
    <style>
        /* Base colors */
        :root {
            --primary-color: #007f3e; /* Unimed Green */
            --secondary-color: #006633; /* Darker Green */
            --background-color: #f0f2f6; /* Light grey background */
            --card-background-color: #ffffff;
            --text-color: #333333;
            --sidebar-background-color: #e8f5e9; /* Lighter green for sidebar */
        }
        body, .stApp { background-color: var(--background-color); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .stApp > header { background-color: var(--primary-color); color: white; }
        .stApp > header .st-emotion-cache-1avcm0n { color: white; }
        h1, h2, h3 { color: var(--primary-color); }
        .st-emotion-cache-16txtl3 { background-color: var(--sidebar-background-color); }
        .st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 .st-emotion-cache-10oheav { color: var(--secondary-color); }
        .stMetric { background-color: var(--card-background-color); border-radius: 8px; padding: 15px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .stMetric label { color: var(--secondary-color) !important; font-weight: bold; }
        .stMetric .st-emotion-cache-1wivap2 { font-size: 2em !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: var(--card-background-color); border-radius: 4px 4px 0px 0px; padding: 10px 20px; color: var(--secondary-color); }
        .stTabs [aria-selected="true"] { background-color: var(--primary-color); color: white; font-weight: bold; }
        .stExpander { border: 1px solid #e0e0e0; border-radius: 8px; background-color: var(--card-background-color); }
        .stExpander header { background-color: #f9f9f9; color: var(--primary-color); font-weight: bold; }
        .stDataFrame { width: 100%; }
        .stTextInput input, .stSelectbox select, .stDateInput input { border-radius: 5px; }
        .custom-card { background-color: var(--card-background-color); padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; height: 100%; }
        .custom-card h5 { color: var(--primary-color); margin-top: 0px; margin-bottom: 8px; font-size: 1.1em; }
        .custom-card p.value { font-size: 1.8em; font-weight: bold; color: var(--secondary-color); margin-bottom: 5px; }
        .custom-card p.help-text { font-size: 0.9em; color: #555555; margin-bottom: 0px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #007f3e;'>🩺 Painel de IA para Resultados Laboratoriais Unimed</h1>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.image("unimed-removebg-preview.png", width=350)
    st.markdown("<h2 style='color: #006633;'>🔐 Configuração da IA</h2>", unsafe_allow_html=True)
    api_key = st.text_input("Chave da API da OpenAI", type="password", help="Insira sua chave da API OpenAI.")
    model_option = st.selectbox("Modelo OpenAI", ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"], index=0)
    st.markdown("<h2 style='color: #006633;'>📁 Upload de Dados</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Escolha um arquivo CSV:", type=["csv"], help="CSV com resultados e colunas '_status'.")

if not api_key:
    st.warning("🔑 Insira sua chave da API OpenAI na barra lateral.")
    st.stop()

llm = None
pandas_data_analyst = None
if api_key:
    try:
        llm = ChatOpenAI(model=model_option, api_key=api_key, temperature=0.3)
        data_wrangling_agent = DataWranglingAgent(model=llm, bypass_recommended_steps=True, log=False)
        data_visualization_agent = DataVisualizationAgent(model=llm, log=False)
        pandas_data_analyst = PandasDataAnalyst(model=llm, data_wrangling_agent=data_wrangling_agent, data_visualization_agent=data_visualization_agent)
    except Exception as e:
        st.error(f"Erro ao inicializar modelos de IA: {e}")
        st.stop()

if not uploaded_file:
    st.info("⬆️ Envie um arquivo CSV para prosseguir.")
    st.stop()

@st.cache_data
def load_data(file):
    df_loaded = pd.read_csv(file)
    df_loaded.columns = df_loaded.columns.str.lower().str.replace(' ', '_')
    if "data_nascimento" in df_loaded.columns:
        df_loaded["data_nascimento"] = pd.to_datetime(df_loaded["data_nascimento"], errors="coerce")
        current_year = datetime.now().year
        df_loaded["idade"] = df_loaded["data_nascimento"].apply(lambda x: current_year - x.year if pd.notnull(x) and x.year > 1900 else None)
    elif "idade" not in df_loaded.columns:
        st.warning("Coluna 'data_nascimento' ou 'idade' não encontrada.")
        df_loaded["idade"] = None
    
    status_cols_local = [col for col in df_loaded.columns if col.endswith("_status")]
    # Using a fixed list of markers internally, consistent with how ALTERATION_MARKERS will be defined globally
    internal_markers = ["↑", "↓", "Alto", "Baixo", "Aumentado", "Diminuído", "Positivo"]
    if status_cols_local:
        df_loaded["paciente_com_alteracao"] = df_loaded[status_cols_local].apply(lambda row: row.isin(internal_markers).any(), axis=1)
        df_loaded["qtde_exames_alterados"] = df_loaded[status_cols_local].apply(lambda row: sum(row.isin(internal_markers)), axis=1)
    else:
        df_loaded["paciente_com_alteracao"] = False
        df_loaded["qtde_exames_alterados"] = 0
        st.warning("Nenhuma coluna '_status' encontrada.")
    return df_loaded, status_cols_local

try:
    df, status_cols = load_data(uploaded_file)
except Exception as e:
    st.error(f"Erro ao carregar ou processar o arquivo: {e}")
    st.stop()

# --- FIX 1: Define ALTERATION_MARKERS globally ---
ALTERATION_MARKERS = ["↑", "↓", "Alto", "Baixo", "Aumentado", "Diminuído", "Positivo"]

if not status_cols and uploaded_file:
    st.error("Nenhuma coluna de status (terminada em '_status') foi encontrada. Verifique o CSV.")

def calculate_top_altered_exams(dataframe, status_column_list, markers):
    if dataframe.empty or not status_column_list:
        return pd.DataFrame(columns=["Exame", "Número de Alterações"])
    alteracoes = collections.Counter()
    for col in status_column_list:
        if col in dataframe.columns:
            exam_name = col.replace("_status", "").replace("_", " ").title()
            alteracoes[exam_name] += dataframe[col].isin(markers).sum()
    if alteracoes:
        df_top_altered = pd.DataFrame.from_dict(alteracoes, orient="index", columns=["Número de Alterações"])
        df_top_altered = df_top_altered.sort_values(by="Número de Alterações", ascending=False).reset_index().rename(columns={"index": "Exame"})
        return df_top_altered[df_top_altered["Número de Alterações"] > 0]
    return pd.DataFrame(columns=["Exame", "Número de Alterações"])

top_alterados_df_global = calculate_top_altered_exams(df, status_cols, ALTERATION_MARKERS)

# Note: The 'markers' parameter in generate_dynamic_insights is not used by its current internal logic,
# but kept for signature consistency if calls provide it.
def generate_dynamic_insights(current_df, current_status_cols, current_top_alterados_df, markers_unused):
    insights_list = []
    THRESHOLD_MULTIPLE_ALTERATIONS = 3
    if current_df.empty:
        for i in range(6): insights_list.append({"title": f"Insight {i+1} Indisponível", "value": "N/A", "help": "Dados insuficientes."})
        return insights_list
    total_pacientes = len(current_df)
    if "paciente_com_alteracao" in current_df.columns:
        pacientes_com_alt = current_df['paciente_com_alteracao'].sum()
        percent_com_alt = (pacientes_com_alt / total_pacientes * 100) if total_pacientes > 0 else 0
        insights_list.append({"title": "Taxa de Alteração Geral", "value": f"{pacientes_com_alt}/{total_pacientes} ({percent_com_alt:.1f}%)", "help": "Pacientes com ≥1 exame alterado."})
    else: insights_list.append({"title": "Taxa de Alteração Geral", "value": "N/A", "help": "Info 'paciente_com_alteracao' indisponível."})

    if "qtde_exames_alterados" in current_df.columns:
        multiple_alt_count = current_df[current_df['qtde_exames_alterados'] >= THRESHOLD_MULTIPLE_ALTERATIONS].shape[0]
        percent_multiple_alt = (multiple_alt_count / total_pacientes * 100) if total_pacientes > 0 else 0
        insights_list.append({"title": f"Alerta: ≥{THRESHOLD_MULTIPLE_ALTERATIONS} Alterações", "value": f"{multiple_alt_count} ({percent_multiple_alt:.1f}%)", "help": f"Pacientes com ≥{THRESHOLD_MULTIPLE_ALTERATIONS} exames alterados."})
    else: insights_list.append({"title": f"Alerta: ≥{THRESHOLD_MULTIPLE_ALTERATIONS} Alterações", "value": "N/A", "help": "Info 'qtde_exames_alterados' indisponível."})

    if not current_top_alterados_df.empty:
        insights_list.append({"title": "Principal Exame Alterado", "value": f"{current_top_alterados_df['Exame'].iloc[0]}", "help": f"{current_top_alterados_df['Número de Alterações'].iloc[0]} ocorrências."})
    else: insights_list.append({"title": "Principal Exame Alterado", "value": "N/A", "help": "Sem dados de exames alterados."})

    if "idade" in current_df.columns and current_df["idade"].notna().any() and "paciente_com_alteracao" in current_df.columns:
        avg_age_with_alt = current_df[current_df['paciente_com_alteracao'] & current_df['idade'].notna()]['idade'].mean()
        avg_age_without_alt = current_df[~current_df['paciente_com_alteracao'] & current_df['idade'].notna()]['idade'].mean()
        val_with_alt = f"{avg_age_with_alt:.1f}a" if pd.notna(avg_age_with_alt) else "N/D"
        val_without_alt = f"{avg_age_without_alt:.1f}a" if pd.notna(avg_age_without_alt) else "N/D"
        insights_list.append({"title": "Idade Média (Com/Sem Alter.)", "value": f"{val_with_alt} / {val_without_alt}", "help": "Média idade: c/ alteração vs. s/ alteração."})
    else: insights_list.append({"title": "Idade Média e Alterações", "value": "N/A", "help": "Dados de idade/alterações insuficientes."})

    if "idade" in current_df.columns and current_df["idade"].notna().any() and "paciente_com_alteracao" in current_df.columns:
        youngest_series = current_df[current_df['paciente_com_alteracao'] & current_df['idade'].notna()]['idade']
        insights_list.append({"title": "Alerta Jovem c/ Alteração", "value": f"{youngest_series.min():.0f}a" if not youngest_series.empty else "N/A", "help": "Paciente mais jovem c/ alteração."})
    else: insights_list.append({"title": "Alerta Jovem c/ Alteração", "value": "N/A", "help": "Dados insuficientes."})
        
    if "idade" in current_df.columns and current_df["idade"].notna().any() and "paciente_com_alteracao" in current_df.columns:
        oldest_series = current_df[current_df['paciente_com_alteracao'] & current_df['idade'].notna()]['idade']
        insights_list.append({"title": "Alerta Idoso c/ Alteração", "value": f"{oldest_series.max():.0f}a" if not oldest_series.empty else "N/A", "help": "Paciente mais idoso c/ alteração."})
    else: insights_list.append({"title": "Alerta Idoso c/ Alteração", "value": "N/A", "help": "Dados insuficientes."})
    return insights_list[:6]

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visão Geral e Filtros", "🤖 Chat Analítico", "📋 Dados com AgGrid", "💡 Insights Dinâmicos (IA)"
])

with tab1:
    st.markdown("## 🩺 Panorama dos Resultados Laboratoriais")
    st.markdown("Explore os dados e filtre por diversos critérios.")
    with st.container(border=True):
        st.subheader("Resumo Geral (Dataset Completo)")
        # --- FIX 2: Correct call to generate_dynamic_insights ---
        dynamic_insights = generate_dynamic_insights(df, status_cols, top_alterados_df_global, ALTERATION_MARKERS)
        if dynamic_insights:
            row1_cols, row2_cols = st.columns(3), st.columns(3)
            for i, insight in enumerate(dynamic_insights):
                target_col = row1_cols[i] if i < 3 else row2_cols[i-3]
                with target_col:
                    st.markdown(f"<div class='custom-card'><h5>{insight['title']}</h5><p class='value'>{insight['value']}</p><p class='help-text'>{insight['help']}</p></div>", unsafe_allow_html=True)
        else: st.info("Não foi possível gerar insights para o dataset completo.")

    st.markdown("### 🔬 Filtros Detalhados e Visualizações")
    df_filtrado_tab1 = df.copy()
    with st.expander("🔬 Ajuste os Filtros:", expanded=True):
        col_filt1, col_filt2 = st.columns([1, 2])
        with col_filt1: # Age, Sex, Num Alterations filters (ensure df_filtrado_tab1 is updated)
            if "idade" in df_filtrado_tab1.columns and df_filtrado_tab1["idade"].notna().any():
                idade_min, idade_max = int(df_filtrado_tab1["idade"].dropna().min()), int(df_filtrado_tab1["idade"].dropna().max())
                if idade_min < idade_max:
                    faixa_idade = st.slider("Faixa Etária:", idade_min, idade_max, (idade_min, idade_max), key="t1_idade")
                    df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["idade"].between(faixa_idade[0], faixa_idade[1])]
            if "sexo" in df_filtrado_tab1.columns and df_filtrado_tab1["sexo"].notna().any():
                sexo_opts = ["Todos"] + sorted(df_filtrado_tab1["sexo"].dropna().unique())
                if len(sexo_opts) > 1:
                    sexo_sel = st.radio("Sexo:", sexo_opts, horizontal=True, key="t1_sexo")
                    if sexo_sel != "Todos": df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["sexo"] == sexo_sel]
            if "qtde_exames_alterados" in df_filtrado_tab1.columns and df_filtrado_tab1["qtde_exames_alterados"].notna().any():
                min_a, max_a = 0, int(df_filtrado_tab1["qtde_exames_alterados"].max())
                if max_a > 0 and min_a < max_a:
                    num_alt_range = st.slider("Qtde Exames Alterados:", min_a, max_a, (min_a, max_a), key="t1_qtde_alt")
                    df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["qtde_exames_alterados"].between(num_alt_range[0], num_alt_range[1])]

        with col_filt2: # Specific exam filters
            exam_names_clean = [col.replace("_status", "").replace("_", " ").title() for col in status_cols]
            sel_exam_names = st.multiselect("Selecionar Exames:", options=exam_names_clean, key="t1_sel_exames", disabled=not status_cols)
            sel_exam_status_cols = [status_cols[exam_names_clean.index(name)] for name in sel_exam_names]

        if sel_exam_status_cols:
            st.markdown("##### Filtros Avançados por Exame:")
            filt_stat, filt_val = {}, {}
            num_cols_filt, col_idx = min(len(sel_exam_status_cols), 3), 0
            filter_cols_dyn = st.columns(num_cols_filt)
            for ex_stat_col in sel_exam_status_cols:
                ex_base, ex_disp = ex_stat_col.removesuffix("_status"), ex_stat_col.replace("_status", "").replace("_", " ").title()
                with filter_cols_dyn[col_idx % num_cols_filt]:
                    uniq_stat = df_filtrado_tab1[ex_stat_col].dropna().unique()
                    if len(uniq_stat) > 0:
                        stat_opts = ["Todos"] + [p for p in ALTERATION_MARKERS if p in uniq_stat] + sorted([o for o in uniq_stat if o not in ALTERATION_MARKERS])
                        stat_sel = st.radio(f"Status {ex_disp}:", stat_opts, key=f"t1_{ex_base}_stat", horizontal=True)
                        filt_stat[ex_stat_col] = stat_sel
                    if ex_base in df_filtrado_tab1.columns and pd.api.types.is_numeric_dtype(df_filtrado_tab1[ex_base]) and df_filtrado_tab1[ex_base].notna().any():
                        min_v, max_v = float(df_filtrado_tab1[ex_base].dropna().min()), float(df_filtrado_tab1[ex_base].dropna().max())
                        if min_v < max_v:
                            val_r = st.slider(f"Valores {ex_disp}:", min_v, max_v, (min_v, max_v), step=(max_v - min_v)/100 or 0.1, key=f"t1_{ex_base}_range")
                            filt_val[ex_base] = val_r
                col_idx +=1
            for ex_s_col, s_sel in filt_stat.items():
                if s_sel != "Todos": df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1[ex_s_col] == s_sel]
            for ex_b, (min_v_f, max_v_f) in filt_val.items():
                df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1[ex_b].between(min_v_f, max_v_f)]
    
    with st.container(border=True):
        st.subheader(f"Resultados Filtrados ({len(df_filtrado_tab1)} Pacientes)")
        if df_filtrado_tab1.empty: st.warning("Nenhum paciente corresponde aos filtros.")
        else:
            cols_base = [c for c in ["nome", "codigo_os", "sexo", "idade", "qtde_exames_alterados"] if c in df_filtrado_tab1.columns]
            cols_dyn_disp = []
            for es_col_disp in sel_exam_status_cols:
                eb_disp = es_col_disp.removesuffix("_status")
                if eb_disp in df_filtrado_tab1.columns: cols_dyn_disp.append(eb_disp)
                if es_col_disp in df_filtrado_tab1.columns: cols_dyn_disp.append(es_col_disp)
            st.dataframe(df_filtrado_tab1[list(dict.fromkeys(cols_base + cols_dyn_disp))], height=300, use_container_width=True)
            
            st.markdown("##### Análise Visual (Dados Filtrados)")
            viz_c1, viz_c2 = st.columns(2)
            with viz_c1:
                if "qtde_exames_alterados" in df_filtrado_tab1.columns and df_filtrado_tab1["qtde_exames_alterados"].notna().any() and df_filtrado_tab1["qtde_exames_alterados"].nunique() > 0:
                    fig_hist = px.histogram(df_filtrado_tab1, x="qtde_exames_alterados", title="Distribuição Nº Exames Alterados", labels={"qtde_exames_alterados": "Qtde Exames Alterados"}, color_discrete_sequence=["#007f3e"], marginal="rug")
                    mean_val_hist = df_filtrado_tab1["qtde_exames_alterados"].mean()
                    fig_hist.add_vline(x=mean_val_hist, line_dash="dash", line_color="firebrick", annotation_text=f"Média: {mean_val_hist:.1f}")
                    st.plotly_chart(fig_hist, use_container_width=True)
                else: st.info("Histograma de qtde. alterações indisponível para dados filtrados.")
            
            with viz_c2:
                # --- FIX 3: Use calculate_top_altered_exams and ALTERATION_MARKERS ---
                if not df_filtrado_tab1.empty and sel_exam_status_cols:
                    top_alt_filt_df = calculate_top_altered_exams(df_filtrado_tab1, sel_exam_status_cols, ALTERATION_MARKERS)
                    if not top_alt_filt_df.empty:
                        fig_bar = px.bar(top_alt_filt_df, x="Número de Alterações", y="Exame", orientation='h', title="Exames Selecionados Mais Alterados", labels={"Exame":"Exame"}, color_discrete_sequence=["#007f3e"], text_auto=True)
                        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Nº Pacientes com Alteração")
                        st.plotly_chart(fig_bar, use_container_width=True)
                    else: st.info("Nenhuma alteração nos exames selecionados (filtrado).")
                elif not sel_exam_status_cols: st.info("Selecione exames para ver gráfico de alterações.")
            
            # Additional visualizations like Age Distribution, Correlation Matrix, Scatter Plot
            # Ensure they correctly use df_filtrado_tab1 and ALTERATION_MARKERS where applicable.
            # (Code for these plots omitted for brevity but should be reviewed for df_filtrado_tab1 usage)
with tab2: # Or st if you are not using tabs for testing
    st.markdown("## 🤖 Chat Analítico com IA (Dados Atuais da Aba 1)")
    st.markdown("Faça perguntas sobre os dados **visíveis na Aba 1 (aplicando os filtros)**. A IA pode ajudar a realizar análises, gerar tabelas e gráficos, entendendo linguagem natural e termos médicos comuns.")

    data_for_tab2_chat = df_filtrado_tab1.copy()

    if data_for_tab2_chat.empty and not df.empty:
        st.info("Os filtros atuais na Aba 1 resultaram em nenhum dado. O chat abaixo operará sobre o conjunto de dados completo.")
        data_for_tab2_chat = df.copy()
    elif data_for_tab2_chat.empty and df.empty:
        st.error("Nenhum dado carregado para o chat.")
        st.stop()

    # Generate data context for the AI
    data_context_for_ai = data_for_tab2_chat

    with st.container(border=True):
        msgs_tab2 = StreamlitChatMessageHistory(key="langchain_unimed_messages_tab2_v2") # Changed key to avoid conflicts if rerunning
        if "plots_tab2" not in st.session_state:
            st.session_state.plots_tab2 = []
        if "dataframes_tab2" not in st.session_state:
            st.session_state.dataframes_tab2 = []

        if len(msgs_tab2.messages) == 0:
            initial_message_tab2 = "Olá! Sou sua assistente de IA para análise de dados. "
            if data_for_tab2_chat.equals(df) and not df_filtrado_tab1.empty and not df.empty:
                 initial_message_tab2 += "Estou analisando os dados **gerais** (nenhum filtro ativo ou os filtros resultaram em todos os dados). Como posso ajudar?"
            elif data_for_tab2_chat.equals(df) and (df_filtrado_tab1.empty or df.empty):
                 initial_message_tab2 += "Estou analisando os dados **gerais** (os filtros não retornaram dados ou nenhum dado foi carregado inicialmente, então usando o dataset completo, se disponível). Como posso ajudar?"
            else:
                 initial_message_tab2 += "Estou analisando os dados **filtrados** da Aba 1. Como posso ajudar?"
            msgs_tab2.add_ai_message(initial_message_tab2)


        def display_chat_history_tab2():
            for i, msg in enumerate(msgs_tab2.messages):
                with st.chat_message(msg.type):
                    if isinstance(msg.content, str) and "PLOT_INDEX_TAB2:" in msg.content: # Check type
                        try:
                            parts = msg.content.split("PLOT_INDEX_TAB2:")
                            text_content = parts[0]
                            if text_content.strip(): # Display text before plot if any
                                st.markdown(text_content)
                            idx = int(parts[1])
                            st.plotly_chart(st.session_state.plots_tab2[idx], use_container_width=True)
                        except (IndexError, ValueError, TypeError) as e:
                            st.error(f"Erro ao exibir gráfico: {e}. Conteúdo: {msg.content}")
                            if isinstance(msg.content, str):
                                st.markdown(msg.content.split("PLOT_INDEX_TAB2:")[0] if "PLOT_INDEX_TAB2:" in msg.content else msg.content)
                    elif isinstance(msg.content, str) and "DATAFRAME_INDEX_TAB2:" in msg.content: # Check type
                        try:
                            parts = msg.content.split("DATAFRAME_INDEX_TAB2:")
                            text_content = parts[0]
                            if text_content.strip(): # Display text before dataframe if any
                                st.markdown(text_content)
                            idx = int(parts[1])
                            st.dataframe(st.session_state.dataframes_tab2[idx], use_container_width=True)
                        except (IndexError, ValueError, TypeError) as e:
                            st.error(f"Erro ao exibir DataFrame: {e}. Conteúdo: {msg.content}")
                            if isinstance(msg.content, str):
                                st.markdown(msg.content.split("DATAFRAME_INDEX_TAB2:")[0] if "DATAFRAME_INDEX_TAB2:" in msg.content else msg.content)
                    else:
                        st.markdown(msg.content)

        display_chat_history_tab2()

        if not pandas_data_analyst:
            st.error("Agente de IA (Pandas Analyst) não inicializado. Verifique a chave da API ou a configuração.")
        elif question_tab2 := st.chat_input("Descreva o que você quer analisar ou qual informação busca... (Ex: 'Qual a média de idade dos pacientes com CID I10?')", key="chat_input_tab2_v2"):
            msgs_tab2.add_user_message(question_tab2)
            # Display user message immediately - this was missing and improves UX
            with st.chat_message("human"):
                 st.markdown(question_tab2)

            with st.spinner("👩‍⚕️ A IA está analisando os dados e preparando sua resposta..."):
                try:
                    if data_for_tab2_chat.empty:
                        st.error("Não há dados para a IA analisar. Verifique seus filtros ou o arquivo carregado.")
                        msgs_tab2.add_ai_message("Não há dados para analisar. Por favor, verifique os filtros ou o arquivo carregado.")
                        st.rerun() # Use rerun after adding message
                    else:
                        # --- ENHANCED PROMPT ---
                        system_prompt = f"""Você é um assistente de IA especializado em analisar dados, com foco em informações da área da saúde e médicas.
Seja o mais prestativo possível. Use linguagem clara e objetiva.
Seja flexível com a linguagem natural do usuário, incluindo termos médicos comuns em Português do Brasil.
Quando apropriado, gere tabelas (dataframes) ou gráficos (plotly charts) para ilustrar suas respostas.
para plotly charts, traduza as informações do gráfico para Português do Brasil e utilize o background
Se uma pergunta for ambígua ou se você precisar de mais detalhes para respondê-la corretamente, peça esclarecimentos ao usuário.

{data_context_for_ai}

Baseado no contexto acima e nos dados fornecidos, responda à seguinte pergunta do usuário:
"""
                        full_user_instructions = f"{system_prompt}\n\nPergunta do usuário: {question_tab2}"

                        # Make a fresh copy for the agent to avoid unintended modifications
                        agent_data = data_for_tab2_chat.copy()
                        pandas_data_analyst.invoke_agent(user_instructions=full_user_instructions, data_raw=agent_data)
                        result_tab2 = pandas_data_analyst.get_response()

                except Exception as e:
                    st.error(f"Erro ao processar com IA: {e}")
                    msgs_tab2.add_ai_message(f"Desculpe, ocorreu um erro durante a análise: {str(e)[:500]}") # Truncate long errors
                    st.rerun() # Use rerun after adding message

                ai_response_message_tab2 = ""
                if result_tab2 and result_tab2.get("answer"):
                    ai_response_message_tab2 += result_tab2.get("answer") # No need for extra \n\n initially

                # IMPORTANT: Check if a chart or dataframe is part of the response
                # The AI should ideally put text AND placeholders in the same "answer"
                # or have a clear structure for mixed content.
                # The following logic assumes text comes first, then placeholder.

                generated_content = False # Flag to track if we added a plot/df

                if result_tab2 and result_tab2.get("routing_preprocessor_decision") == "chart" and result_tab2.get("plotly_graph"):
                    try:
                        if isinstance(result_tab2.get("plotly_graph"), dict): # Plotly JSON
                            plot_tab2 = go.Figure(result_tab2.get("plotly_graph"))
                        else: # Already a Plotly Figure object
                            plot_tab2 = result_tab2.get("plotly_graph")

                        idx_tab2 = len(st.session_state.plots_tab2)
                        st.session_state.plots_tab2.append(plot_tab2)
                        # Append placeholder to the existing text message
                        ai_response_message_tab2 += f"\nPLOT_INDEX_TAB2:{idx_tab2}"
                        generated_content = True
                    except Exception as e:
                        error_msg_tab2 = f"Erro ao gerar gráfico: {e}. A IA tentou criar um gráfico, mas falhou."
                        if not ai_response_message_tab2.strip(): ai_response_message_tab2 = "Não houve resposta textual da IA.\n"
                        ai_response_message_tab2 += f"\n\n{error_msg_tab2}"

                elif result_tab2 and result_tab2.get("data_wrangled") is not None:
                    data_wrangled_tab2 = result_tab2.get("data_wrangled")
                    if not isinstance(data_wrangled_tab2, pd.DataFrame):
                        try:
                            data_wrangled_tab2 = pd.DataFrame(data_wrangled_tab2)
                        except Exception as e:
                            error_msg_tab2 = f"Erro ao converter para DataFrame: {e}. A IA tentou retornar uma tabela, mas falhou."
                            if not ai_response_message_tab2.strip(): ai_response_message_tab2 = "Não houve resposta textual da IA.\n"
                            ai_response_message_tab2 += f"\n\n{error_msg_tab2}"
                            data_wrangled_tab2 = None # Ensure it's None so we don't proceed

                    if isinstance(data_wrangled_tab2, pd.DataFrame) and not data_wrangled_tab2.empty:
                        idx_tab2 = len(st.session_state.dataframes_tab2)
                        st.session_state.dataframes_tab2.append(data_wrangled_tab2)
                        ai_response_message_tab2 += f"\nDATAFRAME_INDEX_TAB2:{idx_tab2}"
                        generated_content = True
                    elif isinstance(data_wrangled_tab2, pd.DataFrame) and data_wrangled_tab2.empty:
                         ai_response_message_tab2 += "\n\nA IA retornou uma tabela vazia."


                # Final message handling
                if not ai_response_message_tab2.strip() and not generated_content: # No text, no plot, no df
                     ai_response_message_tab2 = "A IA processou sua solicitação, mas não retornou um texto, gráfico ou tabela específica. "
                     ai_response_message_tab2 += f"Resposta completa da IA: {str(result_tab2)}" if result_tab2 else "Nenhuma resposta da IA."

                msgs_tab2.add_ai_message(ai_response_message_tab2)
                st.rerun() # Rerun to display the new AI message with potential plot/df



with tab3:
    st.markdown("## 📋 Visualização Geral dos Dados com AgGrid")
    st.markdown("Explore os dados completos de forma interativa com recursos avançados de ordenação, filtragem e seleção.")

    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

    if df.empty:
        st.warning("Os dados não foram carregados corretamente. Por favor, envie um arquivo válido na barra lateral.")
    else:
        gb = GridOptionsBuilder.from_dataframe(df)

        gb.configure_default_column(
            filter=True, sortable=True, resizable=True, editable=False,
            # --- NEW --- Adding tooltip from cell value
            tooltipValueGetter = JsCode("function(params) { return params.value; }")
        )
        gb.configure_grid_options(
            domLayout='normal', # 'autoHeight' could also be an option
            pagination=True,
            paginationPageSize=20,
            floatingFilter=True,
            rowHoverHighlight=True,
            suppressRowClickSelection=False,
            rowSelection='multiple',
            # --- NEW --- Enable Excel export with styles
            defaultExcelExportParams = {
                'processCellCallback': JsCode("""
                    function(params) {
                        if (params.value && typeof params.value === 'string' && (params.value.includes('↑') || params.value.includes('↓'))) {
                            return { styleId: params.value.includes('↑') ? 'highlightUp' : 'highlightDown' };
                        }
                        return null;
                    }
                """),
            },
            excelStyles = [
                { 'id': 'header', 'font': { 'bold': True } },
                { 'id': 'highlightUp', 'font': { 'color': '#FF0000' }, 'interior': { 'color': '#FFCCCC', 'pattern': 'Solid'} }, # Red for Up
                { 'id': 'highlightDown', 'font': { 'color': '#0000FF' }, 'interior': { 'color': '#CCCCFF', 'pattern': 'Solid'} }  # Blue for Down
            ],

            localeText = {
                "page": "Página", "more": "Mais", "to": "até", "of": "de", "next": "Próxima",
                "last": "Última", "first": "Primeira", "previous": "Anterior", "loadingOoo": "Carregando...",
                "noRowsToShow": "Nenhum dado para mostrar", "filterOoo": "Filtrar...", "applyFilter": "Aplicar",
                "equals": "Igual", "notEqual": "Diferente", "blank": "Vazio", "notBlank": "Preenchido",
                "greaterThan": "Maior que", "greaterThanOrEqual": "Maior ou igual a", "lessThan": "Menor que",
                "lessThanOrEqual": "Menor ou igual a", "inRange": "Entre", "contains": "Contém",
                "notContains": "Não contém", "startsWith": "Começa com", "endsWith": "Termina com",
                "andCondition": "E", "orCondition": "OU", "clearFilter": "Limpar Filtro", "resetFilter": "Redefinir Filtro",
                "filterConditions": "Condições", "filterValue": "Valor", "filterFrom": "De", "filterTo": "Até",
                "selectAll": "(Selecionar Tudo)", "searchOoo": "Buscar...", "noMatches": "Nenhum resultado",
                "group": "Grupo", "columns": "Colunas", "filters": "Filtros",
                "rowGroupColumns": "Colunas para Agrupar por Linha",
                "rowGroupColumnsEmptyMessage": "Arraste colunas aqui para agrupar",
                "valueColumns": "Colunas de Valor", "pivotMode": "Modo Pivô", "groups": "Grupos",
                "values": "Valores", "pivots": "Pivôs",
                "valueColumnsEmptyMessage": "Arraste colunas aqui para agregar",
                "pivotColumnsEmptyMessage": "Arraste aqui para definir colunas pivô",
                "toolPanelButton": "Painel de Ferramentas", "noRowsLabel": "Sem dados",
                "pinColumn": "Fixar Coluna", "valueAggregation": "Agregação de Valor",
                "autosizeThiscolumn": "Ajustar Esta Coluna", "autosizeAllColumns": "Ajustar Todas as Colunas",
                "groupBy": "Agrupar por", "ungroupBy": "Desagrupar por", "resetColumns": "Redefinir Colunas",
                "expandAll": "Expandir Tudo", "collapseAll": "Recolher Tudo", "copy": "Copiar",
                "copyWithHeaders": "Copiar com Cabeçalhos", "ctrlC": "Ctrl+C", "paste": "Colar", "ctrlV": "Ctrl+V",
                "export": "Exportar", "csvExport": "Exportar para CSV", "excelExport": "Exportar para Excel (.xlsx)",
                "sum": "Soma", "min": "Mínimo", "max": "Máximo", "none": "Nenhum", "count": "Contagem",
                "avg": "Média", "filteredRows": "Linhas Filtradas", "selectedRows": "Linhas Selecionadas",
                "totalRows": "Total de Linhas", "pinLeft": "Fixar à Esquerda", "pinRight": "Fixar à Direita",
                "noPin": "Não Fixar", "pivotChartTitle": "Gráfico Pivô",
                "advancedFilterContains": "Contém", "advancedFilterNotContains": "Não contém",
                "advancedFilterEquals": "É igual a", "advancedFilterNotEqual": "Não é igual a",
                "advancedFilterStartsWith": "Começa com", "advancedFilterEndsWith": "Termina com",
            }
        )
        # --- NEW --- Enable side bar for column selection, grouping etc.
       # gb.enable_enterprise_modules(enable_sidebar=True)

        # Specific column configurations can be added here if needed
        # Example: gb.configure_column("idade", type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=0)

        grid_options = gb.build()
      
        AgGrid(
            df,
            gridOptions=grid_options,
            height=700, # Increased height
            width='100%',
            theme="streamlit", # Using streamlit theme for better integration, 'material' or 'alpine' also good
            update_mode=GridUpdateMode.MODEL_CHANGED, # More responsive update mode
            allow_unsafe_jscode=True, # Required for JsCode features
            fit_columns_on_grid_load=True, # Adjust columns on load
            # --- NEW --- Adding sidebar configuration
            sideBar={'toolPanels': [
                {
                    'id': 'columns',
                    'labelDefault': 'Colunas',
                    'labelKey': 'columns',
                    'iconKey': 'columns',
                    'toolPanel': 'agColumnsToolPanel',
                    'toolPanelParams': { 'suppressRowGroups': False, 'suppressValues': False, 'suppressPivots': False, 'suppressPivotMode': False}
                },
                {
                    'id': 'filters',
                    'labelDefault': 'Filtros',
                    'labelKey': 'filters',
                    'iconKey': 'filter',
                    'toolPanel': 'agFiltersToolPanel',
                }
            ],
            'defaultToolPanel': 'columns'
            }
        )

# --- NEW --- TAB 4: BUSINESS INSIGHTS (IA) ---


# --- TAB 4: Dynamic Business Insights ---
with tab4:
    st.markdown("## 💡 Insights de Negócios Dinâmicos (Gerados por IA)")
    st.markdown("Obtenha uma análise estratégica com base nos **dados filtrados na Aba 1**.")
    st.markdown("---")
    data_for_insights = df_filtrado_tab1.copy()
    is_filtered = not data_for_insights.equals(df)
    num_pac_insights = len(data_for_insights)

    st.markdown(f"**Análise Atual Baseada em:** `{num_pac_insights} paciente(s)` (Aba 1).")
    if is_filtered and num_pac_insights < len(df): st.caption(f"Dataset original: `{len(df)}` pacientes.")
    elif not is_filtered and num_pac_insights > 0: st.caption("Analisando o conjunto de dados completo.")

    if 'dyn_biz_insights' not in st.session_state: st.session_state.dyn_biz_insights = ""
    if 'gen_dyn_insights' not in st.session_state: st.session_state.gen_dyn_insights = False

    if not llm: st.error("Modelo IA não inicializado. Verifique a chave API.")
    elif df.empty: st.warning("Nenhum dado carregado. Faça upload de um CSV.")
    else:
        if st.button("🔍 Gerar Novos Insights (Dados Atuais)", key="gen_dyn_biz_insights_btn", disabled=st.session_state.gen_dyn_insights, use_container_width=True):
            if data_for_insights.empty:
                st.error("Não há dados para os filtros atuais. Ajuste os filtros na Aba 1.")
                st.session_state.dyn_biz_insights = ""
            else:
                st.session_state.gen_dyn_insights = True
                st.session_state.dyn_biz_insights = ""
                with st.spinner("🧠 IA analisando dados selecionados..."):
                    try:
                        num_cols_ins = len(data_for_insights.columns)
                        ls_stat_cols_str = ", ".join([s.replace('_status','').replace('_',' ').title() for s in status_cols[:10]]) + ("..." if len(status_cols) > 10 else "")
                        pac_alt_ins, pc_pac_alt_ins = 0, 0.0
                        if "paciente_com_alteracao" in data_for_insights.columns:
                            pac_alt_ins = data_for_insights['paciente_com_alteracao'].sum()
                            pc_pac_alt_ins = (pac_alt_ins / num_pac_insights * 100) if num_pac_insights > 0 else 0.0
                        
                        med_ex_alt_geral, med_ex_alt_com_alt = 0.0, 0.0
                        if "qtde_exames_alterados" in data_for_insights.columns and data_for_insights["qtde_exames_alterados"].notna().any():
                            med_ex_alt_geral = data_for_insights['qtde_exames_alterados'].mean()
                            df_pac_alt_ins = data_for_insights[data_for_insights['paciente_com_alteracao'] & data_for_insights['qtde_exames_alterados'].notna()]
                            if not df_pac_alt_ins.empty: med_ex_alt_com_alt = df_pac_alt_ins['qtde_exames_alterados'].mean()

                        top_alt_df_ins = calculate_top_altered_exams(data_for_insights, status_cols, ALTERATION_MARKERS)
                        top_alt_str_ins = ""
                        if not top_alt_df_ins.empty:
                            for _, r in top_alt_df_ins.head(5).iterrows(): top_alt_str_ins += f"- {r['Exame']}: {r['Número de Alterações']} alterações\n"
                        else: top_alt_str_ins = "Nenhum exame alterado proeminente neste subconjunto."
                        
                        dataset_desc = "completo" if not is_filtered else f"filtrado ({num_pac_insights} de {len(df)} pacientes)"
                        prompt_dyn = f"""
                        Você é um consultor de negócios sênior para uma cooperativa de saúde (Unimed), especializado em análise de dados laboratoriais.
                        Analise o resumo do conjunto de dados {dataset_desc} e forneça 3-5 insights de negócios estratégicos e acionáveis em português do Brasil.

                        Resumo dos Dados ({dataset_desc}):
                        - Pacientes: {num_pac_insights}
                        - Colunas: {num_cols_ins}
                        - Exames monitorados (amostra): {ls_stat_cols_str if ls_stat_cols_str else "N/A"}
                        - Pacientes c/ ≥1 alteração: {pac_alt_ins} ({pc_pac_alt_ins:.1f}%)
                        - Média exames alterados/paciente (geral): {med_ex_alt_geral:.2f}
                        - Média exames alterados/paciente (c/ alteração): {med_ex_alt_com_alt:.2f}
                        - Top 5 exames alterados (neste conjunto):
                        {top_alt_str_ins if top_alt_str_ins.strip() else "   - Sem dados suficientes."}

                        Insights devem focar em:
                        1. Tendências de saúde específicas do grupo.
                        2. Oportunidades de otimização/intervenção para este subconjunto.
                        3. Sugestões de comunicação/programas para este perfil.
                        4. Investigações adicionais relevantes.
                        5. Considerações de impacto (financeiro, operacional, cuidado).

                        Formato: **Principais Insights (Grupo Selecionado):**\n* **[Insight 1]:** [Detalhes e ação]\n* ...
                        Linguagem clara para gestores.
                        """
                        response = llm.invoke(prompt_dyn)
                        st.session_state.dyn_biz_insights = response.content
                    except Exception as e:
                        st.error(f"Erro ao gerar insights: {str(e)}")
                        st.session_state.dyn_biz_insights = "Não foi possível gerar insights. Tente novamente."
                    finally:
                        st.session_state.gen_dyn_insights = False
                        st.rerun()
        
        if st.session_state.gen_dyn_insights: st.info("Gerando insights para dados selecionados...")
        elif st.session_state.dyn_biz_insights:
            with st.container(border=True):
                st.markdown("#### 🧠 Análise da IA (Filtros Atuais):")
                st.markdown(st.session_state.dyn_biz_insights)
        elif not st.session_state.gen_dyn_insights and not st.session_state.dyn_biz_insights and not data_for_insights.empty:
            st.info("Clique acima para gerar insights sobre os dados filtrados.")
        elif data_for_insights.empty and not df.empty:
            st.warning("Filtros não retornaram dados. Ajuste-os na Aba 1 ou limpe-os.")