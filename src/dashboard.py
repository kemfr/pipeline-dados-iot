"""Dashboard analítico de leituras IoT usando Streamlit, Plotly e PostgreSQL."""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

st.set_page_config(
    page_title="IoT | Central de Temperaturas",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Visual: painel escuro, contraste alto, cards discretos e gráficos consistentes.
st.markdown(
    """
    <style>
      :root {
        --iot-bg: #08111f;
        --iot-panel: #101d30;
        --iot-panel-alt: #13243a;
        --iot-border: rgba(148, 163, 184, .17);
        --iot-text: #edf5ff;
        --iot-muted: #91a4bb;
        --iot-cyan: #4dd6d0;
        --iot-blue: #68a9ff;
        --iot-violet: #a99bff;
      }
      html, body, [data-testid="stAppViewContainer"] {
        background: radial-gradient(ellipse at top left, #12233a 0%, var(--iot-bg) 43%, #060d17 100%);
        color: var(--iot-text);
      }
      [data-testid="stHeader"] { background: rgba(8, 17, 31, .72); }
      [data-testid="stToolbar"] { right: 1rem; }
      .block-container { max-width: 1500px; padding-top: 2rem; padding-bottom: 2.5rem; }
      h1, h2, h3 { color: var(--iot-text) !important; letter-spacing: -0.025em; }
      h1 { font-size: clamp(2rem, 3.1vw, 2.8rem) !important; font-weight: 750 !important; }
      h2 { font-size: 1.25rem !important; font-weight: 680 !important; }
      p, label, [data-testid="stCaptionContainer"] { color: var(--iot-muted); }
      .hero { padding: .25rem 0 1rem 0; }
      .eyebrow {
        display: inline-flex; align-items: center; gap: .5rem;
        padding: .38rem .72rem; border: 1px solid rgba(77,214,208,.28);
        border-radius: 999px; color: #9bf0ea; background: rgba(77,214,208,.08);
        font-size: .74rem; font-weight: 750; letter-spacing: .13em; text-transform: uppercase;
      }
      .hero-subtitle { color: #9aacc2; font-size: 1rem; margin-top: -.4rem; }
      .hero-meta { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1rem; }
      .meta-pill { border: 1px solid var(--iot-border); background: rgba(16,29,48,.74); color: #b8c8dc;
        border-radius: 8px; padding: .38rem .62rem; font-size: .78rem; }
      .metric-card {
        position: relative; overflow: hidden; min-height: 132px; height: 100%;
        border: 1px solid var(--iot-border); border-radius: 16px;
        padding: 1.05rem 1.1rem 1rem;
        background: linear-gradient(145deg, rgba(19,36,58,.96), rgba(12,24,41,.96));
        box-shadow: 0 12px 28px rgba(0,0,0,.12);
      }
      .metric-card:before { content: ""; position: absolute; left: 0; top: 0; width: 100%; height: 3px;
        background: var(--metric-accent, var(--iot-cyan)); opacity: .9; }
      .metric-head { display: flex; align-items: center; justify-content: space-between; gap: .5rem; }
      .metric-label { color: #9fb2c9; font-size: .81rem; font-weight: 650; }
      .metric-icon { display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px;
        border-radius: 9px; background: rgba(255,255,255,.055); font-size: 1rem; }
      .metric-value { margin-top: .65rem; color: var(--iot-text); font-size: clamp(1.35rem, 2.1vw, 1.9rem);
        font-weight: 760; line-height: 1.15; letter-spacing: -.035em; overflow-wrap: anywhere; }
      .metric-foot { margin-top: .45rem; color: #7f94ad; font-size: .74rem; }
      .section-kicker { color: #6f91b5; font-size: .72rem; font-weight: 750; letter-spacing: .13em;
        text-transform: uppercase; margin: .25rem 0 .1rem; }
      .section-note { color: #91a4bb; font-size: .88rem; margin-top: -.65rem; margin-bottom: .7rem; }
      .panel { border: 1px solid var(--iot-border); border-radius: 16px; padding: .35rem .8rem .15rem;
        background: rgba(13, 26, 44, .76); }
      .insight-card { height: 100%; border: 1px solid var(--iot-border); border-radius: 14px; padding: 1rem;
        background: rgba(16,29,48,.8); }
      .insight-label { color: #90a5bd; font-size: .78rem; font-weight: 650; }
      .insight-value { color: #f1f7ff; font-size: 1.35rem; font-weight: 760; margin-top: .42rem; }
      .insight-detail { color: #8fa4bd; font-size: .78rem; line-height: 1.45; margin-top: .32rem; }
      .note-box { border-left: 3px solid var(--iot-cyan); padding: .72rem .9rem; background: rgba(77,214,208,.055);
        border-radius: 0 10px 10px 0; color: #a9bbcf; font-size: .82rem; }
      hr { border-color: var(--iot-border) !important; margin: 1.5rem 0 !important; }
      [data-testid="stExpander"] { background: rgba(16,29,48,.58); border: 1px solid var(--iot-border); border-radius: 12px; }
      [data-testid="stDataFrame"] { border: 1px solid var(--iot-border); border-radius: 10px; }
      .footer { text-align: center; color: #637891; font-size: .76rem; padding-top: 1.3rem; }
      @media (max-width: 800px) { .block-container { padding-top: 1rem; } .metric-card { min-height: 120px; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def number_pt(value: int | float) -> str:
    """Formata número usando separadores comuns no Brasil."""
    if pd.isna(value):
        return "—"
    if isinstance(value, int) or float(value).is_integer():
        return f"{int(value):,}".replace(",", ".")
    return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def metric_card(label: str, value: str, foot: str, icon: str, accent: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card" style="--metric-accent:{accent}">
          <div class="metric-head">
            <span class="metric-label">{label}</span>
            <span class="metric-icon">{icon}</span>
          </div>
          <div class="metric-value">{value}</div>
          <div class="metric-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(label: str, value: str, detail: str) -> None:
    st.markdown(
        f"""
        <div class="insight-card">
          <div class="insight-label">{label}</div>
          <div class="insight-value">{value}</div>
          <div class="insight-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_figure(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=18, r=18, t=18, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#b4c5d9", size=12),
        hoverlabel=dict(bgcolor="#14243a", bordercolor="#2d4664", font=dict(color="#f3f7fb", size=12)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(148,163,184,.22)",
        tickfont=dict(color="#93a9c2", size=11),
        title_font=dict(color="#a9bbcf", size=12),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,.13)",
        zeroline=False,
        linecolor="rgba(148,163,184,.12)",
        tickfont=dict(color="#93a9c2", size=11),
        title_font=dict(color="#a9bbcf", size=12),
    )
    return fig


