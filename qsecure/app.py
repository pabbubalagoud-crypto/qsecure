"""
Q-Secure: BB84 Quantum Key Distribution & Eavesdropper Detector
Run with: streamlit run app.py
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from bb84 import BB84Simulator

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Q-Secure | Quantum Eavesdropper Detector",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Dark quantum theme */
  .stApp { background-color: #05080f; color: #e2e8f0; }
  .block-container { padding-top: 1rem; }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: #0b1120;
    border: 1px solid #1e3058;
    border-radius: 10px;
    padding: 14px 18px;
  }
  [data-testid="stMetricLabel"] { color: #6b7fa3 !important; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; }
  [data-testid="stMetricValue"] { color: #00d4ff !important; font-size: 1.8rem; font-weight: 800; }

  /* Buttons */
  .stButton>button {
    border-radius: 8px; font-weight: 700;
    transition: opacity .2s;
  }
  .stButton>button:hover { opacity: .85; }

  /* Sidebar */
  [data-testid="stSidebar"] { background: #0b1120; border-right: 1px solid #1e3058; }

  /* Status boxes */
  .secure-box {
    background: rgba(0,230,118,.09);
    border: 2px solid #00e676;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
  }
  .danger-box {
    background: rgba(255,61,113,.09);
    border: 2px solid #ff3d71;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
  }
  .idle-box {
    background: #0b1120;
    border: 2px solid #1e3058;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
  }
  .stat-title { font-size: 1.3rem; font-weight: 800; margin-bottom: 6px; }
  .stat-desc  { font-size: 0.82rem; color: #6b7fa3; }

  /* Channel diagram */
  .channel-box {
    background: #0b1120;
    border: 1px solid #1e3058;
    border-radius: 14px;
    padding: 24px;
    font-family: monospace;
    font-size: 0.9rem;
    color: #e2e8f0;
    white-space: pre;
    line-height: 1.9;
  }
  .info-card {
    background: #0b1120;
    border: 1px solid #1e3058;
    border-radius: 10px;
    padding: 16px;
  }
  h1, h2, h3 { color: #e2e8f0 !important; }
  .stDataFrame { border: 1px solid #1e3058; border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 🔐 Q-Secure")
st.markdown("**Quantum Key Distribution & Eavesdropper Detector** · BB84 Protocol Simulator")
st.divider()

# ── Sidebar controls ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Simulation Controls")
    st.divider()

    eve_on = st.toggle("🔴 Enable Eve (Eavesdropper)", value=False)

    if eve_on:
        st.error("⚠️ Eve is **ACTIVE** — intercepting all qubits")
    else:
        st.success("✅ Channel is **CLEAR** — no eavesdropper")

    st.divider()
    n_qubits = st.slider("Number of Qubits", min_value=20, max_value=500, value=100, step=10)
    sample_pct = st.slider("QBER Sample Size (%)", min_value=10, max_value=50, value=25, step=5,
                           help="Percentage of sifted key used to estimate QBER")
    threshold = st.slider("QBER Security Threshold (%)", min_value=5, max_value=20, value=11, step=1,
                          help="QBER above this % means eavesdropping detected")

    st.divider()
    run_btn = st.button("⚛️ Run Quantum Simulation", use_container_width=True, type="primary")

    st.divider()
    st.markdown("### 📡 BB84 Protocol")
    st.markdown("""
**Z-basis** (rectilinear): `|0⟩` `|1⟩`  
**X-basis** (diagonal): `|+⟩` `|−⟩`

