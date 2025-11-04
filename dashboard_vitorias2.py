
import streamlit as st
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
import plotly.express as px
import pandas as pd

# ======================
# CONFIGURAÇÕES INICIAIS
# ======================
st.set_page_config(
    page_title="Dashboard Brasileirão",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Criar sessão Spark
spark = SparkSession.builder.appName("DashboardVitorias").getOrCreate()

# ======================
# CARREGAR OS DADOS
# ======================
df = spark.read.csv("mundo_transfermarkt_competicoes_brasileirao_serie_a (1).csv", header=True, inferSchema=True)
df_ultimos5 = df.filter(col("ano_campeonato") >= 2020)

# Determinar o vencedor de cada partida
df_ultimos5 = df_ultimos5.withColumn(
    "vencedor",
    when(col("gols_mandante") > col("gols_visitante"), col("time_mandante"))
    .when(col("gols_visitante") > col("gols_mandante"), col("time_visitante"))
    .otherwise("Empate")
)

# ======================
# AGRUPAR RESULTADOS
# ======================

# Vitórias como mandante
vitorias_mandante = (
    df_ultimos5.filter(col("vencedor") == col("time_mandante"))
    .groupBy("ano_campeonato", "time_mandante")
    .count()
    .withColumnRenamed("count", "vitorias_casa")
)

# Vitórias como visitante
vitorias_visitante = (
    df_ultimos5.filter(col("vencedor") == col("time_visitante"))
    .groupBy("ano_campeonato", "time_visitante")
    .count()
    .withColumnRenamed("count", "vitorias_fora")
)

# ======================
# JOGOS DISPUTADOS
# ======================
jogos_mandante = (
    df_ultimos5.groupBy("ano_campeonato", "time_mandante")
    .count()
    .withColumnRenamed("count", "jogos_casa")
)

jogos_visitante = (
    df_ultimos5.groupBy("ano_campeonato", "time_visitante")
    .count()
    .withColumnRenamed("count", "jogos_fora")
)

# ======================
# APROVEITAMENTO (%)
# ======================
df_casa_stats = vitorias_mandante.join(jogos_mandante, ["ano_campeonato", "time_mandante"], "left") \
    .withColumn("aproveitamento_casa", (col("vitorias_casa") / col("jogos_casa")) * 100)

df_fora_stats = vitorias_visitante.join(jogos_visitante, ["ano_campeonato", "time_visitante"], "left") \
    .withColumn("aproveitamento_fora", (col("vitorias_fora") / col("jogos_fora")) * 100)

# Converter para Pandas
df_vit_casa = df_casa_stats.toPandas()
df_vit_fora = df_fora_stats.toPandas()

# ======================
# INTERFACE STREAMLIT
# ======================

st.markdown(
    """
    <style>
    .big-title {
        font-size: 36px;
        font-weight: bold;
        color: #FFD700;
        text-align: center;
    }
    .subtitle {
        font-size: 20px;
        color: #CCCCCC;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<p class="big-title">🏆 Dashboard Brasileirão - Vitórias & Aproveitamento (2020–2024)</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análise dos times com mais vitórias e melhor aproveitamento em casa e fora</p>', unsafe_allow_html=True)

# ======================
# SIDEBAR
# ======================
anos_disponiveis = sorted(df_vit_casa["ano_campeonato"].unique())
ano_selecionado = st.sidebar.selectbox("📅 Selecione o ano", anos_disponiveis)

todos_times = sorted(
    set(df_vit_casa["time_mandante"].unique()) |
    set(df_vit_fora["time_visitante"].unique())
)
time_selecionado = st.sidebar.selectbox("⚽ Selecione um time para ver evolução", todos_times)

# ======================
# GRÁFICOS PRINCIPAIS
# ======================
col1, col2 = st.columns(2)

df_casa_ano = df_vit_casa[df_vit_casa["ano_campeonato"] == ano_selecionado]
df_fora_ano = df_vit_fora[df_vit_fora["ano_campeonato"] == ano_selecionado]

df_casa_top = df_casa_ano.sort_values(by="vitorias_casa", ascending=False).head(10)
df_fora_top = df_fora_ano.sort_values(by="vitorias_fora", ascending=False).head(10)

with col1:
    st.subheader(f"🏠 Top 10 Times Mandantes - {ano_selecionado}")
    fig_casa = px.bar(
        df_casa_top,
        x="time_mandante",
        y="vitorias_casa",
        color="time_mandante",
        text="vitorias_casa",
        title="Vitórias em Casa",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_casa.update_layout(template="plotly_dark", xaxis_title=None, yaxis_title="Vitórias", title_x=0.5)
    st.plotly_chart(fig_casa, use_container_width=True)

with col2:
    st.subheader(f"🚗 Top 10 Times Visitantes - {ano_selecionado}")
    fig_fora = px.bar(
        df_fora_top,
        x="time_visitante",
        y="vitorias_fora",
        color="time_visitante",
        text="vitorias_fora",
        title="Vitórias Fora de Casa",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_fora.update_layout(template="plotly_dark", xaxis_title=None, yaxis_title="Vitórias", title_x=0.5)
    st.plotly_chart(fig_fora, use_container_width=True)

# ======================
# TABELA DE APROVEITAMENTO
# ======================
st.markdown("### ⚙️ Aproveitamento dos 10 Melhores Times")

df_casa_aprov = df_casa_ano.sort_values(by="aproveitamento_casa", ascending=False).head(10)
df_fora_aprov = df_fora_ano.sort_values(by="aproveitamento_fora", ascending=False).head(10)

col1, col2 = st.columns(2)
with col1:
    st.write("🏠 **Aproveitamento em Casa (%)**")
    st.dataframe(df_casa_aprov[["time_mandante", "vitorias_casa", "jogos_casa", "aproveitamento_casa"]])

with col2:
    st.write("🚗 **Aproveitamento Fora (%)**")
    st.dataframe(df_fora_aprov[["time_visitante", "vitorias_fora", "jogos_fora", "aproveitamento_fora"]])

# ======================
# EVOLUÇÃO POR TIME
# ======================
st.markdown("---")
st.subheader(f"📈 Evolução de Vitórias e Aproveitamento – {time_selecionado}")

df_casa_time = df_vit_casa[df_vit_casa["time_mandante"] == time_selecionado]
df_fora_time = df_vit_fora[df_vit_fora["time_visitante"] == time_selecionado]

df_evolucao = pd.merge(df_casa_time, df_fora_time, on="ano_campeonato", how="outer").fillna(0)
df_evolucao["total_vitorias"] = df_evolucao["vitorias_casa"] + df_evolucao["vitorias_fora"]
df_evolucao["aproveitamento_total"] = (
    (df_evolucao["vitorias_casa"] + df_evolucao["vitorias_fora"]) /
    (df_evolucao["jogos_casa"] + df_evolucao["jogos_fora"])
) * 100

fig_evolucao = px.line(
    df_evolucao,
    x="ano_campeonato",
    y=["vitorias_casa", "vitorias_fora", "total_vitorias"],
    markers=True,
    title=f"Evolução de Vitórias do {time_selecionado}",
    color_discrete_map={
        "vitorias_casa": "#1f77b4",
        "vitorias_fora": "#2ca02c",
        "total_vitorias": "#FFD700"
    }
)
fig_evolucao.update_layout(template="plotly_dark", xaxis_title="Ano", yaxis_title="Vitórias", title_x=0.5)
st.plotly_chart(fig_evolucao, use_container_width=True)

# ======================
# RODAPÉ
# ======================
st.markdown("---")
st.caption("📊 Desenvolvido por Tereza Figueiredo | PySpark + Streamlit + Plotly")