# Conexão com o banco: endereço vem do arquivo .env e nunca é exibido na página.
database_url = os.getenv("DATABASE_URL")
if not database_url:
    st.error("A conexão com o banco não está configurada. Copie .env.example para .env e preencha DATABASE_URL.")
    st.stop()


@st.cache_resource
def get_engine(url: str):
    return create_engine(url, pool_pre_ping=True, pool_recycle=1800)


@st.cache_data(ttl=60)
def read_view(view_name: str) -> pd.DataFrame:
    # Os nomes usados aqui são fixos, não vêm de entradas do usuário.
    allowed_views = {
        "avg_temp_por_categoria",
        "leituras_por_hora",
        "temp_max_min_por_dia",
    }
    if view_name not in allowed_views:
        raise ValueError("View não permitida.")
    with get_engine(database_url).connect() as connection:
        return pd.read_sql(text(f'SELECT * FROM "{view_name}"'), connection)


# Cabeçalho
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">● &nbsp; IoT DATA PLATFORM</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.title("Central de Temperaturas")
st.markdown(
    '<div class="hero-subtitle">Uma visão operacional das leituras de temperatura coletadas por dispositivos IoT.</div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="hero-meta">
      <span class="meta-pill">PIPELINE &nbsp; CSV → PYTHON → POSTGRESQL</span>
      <span class="meta-pill">VISUALIZAÇÃO &nbsp; STREAMLIT + PLOTLY</span>
      <span class="meta-pill">FONTE &nbsp; KAGGLE</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

try:
    by_category = read_view("avg_temp_por_categoria").copy()
    by_hour = read_view("leituras_por_hora").copy()
    by_day = read_view("temp_max_min_por_dia").copy()
except Exception as exc:  # A mensagem ajuda a diagnosticar erros locais de configuração.
    st.error("Não foi possível consultar as views do PostgreSQL.")
    st.code(str(exc))
    st.info("Verifique se o contêiner está ativo e execute: python src/load_data.py e python src/create_views.py")
    st.stop()

if by_category.empty or by_hour.empty or by_day.empty:
    st.warning("Uma ou mais views estão vazias. Verifique a carga do CSV e as views SQL.")
    st.stop()

required = {
    "avg_temp_por_categoria": {"tipo_local", "total_leituras", "temp_media", "temp_min", "temp_max"},
    "leituras_por_hora": {"hora", "contagem"},
    "temp_max_min_por_dia": {"data", "temp_max", "temp_min", "temp_media", "total_leituras"},
}
for view, frame in [
    ("avg_temp_por_categoria", by_category),
    ("leituras_por_hora", by_hour),
    ("temp_max_min_por_dia", by_day),
]:
    missing = required[view] - set(frame.columns)
    if missing:
        st.error(f"A view {view} não possui as colunas esperadas: {', '.join(sorted(missing))}.")
        st.stop()

by_category["total_leituras"] = pd.to_numeric(by_category["total_leituras"], errors="coerce").fillna(0)
by_category["temp_media"] = pd.to_numeric(by_category["temp_media"], errors="coerce")
by_category["temp_min"] = pd.to_numeric(by_category["temp_min"], errors="coerce")
by_category["temp_max"] = pd.to_numeric(by_category["temp_max"], errors="coerce")
by_hour["hora"] = pd.to_numeric(by_hour["hora"], errors="coerce")
by_hour["contagem"] = pd.to_numeric(by_hour["contagem"], errors="coerce")
by_day["data"] = pd.to_datetime(by_day["data"], errors="coerce")
for column in ["temp_max", "temp_min", "temp_media", "total_leituras"]:
    by_day[column] = pd.to_numeric(by_day[column], errors="coerce")

# KPIs: agregados calculados a partir das views criadas no PostgreSQL.
total_readings = int(by_category["total_leituras"].sum())
valid_weight = by_category["temp_media"].notna() & (by_category["total_leituras"] > 0)
avg_temp = (
    (by_category.loc[valid_weight, "temp_media"] * by_category.loc[valid_weight, "total_leituras"]).sum()
    / by_category.loc[valid_weight, "total_leituras"].sum()
    if valid_weight.any()
    else float("nan")
)
valid_dates = by_day["data"].dropna()
min_date = valid_dates.min().strftime("%d/%m/%Y") if not valid_dates.empty else "—"
max_date = valid_dates.max().strftime("%d/%m/%Y") if not valid_dates.empty else "—"
days_count = int(valid_dates.dt.date.nunique()) if not valid_dates.empty else 0

st.markdown('<div class="section-kicker">VISÃO GERAL</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4, gap="medium")
with k1:
    metric_card("Total de leituras", number_pt(total_readings), "Registros carregados no PostgreSQL", "▦", "#4dd6d0")
with k2:
    metric_card("Temperatura média", number_pt(avg_temp), "Unidade original do arquivo", "◉", "#68a9ff")
with k3:
    metric_card("Dias com registros", number_pt(days_count), "Dias distintos identificados", "▣", "#a99bff")
with k4:
    metric_card("Janela temporal", f"{min_date} – {max_date}", "Primeira e última data da base", "◷", "#f7b267")

st.write("")
st.markdown(
    '<div class="note-box">A base não declara a unidade da temperatura no cabeçalho. Por isso, os valores são apresentados na unidade original, sem assumir °C ou °F.</div>',
    unsafe_allow_html=True,
)
st.write("")
st.markdown('<div class="section-kicker">ANÁLISE DAS LEITURAS</div>', unsafe_allow_html=True)
st.header("Temperatura e volume de leituras")
st.markdown('<div class="section-note">Compare as médias por categoria e observe em quais horários os registros se concentram.</div>', unsafe_allow_html=True)

category_order = [x for x in ["In", "Out"] if x in by_category["tipo_local"].astype(str).tolist()]
category_order += [x for x in by_category["tipo_local"].astype(str).tolist() if x not in category_order]
category_plot = by_category.copy()
category_plot["tipo_local"] = category_plot["tipo_local"].astype(str)
category_plot = category_plot.set_index("tipo_local").reindex(category_order).reset_index()
category_colors = {"In": "#4dd6d0", "Out": "#68a9ff"}
bar_colors = [category_colors.get(category, "#a99bff") for category in category_plot["tipo_local"]]
fig_category = go.Figure(
    go.Bar(
        x=category_plot["tipo_local"],
        y=category_plot["temp_media"],
        marker=dict(color=bar_colors, line=dict(color="rgba(255,255,255,.10)", width=1)),
        text=[number_pt(value) for value in category_plot["temp_media"]],
        textposition="outside",
        cliponaxis=False,
        customdata=category_plot[["total_leituras", "temp_min", "temp_max"]].to_numpy(),
        hovertemplate="Categoria: %{x}<br>Média: %{y:.2f}<br>Leituras: %{customdata[0]:,.0f}<br>Mínima: %{customdata[1]}<br>Máxima: %{customdata[2]}<extra></extra>",
    )
)
fig_category.update_layout(showlegend=False, bargap=0.55, yaxis_title="Temperatura média (unidade original)", xaxis_title="Categoria")
fig_category.update_yaxes(rangemode="tozero")
style_figure(fig_category, 330)

# O gráfico de horas e o de categorias ficam lado a lado para melhorar a leitura na tela.
left_chart, right_chart = st.columns([1, 1], gap="large")
with left_chart:
    st.subheader("Temperatura média por categoria")
    st.caption("Comparação das categorias In e Out.")
    st.plotly_chart(fig_category, use_container_width=True, config={"displayModeBar": False, "responsive": True}, key="category_chart")
with right_chart:
    st.subheader("Quantidade por hora")
    st.caption("Volume de registros agrupado pela hora da medição.")
    by_hour = by_hour.dropna(subset=["hora", "contagem"]).sort_values("hora")
    peak_hour_row = by_hour.loc[by_hour["contagem"].idxmax()] if not by_hour.empty else None
    peak_hour = int(peak_hour_row["hora"]) if peak_hour_row is not None else None
    hourly_colors = ["#4dd6d0" if peak_hour is not None and int(hour) == peak_hour else "#68a9ff" for hour in by_hour["hora"]]
    fig_hour = go.Figure(
        go.Scatter(
            x=by_hour["hora"], y=by_hour["contagem"], mode="lines+markers",
            line=dict(color="#68a9ff", width=3, shape="spline", smoothing=0.35),
            marker=dict(color=hourly_colors, size=7, line=dict(color="#0b1727", width=1.5)),
            fill="tozeroy", fillcolor="rgba(104,169,255,.08)",
            hovertemplate="Hora: %{x}:00<br>Leituras: %{y:,.0f}<extra></extra>",
        )
    )
    fig_hour.update_layout(showlegend=False, xaxis_title="Hora do dia", yaxis_title="Número de leituras")
    fig_hour.update_xaxes(dtick=2, range=[-0.5, 23.5])
    fig_hour.update_yaxes(rangemode="tozero")
    style_figure(fig_hour, 330)
    st.plotly_chart(fig_hour, use_container_width=True, config={"displayModeBar": False, "responsive": True}, key="hour_chart")

st.write("")
st.subheader("Evolução diária das temperaturas")
st.markdown('<div class="section-note">Valores máximos e mínimos registrados em cada dia do período disponível.</div>', unsafe_allow_html=True)
by_day = by_day.dropna(subset=["data"]).sort_values("data")
fig_day = go.Figure()
fig_day.add_trace(
    go.Scatter(
        x=by_day["data"], y=by_day["temp_max"], name="Máxima", mode="lines+markers",
        line=dict(color="#4dd6d0", width=2.6), marker=dict(size=5, color="#4dd6d0"),
        hovertemplate="Data: %{x|%d/%m/%Y}<br>Máxima: %{y}<extra></extra>",
    )
)
fig_day.add_trace(
    go.Scatter(
        x=by_day["data"], y=by_day["temp_min"], name="Mínima", mode="lines+markers",
        line=dict(color="#a99bff", width=2.4), marker=dict(size=5, color="#a99bff"),
        hovertemplate="Data: %{x|%d/%m/%Y}<br>Mínima: %{y}<extra></extra>",
    )
)
fig_day.update_layout(xaxis_title="Data", yaxis_title="Temperatura (unidade original)")
fig_day.update_xaxes(tickformat="%d/%m", nticks=10)
style_figure(fig_day, 410)
st.plotly_chart(fig_day, use_container_width=True, config={"displayModeBar": False, "responsive": True}, key="daily_chart")

# Insights calculados dos próprios agregados: não dependem de números digitados manualmente.
st.markdown('<div class="section-kicker">DESTAQUES DO CONJUNTO DE DADOS</div>', unsafe_allow_html=True)
i1, i2, i3 = st.columns(3, gap="medium")
with i1:
    if peak_hour_row is not None:
        insight_card("Hora com mais registros", f"{int(peak_hour_row['hora']):02d}:00", f"{number_pt(peak_hour_row['contagem'])} leituras agrupadas nessa hora.")
    else:
        insight_card("Hora com mais registros", "—", "Não há dados horários disponíveis.")
with i2:
    valid_categories = by_category.dropna(subset=["temp_media"])
    if not valid_categories.empty:
        warmest = valid_categories.loc[valid_categories["temp_media"].idxmax()]
        insight_card("Maior média por categoria", str(warmest["tipo_local"]), f"Média de {number_pt(warmest['temp_media'])} na unidade original do arquivo.")
    else:
        insight_card("Maior média por categoria", "—", "Não há médias disponíveis.")
with i3:
    if not by_day.empty and by_day["temp_max"].notna().any():
        max_idx = by_day["temp_max"].idxmax()
        max_row = by_day.loc[max_idx]
        insight_card("Maior máxima diária", number_pt(max_row["temp_max"]), f"Registrada em {max_row['data'].strftime('%d/%m/%Y')}.")
    else:
        insight_card("Maior máxima diária", "—", "Não há máximas diárias disponíveis.")

with st.expander("Consultar resumo por categoria"):
    category_display = by_category.rename(columns={
        "tipo_local": "Categoria", "total_leituras": "Total de leituras", "temp_media": "Temperatura média",
        "temp_min": "Temperatura mínima", "temp_max": "Temperatura máxima",
    })
    st.dataframe(category_display, use_container_width=True, hide_index=True)
with st.expander("Consultar resumo diário"):
    daily_display = by_day.rename(columns={
        "data": "Data", "temp_max": "Temperatura máxima", "temp_min": "Temperatura mínima",
        "temp_media": "Temperatura média", "total_leituras": "Total de leituras",
    }).copy()
    if "Data" in daily_display:
        daily_display["Data"] = daily_display["Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(daily_display, use_container_width=True, hide_index=True)

st.markdown(
    """
    <div class="footer">
      PIPELINE DE DADOS IOT &nbsp; • &nbsp; Dados: Temperature Readings: IoT Devices / Kaggle<br>
      Python + Pandas · PostgreSQL · Streamlit · Plotly
    </div>
    """,
    unsafe_allow_html=True,
)
