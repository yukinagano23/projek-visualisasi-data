"""
Dashboard Interaktif - Indeks Persepsi Korupsi (IPK/CPI) Indonesia 2004-2025
Tiga Era Kepemimpinan: SBY -> Jokowi -> Prabowo
Sumber data: Transparency International - Corruption Perceptions Index

Cara menjalankan:
    streamlit run dashboard_ipk.py
"""

import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# KONFIGURASI HALAMAN
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="IPK Indonesia | Tiga Era",
    page_icon="\u25CE",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# DESIGN TOKENS
# ----------------------------------------------------------------------------
BG = "#13171F"
BG_PANEL = "#1B212C"
BG_PANEL_2 = "#202836"
INK = "#EDEFF3"
INK_DIM = "#8A93A6"
HAIRLINE = "#2C3441"

ERA_COLORS = {
    "Era SBY (2004-2014)": "#4FA3C4",
    "Era Jokowi (2014-2024)": "#E0B04F",
    "Era Prabowo (2024-sekarang)": "#B07BC4",
}
ERA_SHORT = {
    "Era SBY (2004-2014)": "SBY",
    "Era Jokowi (2014-2024)": "Jokowi",
    "Era Prabowo (2024-sekarang)": "Prabowo",
}
ERA_ORDER = list(ERA_COLORS.keys())

LOW_COLOR = "#C0392B"   # merah - skor rendah
HIGH_COLOR = "#2FA866"  # hijau - skor tinggi

FONT_DISPLAY = "Sora, sans-serif"
FONT_BODY = "Inter, sans-serif"
FONT_MONO = "JetBrains Mono, monospace"

