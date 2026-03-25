# app.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.data_fetcher import load_or_fetch, get_curve_snapshot
from src.analyzer import (
    classify_yield_curve,
    recession_signal,
    rolling_volatility,
    spread_zscore,
    summary_stats
)

# --- Page Config ---
st.set_page_config(
    page_title="Fixed Income Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- Load Data ---
@st.cache_data(ttl=3600)
def get_data():
    df, spreads = load_or_fetch()
    return df, spreads

df, spreads = get_data()
snapshot    = get_curve_snapshot(df)
signals     = recession_signal(spreads)
vol         = rolling_volatility(df)
stats       = summary_stats(df, spreads)
shape, desc = classify_yield_curve(snapshot)

# --- Header ---
st.title("📈 Fixed Income Analytics Dashboard")
st.caption("US Treasury Yield Curve | Data source: FRED (Federal Reserve)")
st.divider()

# --- KPI Cards Row 1 — Current Yields ---
st.subheader("Current Treasury Yields")
c1, c2, c3, c4, c5 = st.columns(5)

def delta_color(val):
    return "normal" if val >= 0 else "inverse"

c1.metric("3M Yield",  f"{snapshot['3M']:.2f}%",  f"{stats.loc['3M Yield',  'change']:+.3f}%")
c2.metric("2Y Yield",  f"{snapshot['2Y']:.2f}%",  f"{stats.loc['2Y Yield',  'change']:+.3f}%")
c3.metric("5Y Yield",  f"{snapshot['5Y']:.2f}%",  f"{stats.loc['5Y Yield',  'change']:+.3f}%")
c4.metric("10Y Yield", f"{snapshot['10Y']:.2f}%", f"{stats.loc['10Y Yield', 'change']:+.3f}%")
c5.metric("30Y Yield", f"{snapshot['30Y']:.2f}%", f"{stats.loc['30Y Yield', 'change']:+.3f}%")

# --- KPI Cards Row 2 — Spreads ---
st.subheader("Key Spreads")
s1, s2, s3, s4, s5 = st.columns(5)

s1.metric("Curve Shape", shape)
s2.metric("10Y-2Y Spread", f"{stats.loc['10Y-2Y Spread', 'current']:.2f}%",
          f"{stats.loc['10Y-2Y Spread', 'change']:+.3f}%")
s3.metric("10Y-3M Spread", f"{stats.loc['10Y-3M Spread', 'current']:.2f}%",
          f"{stats.loc['10Y-3M Spread', 'change']:+.3f}%")
s4.metric("30Y-10Y Spread", f"{stats.loc['30Y-10Y Spread', 'current']:.2f}%",
          f"{stats.loc['30Y-10Y Spread', 'change']:+.3f}%")
s5.metric("5Y-2Y Spread", f"{stats.loc['5Y-2Y Spread', 'current']:.2f}%",
          f"{stats.loc['5Y-2Y Spread', 'change']:+.3f}%")

st.divider()

# --- Date Range Filter ---
st.subheader("Historical Analysis")
col_start, col_end, _ = st.columns([1, 1, 3])
start_date = col_start.date_input("From", value=pd.Timestamp("2015-01-01"))
end_date   = col_end.date_input("To",   value=df.index[-1])

df_filtered      = df.loc[start_date:end_date]
spreads_filtered = spreads.loc[start_date:end_date]
signals_filtered = signals.loc[start_date:end_date]
vol_filtered     = vol.loc[start_date:end_date]

# --- Chart 1 — Yield Curve Snapshot ---
left, right = st.columns(2)

with left:
    st.markdown("#### 📉 Current Yield Curve Shape")
    tenors = ["3M", "2Y", "5Y", "10Y", "30Y"]
    values = [snapshot[t] for t in tenors]
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=tenors, y=values,
        mode="lines+markers",
        line=dict(color="#2563eb", width=3),
        marker=dict(size=10)
    ))
    fig1.update_layout(
        yaxis_title="Yield (%)",
        xaxis_title="Maturity",
        height=350,
        margin=dict(t=20)
    )
    st.plotly_chart(fig1, use_container_width=True)

# --- Chart 2 — Historical Yields ---
with right:
    st.markdown("#### 📈 Historical Treasury Yields")
    fig2 = go.Figure()
    colors = ["#2563eb", "#16a34a", "#d97706", "#dc2626", "#7c3aed"]
    for i, col in enumerate(["3M", "2Y", "5Y", "10Y", "30Y"]):
        fig2.add_trace(go.Scatter(
            x=df_filtered.index,
            y=df_filtered[col],
            name=col,
            line=dict(color=colors[i], width=1.5)
        ))
    fig2.update_layout(
        yaxis_title="Yield (%)",
        height=350,
        margin=dict(t=20),
        legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Chart 3 — Spread History ---
st.markdown("#### 📊 Yield Spread History")
fig3 = go.Figure()
spread_colors = {"10Y-2Y": "#dc2626", "10Y-3M": "#d97706",
                 "30Y-10Y": "#2563eb", "5Y-2Y": "#16a34a"}
for col, color in spread_colors.items():
    fig3.add_trace(go.Scatter(
        x=spreads_filtered.index,
        y=spreads_filtered[col],
        name=col,
        line=dict(color=color, width=1.5)
    ))
fig3.add_hline(y=0, line_dash="dash", line_color="black", line_width=1.5,
               annotation_text="Inversion Line")
fig3.update_layout(
    yaxis_title="Spread (%)",
    height=350,
    margin=dict(t=20),
    legend=dict(orientation="h", y=-0.2)
)
st.plotly_chart(fig3, use_container_width=True)

# --- Chart 4 & 5 side by side ---
col_left, col_right = st.columns(2)

# Chart 4 — Recession Signal
with col_left:
    st.markdown("#### 🚨 10Y-2Y Recession Signal")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=signals_filtered.index,
        y=signals_filtered["10Y-2Y"],
        fill="tozeroy",
        line=dict(color="#2563eb", width=1.5),
        name="10Y-2Y Spread"
    ))
    fig4.add_hline(y=0, line_dash="dash", line_color="#dc2626",
                   line_width=2, annotation_text="⛔ Inversion")
    fig4.update_layout(
        yaxis_title="Spread (%)",
        height=320,
        margin=dict(t=20)
    )
    st.plotly_chart(fig4, use_container_width=True)

# Chart 5 — Rolling Volatility
with col_right:
    st.markdown("#### 📉 30-Day Rolling Volatility")
    fig5 = go.Figure()
    vol_colors = {"2Y_vol": "#16a34a", "5Y_vol": "#d97706",
                  "10Y_vol": "#dc2626", "30Y_vol": "#7c3aed"}
    for col, color in vol_colors.items():
        fig5.add_trace(go.Scatter(
            x=vol_filtered.index,
            y=vol_filtered[col],
            name=col.replace("_vol", "Y"),
            line=dict(color=color, width=1.5)
        ))
    fig5.update_layout(
        yaxis_title="Volatility (std)",
        height=320,
        margin=dict(t=20),
        legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig5, use_container_width=True)

# --- Summary Table ---
st.divider()
st.markdown("#### 📋 Summary Statistics Table")
st.dataframe(
    stats.style.format({
        "current": "{:.2f}",
        "change":  "{:+.3f}",
        "1Y_high": "{:.2f}",
        "1Y_low":  "{:.2f}"
    }),
    use_container_width=True
)

# --- Footer ---
st.divider()
st.caption("Built with Python · Streamlit · Plotly · FRED API | Morgan Stanley Interview Project")