- Same basis → deterministic result  
- Different basis → 50/50 random  
- Eve guessing wrong basis → **~25% QBER**
    """)

# ── Channel Diagram ───────────────────────────────────────────────────────────
col_diag, col_status = st.columns([3, 2])

with col_diag:
    st.markdown("#### 📡 Quantum Channel")
    if eve_on:
        diagram = """
  Alice ──────────────────────────────→ Bob
    │        QUANTUM CHANNEL           │
    │                                  │
    └──────────── Eve ─────────────────┘
               🦹 INTERCEPTING
        """
    else:
        diagram = """
  Alice ──────────────────────────────→ Bob
           QUANTUM CHANNEL
                  
           👤 Eve: Dormant
        """
    st.markdown(f'<div class="channel-box">{diagram}</div>', unsafe_allow_html=True)

with col_status:
    st.markdown("#### 🔑 System Status")
    if "result" not in st.session_state:
        st.markdown('<div class="idle-box"><div class="stat-title" style="color:#6b7fa3">⚛️ Ready</div><div class="stat-desc">Run simulation to see results</div></div>', unsafe_allow_html=True)
    else:
        r = st.session_state.result
        is_secure = r["qber"] < (threshold / 100)
        if is_secure:
            st.markdown(f'<div class="secure-box"><div class="stat-title" style="color:#00e676">🔒 SECURE</div><div class="stat-desc">QBER = {r["qber"]*100:.1f}% — Channel is safe<br>Key length: {r["key_length"]} bits</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="danger-box"><div class="stat-title" style="color:#ff3d71">🚨 EAVESDROPPING DETECTED</div><div class="stat-desc">QBER = {r["qber"]*100:.1f}% — Discard key!<br>Eve introduced {r["errors"]} errors</div></div>', unsafe_allow_html=True)

st.divider()

# ── Run Simulation ────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner("⚛️ Simulating quantum channel…"):
        sim = BB84Simulator(n_qubits=n_qubits, eve_present=eve_on, sample_pct=sample_pct/100)
        result = sim.run()
        st.session_state.result = result
        st.session_state.sim = sim
    st.rerun()

# ── Metrics ───────────────────────────────────────────────────────────────────
if "result" in st.session_state:
    r = st.session_state.result
    is_secure = r["qber"] < (threshold / 100)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Qubits Sent", r["n_qubits"])
    with m2:
        st.metric("Matching Bases", r["matching_bases"])
    with m3:
        st.metric("Raw Key Length", r["key_length"])
    with m4:
        st.metric("Errors Found", r["errors"])
    with m5:
        color_val = f"{r['qber']*100:.1f}%"
        st.metric("QBER", color_val)

    st.divider()

    # ── Charts Row ───────────────────────────────────────────────────────────
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("#### 📊 QBER Gauge")
        qber_pct = r["qber"] * 100
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=qber_pct,
            title={"text": "Quantum Bit Error Rate (%)", "font": {"color": "#e2e8f0", "size": 14}},
            number={"suffix": "%", "font": {"color": "#00d4ff", "size": 36}},
            delta={"reference": threshold, "decreasing": {"color": "#00e676"}, "increasing": {"color": "#ff3d71"}},
            gauge={
                "axis": {"range": [0, 30], "tickcolor": "#6b7fa3", "tickfont": {"color": "#6b7fa3"}},
                "bar": {"color": "#00e676" if is_secure else "#ff3d71"},
                "bgcolor": "#0b1120",
                "bordercolor": "#1e3058",
                "steps": [
                    {"range": [0, threshold], "color": "rgba(0,230,118,0.1)"},
                    {"range": [threshold, 30], "color": "rgba(255,61,113,0.1)"},
                ],
                "threshold": {
                    "line": {"color": "#ffd740", "width": 3},
                    "thickness": 0.85,
                    "value": threshold,
                },
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#05080f", plot_bgcolor="#05080f",
            font={"color": "#e2e8f0"}, height=260, margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with ch2:
        st.markdown("#### 📈 Basis Matching Distribution")
        sim = st.session_state.sim
        labels = ["Alice Z, Bob Z", "Alice X, Bob X", "Alice Z, Bob X", "Alice X, Bob Z"]
        counts = sim.basis_distribution()
        colors = ["#00d4ff", "#7b61ff", "#1e3058", "#1e3058"]
        fig_bar = go.Figure(go.Bar(
            x=labels, y=counts, marker_color=colors,
            text=counts, textposition="outside",
            textfont={"color": "#e2e8f0"},
        ))
        fig_bar.update_layout(
            paper_bgcolor="#05080f", plot_bgcolor="#0b1120",
            font={"color": "#e2e8f0"}, height=260,
            margin=dict(l=20, r=20, t=20, b=60),
            xaxis={"gridcolor": "#1e3058", "tickfont": {"size": 10}},
            yaxis={"gridcolor": "#1e3058", "title": "Count"},
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Key Bits Visualization ────────────────────────────────────────────────
    st.markdown("#### 🔑 Shared Secret Key Bits")
    key_bits = r["alice_key"]
    bob_bits  = r["bob_key"]
    if len(key_bits) > 0:
        display_n = min(len(key_bits), 80)
        bit_labels = [str(b) for b in key_bits[:display_n]]
        bit_colors = []
        for i in range(display_n):
            if key_bits[i] != bob_bits[i]:
                bit_colors.append("#ff3d71")   # error
            elif key_bits[i] == 0:
                bit_colors.append("#00d4ff")   # 0
            else:
                bit_colors.append("#7b61ff")   # 1

        fig_bits = go.Figure(go.Bar(
            x=list(range(display_n)),
            y=[1] * display_n,
            marker_color=bit_colors,
            text=bit_labels,
            textposition="inside",
            textfont={"color": "#e2e8f0", "size": 10},
            hovertext=[f"Bit {i}: Alice={key_bits[i]}, Bob={bob_bits[i]}" for i in range(display_n)],
            hoverinfo="text",
        ))
        fig_bits.update_layout(
            paper_bgcolor="#05080f", plot_bgcolor="#0b1120",
            height=100, margin=dict(l=0, r=0, t=10, b=10),
            xaxis={"visible": False}, yaxis={"visible": False},
            showlegend=False, bargap=0.05,
        )
        st.plotly_chart(fig_bits, use_container_width=True)
        st.caption(f"🔵 Bit 0 &nbsp;&nbsp; 🟣 Bit 1 &nbsp;&nbsp; 🔴 Error (Eve's interference) &nbsp;&nbsp; Showing first {display_n} of {len(key_bits)} key bits")

    # ── Protocol Table ────────────────────────────────────────────────────────
    st.markdown("#### 📋 Protocol Detail (First 30 Qubits)")
    import pandas as pd
    df = sim.protocol_dataframe(30)
    st.dataframe(
        df.style
          .map(lambda v: "color: #00e676" if v == "✓" else ("color: #ff3d71" if v in ("✗", "YES") else ""), subset=["Bases Match?", "Error?"])
          .map(lambda v: "color: #00d4ff; font-weight:bold" if isinstance(v, (int, float)) and not isinstance(v, bool) and str(v) in ("0","1") else "", subset=["Alice Bit", "Bob Result"])
          .set_properties(**{"background-color": "#0b1120", "color": "#e2e8f0", "border-color": "#1e3058"}),
        use_container_width=True, hide_index=True,
    )

    # ── Simulation Log ────────────────────────────────────────────────────────
    st.markdown("#### 📝 Simulation Log")
    with st.expander("View full log", expanded=False):
        for entry in r["log"]:
            if "ERROR" in entry or "DETECTED" in entry:
                st.error(entry)
            elif "SECURE" in entry or "✅" in entry:
                st.success(entry)
            elif "Eve" in entry or "⚠" in entry:
                st.warning(entry)
            else:
                st.info(entry)

else:
    # ── Explainer cards ───────────────────────────────────────────────────────
    st.markdown("#### 💡 How BB84 Works")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
<div class="info-card">
<h4>⚛️ Quantum Encoding</h4>
<p style="color:#6b7fa3;font-size:0.82rem;margin-top:8px">
Alice encodes each bit using a randomly chosen basis:<br><br>
<b>Z-basis:</b> |0⟩ = ↑, |1⟩ = ↓<br>
<b>X-basis:</b> |+⟩ = ↗, |−⟩ = ↘<br><br>
Bob randomly picks a basis to measure each qubit.
</p>
</div>
""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
<div class="info-card">
<h4>🕵️ Why Eve Gets Caught</h4>
<p style="color:#6b7fa3;font-size:0.82rem;margin-top:8px">
Eve must guess the basis before measuring. A wrong guess collapses the qubit into a random state — disturbing the channel and introducing ~25% errors even on matching bases.
</p>
</div>
""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
<div class="info-card">
<h4>📊 QBER Detection</h4>
<p style="color:#6b7fa3;font-size:0.82rem;margin-top:8px">
QBER below ~11% → secure channel.<br>
QBER ≈ 25% → Eve is intercepting.<br><br>
Alice and Bob sacrifice a sample of key bits to compute QBER, then discard them.
</p>
</div>
""", unsafe_allow_html=True)
