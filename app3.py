import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json # Keep for potential future use, though not actively used in main flow
import collections # Keep for potential future use with PandasDataAnalyst
from datetime import datetime

from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_openai import ChatOpenAI
# Assuming ai_data_science_team is a custom library you have for Tab 2
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

        body, .stApp {
            background-color: var(--background-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .stApp > header { background-color: var(--primary-color); color: white; }
        .stApp > header .st-emotion-cache-1avcm0n { color: white; } /* Specific to Streamlit's header text */
        h1, h2, h3 { color: var(--primary-color); }
        .st-emotion-cache-16txtl3 { background-color: var(--sidebar-background-color); } /* Sidebar background */
        .st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 .st-emotion-cache-10oheav { color: var(--secondary-color); } /* Sidebar titles */
        .stMetric { background-color: var(--card-background-color); border-radius: 8px; padding: 15px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .stMetric label { color: var(--secondary-color) !important; font-weight: bold; }
        .stMetric .st-emotion-cache-1wivap2 { font-size: 2em !important; } /* Metric value size */
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: var(--card-background-color); border-radius: 4px 4px 0px 0px; padding: 10px 20px; color: var(--secondary-color); }
        .stTabs [aria-selected="true"] { background-color: var(--primary-color); color: white; font-weight: bold; }
        .stExpander { border: 1px solid #e0e0e0; border-radius: 8px; background-color: var(--card-background-color); }
        .stExpander header { background-color: #f9f9f9; color: var(--primary-color); font-weight: bold; }
        .stDataFrame { width: 100%; }
        .stTextInput input, .stSelectbox select, .stDateInput input { border-radius: 5px; }
        .custom-card {
            background-color: var(--card-background-color);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 15px; /* Provides space if cards stack in a column or for rows */
            height: 100%; /* For consistent card height in a row, if needed by content */
        }
        .custom-card h5 { /* Specific styling for titles within custom cards */
            color: var(--primary-color);
            margin-top: 0px; /* Remove default top margin */
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        .custom-card p.value { /* Styling for the main value in custom cards */
            font-size: 1.8em;
            font-weight: bold;
            color: var(--secondary-color);
            margin-bottom: 5px;
        }
        .custom-card p.help-text { /* Styling for the help text in custom cards */
            font-size: 0.9em;
            color: #555555;
            margin-bottom: 0px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #007f3e;'>🩺 Painel de IA para Resultados Laboratoriais Unimed</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.image("unimed-removebg-preview.png", width=350)
    st.markdown("<h2 style='color: #006633;'>🔐 Configuração da IA</h2>", unsafe_allow_html=True)
    api_key = st.text_input("Chave da API da OpenAI", type="password", help="Insira sua chave da API OpenAI para ativar os recursos de IA.")
    model_option = st.selectbox("Modelo OpenAI", ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"], index=0)

    st.markdown("<h2 style='color: #006633;'>📁 Upload de Dados</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Escolha um arquivo CSV com os resultados laboratoriais:",
        type=["csv"],
        help="O arquivo CSV deve conter colunas com resultados de exames e colunas com sufixo '_status' indicando alterações (↑, ↓)."
    )

if not api_key:
    st.warning("🔑 Por favor, insira sua chave da API da OpenAI na barra lateral para habilitar as funcionalidades de IA e carregar os dados.")
    st.stop()

# --- Initialize LLM (globally available if API key is present) ---
llm = None
pandas_data_analyst = None # For Tab 2

if api_key:
    try:
        llm = ChatOpenAI(model=model_option, api_key=api_key, temperature=0.3)
        data_wrangling_agent = DataWranglingAgent(model=llm, bypass_recommended_steps=True, log=False)
        data_visualization_agent = DataVisualizationAgent(model=llm, log=False)
        pandas_data_analyst = PandasDataAnalyst(
            model=llm,
            data_wrangling_agent=data_wrangling_agent,
            data_visualization_agent=data_visualization_agent
        )
    except Exception as e:
        st.error(f"Erro ao inicializar os modelos de IA: {e}. Verifique sua chave da API.")
        st.stop()

if not uploaded_file:
    st.info("⬆️ Envie um arquivo CSV com resultados de exames para prosseguir e visualizar o painel.")
    st.stop()

# --- GLOBAL DEFINITIONS ---
ALTERATION_MARKERS = ["↑", "↓", "Alto", "Baixo", "Aumentado", "Diminuído", "Positivo"]

# --- DATA LOADING AND PREPROCESSING ---
@st.cache_data
def load_data(file):
    df_loaded = pd.read_csv(file)
    df_loaded.columns = df_loaded.columns.str.lower().str.replace(' ', '_')
    if "data_nascimento" in df_loaded.columns:
        df_loaded["data_nascimento"] = pd.to_datetime(df_loaded["data_nascimento"], errors="coerce")
        current_year = datetime.now().year
        df_loaded["idade"] = df_loaded["data_nascimento"].apply(
            lambda x: current_year - x.year if pd.notnull(x) and x.year > 1900 else None
        )
    elif "idade" not in df_loaded.columns:
        st.warning("Coluna 'data_nascimento' ou 'idade' não encontrada. A funcionalidade de filtro por idade pode não funcionar.")
        df_loaded["idade"] = None
    
    status_cols_local = [col for col in df_loaded.columns if col.endswith("_status")]
    if status_cols_local:
        df_loaded["paciente_com_alteracao"] = df_loaded[status_cols_local].apply(lambda row: row.isin(ALTERATION_MARKERS).any(), axis=1)
        df_loaded["qtde_exames_alterados"] = df_loaded[status_cols_local].apply(lambda row: sum(row.isin(ALTERATION_MARKERS)), axis=1)
    else:
        df_loaded["paciente_com_alteracao"] = False
        df_loaded["qtde_exames_alterados"] = 0
        st.warning("Nenhuma coluna '_status' encontrada. Funcionalidades de alteração podem não funcionar corretamente.")
    return df_loaded, status_cols_local

try:
    df, status_cols = load_data(uploaded_file)
except Exception as e:
    st.error(f"Erro ao carregar ou processar o arquivo: {e}")
    st.stop()

if not status_cols and uploaded_file:
    st.error("Nenhuma coluna de status de exame (terminada em '_status') foi encontrada no arquivo após o processamento. Verifique o formato do CSV. Algumas funcionalidades de insights podem não funcionar como esperado.")

# --- HELPER FUNCTION TO CALCULATE TOP ALTERED EXAMS (from second script) ---
def calculate_top_altered_exams(dataframe, status_column_list, markers):
    if dataframe.empty or not status_column_list:
        return pd.DataFrame(columns=["Exame", "Número de Alterações"])
    alteracoes = collections.Counter()
    for col in status_column_list:
        if col in dataframe.columns: # Ensure column exists
            exam_name = col.replace("_status", "").replace("_", " ").title()
            alteracoes[exam_name] += dataframe[col].isin(markers).sum()
    if alteracoes:
        df_top_altered = pd.DataFrame.from_dict(alteracoes, orient="index", columns=["Número de Alterações"])
        df_top_altered = df_top_altered.sort_values(by="Número de Alterações", ascending=False).reset_index().rename(columns={"index": "Exame"})
        return df_top_altered[df_top_altered["Número de Alterações"] > 0] # Filter out exams with 0 alterations
    return pd.DataFrame(columns=["Exame", "Número de Alterações"])

# Calculate top altered exams for the global dataset
top_alterados_df = calculate_top_altered_exams(df, status_cols, ALTERATION_MARKERS)


def generate_dynamic_insights(current_df, current_status_cols, current_top_alterados_df): # Removed markers_unused
    insights_list = []
    THRESHOLD_MULTIPLE_ALTERATIONS = 3

    if current_df.empty:
        for i in range(6):
            insights_list.append({
                "title": f"Insight {i+1} Indisponível",
                "value": "N/A",
                "help": "Dados não carregados ou insuficientes para este insight."
            })
        return insights_list

    total_pacientes = len(current_df)

    if "paciente_com_alteracao" in current_df.columns:
        pacientes_com_alt = current_df['paciente_com_alteracao'].sum()
        percent_com_alt = (pacientes_com_alt / total_pacientes * 100) if total_pacientes > 0 else 0
        insights_list.append({
            "title": "Taxa de Alteração Geral",
            "value": f"{pacientes_com_alt} / {total_pacientes} ({percent_com_alt:.1f}%)",
            "help": "Pacientes com pelo menos um exame alterado."
        })
    else:
        insights_list.append({"title": "Taxa de Alteração Geral", "value": "N/A", "help": "Info não disponível ('paciente_com_alteracao')."})

    if "qtde_exames_alterados" in current_df.columns:
        multiple_alt_count = current_df[current_df['qtde_exames_alterados'] >= THRESHOLD_MULTIPLE_ALTERATIONS].shape[0]
        percent_multiple_alt = (multiple_alt_count / total_pacientes * 100) if total_pacientes > 0 else 0
        insights_list.append({
            "title": f"Alerta: ≥{THRESHOLD_MULTIPLE_ALTERATIONS} Alterações",
            "value": f"{multiple_alt_count} ({percent_multiple_alt:.1f}%)",
            "help": f"Pacientes com {THRESHOLD_MULTIPLE_ALTERATIONS} ou mais exames alterados."
        })
    else:
        insights_list.append({"title": f"Alerta: ≥{THRESHOLD_MULTIPLE_ALTERATIONS} Alterações", "value": "N/A", "help": "Info não disponível ('qtde_exames_alterados')."})

    if not current_top_alterados_df.empty:
        exam_name = current_top_alterados_df['Exame'].iloc[0]
        exam_count = current_top_alterados_df['Número de Alterações'].iloc[0]
        insights_list.append({
            "title": "Principal Exame Alterado",
            "value": f"{exam_name}",
            "help": f"{exam_count} ocorrências de alteração neste exame."
        })
    else:
        insights_list.append({"title": "Principal Exame Alterado", "value": "N/A", "help": "Não há dados consolidados de exames alterados."})

    if "idade" in current_df.columns and current_df["idade"].notna().any() and "paciente_com_alteracao" in current_df.columns:
        avg_age_with_alt_series = current_df[current_df['paciente_com_alteracao'] & current_df['idade'].notna()]['idade']
        avg_age_without_alt_series = current_df[~current_df['paciente_com_alteracao'] & current_df['idade'].notna()]['idade']
        val_with_alt = f"{avg_age_with_alt_series.mean():.1f}a" if not avg_age_with_alt_series.empty else "N/D"
        val_without_alt = f"{avg_age_without_alt_series.mean():.1f}a" if not avg_age_without_alt_series.empty else "N/D"
        insights_list.append({
            "title": "Idade Média (Com/Sem Alter.)",
            "value": f"{val_with_alt} / {val_without_alt}",
            "help": "Média de idade: pacientes com alterações vs. sem alterações."
        })
    else:
        insights_list.append({"title": "Idade Média e Alterações", "value": "N/A", "help": "Dados de idade ou de alterações insuficientes."})

    if "idade" in current_df.columns and current_df["idade"].notna().any() and "paciente_com_alteracao" in current_df.columns:
        youngest_series = current_df[current_df['paciente_com_alteracao'] & current_df['idade'].notna()]['idade']
        if not youngest_series.empty:
            insights_list.append({
                "title": "Alerta Jovem com Alteração",
                "value": f"{youngest_series.min():.0f} anos",
                "help": "Idade do paciente mais jovem com ao menos uma alteração."
            })
        else:
            insights_list.append({"title": "Alerta Jovem com Alteração", "value": "N/A", "help": "Sem dados de pacientes jovens com alterações."})
    else:
        insights_list.append({"title": "Alerta Jovem com Alteração", "value": "N/A", "help": "Dados de idade ou de alterações insuficientes."})
        
    if "idade" in current_df.columns and current_df["idade"].notna().any() and "paciente_com_alteracao" in current_df.columns:
        oldest_series = current_df[current_df['paciente_com_alteracao'] & current_df['idade'].notna()]['idade']
        if not oldest_series.empty:
            insights_list.append({
                "title": "Alerta Idoso com Alteração",
                "value": f"{oldest_series.max():.0f} anos",
                "help": "Idade do paciente mais idoso com ao menos uma alteração."
            })
        else:
            insights_list.append({"title": "Alerta Idoso com Alteração", "value": "N/A", "help": "Sem dados de pacientes idosos com alterações."})
    else:
        insights_list.append({"title": "Alerta Idoso com Alteração", "value": "N/A", "help": "Dados de idade ou de alterações insuficientes."})
        
    return insights_list[:6]


# --- TABS ---
# --- Tab name for Tab 4 changed to reflect its new dynamic functionality ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visão Geral e Filtros Interativos",
    "🤖 Chat Analítico (Dados Filtrados)",
    "📋 Visualização Geral dos Dados com AgGrid",
    "💡 Insights Dinâmicos (IA)" # Changed tab name
])


# --- TAB 1: VISÃO GERAL E FILTROS ---
with tab1:
    st.markdown("## 🩺 Panorama dos Resultados Laboratoriais")
    st.markdown("Explore os dados dos pacientes e filtre por diversos critérios para identificar padrões.")

    with st.container(border=True):
        st.subheader("Resumo Geral dos Pacientes (Dataset Completo)")
        # Pass the globally calculated top_alterados_df
        dynamic_insights_global = generate_dynamic_insights(df, status_cols, top_alterados_df)

        if dynamic_insights_global:
            row1_cols = st.columns(3)
            row2_cols = st.columns(3)

            for i, insight in enumerate(dynamic_insights_global):
                target_col = row1_cols[i] if i < 3 else row2_cols[i-3]
                with target_col:
                    st.markdown(f"""
                    <div class="custom-card">
                        <h5>{insight['title']}</h5>
                        <p class="value">{insight['value']}</p>
                        <p class="help-text">{insight['help']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Não foi possível gerar insights dinâmicos para o dataset completo devido à falta de dados ou colunas necessárias.")

    st.markdown("### 🔬 Filtros Detalhados e Visualização de Dados (Interativo)")

    df_filtrado_tab1 = df.copy() # Initialize df_filtrado_tab1 for Tab 1 filters

    with st.expander("🔬 Ajuste os Filtros para Refinar sua Análise:", expanded=True):
        col_filt1, col_filt2 = st.columns([1, 2])

        with col_filt1:
            if "idade" in df_filtrado_tab1.columns and df_filtrado_tab1["idade"].notna().any():
                idade_min_val = int(df_filtrado_tab1["idade"].dropna().min())
                idade_max_val = int(df_filtrado_tab1["idade"].dropna().max())
                if idade_min_val < idade_max_val:
                    faixa_idade = st.slider(
                        "Filtrar por Faixa Etária:",
                        min_value=idade_min_val,
                        max_value=idade_max_val,
                        value=(idade_min_val, idade_max_val),
                        key="tab1_idade_slider"
                    )
                    df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["idade"].between(faixa_idade[0], faixa_idade[1])]
                elif idade_min_val == idade_max_val:
                     st.caption(f"Todos os pacientes filtrados têm a mesma idade: {idade_min_val} anos.")
                else:
                    st.caption("Dados de idade inconsistentes para criar o filtro.")
            else:
                st.caption("Filtro de idade indisponível (dados ausentes ou não aplicáveis).")

            if "sexo" in df_filtrado_tab1.columns and df_filtrado_tab1["sexo"].notna().any():
                sexo_opcoes = sorted(df_filtrado_tab1["sexo"].dropna().unique())
                if sexo_opcoes: # Check if list is not empty
                    sexo_sel = st.radio(
                        "Filtrar por Sexo:",
                        options=["Todos"] + sexo_opcoes,
                        horizontal=True,
                        key="tab1_sexo_radio"
                    )
                    if sexo_sel != "Todos":
                        df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["sexo"] == sexo_sel]
                else:
                    st.caption("Filtro de sexo indisponível (sem opções válidas).")
            else:
                st.caption("Filtro de sexo indisponível (coluna 'sexo' ausente ou vazia).")


            if "qtde_exames_alterados" in df_filtrado_tab1.columns and df_filtrado_tab1["qtde_exames_alterados"].notna().any() and df_filtrado_tab1["qtde_exames_alterados"].max() > 0 :
                min_alt = 0
                max_alt = int(df_filtrado_tab1["qtde_exames_alterados"].max())
                if min_alt < max_alt:
                    num_alteracoes_range = st.slider(
                        "Filtrar por Quantidade de Exames Alterados:",
                        min_value=min_alt,
                        max_value=max_alt,
                        value=(min_alt, max_alt),
                        key="tab1_qtde_alt_slider"
                    )
                    df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1["qtde_exames_alterados"].between(num_alteracoes_range[0], num_alteracoes_range[1])]
                elif min_alt == max_alt and min_alt == 0:
                     st.caption("Nenhum paciente no filtro atual possui exames alterados.")
                elif min_alt == max_alt:
                    st.caption(f"Todos os pacientes no filtro atual possuem {min_alt} exame(s) alterado(s).")
            else:
                st.caption("Filtro de quantidade de alterações indisponível.")


        with col_filt2:
            exames_nomes_limpos = [col.replace("_status", "").replace("_", " ").title() for col in status_cols]
            exames_selecionados_nomes = st.multiselect(
                "Selecionar Exames Específicos para Filtragem e Análise Visual:",
                options=exames_nomes_limpos,
                help="Escolha um ou mais exames para aplicar filtros de status/valor e para gerar gráficos comparativos (correlação, dispersão).",
                key="tab1_exames_multiselect",
                disabled=not status_cols # Disable if no status_cols found
            )
            # Convert selected display names back to original status column names
            exames_status_selecionados = [status_cols[exames_nomes_limpos.index(nome)] for nome in exames_selecionados_nomes]


        if exames_status_selecionados: # Only show if exams are selected
            st.markdown("##### Filtros Avançados por Exame Selecionado:")
            filtros_status = {}
            filtros_valores = {}

            num_cols_filter = min(len(exames_status_selecionados), 3) # Max 3 columns for filters
            filter_cols = st.columns(num_cols_filter)
            col_idx = 0

            for exame_status_col in exames_status_selecionados:
                exame_base = exame_status_col.removesuffix("_status")
                exame_display_name = exame_base.replace("_", " ").title()

                with filter_cols[col_idx % num_cols_filter]: # Cycle through columns
                        # Status filter for the selected exam
                        unique_status_vals = df_filtrado_tab1[exame_status_col].dropna().unique()
                        if len(unique_status_vals) > 0:
                            status_options = ["Todos"] + list(unique_status_vals)
                            # Prioritize common alteration markers in options for easier access
                            priority_status = ALTERATION_MARKERS
                            remaining_options = [opt for opt in status_options if opt not in ["Todos"] + priority_status]
                            sorted_status_options = ["Todos"] + [p for p in priority_status if p in status_options] + sorted(remaining_options)

                            status_sel = st.radio(
                                f"Status de {exame_display_name}:",
                                options=sorted_status_options,
                                key=f"tab1_{exame_base}_status_radio",
                                horizontal=True # Display radio buttons horizontally
                            )
                            filtros_status[exame_status_col] = status_sel
                        else:
                            st.caption(f"Status para {exame_display_name} não disponível/variado nos dados filtrados.")

                        # Value range filter for the selected exam (if numeric)
                        if exame_base in df_filtrado_tab1.columns and pd.api.types.is_numeric_dtype(df_filtrado_tab1[exame_base]):
                            if df_filtrado_tab1[exame_base].notna().any(): # Check if there are any non-NaN values
                                min_val_exam = float(df_filtrado_tab1[exame_base].dropna().min())
                                max_val_exam = float(df_filtrado_tab1[exame_base].dropna().max())
                                if min_val_exam < max_val_exam :
                                    step_val = (max_val_exam - min_val_exam) / 100 if (max_val_exam - min_val_exam) > 0 else 0.1
                                    valor_range = st.slider(
                                        f"Intervalo de Valores para {exame_display_name}:",
                                        min_value=min_val_exam,
                                        max_value=max_val_exam,
                                        value=(min_val_exam, max_val_exam),
                                        step=step_val if step_val > 0 else None, # step=None if min=max
                                        key=f"tab1_{exame_base}_range_slider"
                                    )
                                    filtros_valores[exame_base] = valor_range
                                elif min_val_exam == max_val_exam:
                                    st.caption(f"Valores de {exame_display_name} são constantes ({min_val_exam}).")
                                else: # Should not happen
                                    st.caption(f"Dados de valor para {exame_display_name} inconsistentes.")
                            else:
                                st.caption(f"Valores numéricos para {exame_display_name} não disponíveis para filtro.")
                col_idx +=1

            # Apply collected filters
            for exame_status_col in exames_status_selecionados:
                exame_base = exame_status_col.removesuffix("_status")
                status_sel = filtros_status.get(exame_status_col)
                if status_sel and status_sel != "Todos":
                    df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1[exame_status_col] == status_sel]

                if exame_base in filtros_valores:
                    min_v, max_v = filtros_valores[exame_base]
                    df_filtrado_tab1 = df_filtrado_tab1[df_filtrado_tab1[exame_base].between(min_v, max_v)]

    with st.container(border=True):
        st.subheader(f"Resultados Filtrados ({len(df_filtrado_tab1)} Pacientes)")
        if df_filtrado_tab1.empty:
            st.warning("Nenhum paciente corresponde aos filtros selecionados.")
        else:
            # Define base columns and add dynamic columns based on selected exams
            colunas_base = ["nome", "codigo_os","sexo"] # Add other relevant base columns if they exist
            if "idade" in df_filtrado_tab1.columns:
                colunas_base.append("idade")
            if "qtde_exames_alterados" in df_filtrado_tab1.columns:
                colunas_base.append("qtde_exames_alterados")

            colunas_dinamicas_selecionadas = []
            for exame_status_col in exames_status_selecionados: # Use the list from multiselect
                exame_base = exame_status_col.removesuffix("_status")
                if exame_base in df_filtrado_tab1.columns: # Add value column if exists
                    colunas_dinamicas_selecionadas.append(exame_base)
                colunas_dinamicas_selecionadas.append(exame_status_col) # Add status column

            colunas_finais_temp = colunas_base + colunas_dinamicas_selecionadas
            # Ensure columns exist in the dataframe and remove duplicates while preserving order
            colunas_finais = [col for col in colunas_finais_temp if col in df_filtrado_tab1.columns]
            colunas_finais = list(dict.fromkeys(colunas_finais))


            st.dataframe(df_filtrado_tab1[colunas_finais], height=300, use_container_width=True)

            st.markdown("##### Análise Visual dos Dados Filtrados")
            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                if not df_filtrado_tab1.empty and "qtde_exames_alterados" in df_filtrado_tab1.columns and df_filtrado_tab1["qtde_exames_alterados"].notna().any():
                    if df_filtrado_tab1["qtde_exames_alterados"].nunique() > 0 : # Check if there is data to plot
                        fig_dist_alt = px.histogram(
                            df_filtrado_tab1,
                            x="qtde_exames_alterados",
                            title="Distribuição do Nº de Exames Alterados (Filtrado)",
                            labels={"qtde_exames_alterados": "Quantidade de Exames Alterados por Paciente"},
                            color_discrete_sequence=["#007f3e"],
                            marginal="rug" # Adds a small plot showing individual data points
                        )
                        fig_dist_alt.update_layout(bargap=0.1, yaxis_title="Número de Pacientes")
                        if df_filtrado_tab1["qtde_exames_alterados"].notna().any(): # Ensure mean can be calculated
                            mean_val = df_filtrado_tab1["qtde_exames_alterados"].mean()
                            fig_dist_alt.add_vline(
                                x=mean_val,
                                line_dash="dash",
                                line_color="firebrick",
                                annotation_text=f"Média: {mean_val:.1f}",
                                annotation_position="top right"
                            )
                        st.plotly_chart(fig_dist_alt, use_container_width=True)
                    else:
                        st.info("Não há variação na quantidade de exames alterados nos dados filtrados para exibir o histograma.")
                else:
                    st.info("Não há dados de quantidade de exames alterados para exibir no histograma (coluna ausente, vazia ou sem variação).")

            with viz_col2:
                 if not df_filtrado_tab1.empty and exames_status_selecionados: # Check if exams were selected
                    # Use calculate_top_altered_exams for filtered data
                    top_alt_filtrado_df = calculate_top_altered_exams(df_filtrado_tab1, exames_status_selecionados, ALTERATION_MARKERS)

                    if not top_alt_filtrado_df.empty:
                        fig_top_alt_filt = px.bar(
                            top_alt_filtrado_df,
                            x="Número de Alterações", # Corrected column name from calculate_top_altered_exams
                            y="Exame",               # Corrected column name
                            orientation='h',
                            title="Exames Selecionados Mais Alterados (Filtrado)",
                            labels={"Exame": "Exame", "Número de Alterações": "Número de Pacientes com Alteração"},
                            color_discrete_sequence=["#007f3e"],
                            text_auto=True
                        )
                        fig_top_alt_filt.update_layout(
                            yaxis={'categoryorder':'total ascending'}, # Show highest bar at the top
                            xaxis_title="Número de Pacientes com Alteração"
                        )
                        st.plotly_chart(fig_top_alt_filt, use_container_width=True)
                    else:
                        st.info("Nenhuma alteração nos exames selecionados para o conjunto de dados filtrado.")
                 elif not exames_status_selecionados:
                    st.info("Selecione um ou mais exames nos filtros acima para ver o gráfico de alterações.")
                 else: # df_filtrado_tab1 is empty but exams were selected
                    st.info("Nenhum dado no filtro atual para exibir alterações dos exames selecionados.")


            st.markdown("---") 
            st.markdown("##### Mais Análises Visuais dos Dados Filtrados")

            # Age distribution by alteration status
            if "idade" in df_filtrado_tab1.columns and "paciente_com_alteracao" in df_filtrado_tab1.columns and df_filtrado_tab1["idade"].notna().any():
                if not df_filtrado_tab1.empty: # Ensure data exists for plotting
                    df_copy_for_plot = df_filtrado_tab1.copy() # Avoid modifying the filtered df
                    df_copy_for_plot['status_alteracao_label'] = df_copy_for_plot['paciente_com_alteracao'].map({True: 'Com Alteração', False: 'Sem Alteração'})

                    fig_age_alt = px.histogram(
                        df_copy_for_plot.dropna(subset=['idade']), # Drop rows where age is NaN for this plot
                        x="idade",
                        color="status_alteracao_label",
                        title="Distribuição de Idade por Status de Alteração Geral (Filtrado)",
                        labels={"idade": "Idade", "status_alteracao_label": "Status de Alteração"},
                        barmode="overlay", # Overlay bars for comparison
                        marginal="box",    # Show box plots on margins
                        color_discrete_map={'Com Alteração': '#d62728', 'Sem Alteração': '#007f3e'} # Custom colors
                    )
                    fig_age_alt.update_layout(yaxis_title="Número de Pacientes")
                    st.plotly_chart(fig_age_alt, use_container_width=True)
                else:
                    st.caption("Dados filtrados vazios, não é possível exibir a distribuição de idade.")
            elif "idade" not in df_filtrado_tab1.columns:
                 st.caption("Coluna 'idade' não disponível nos dados filtrados para exibir a distribuição por status de alteração.")
            else: # Covers case where 'paciente_com_alteracao' might be missing or 'idade' has no data
                 st.caption("Dados insuficientes ('idade' ou 'paciente_com_alteracao') para exibir a distribuição de idade por status de alteração.")

            # Correlation Matrix and Scatter Plot for selected numeric exams
            selected_exam_bases_for_viz = [s.replace("_status", "") for s in exames_status_selecionados]
            numeric_exam_cols_for_viz = []
            if not df_filtrado_tab1.empty:
                for base_name in selected_exam_bases_for_viz:
                    if base_name in df_filtrado_tab1.columns and pd.api.types.is_numeric_dtype(df_filtrado_tab1[base_name]):
                        # Only include if there's more than one unique value (otherwise correlation is NaN or not meaningful)
                        if df_filtrado_tab1[base_name].nunique(dropna=True) > 1:
                            numeric_exam_cols_for_viz.append(base_name)

            if len(numeric_exam_cols_for_viz) >= 2:
                corr_matrix = df_filtrado_tab1[numeric_exam_cols_for_viz].corr()
                if not corr_matrix.empty and corr_matrix.shape[0] > 1 and corr_matrix.shape[1] > 1 : # Ensure matrix is not trivial
                    # Clean names for display in the matrix
                    corr_matrix.columns = [col.replace("_", " ").title() for col in corr_matrix.columns]
                    corr_matrix.index = [idx.replace("_", " ").title() for idx in corr_matrix.index]

                    fig_corr_matrix = px.imshow(
                        corr_matrix,
                        text_auto=True, # Show correlation values on the heatmap
                        aspect="auto", 
                        color_continuous_scale='RdBu_r', # Red-Blue diverging scale, good for correlations
                        title=f"Matriz de Correlação entre Exames Numéricos Selecionados (Filtrado)",
                        labels=dict(color="Correlação"),
                        zmin=-1, zmax=1 # Ensure full scale for correlation
                    )
                    fig_corr_matrix.update_xaxes(side="bottom") # Move x-axis labels to bottom for readability
                    st.plotly_chart(fig_corr_matrix, use_container_width=True)
                else:
                    st.caption("Não foi possível calcular uma matriz de correlação significativa para os exames numéricos selecionados (pouca variação ou dados insuficientes).")
            elif exames_status_selecionados and len(numeric_exam_cols_for_viz) < 2 : 
                st.caption(f"Para a matriz de correlação, selecione pelo menos dois exames com dados numéricos distintos e variados. Encontrados válidos: {len(numeric_exam_cols_for_viz)}.")

            # Scatter plot if exactly two numeric exams are selected
            if len(numeric_exam_cols_for_viz) == 2:
                exam1_key, exam2_key = numeric_exam_cols_for_viz[0], numeric_exam_cols_for_viz[1]
                exam1_name = exam1_key.replace("_", " ").title()
                exam2_name = exam2_key.replace("_", " ").title()

                df_copy_for_scatter = df_filtrado_tab1.copy()
                color_option_scatter = None
                color_discrete_map_scatter = None
                title_suffix_scatter = ""

                if "paciente_com_alteracao" in df_copy_for_scatter.columns:
                    df_copy_for_scatter['status_alteracao_label'] = df_copy_for_scatter['paciente_com_alteracao'].map({True: 'Com Alteração', False: 'Sem Alteração'})
                    color_option_scatter = 'status_alteracao_label'
                    color_discrete_map_scatter = {'Com Alteração': '#d62728', 'Sem Alteração': '#007f3e'}
                    title_suffix_scatter = " (Colorido por Status de Alteração Geral)"

                hover_data_scatter = ['nome'] if 'nome' in df_copy_for_scatter.columns else []
                if 'idade' in df_copy_for_scatter.columns: hover_data_scatter.append('idade')

                # Ensure there's data after dropping NaNs for the specific exam keys
                if not df_copy_for_scatter.dropna(subset=[exam1_key, exam2_key]).empty:
                    fig_scatter = px.scatter(
                        df_copy_for_scatter.dropna(subset=[exam1_key, exam2_key]), # Drop NaNs for the axes
                        x=exam1_key,
                        y=exam2_key,
                        color=color_option_scatter,
                        color_discrete_map=color_discrete_map_scatter,
                        title=f"Relação entre {exam1_name} e {exam2_name}{title_suffix_scatter}",
                        labels={
                            exam1_key: exam1_name,
                            exam2_key: exam2_name,
                            "status_alteracao_label": "Status Geral do Paciente"
                        },
                        marginal_x="box", 
                        marginal_y="box",
                        hover_data=hover_data_scatter if hover_data_scatter else None
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                     st.caption(f"Não há dados suficientes para exibir o gráfico de dispersão entre {exam1_name} e {exam2_name} após remover valores ausentes.")
            elif exames_status_selecionados and len(numeric_exam_cols_for_viz) !=2 and len(numeric_exam_cols_for_viz) >=1 :
                 st.caption("Para um gráfico de dispersão, selecione exatamente dois exames com dados numéricos e variados.")


# --- TAB 2: IA CHAT (FOCUSED ON FILTERED DATA IF AVAILABLE, OR GENERAL DF) ---
with tab2:
    st.markdown("## 🤖 Chat Analítico com IA (Dados Atuais da Aba 1)")
    st.markdown("Faça perguntas sobre os dados **visíveis na Aba 1 (aplicando os filtros)**. A IA pode ajudar a realizar análises, gerar tabelas e gráficos.")

    # data_for_tab2_chat will be df_filtrado_tab1 from Tab 1
    data_for_tab2_chat = df_filtrado_tab1.copy() 

    if data_for_tab2_chat.empty and not df.empty: # If filters result in empty, use full df
        st.info("Os filtros atuais na Aba 1 resultaram em nenhum dado. O chat abaixo operará sobre o conjunto de dados completo.")
        data_for_tab2_chat = df.copy() # Fallback to the original full dataframe
    elif data_for_tab2_chat.empty and df.empty: # Should not happen if file is uploaded
        st.error("Nenhum dado carregado para o chat.")
        st.stop() # Stop if df itself is empty and therefore data_for_tab2_chat is also empty

    with st.container(border=True):
        msgs_tab2 = StreamlitChatMessageHistory(key="langchain_unimed_messages_tab2") # Unique key for this tab's chat
        if "plots_tab2" not in st.session_state:
            st.session_state.plots_tab2 = []
        if "dataframes_tab2" not in st.session_state:
            st.session_state.dataframes_tab2 = []

        if len(msgs_tab2.messages) == 0:
            initial_message_tab2 = "Olá! Sou sua assistente de IA. Como posso te ajudar a analisar os dados"
            if data_for_tab2_chat.equals(df) and not df_filtrado_tab1.empty: # Using full df because no effective filter
                 initial_message_tab2 += " **gerais** (nenhum filtro ativo ou os filtros resultaram em todos os dados)?"
            elif data_for_tab2_chat.equals(df) and df_filtrado_tab1.empty: # Filtered resulted in empty, so using full df
                 initial_message_tab2 += " **gerais** (os filtros não retornaram dados, então usando o dataset completo)?"
            else: # Using filtered data
                 initial_message_tab2 += " **filtrados** da Aba 1?"
            msgs_tab2.add_ai_message(initial_message_tab2)


        def display_chat_history_tab2():
            for i, msg in enumerate(msgs_tab2.messages):
                with st.chat_message(msg.type):
                    # Check if content is a string before attempting string operations
                    if isinstance(msg.content, str) and "PLOT_INDEX_TAB2:" in msg.content:
                        try:
                            parts = msg.content.split("PLOT_INDEX_TAB2:")
                            text_content = parts[0]
                            if text_content.strip(): st.markdown(text_content) # Display text before plot
                            idx = int(parts[1])
                            st.plotly_chart(st.session_state.plots_tab2[idx], use_container_width=True)
                        except (IndexError, ValueError, TypeError) as e: # Added TypeError for robustness
                            st.error(f"Erro ao exibir gráfico: {e}. Conteúdo: {msg.content}")
                            # Fallback to display raw content or part of it
                            if isinstance(msg.content, str):
                                st.markdown(msg.content.split("PLOT_INDEX_TAB2:")[0] if "PLOT_INDEX_TAB2:" in msg.content else msg.content)
                    elif isinstance(msg.content, str) and "DATAFRAME_INDEX_TAB2:" in msg.content:
                        try:
                            parts = msg.content.split("DATAFRAME_INDEX_TAB2:")
                            text_content = parts[0]
                            if text_content.strip(): st.markdown(text_content) # Display text before dataframe
                            idx = int(parts[1])
                            st.dataframe(st.session_state.dataframes_tab2[idx], use_container_width=True)
                        except (IndexError, ValueError, TypeError) as e: # Added TypeError
                            st.error(f"Erro ao exibir DataFrame: {e}. Conteúdo: {msg.content}")
                            if isinstance(msg.content, str):
                                st.markdown(msg.content.split("DATAFRAME_INDEX_TAB2:")[0] if "DATAFRAME_INDEX_TAB2:" in msg.content else msg.content)
                    else:
                        st.markdown(msg.content) # Handles non-string content by Streamlit's default markdown

        display_chat_history_tab2()

        if not pandas_data_analyst: 
            st.error("Agente de IA (Pandas Analyst) não inicializado. Verifique a chave da API.")
        elif question_tab2 := st.chat_input("Pergunte sobre os dados atuais... (Ex: 'Qual a média de idade aqui?')", key="chat_input_tab2"):
            msgs_tab2.add_user_message(question_tab2)
            # Display user message immediately
            with st.chat_message("human"):
                 st.markdown(question_tab2)


            with st.spinner("👩‍⚕️ A IA está analisando os dados..."):
                try:
                    if data_for_tab2_chat.empty:
                        st.error("Não há dados para a IA analisar. Verifique seus filtros ou o arquivo carregado.")
                        msgs_tab2.add_ai_message("Não há dados para analisar. Por favor, verifique os filtros ou o arquivo carregado.")
                        st.rerun() # Use rerun after adding message
                    else:
                        # Send a copy of the data to the agent
                        pandas_data_analyst.invoke_agent(user_instructions=question_tab2, data_raw=data_for_tab2_chat.copy())
                        result_tab2 = pandas_data_analyst.get_response()
                except Exception as e:
                    st.error(f"Erro ao processar com IA: {e}")
                    msgs_tab2.add_ai_message(f"Desculpe, ocorreu um erro durante a análise: {str(e)[:500]}") # Truncate long errors
                    st.rerun() # Use rerun after adding message
                    st.stop() # Stop execution for this branch on error

                ai_response_message_tab2 = ""
                if result_tab2 and result_tab2.get("answer"):
                    ai_response_message_tab2 += result_tab2.get("answer")

                # Handle Plotly graph in response
                if result_tab2 and result_tab2.get("routing_preprocessor_decision") == "chart" and result_tab2.get("plotly_graph"):
                    try:
                        if isinstance(result_tab2.get("plotly_graph"), dict): # If it's a JSON dict for Plotly
                            plot_tab2 = go.Figure(result_tab2.get("plotly_graph"))
                        else: # Assuming it's already a Plotly Figure object
                            plot_tab2 = result_tab2.get("plotly_graph")

                        idx_tab2 = len(st.session_state.plots_tab2)
                        st.session_state.plots_tab2.append(plot_tab2)
                        ai_response_message_tab2 += f"\nPLOT_INDEX_TAB2:{idx_tab2}" # Append placeholder
                        msgs_tab2.add_ai_message(ai_response_message_tab2)
                        st.rerun() 
                    except Exception as e:
                        error_msg_tab2 = f"Erro ao gerar gráfico: {e}. A IA tentou criar um gráfico, mas falhou."
                        if not ai_response_message_tab2.strip(): ai_response_message_tab2 = "Não houve resposta textual da IA.\n"
                        ai_response_message_tab2 += f"\n\n{error_msg_tab2}"
                        msgs_tab2.add_ai_message(ai_response_message_tab2)
                        st.rerun()

                # Handle DataFrame in response
                elif result_tab2 and result_tab2.get("data_wrangled") is not None: 
                    data_wrangled_tab2 = result_tab2.get("data_wrangled")
                    if not isinstance(data_wrangled_tab2, pd.DataFrame):
                        try:
                            # Attempt to convert if it's list of dicts or similar
                            data_wrangled_tab2 = pd.DataFrame(data_wrangled_tab2)
                        except Exception as e:
                            error_msg_tab2 = f"Erro ao converter para DataFrame: {e}. A IA tentou retornar uma tabela, mas falhou."
                            if not ai_response_message_tab2.strip(): ai_response_message_tab2 = "Não houve resposta textual da IA.\n"
                            ai_response_message_tab2 += f"\n\n{error_msg_tab2}"
                            msgs_tab2.add_ai_message(ai_response_message_tab2)
                            st.rerun()
                            st.stop() # Critical error converting, stop this path
                    
                    # Proceed if conversion was successful or it was already a DataFrame
                    if isinstance(data_wrangled_tab2, pd.DataFrame): 
                        idx_tab2 = len(st.session_state.dataframes_tab2)
                        st.session_state.dataframes_tab2.append(data_wrangled_tab2)
                        ai_response_message_tab2 += f"\nDATAFRAME_INDEX_TAB2:{idx_tab2}" # Append placeholder
                        msgs_tab2.add_ai_message(ai_response_message_tab2)
                        st.rerun() 
                else: 
                    # If only text response or no specific content type identified
                    if not (result_tab2 and ai_response_message_tab2.strip()): # If response is empty or only whitespace
                         ai_response_message_tab2 = "A IA processou sua solicitação, mas não retornou um texto, gráfico ou tabela específica. "
                         ai_response_message_tab2 += f"Resposta completa da IA: {str(result_tab2)}" if result_tab2 else "Nenhuma resposta da IA."
                    msgs_tab2.add_ai_message(ai_response_message_tab2)
                    st.rerun()

# --- TAB 3: AgGrid Viewer ---
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
            tooltipValueGetter = JsCode("function(params) { return params.value; }")
        )
        gb.configure_grid_options(
            domLayout='normal',
            pagination=True,
            paginationPageSize=20,
            floatingFilter=True,
            rowHoverHighlight=True,
            suppressRowClickSelection=False,
            rowSelection='multiple',
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
                { 'id': 'highlightUp', 'font': { 'color': '#FF0000' }, 'interior': { 'color': '#FFCCCC', 'pattern': 'Solid'} },
                { 'id': 'highlightDown', 'font': { 'color': '#0000FF' }, 'interior': { 'color': '#CCCCFF', 'pattern': 'Solid'} }
            ],
            localeText = { # Extensive localization for AgGrid
                "page": "Página", "more": "Mais", "to": "até", "of": "de", "next": "Próxima",
                "last": "Última", "first": "Primeira", "previous": "Anterior", "loadingOoo": "Carregando...",
                "noRowsToShow": "Nenhum dado para mostrar", "filterOoo": "Filtrar...", "applyFilter": "Aplicar",
                "equals": "Igual", "notEqual": "Diferente", "blank": "Vazio", "notBlank": "Preenchido",
                "greaterThan": "Maior que", "greaterThanOrEqual": "Maior ou igual a", "lessThan": "Menor que",
                "lessThanOrEqual": "Menor ou igual a", "inRange": "Entre", "contains": "Contém",
                "notContains": "Não contém", "startsWith": "Começa com", "endsWith": "Termina com",
                "andCondition": "E", "orCondition": "OU", "clearFilter": "Limpar Filtro", "resetFilter": "Redefinir Filtro",
                # ... (keep all other localeText entries from the original script)
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

        grid_options = gb.build()
      
        AgGrid(
            df,
            gridOptions=grid_options,
            height=700,
            width='100%',
            theme="streamlit",
            update_mode=GridUpdateMode.MODEL_CHANGED,
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True,
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

# --- TAB 4: Dynamic Business Insights (from second script) ---
with tab4:
    st.markdown("## 💡 Insights de Negócios Dinâmicos (Gerados por IA)")
    st.markdown("Obtenha uma análise estratégica com base nos **dados filtrados na Aba 1**.")
    st.markdown("---")
    
    # data_for_insights will be df_filtrado_tab1 from Tab 1
    data_for_insights = df_filtrado_tab1.copy() 
    is_filtered = not data_for_insights.equals(df) # Check if it's different from the original df
    num_pac_insights = len(data_for_insights)

    st.markdown(f"**Análise Atual Baseada em:** `{num_pac_insights} paciente(s)` (dados conforme Aba 1).")
    if is_filtered and num_pac_insights < len(df):
        st.caption(f"Dataset original completo continha `{len(df)}` pacientes. Os insights abaixo são para o subconjunto filtrado.")
    elif not is_filtered and num_pac_insights > 0:
        st.caption("Analisando o conjunto de dados completo (nenhum filtro ativo ou filtros não alteraram o conjunto).")
    elif num_pac_insights == 0 and not df.empty: # Filters resulted in zero patients
        st.warning("Os filtros atuais na Aba 1 resultaram em nenhum paciente. Não é possível gerar insights para este subconjunto.")
    elif df.empty: # Original df is empty
        st.warning("Nenhum dado carregado. Por favor, faça o upload de um arquivo CSV para gerar insights.")


    if 'dyn_biz_insights' not in st.session_state: 
        st.session_state.dyn_biz_insights = ""
    if 'gen_dyn_insights' not in st.session_state: 
        st.session_state.gen_dyn_insights = False

    if not llm: 
        st.error("O modelo de IA não foi inicializado. Verifique sua chave da API na barra lateral.")
    elif not df.empty: # Only show button if there's data to potentially analyze
        if st.button("🔍 Gerar Novos Insights (Dados Atuais da Aba 1)", key="gen_dyn_biz_insights_btn", disabled=st.session_state.gen_dyn_insights, use_container_width=True):
            if data_for_insights.empty:
                st.error("Não há dados para os filtros atuais. Ajuste os filtros na Aba 1 para gerar insights.")
                st.session_state.dyn_biz_insights = "" # Clear any previous insights
                st.session_state.gen_dyn_insights = False # Reset button state
            else:
                st.session_state.gen_dyn_insights = True
                st.session_state.dyn_biz_insights = "" # Clear previous insights
                with st.spinner("🧠 A Inteligência Artificial está analisando os dados selecionados e elaborando os insights... Por favor, aguarde."):
                    try:
                        # Prepare a summary of the data_for_insights for the prompt
                        num_cols_ins = len(data_for_insights.columns)
                        
                        # Use status_cols which is globally available and reflects columns ending with _status from the uploaded file
                        ls_stat_cols_str = ", ".join([s.replace('_status','').replace('_',' ').title() for s in status_cols[:10]]) + ("..." if len(status_cols) > 10 else "")
                        
                        pac_alt_ins, pc_pac_alt_ins = 0, 0.0
                        if "paciente_com_alteracao" in data_for_insights.columns:
                            pac_alt_ins = data_for_insights['paciente_com_alteracao'].sum()
                            pc_pac_alt_ins = (pac_alt_ins / num_pac_insights * 100) if num_pac_insights > 0 else 0.0
                        
                        med_ex_alt_geral, med_ex_alt_com_alt = 0.0, 0.0
                        if "qtde_exames_alterados" in data_for_insights.columns and data_for_insights["qtde_exames_alterados"].notna().any():
                            med_ex_alt_geral = data_for_insights['qtde_exames_alterados'].mean()
                            # Calculate mean only for those with alterations and non-NaN qtde_exames_alterados
                            df_pac_alt_ins = data_for_insights[data_for_insights['paciente_com_alteracao'] & data_for_insights['qtde_exames_alterados'].notna()]
                            if not df_pac_alt_ins.empty:
                                 med_ex_alt_com_alt = df_pac_alt_ins['qtde_exames_alterados'].mean()

                        # Use the calculate_top_altered_exams function
                        top_alt_df_ins = calculate_top_altered_exams(data_for_insights, status_cols, ALTERATION_MARKERS)
                        top_alt_str_ins = ""
                        if not top_alt_df_ins.empty:
                            for _, r in top_alt_df_ins.head(5).iterrows(): 
                                top_alt_str_ins += f"- {r['Exame']}: {r['Número de Alterações']} alterações\n"
                        else: 
                            top_alt_str_ins = "Nenhum exame alterado proeminente identificado neste subconjunto de dados."
                        
                        dataset_desc = "completo" if not is_filtered else f"filtrado ({num_pac_insights} de {len(df)} pacientes)"
                        prompt_dyn = f"""
                        Você é um consultor de negócios sênior para uma cooperativa de saúde como a Unimed, especializado em análise de dados laboratoriais para otimização de gestão e cuidado ao paciente.
                        Sua tarefa é analisar o resumo do conjunto de dados laboratoriais ({dataset_desc}) de {num_pac_insights} pacientes e fornecer de 3 a 5 insights de negócios estratégicos e acionáveis em português do Brasil.

                        Resumo dos Dados Analisados ({dataset_desc}):
                        - Número total de pacientes neste conjunto: {num_pac_insights}
                        - Número total de colunas de dados (exames, dados demográficos, etc.): {num_cols_ins}
                        - Alguns dos principais exames com status de alteração monitorados no dataset original: {ls_stat_cols_str if ls_stat_cols_str else "N/A"}
                        - Pacientes com pelo menos um exame alterado (neste conjunto): {pac_alt_ins} ({pc_pac_alt_ins:.1f}%)
                        - Média de exames alterados por paciente (neste conjunto, geral): {med_ex_alt_geral:.2f}
                        - Média de exames alterados (neste conjunto, considerando apenas pacientes com alguma alteração): {med_ex_alt_com_alt:.2f}
                        - Top 5 exames com maior número de alterações totais (neste conjunto):
                        {top_alt_str_ins if top_alt_str_ins.strip() and top_alt_str_ins != "Nenhum exame alterado proeminente identificado neste subconjunto de dados." else "   - Não há dados suficientes ou nenhuma alteração proeminente para listar os top exames neste subconjunto."}

                        Com base neste resumo específico do conjunto de dados ({dataset_desc}), por favor, gere de 3 a 5 insights de negócios acionáveis.
                        Os insights devem ser apresentados em formato de lista (bullet points).
                        Foque em:
                        1.  Identificação de tendências de saúde específicas deste grupo de pacientes que podem requerer atenção ou programas preventivos direcionados.
                        2.  Oportunidades para otimizar recursos ou processos com base nas alterações mais frequentes observadas neste subconjunto.
                        3.  Sugestões para comunicação ou engajamento com este perfil específico de pacientes (se aplicável).
                        4.  Possíveis investigações adicionais que a Unimed poderia conduzir para aprofundar o entendimento sobre este grupo.
                        5.  Considerações sobre o impacto financeiro ou operacional das tendências observadas neste subconjunto.

                        Formato da Resposta (exclusivamente em português do Brasil):
                        **Principais Insights Estratégicos para a Unimed (referente ao grupo de {num_pac_insights} pacientes analisados):**

                        * **[Insight 1]:** [Descrição detalhada do insight e sugestão de ação específica para este grupo]
                        * **[Insight 2]:** [Descrição detalhada do insight e sugestão de ação específica para este grupo]
                        * ... e assim por diante.

                        Seja claro, conciso e oriente suas sugestões para a realidade de uma operadora de saúde, considerando as características do grupo analisado.
                        Evite jargões excessivamente técnicos na apresentação final dos insights, visando a compreensão por gestores.
                        Se o número de pacientes ({num_pac_insights}) for muito baixo (e.g., menos de 10-20), mencione isso como uma limitação para a generalização dos achados e sugira cautela na interpretação.
                        """
                        response = llm.invoke(prompt_dyn) # Assuming llm is ChatOpenAI and has invoke method
                        st.session_state.dyn_biz_insights = response.content # Adjust if response structure is different (e.g. response.text)
                    except Exception as e:
                        st.error(f"Ocorreu um erro ao gerar os insights: {str(e)}")
                        st.session_state.dyn_biz_insights = "Não foi possível gerar os insights no momento. Tente novamente."
                    finally:
                        st.session_state.gen_dyn_insights = False
                        st.rerun() # Rerun to update button state and display insights/error
        
        if st.session_state.gen_dyn_insights:
             st.info("Gerando insights para os dados selecionados... Este processo pode levar alguns instantes.")
        elif st.session_state.dyn_biz_insights: # If insights have been generated
            with st.container(border=True):
                st.markdown("#### 🧠 Análise da IA (Baseada nos Filtros Atuais da Aba 1):")
                st.markdown(st.session_state.dyn_biz_insights)
        elif not st.session_state.gen_dyn_insights and not st.session_state.dyn_biz_insights and not data_for_insights.empty:
            # No insights generated yet, not currently generating, and there's data to analyze
            st.info("Clique no botão acima para que a Inteligência Artificial gere insights de negócios com base nos dados atualmente filtrados na Aba 1.")
        # If data_for_insights is empty (but df is not), the message is already handled by the warning at the top of the tab.