# ----------------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        .stApp {{
            background-color: {BG};
            color: {INK};
            font-family: {FONT_BODY};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {BG_PANEL};
            border-right: 1px solid {HAIRLINE};
        }}
        h1, h2, h3 {{
            font-family: {FONT_DISPLAY} !important;
            letter-spacing: -0.01em;
        }}
        .eyebrow {{
            font-family: {FONT_MONO};
            font-size: 0.72rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: {INK_DIM};
            margin-bottom: 0.3rem;
        }}
        .hero-title {{
            font-family: {FONT_DISPLAY};
            font-weight: 800;
            font-size: 2.6rem;
            line-height: 1.08;
            color: {INK};
            margin: 0;
        }}
        .hero-sub {{
            color: {INK_DIM};
            font-size: 1rem;
            margin-top: 0.6rem;
            max-width: 640px;
        }}
        .era-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.3rem 0.75rem;
            border-radius: 999px;
            font-family: {FONT_MONO};
            font-size: 0.78rem;
            border: 1px solid {HAIRLINE};
            margin-right: 0.5rem;
            color: {INK_DIM};
        }}
        .era-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }}
        .kpi-box {{
            background-color: {BG_PANEL};
            border: 1px solid {HAIRLINE};
            border-radius: 10px;
            padding: 1.1rem 1.3rem;
        }}
        .kpi-label {{
            font-family: {FONT_MONO};
            font-size: 0.7rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {INK_DIM};
        }}
        .kpi-value {{
            font-family: {FONT_MONO};
            font-size: 2rem;
            font-weight: 700;
            color: {INK};
            margin-top: 0.2rem;
        }}
        .kpi-delta-up {{ color: {HIGH_COLOR}; font-family: {FONT_MONO}; font-size: 0.85rem; }}
        .kpi-delta-down {{ color: {LOW_COLOR}; font-family: {FONT_MONO}; font-size: 0.85rem; }}
        .section-divider {{
            border-top: 1px solid {HAIRLINE};
            margin: 2.2rem 0 1.6rem 0;
        }}
        .section-eyebrow {{
            font-family: {FONT_MONO};
            font-size: 0.75rem;
            color: {INK_DIM};
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}
        .section-title {{
            font-family: {FONT_DISPLAY};
            font-weight: 700;
            font-size: 1.5rem;
            color: {INK};
            margin: 0.2rem 0 0.3rem 0;
        }}
        .section-desc {{
            color: {INK_DIM};
            font-size: 0.92rem;
            max-width: 760px;
            margin-bottom: 1rem;
        }}
        .note-box {{
            background-color: {BG_PANEL_2};
            border-left: 3px solid {ERA_COLORS['Era Jokowi (2014-2024)']};
            border-radius: 4px;
            padding: 0.7rem 1rem;
            font-size: 0.85rem;
            color: {INK_DIM};
            margin-top: 0.6rem;
        }}
        [data-testid="stMetricValue"] {{
            font-family: {FONT_MONO};
        }}
        footer {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "ipk_indonesia_tiga_era.csv")


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Tahun"] = df["Tahun"].astype(int)
    df["Skor_IPK"] = df["Skor_IPK"].astype(float)
    return df.sort_values("Tahun").reset_index(drop=True)


df = load_data(CSV_PATH)

def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


PLOTLY_LAYOUT_BASE = dict(
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    font=dict(family=FONT_BODY, color=INK, size=13),
    margin=dict(l=10, r=10, t=50, b=10),
    hoverlabel=dict(
        bgcolor=BG_PANEL_2,
        bordercolor=HAIRLINE,
        font=dict(family=FONT_MONO, color=INK, size=12),
    ),
)

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
st.sidebar.markdown(
    f"<div class='eyebrow'>Filter Tampilan</div>", unsafe_allow_html=True
)
st.sidebar.markdown("### Rentang Tahun")

tahun_min, tahun_max = int(df["Tahun"].min()), int(df["Tahun"].max())
rentang_tahun = st.sidebar.slider(
    "Pilih rentang tahun",
    min_value=tahun_min,
    max_value=tahun_max,
    value=(tahun_min, tahun_max),
    label_visibility="collapsed",
)

st.sidebar.markdown("### Era yang Ditampilkan")
era_dipilih = []
for era in ERA_ORDER:
    checked = st.sidebar.checkbox(ERA_SHORT[era], value=True, key=f"chk_{era}")
    if checked:
        era_dipilih.append(era)

df_filtered = df[
    (df["Tahun"] >= rentang_tahun[0])
    & (df["Tahun"] <= rentang_tahun[1])
    & (df["Era"].isin(era_dipilih))
].copy()

st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
st.sidebar.markdown(
    f"""
    <div class='eyebrow'>Tentang IPK</div>
    <div style='color:{INK_DIM}; font-size:0.85rem; line-height:1.5;'>
    Indeks Persepsi Korupsi (Corruption Perceptions Index) mengukur persepsi
    tingkat korupsi sektor publik dalam skala <b>0-100</b>.<br><br>
    <b>0</b> = sangat korup &nbsp;&nbsp; <b>100</b> = sangat bersih<br><br>
    Sumber: Transparency International.
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------------
col_hero, col_kpi = st.columns([1.3, 1])

with col_hero:
    st.markdown("<div class='eyebrow'>Indeks Persepsi Korupsi &mdash; Indonesia</div>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title'>Dua Dekade,<br>Tiga Era, Satu Garis.</h1>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <p class='hero-sub'>
        Skor IPK Indonesia 2004&ndash;2025 ditelusuri lintas tiga era kepemimpinan
        untuk melihat momentum naik-turun, siapa mewarisi skor terbaik, dan
        tahun-tahun mana yang paling gelap atau paling terang.
        </p>
        """,
        unsafe_allow_html=True,
    )
    pills_html = ""
    for era in ERA_ORDER:
        pills_html += (
            f"<span class='era-pill'><span class='era-dot' "
            f"style='background:{ERA_COLORS[era]};'></span>{era}</span>"
        )
    st.markdown(f"<div style='margin-top:1rem;'>{pills_html}</div>", unsafe_allow_html=True)

with col_kpi:
    if not df_filtered.empty:
        skor_terbaru = df_filtered.iloc[-1]
        skor_awal = df_filtered.iloc[0]
        selisih_total = skor_terbaru["Skor_IPK"] - skor_awal["Skor_IPK"]
        skor_tertinggi_row = df_filtered.loc[df_filtered["Skor_IPK"].idxmax()]
        skor_terendah_row = df_filtered.loc[df_filtered["Skor_IPK"].idxmin()]

        k1, k2 = st.columns(2)
        with k1:
            arrow = "&#9650;" if selisih_total >= 0 else "&#9660;"
            delta_class = "kpi-delta-up" if selisih_total >= 0 else "kpi-delta-down"
            st.markdown(
                f"""
                <div class='kpi-box'>
                    <div class='kpi-label'>Skor {int(skor_terbaru['Tahun'])}</div>
                    <div class='kpi-value'>{skor_terbaru['Skor_IPK']:.0f}</div>
                    <div class='{delta_class}'>{arrow} {abs(selisih_total):.0f} sejak {int(skor_awal['Tahun'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                f"""
                <div class='kpi-box'>
                    <div class='kpi-label'>Tertinggi Sepanjang Periode</div>
                    <div class='kpi-value'>{skor_tertinggi_row['Skor_IPK']:.0f}</div>
                    <div style='color:{INK_DIM}; font-family:{FONT_MONO}; font-size:0.85rem;'>
                        Tahun {int(skor_tertinggi_row['Tahun'])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        k3, k4 = st.columns(2)
        with k3:
            st.markdown(
                f"""
                <div class='kpi-box'>
                    <div class='kpi-label'>Terendah Sepanjang Periode</div>
                    <div class='kpi-value'>{skor_terendah_row['Skor_IPK']:.0f}</div>
                    <div style='color:{INK_DIM}; font-family:{FONT_MONO}; font-size:0.85rem;'>
                        Tahun {int(skor_terendah_row['Tahun'])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k4:
            st.markdown(
                f"""
                <div class='kpi-box'>
                    <div class='kpi-label'>Jumlah Tahun Data</div>
                    <div class='kpi-value'>{len(df_filtered)}</div>
                    <div style='color:{INK_DIM}; font-family:{FONT_MONO}; font-size:0.85rem;'>
                        dari total {len(df)} tahun
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.warning("Tidak ada data pada filter yang dipilih.")

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# GRAFIK 1 - LINE CHART TREN PER ERA
# ----------------------------------------------------------------------------
st.markdown("<div class='section-eyebrow'>01 &middot; Tren Berkesinambungan</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Momentum Skor IPK 2004&ndash;2025</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-desc'>Satu garis waktu yang sama, diwarnai per era, "
    "untuk melihat momentum naik dan turun secara berkesinambungan tanpa "
    "memutus alur antar periode kepemimpinan.</div>",
    unsafe_allow_html=True,
)

if not df_filtered.empty:
    fig1 = go.Figure()

    # garis penghubung tipis abu-abu sebagai latar kontinuitas penuh
    fig1.add_trace(
        go.Scatter(
            x=df_filtered["Tahun"],
            y=df_filtered["Skor_IPK"],
            mode="lines",
            line=dict(color=HAIRLINE, width=1.5),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    for era in ERA_ORDER:
        if era not in era_dipilih:
            continue
        d = df_filtered[df_filtered["Era"] == era]
        if d.empty:
            continue
        fig1.add_trace(
            go.Scatter(
                x=d["Tahun"],
                y=d["Skor_IPK"],
                mode="lines+markers",
                name=ERA_SHORT[era],
                line=dict(color=ERA_COLORS[era], width=3.5),
                marker=dict(size=7, color=ERA_COLORS[era], line=dict(width=1, color=BG)),
                hovertemplate=(
                    "<b>%{x}</b><br>Skor IPK: %{y}<br>" + ERA_SHORT[era] + "<extra></extra>"
                ),
            )
        )

    fig1.update_layout(
        **PLOTLY_LAYOUT_BASE,
        height=440,
        xaxis=dict(
            dtick=1, gridcolor=HAIRLINE, showgrid=False, color=INK_DIM,
            title=None,
        ),
        yaxis=dict(
            title="Skor IPK (0-100)", gridcolor=HAIRLINE, color=INK_DIM,
            range=[0, 50],
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0,
                     font=dict(family=FONT_MONO, size=12)),
        hovermode="x unified",
    )
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("Tidak ada data untuk ditampilkan pada filter saat ini.")

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# GRAFIK 2 - BAR CHART RATA-RATA PER ERA
# ----------------------------------------------------------------------------
st.markdown("<div class='section-eyebrow'>02 &middot; Perbandingan Langsung</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Rata-rata Skor per Era</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-desc'>Tiga batang berdampingan menjawab pertanyaan "
    "paling langsung: era mana yang rata-rata skornya paling tinggi?</div>",
    unsafe_allow_html=True,
)

df_avg = df[df["Era"].isin(era_dipilih)].groupby("Era", sort=False)["Skor_IPK"].agg(
    ["mean", "min", "max", "count"]
).reindex([e for e in ERA_ORDER if e in era_dipilih])

if not df_avg.empty:
    fig2 = go.Figure()
    for era in df_avg.index:
        fig2.add_trace(
            go.Bar(
                x=[ERA_SHORT[era]],
                y=[df_avg.loc[era, "mean"]],
                name=ERA_SHORT[era],
                marker_color=ERA_COLORS[era],
                text=[f"{df_avg.loc[era, 'mean']:.1f}"],
                textposition="outside",
                textfont=dict(family=FONT_MONO, size=15, color=INK),
                width=0.55,
                hovertemplate=(
                    f"<b>{ERA_SHORT[era]}</b><br>Rata-rata: %{{y:.2f}}<br>"
                    f"Min: {df_avg.loc[era,'min']:.0f} &middot; Maks: {df_avg.loc[era,'max']:.0f}<br>"
                    f"({int(df_avg.loc[era,'count'])} tahun data)<extra></extra>"
                ),
                showlegend=False,
            )
        )

    fig2.update_layout(
        **PLOTLY_LAYOUT_BASE,
        height=420,
        xaxis=dict(color=INK_DIM, showgrid=False),
        yaxis=dict(title="Rata-rata Skor IPK", gridcolor=HAIRLINE, color=INK_DIM, range=[0, 45]),
        bargap=0.35,
    )
    st.plotly_chart(fig2, use_container_width=True)

    juara = df_avg["mean"].idxmax()
    st.markdown(
        f"""
        <div class='note-box'>
        Rata-rata tertinggi: <b style='color:{ERA_COLORS[juara]}'>{ERA_SHORT[juara]}</b>
        ({df_avg.loc[juara, 'mean']:.1f} poin). Perlu diingat era Prabowo baru memiliki
        satu tahun data (2025), sehingga perbandingannya belum setara dengan dua era lain
        yang memiliki data lebih dari 10 tahun.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("Pilih minimal satu era untuk menampilkan perbandingan.")

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# GRAFIK 3 - ANNOTATED AREA CHART
# ----------------------------------------------------------------------------
st.markdown("<div class='section-eyebrow'>03 &middot; Kepemilikan Periode</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Area Skor per Era</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-desc'>Area di bawah garis diisi warna era masing-masing, "
    "memberi kesan visual wilayah waktu yang dimiliki tiap presiden.</div>",
    unsafe_allow_html=True,
)

if not df_filtered.empty:
    fig3 = go.Figure()

    for era in ERA_ORDER:
        if era not in era_dipilih:
            continue
        d = df_filtered[df_filtered["Era"] == era]
        if d.empty:
            continue
        color = ERA_COLORS[era]
        fig3.add_trace(
            go.Scatter(
                x=d["Tahun"],
                y=d["Skor_IPK"],
                mode="lines",
                name=ERA_SHORT[era],
                line=dict(color=color, width=2.5),
                fill="tozeroy",
                fillcolor=_hex_to_rgba(color, 0.28),
                hovertemplate=(
                    "<b>%{x}</b><br>Skor IPK: %{y}<br>" + ERA_SHORT[era] + "<extra></extra>"
                ),
            )
        )

    # anotasi tahun-tahun penting dari kolom Catatan
    catatan_df = df_filtered.dropna(subset=["Catatan"])
    for _, row in catatan_df.iterrows():
        fig3.add_annotation(
            x=row["Tahun"],
            y=row["Skor_IPK"],
            text="&#9670;",
            showarrow=False,
            font=dict(size=9, color=INK),
            yshift=10,
        )

    fig3.update_layout(
        **PLOTLY_LAYOUT_BASE,
        height=440,
        xaxis=dict(dtick=1, color=INK_DIM, showgrid=False),
        yaxis=dict(title="Skor IPK (0-100)", gridcolor=HAIRLINE, color=INK_DIM, range=[0, 50]),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0,
                     font=dict(family=FONT_MONO, size=12)),
        hovermode="x unified",
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown(
        f"<div class='note-box'>Tanda &#9670; menunjukkan tahun dengan catatan "
        f"peristiwa khusus &mdash; arahkan kursor ke titik garis untuk detail skornya.</div>",
        unsafe_allow_html=True,
    )
else:
    st.info("Tidak ada data untuk ditampilkan pada filter saat ini.")

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# GRAFIK 4 - SLOPE CHART AWAL VS AKHIR ERA
# ----------------------------------------------------------------------------
st.markdown("<div class='section-eyebrow'>04 &middot; Warisan Era</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Skor Awal vs Akhir Setiap Era</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-desc'>Garis miring ke atas berarti presiden mewariskan "
    "skor lebih baik dari saat mulai menjabat; miring ke bawah sebaliknya.</div>",
    unsafe_allow_html=True,
)

eras_for_slope = [e for e in ERA_ORDER if e in era_dipilih]
slope_rows = []
for era in eras_for_slope:
    d = df[df["Era"] == era].sort_values("Tahun")
    if len(d) == 0:
        continue
    awal = d.iloc[0]
    akhir = d.iloc[-1]
    slope_rows.append(
        {
            "Era": era,
            "Tahun_Awal": int(awal["Tahun"]),
            "Skor_Awal": awal["Skor_IPK"],
            "Tahun_Akhir": int(akhir["Tahun"]),
            "Skor_Akhir": akhir["Skor_IPK"],
        }
    )

if slope_rows:
    fig4 = go.Figure()
    for i, r in enumerate(slope_rows):
        color = ERA_COLORS[r["Era"]]
        naik = r["Skor_Akhir"] >= r["Skor_Awal"]
        line_color = HIGH_COLOR if naik else LOW_COLOR

        x0, x1 = 0, 1
        fig4.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[r["Skor_Awal"], r["Skor_Akhir"]],
                mode="lines+markers",
                line=dict(color=line_color, width=3),
                marker=dict(size=11, color=color, line=dict(width=2, color=BG)),
                showlegend=False,
                hovertemplate=(
                    f"<b>{ERA_SHORT[r['Era']]}</b><br>"
                    f"{r['Tahun_Awal']}: %{{y}}<extra></extra>"
                ),
            )
        )
        # label kiri (awal)
        fig4.add_annotation(
            x=x0 - 0.04, y=r["Skor_Awal"],
            text=f"{r['Skor_Awal']:.0f}  ({r['Tahun_Awal']})",
            showarrow=False, xanchor="right",
            font=dict(family=FONT_MONO, size=12, color=INK_DIM),
        )
        # label kanan (akhir) + nama era
        delta = r["Skor_Akhir"] - r["Skor_Awal"]
        arrow = "&#9650;" if delta >= 0 else "&#9660;"
        fig4.add_annotation(
            x=x1 + 0.04, y=r["Skor_Akhir"],
            text=f"{r['Skor_Akhir']:.0f}  ({r['Tahun_Akhir']}) {arrow} {abs(delta):.0f}",
            showarrow=False, xanchor="left",
            font=dict(family=FONT_MONO, size=12, color=line_color),
        )
        # nama era di atas garis, posisi tengah
        fig4.add_annotation(
            x=0.5, y=max(r["Skor_Awal"], r["Skor_Akhir"]) + 3,
            text=f"<b>{ERA_SHORT[r['Era']]}</b>",
            showarrow=False,
            font=dict(family=FONT_DISPLAY, size=13, color=color),
        )
        # offset antar slope secara vertikal kalau saling tumpang tindih ditangani lewat sumbu y asli (skor)

    fig4.update_layout(
        **PLOTLY_LAYOUT_BASE,
        height=460,
        xaxis=dict(visible=False, range=[-0.5, 1.5]),
        yaxis=dict(title="Skor IPK (0-100)", gridcolor=HAIRLINE, color=INK_DIM, range=[0, 50]),
        showlegend=False,
    )
    st.plotly_chart(fig4, use_container_width=True)

    legacy_lines = []
    for r in slope_rows:
        delta = r["Skor_Akhir"] - r["Skor_Awal"]
        verdict = "lebih baik" if delta >= 0 else "lebih buruk"
        legacy_lines.append(
            f"<b style='color:{ERA_COLORS[r['Era']]}'>{ERA_SHORT[r['Era']]}</b>: "
            f"{abs(delta):.0f} poin {verdict} dari awal era"
        )
    st.markdown(
        f"<div class='note-box'>{' &nbsp;&middot;&nbsp; '.join(legacy_lines)}</div>",
        unsafe_allow_html=True,
    )
else:
    st.info("Pilih minimal satu era untuk menampilkan perbandingan awal-akhir.")

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# GRAFIK 5 - HEATMAP TAHUNAN
# ----------------------------------------------------------------------------
st.markdown("<div class='section-eyebrow'>05 &middot; Pemindaian Cepat</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Heatmap Skor Tahunan</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-desc'>Satu baris, satu skala warna &mdash; merah untuk skor "
    "rendah, hijau untuk skor tinggi, supaya tahun gelap dan terang langsung terlihat.</div>",
    unsafe_allow_html=True,
)

if not df_filtered.empty:
    tahun_list = df_filtered["Tahun"].tolist()
    skor_list = df_filtered["Skor_IPK"].tolist()
    era_list = df_filtered["Era"].tolist()

    custom = list(zip(tahun_list, skor_list, [ERA_SHORT[e] for e in era_list]))

    fig5 = go.Figure(
        data=go.Heatmap(
            z=[skor_list],
            x=tahun_list,
            y=["Skor IPK"],
            colorscale=[[0, LOW_COLOR], [0.5, "#E0B04F"], [1, HIGH_COLOR]],
            zmin=15,
            zmax=45,
            customdata=[custom],
            hovertemplate="Tahun %{x}<br>Skor: %{z}<extra></extra>",
            colorbar=dict(
                title=dict(text="Skor", font=dict(family=FONT_MONO, color=INK_DIM)),
                tickfont=dict(family=FONT_MONO, color=INK_DIM),
                thickness=14,
            ),
            xgap=4,
            ygap=4,
        )
    )

    # angka skor di atas setiap kotak
    for x, z in zip(tahun_list, skor_list):
        fig5.add_annotation(
            x=x, y="Skor IPK", text=f"{z:.0f}",
            showarrow=False,
            font=dict(family=FONT_MONO, size=12, color=BG if 15 <= z <= 45 else INK),
        )

    fig5.update_layout(
        **{**PLOTLY_LAYOUT_BASE, "margin": dict(l=10, r=10, t=10, b=10)},
        height=220,
        xaxis=dict(dtick=1, side="bottom", color=INK_DIM, showgrid=False),
        yaxis=dict(visible=False),
    )
    st.plotly_chart(fig5, use_container_width=True)

    # strip era di bawah heatmap supaya konteks era tetap terlihat
    fig5b = go.Figure()
    for era in ERA_ORDER:
        if era not in era_dipilih:
            continue
        d = df_filtered[df_filtered["Era"] == era]
        if d.empty:
            continue
        fig5b.add_trace(
            go.Bar(
                x=d["Tahun"], y=[1] * len(d),
                marker_color=ERA_COLORS[era],
                name=ERA_SHORT[era],
                hovertemplate=f"{ERA_SHORT[era]}<extra></extra>",
                width=0.95,
            )
        )
    fig5b.update_layout(
        **{**PLOTLY_LAYOUT_BASE, "margin": dict(l=10, r=10, t=0, b=10)},
        height=70,
        xaxis=dict(dtick=1, visible=False),
        yaxis=dict(visible=False, range=[0, 1]),
        barmode="overlay",
        showlegend=False,
    )
    st.plotly_chart(fig5b, use_container_width=True)
else:
    st.info("Tidak ada data untuk ditampilkan pada filter saat ini.")

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# DATA MENTAH
# ----------------------------------------------------------------------------
with st.expander("Lihat data mentah"):
    st.dataframe(df_filtered, use_container_width=True)
    st.download_button(
        label="Unduh data (CSV)",
        data=df_filtered.to_csv(index=False).encode("utf-8"),
        file_name="ipk_filtered.csv",
        mime="text/csv",
    )

st.markdown(
    f"<div style='color:{INK_DIM}; font-size:0.78rem; font-family:{FONT_MONO}; "
    f"text-align:center; padding: 1.5rem 0;'>"
    f"DATA: TRANSPARENCY INTERNATIONAL &middot; CORRUPTION PERCEPTIONS INDEX &middot; "
    f"DASHBOARD DIBUAT DENGAN STREAMLIT + PLOTLY</div>",
    unsafe_allow_html=True,
)
