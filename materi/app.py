import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import os
import threading
import http.server
import socketserver
import warnings
warnings.filterwarnings("ignore")

# PAGE CONFIG
st.set_page_config(
    page_title="SIG Klasifikasi Lahan Jawa Timur",
    page_icon="\U0001f6f0\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1526 50%, #0a1220 100%); color: #e2e8f0; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f1a2e 0%, #0a1220 100%); border-right: 1px solid rgba(56,189,248,0.15); }
[data-testid="stMetric"] { background: linear-gradient(135deg, rgba(15,23,42,0.8), rgba(30,41,59,0.6)); border: 1px solid rgba(56,189,248,0.2); border-radius: 12px; padding: 16px 20px; }
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.8rem; }
[data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: 700; }
.stTabs [data-baseweb="tab-list"] { background: rgba(15,23,42,0.8); border-radius: 12px; padding: 4px; border: 1px solid rgba(56,189,248,0.15); gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: #94a3b8; font-weight: 500; font-size: 0.875rem; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #0ea5e9, #6366f1) !important; color: white !important; }
.section-header { background: linear-gradient(135deg, rgba(14,165,233,0.15), rgba(99,102,241,0.1)); border-left: 4px solid #0ea5e9; border-radius: 0 12px 12px 0; padding: 14px 20px; margin: 20px 0 16px 0; }
.section-header h2 { margin: 0; font-size: 1.3rem; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.section-header p { margin: 4px 0 0 0; color: #64748b; font-size: 0.85rem; }
.info-card { background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,41,59,0.7)); border: 1px solid rgba(56,189,248,0.2); border-radius: 14px; padding: 18px 22px; margin-bottom: 14px; }
.info-card h4 { color: #38bdf8; margin: 0 0 8px 0; font-size: 1rem; }
.info-card p, .info-card li { color: #cbd5e1; font-size: 0.875rem; line-height: 1.6; }
.hero-title { text-align: center; padding: 24px 0 10px 0; }
.hero-title h1 { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #34d399 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px; }
.hero-title p { color: #64748b; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# CONSTANTS
DATA_PATH = os.path.join(os.path.dirname(__file__), "klasifikasi_jawa_timur", "dataset_sentinel2_jatim.csv")
MAP_HTML_PATH = os.path.join(os.path.dirname(__file__), "klasifikasi_jawa_timur", "hasil_klasifikasi_svm.html")
BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "_build/html"))
PORT = 8765

CLASS_COLORS = {
    "Sawah": "#22c55e",
    "Bangunan": "#ef4444",
    "Mangrove": "#84cc16",
    "Lahan Hijau": "#15803d",
    "Perairan Terbuka (Laut)": "#0ea5e9",
    "Danau": "#6366f1",
}
CLASS_ICONS = {
    "Sawah": "\U0001f33e", "Bangunan": "\U0001f3d7\ufe0f", "Mangrove": "\U0001f33f",
    "Lahan Hijau": "\U0001f332", "Perairan Terbuka (Laut)": "\U0001f30a", "Danau": "\U0001f3d4\ufe0f",
}

FEATURES = ["B2","B3","B4","B5","B6","B7","B8","B8A","B11","B12",
            "NDVI","NDWI","MNDWI","NDBI","NDRE","EVI","SAVI","BSI"]

BAND_INFO = [
    {"Band": "B2 - Blue",       "Panjang Gelombang (nm)": "490",  "Resolusi (m)": "10", "Kegunaan": "Deteksi kedalaman air, pemetaan vegetasi bawah air"},
    {"Band": "B3 - Green",      "Panjang Gelombang (nm)": "560",  "Resolusi (m)": "10", "Kegunaan": "Memantau vegetasi sehat (puncak reflektansi)"},
    {"Band": "B4 - Red",        "Panjang Gelombang (nm)": "665",  "Resolusi (m)": "10", "Kegunaan": "Absorbsi klorofil, perhitungan NDVI"},
    {"Band": "B5 - Red Edge 1", "Panjang Gelombang (nm)": "705",  "Resolusi (m)": "20", "Kegunaan": "Sensitivitas kondisi vegetasi / klorofil"},
    {"Band": "B6 - Red Edge 2", "Panjang Gelombang (nm)": "740",  "Resolusi (m)": "20", "Kegunaan": "Estimasi indeks area daun (LAI)"},
    {"Band": "B7 - Red Edge 3", "Panjang Gelombang (nm)": "783",  "Resolusi (m)": "20", "Kegunaan": "Kandungan klorofil dan biomassa"},
    {"Band": "B8 - NIR",        "Panjang Gelombang (nm)": "842",  "Resolusi (m)": "10", "Kegunaan": "Diskriminasi vegetasi vs non-vegetasi"},
    {"Band": "B8A - Narrow NIR","Panjang Gelombang (nm)": "865",  "Resolusi (m)": "20", "Kegunaan": "Referensi atmosfer, klasifikasi tutupan lahan"},
    {"Band": "B11 - SWIR 1",    "Panjang Gelombang (nm)": "1610", "Resolusi (m)": "20", "Kegunaan": "Kandungan air tanah dan vegetasi, deteksi lahan terbangun"},
    {"Band": "B12 - SWIR 2",    "Panjang Gelombang (nm)": "2190", "Resolusi (m)": "20", "Kegunaan": "Diskriminasi lahan terbangun dan mineral tanah"},
]

FEATURE_INFO = [
    {"Fitur": "NDVI",  "Nama Lengkap": "Normalized Difference Vegetation Index", "Rumus": "(B8 - B4) / (B8 + B4)", "Deskripsi": "Indeks kehijauan vegetasi. Nilai tinggi = vegetasi lebat."},
    {"Fitur": "NDWI",  "Nama Lengkap": "Normalized Difference Water Index",      "Rumus": "(B3 - B8) / (B3 + B8)", "Deskripsi": "Deteksi kandungan air pada vegetasi dan permukaan."},
    {"Fitur": "MNDWI", "Nama Lengkap": "Modified NDWI",                           "Rumus": "(B3 - B11) / (B3 + B11)", "Deskripsi": "Mendeteksi perairan terbuka (laut, danau) dengan menekan sinyal urban."},
    {"Fitur": "NDBI",  "Nama Lengkap": "Normalized Difference Built-up Index",   "Rumus": "(B11 - B8) / (B11 + B8)", "Deskripsi": "Mendeteksi lahan terbangun (bangunan, jalan, permukiman)."},
    {"Fitur": "NDRE",  "Nama Lengkap": "Normalized Difference Red Edge",         "Rumus": "(B8 - B5) / (B8 + B5)", "Deskripsi": "Sangat sensitif terhadap kandungan klorofil dan kondisi vegetasi."},
    {"Fitur": "EVI",   "Nama Lengkap": "Enhanced Vegetation Index",              "Rumus": "2.5 x (B8-B4) / (B8 + 6*B4 - 7.5*B2 + 1)", "Deskripsi": "Versi NDVI yang lebih stabil di area kanopi lebat atau aerosol tinggi."},
    {"Fitur": "SAVI",  "Nama Lengkap": "Soil-Adjusted Vegetation Index",         "Rumus": "1.5 x (B8-B4) / (B8 + B4 + 0.5)", "Deskripsi": "Meminimalkan pengaruh latar belakang tanah pada estimasi vegetasi."},
    {"Fitur": "BSI",   "Nama Lengkap": "Bare Soil Index",                        "Rumus": "((B11+B4) - (B8+B2)) / ((B11+B4) + (B8+B2))", "Deskripsi": "Mendeteksi lahan terbuka / tanah gundul yang tidak tertutupi vegetasi."},
]

# DATA LOADING
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["kelas"] = df["kelas"].str.strip()
    return df

@st.cache_data
def run_models(df):
    X = df[FEATURES]
    y = df["kelas"]
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )
    models = {
        "SVM (RBF) ★":       SVC(kernel="rbf", C=10, gamma="scale", probability=True, random_state=42),
        "Extra Trees":        ExtraTreesClassifier(n_estimators=200, random_state=42, n_jobs=-1),
        "Random Forest":      RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
        "Gradient Boosting":  GradientBoostingClassifier(n_estimators=150, random_state=42),
        "KNN (k=5)†":         KNeighborsClassifier(n_neighbors=5),
        "Decision Tree":      DecisionTreeClassifier(max_depth=8, random_state=42),
    }
    results = {}
    for name, clf in models.items():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        results[name] = {
            "model": clf,
            "accuracy": accuracy_score(y_test, y_pred),
            "report": classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True),
            "cm": confusion_matrix(y_test, y_pred),
            "y_test": y_test, "y_pred": y_pred,
        }
    return results, le, X_train, X_test, y_train, y_test, scaler

# LOCAL SERVER FOR JUPYTER BOOK
def start_static_server():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=BUILD_DIR, **kwargs)
        def log_message(self, format, *args):
            pass
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

if "server_started" not in st.session_state:
    if os.path.isdir(BUILD_DIR):
        threading.Thread(target=start_static_server, daemon=True).start()
    st.session_state["server_started"] = True

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px 0;'>
        <div style='font-size:2.5rem;'>&#128752;</div>
        <div style='font-weight:700; font-size:1.1rem; color:#38bdf8;'>SIG Lahan Jawa Timur</div>
        <div style='font-size:0.78rem; color:#64748b; margin-top:4px;'>Sentinel-2A &middot; LULC Classification</div>
    </div>
    """, unsafe_allow_html=True)
    page = st.selectbox("Pilih Halaman", [
        "Beranda & Tujuan",
        "Data Understanding",
        "Peta Klasifikasi Interaktif",
        "Evaluasi Model",
        "Proses Analisis (Jupyter Book)",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<b style='color:#64748b; font-size:0.78rem;'>Kelas Lahan</b>", unsafe_allow_html=True)
    for kls, color in CLASS_COLORS.items():
        icon = CLASS_ICONS.get(kls, "")
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;margin:4px 0;'>"
            f"<div style='width:12px;height:12px;background:{color};border-radius:50%;flex-shrink:0;'></div>"
            f"<span style='font-size:0.8rem;color:#cbd5e1;'>{icon} {kls}</span></div>",
            unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem;color:#475569;text-align:center;'>PSD &middot; 2024<br>LULC Sentinel-2A &middot; Jawa Timur</div>", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font_color="#cbd5e1", title_font_color="#38bdf8",
)

# ===============================================================
# PAGE 1 - BERANDA & TUJUAN
# ===============================================================
if page == "Beranda & Tujuan":
    st.markdown("""
    <div class='hero-title'>
        <h1>&#128752; Sistem Informasi Geografis Klasifikasi</h1>
        <h1>Penggunaan Lahan &mdash; Jawa Timur</h1>
        <p>Berbasis Analisis Spasial Citra Sentinel-2A &middot; Machine Learning &middot; Land Use & Land Cover (LULC)</p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='info-card'><h4>&#128225; Sumber Data</h4><p>Citra satelit <b>Sentinel-2A</b> dari Google Earth Engine (GEE). Resolusi spasial 10-20 meter, 10 band spektral digunakan untuk ekstraksi fitur tutupan lahan.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='info-card'><h4>&#128506; Wilayah Kajian</h4><p>Provinsi <b>Jawa Timur</b> mencakup area pesisir (mangrove, laut), dataran rendah (sawah, permukiman), dan perairan darat (Ranu/Danau).</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='info-card'><h4>&#129302; Metode</h4><p>Klasifikasi multikelas menggunakan <b>Random Forest, Gradient Boosting, SVM, KNN, Decision Tree</b> dengan 18 fitur spektral dan indeks citra.</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'><h2>&#127919; Tujuan Analisis Land Use & Land Cover Classification</h2><p>Mengapa analisis LULC penting untuk Jawa Timur?</p></div>", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown("""
        <div class='info-card'><h4>&#127807; 1. Pemantauan Perubahan Lahan</h4><ul>
        <li>Identifikasi konversi lahan sawah menjadi permukiman/industri</li>
        <li>Monitoring deforestasi mangrove di pesisir Jawa Timur</li>
        <li>Deteksi perubahan tutupan lahan dari tahun ke tahun</li></ul></div>
        <div class='info-card'><h4>&#128203; 2. Mendukung Kebijakan Tata Ruang</h4><ul>
        <li>Acuan pemetaan RTRW (Rencana Tata Ruang Wilayah)</li>
        <li>Perlindungan lahan pertanian sawah (LP2B) &mdash; Perpres No. 88/2017</li>
        <li>Zonasi kawasan pesisir dan laut sesuai Perpres No. 51/2016</li></ul></div>
        <div class='info-card'><h4>&#128167; 3. Pengelolaan Sumber Daya Air</h4><ul>
        <li>Identifikasi daerah tangkapan air (watershed)</li>
        <li>Pemantauan danau / ranu di Jawa Timur (Ranu Kumbolo, Ranu Pani)</li>
        <li>Estimasi ketersediaan air permukaan</li></ul></div>
        """, unsafe_allow_html=True)
    with cb:
        st.markdown("""
        <div class='info-card'><h4>&#127963; 4. Acuan Klasifikasi Lahan Indonesia</h4><ul>
        <li><b>SNI 7645:2014</b> &mdash; Klasifikasi tutupan lahan nasional (BIG)</li>
        <li><b>PP No. 16/2004</b> &mdash; Penatagunaan Tanah (BPN/ATR)</li>
        <li><b>PerMenLHK P.12/2023</b> &mdash; Tata cara penafsiran citra satelit kehutanan</li>
        <li><b>Perpres No. 88/2017</b> &mdash; Lahan Pertanian Pangan Berkelanjutan (LP2B)</li></ul></div>
        <div class='info-card'><h4>&#127754; 5. Konservasi Ekosistem Pesisir</h4><ul>
        <li>Pemetaan sebaran mangrove sesuai PerMenLH No. 17/2009</li>
        <li>Identifikasi kawasan penyangga ekosistem laut</li>
        <li>Monitoring abrasi pantai Jawa Timur</li></ul></div>
        <div class='info-card'><h4>&#128640; 6. Ketahanan Pangan & Iklim</h4><ul>
        <li>Estimasi luas sawah produktif untuk proyeksi produksi padi</li>
        <li>Analisis urban heat island dari sebaran bangunan</li>
        <li>Carbon stock estimation dari tutupan vegetasi</li></ul></div>
        """, unsafe_allow_html=True)

# ===============================================================
# PAGE 2 - DATA UNDERSTANDING
# ===============================================================
elif page == "Data Understanding":
    df = load_data()
    st.markdown("<div class='section-header'><h2>&#128202; Data Understanding</h2><p>Memahami dataset Sentinel-2A untuk klasifikasi lahan Jawa Timur</p></div>", unsafe_allow_html=True)

    total = len(df)
    n_class = df["kelas"].nunique()
    X_tr, X_te, _, _ = train_test_split(df[FEATURES], df["kelas"], test_size=0.2, random_state=42, stratify=df["kelas"])
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Sampel", f"{total:,}")
    c2.metric("Training (80%)", f"{len(X_tr):,}")
    c3.metric("Testing (20%)", f"{len(X_te):,}")
    c4.metric("Jumlah Kelas", f"{n_class}")
    c5.metric("Jumlah Fitur", f"{len(FEATURES)}")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["Distribusi Kelas", "Band Sentinel-2A", "Deskripsi Fitur", "Sample Data"])

    with tab1:
        cc = df["kelas"].value_counts().reset_index()
        cc.columns = ["Kelas", "Jumlah"]
        cl, cr = st.columns([1.2, 1])
        with cl:
            fig = px.bar(cc, x="Kelas", y="Jumlah", color="Kelas", color_discrete_map=CLASS_COLORS,
                         text="Jumlah", title="Distribusi Sampel per Kelas")
            fig.update_traces(textposition="outside", textfont_size=13)
            fig.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                              xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(56,189,248,0.1)"))
            st.plotly_chart(fig, use_container_width=True)
        with cr:
            fig2 = px.pie(cc, names="Kelas", values="Jumlah", color="Kelas",
                          color_discrete_map=CLASS_COLORS, hole=0.45, title="Proporsi Kelas")
            fig2.update_layout(**PLOTLY_LAYOUT, legend=dict(font=dict(color="#94a3b8", size=12)))
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown("#### Detail Sampel per Kelas")
        for _, row in cc.iterrows():
            kls = row["Kelas"]; color = CLASS_COLORS.get(kls, "#64748b"); icon = CLASS_ICONS.get(kls, "")
            pct = row["Jumlah"] / total * 100
            st.markdown(f"<div style='display:flex;align-items:center;gap:12px;margin:6px 0;background:rgba(15,23,42,0.6);padding:10px 16px;border-radius:8px;border-left:4px solid {color};'><span style='font-size:1.1rem;'>{icon}</span><span style='color:#e2e8f0;font-weight:600;min-width:180px;'>{kls}</span><span style='color:#38bdf8;font-weight:700;'>{int(row['Jumlah'])} sampel</span><span style='color:#64748b;margin-left:auto;'>{pct:.1f}%</span></div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='info-card'><h4>Sentinel-2A &mdash; Sensor MSI (MultiSpectral Instrument)</h4><p>Sentinel-2A diluncurkan ESA pada 23 Juni 2015. Sensor MSI memiliki 13 band spektral; analisis ini menggunakan <b>10 band</b> utama untuk klasifikasi penggunaan lahan.</p></div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(BAND_INFO), use_container_width=True, hide_index=True)
        band_names = ["B2","B3","B4","B5","B6","B7","B8","B8A","B11","B12"]
        fig_s = go.Figure()
        for kls, color in CLASS_COLORS.items():
            sub = df[df["kelas"] == kls][band_names].mean().values
            fig_s.add_trace(go.Scatter(x=band_names, y=sub, name=f"{CLASS_ICONS.get(kls,'')} {kls}",
                                       mode="lines+markers", line=dict(color=color, width=2.5), marker=dict(size=7)))
        fig_s.update_layout(**PLOTLY_LAYOUT, title="Profil Reflektansi Spektral per Kelas",
                             xaxis_title="Band Sentinel-2A", yaxis_title="Rata-rata Reflektansi",
                             legend=dict(font=dict(color="#94a3b8")),
                             xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(56,189,248,0.1)"))
        st.plotly_chart(fig_s, use_container_width=True)

    with tab3:
        st.markdown("<div class='info-card'><h4>Fitur yang Digunakan dalam Klasifikasi</h4><p>Total <b>18 fitur</b>: 10 band reflektansi Sentinel-2A + 8 indeks spektral turunan yang dipilih berdasarkan kemampuan membedakan jenis tutupan lahan di Jawa Timur.</p></div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(FEATURE_INFO), use_container_width=True, hide_index=True)
        st.markdown("#### Distribusi Nilai Fitur per Kelas")
        sel_feat = st.selectbox("Pilih fitur:", FEATURES, index=10)
        fig_v = px.violin(df, x="kelas", y=sel_feat, color="kelas", color_discrete_map=CLASS_COLORS,
                          box=True, points="all", title=f"Distribusi {sel_feat} per Kelas")
        fig_v.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(56,189,248,0.1)"))
        st.plotly_chart(fig_v, use_container_width=True)
        st.markdown("#### Heatmap Korelasi Fitur")
        corr = df[FEATURES].corr()
        fig_h = px.imshow(corr, text_auto=".2f", aspect="auto", title="Matriks Korelasi Fitur", color_continuous_scale="RdBu_r")
        fig_h.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_h, use_container_width=True)

    with tab4:
        st.markdown("#### Pratinjau Dataset")
        kelas_filter = st.multiselect("Filter Kelas:", df["kelas"].unique().tolist(), default=df["kelas"].unique().tolist())
        filtered = df[df["kelas"].isin(kelas_filter)]
        st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
        st.caption(f"Menampilkan {len(filtered)} dari {len(df)} baris data")

# ===============================================================
# PAGE 3 - PETA KLASIFIKASI INTERAKTIF
# ===============================================================
# PAGE 3 - PETA KLASIFIKASI INTERAKTIF
# ===============================================================
elif page == "Peta Klasifikasi Interaktif":
    df = load_data()
    st.markdown("<div class='section-header'><h2>&#127757; Peta Klasifikasi Lahan Interaktif</h2><p>Visualisasi poligon shapefile sampel, hasil raster SVM, dan sebaran spasial tutupan lahan Jawa Timur</p></div>", unsafe_allow_html=True)

    tab_peta1, tab_peta2 = st.tabs(["\U0001f5fa\ufe0f Peta Klasifikasi SVM & Poligon Shapefile", "\U0001f4cd Eksplorasi Titik & Indeks Spektral"])

    with tab_peta1:
        st.markdown("<div class='info-card'><h4>Peta Hasil Klasifikasi SVM & Poligon Sampel</h4><p>Peta ini menampilkan poligon shapefile asli per kelas, layer sorot data uji (testing 20%), layer salah klasifikasi (dengan pin marker info oranye), serta overlay raster hasil prediksi spasial citra Sentinel-2A di atas Google Maps Satellite.</p></div>", unsafe_allow_html=True)

        if os.path.exists(MAP_HTML_PATH):
            with open(MAP_HTML_PATH, "r", encoding="utf-8") as f:
                html_map_content = f.read()
            st.components.v1.html(html_map_content, height=680, scrolling=False)
        else:
            st.warning("File hasil_klasifikasi_svm.html belum ditemukan.")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Model Digunakan", "SVM (RBF)")
        m2.metric("Total Poligon Sampel", "285 poligon")
        m3.metric("Data Uji (Testing)", "57 poligon")
        m4.metric("Akurasi Testing", "82.46%")

    with tab_peta2:
        ctrl1, ctrl2, ctrl3 = st.columns(3)
        with ctrl1:
            show_classes = st.multiselect("Tampilkan Kelas:", df["kelas"].unique().tolist(), default=df["kelas"].unique().tolist(), key="tab2_classes")
        with ctrl2:
            map_style = st.selectbox("Basemap:", ["Google Satellite", "Google Hybrid", "OpenStreetMap", "CartoDB Dark"], key="tab2_basemap")
        with ctrl3:
            marker_size = st.slider("Ukuran Marker:", 4, 15, 8, key="tab2_size")

        df_map = df[df["kelas"].isin(show_classes)]
        lat_c = df_map["lat"].mean() if len(df_map) > 0 else -7.5
        lon_c = df_map["lon"].mean() if len(df_map) > 0 else 112.7

        m = folium.Map(location=[lat_c, lon_c], zoom_start=9, tiles=None, control_scale=True)

        tile_configs = {
            "Google Satellite": ("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", "Google Satellite"),
            "Google Hybrid":    ("https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", "Google Hybrid"),
            "CartoDB Dark":     ("https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png", "CartoDB"),
        }
        if map_style in tile_configs:
            url, attr = tile_configs[map_style]
            folium.TileLayer(tiles=url, attr=attr, name=map_style, max_zoom=22).add_to(m)
        else:
            folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)

        for kls in show_classes:
            sub = df_map[df_map["kelas"] == kls]
            color = CLASS_COLORS.get(kls, "#64748b")
            icon = CLASS_ICONS.get(kls, "")
            fg = folium.FeatureGroup(name=f"{icon} {kls}", show=True)
            mc = MarkerCluster(options={"maxClusterRadius": 30, "disableClusteringAtZoom": 13})
            for _, row in sub.iterrows():
                popup_html = (
                    f"<div style='font-family:Arial,sans-serif;min-width:210px;'>"
                    f"<div style='background:{color};color:white;padding:8px 12px;"
                    f"border-radius:8px 8px 0 0;font-weight:600;'>{icon} {kls}</div>"
                    f"<div style='padding:10px 12px;background:#1e293b;color:#e2e8f0;"
                    f"border-radius:0 0 8px 8px;font-size:13px;'>"
                    f"<b>Koordinat:</b> {row['lat']:.5f}, {row['lon']:.5f}<br><br>"
                    f"<b>Indeks Spektral:</b><br>"
                    f"NDVI: {row['NDVI']:.4f} | NDWI: {row['NDWI']:.4f}<br>"
                    f"MNDWI: {row['MNDWI']:.4f} | NDBI: {row['NDBI']:.4f}<br>"
                    f"EVI: {row['EVI']:.4f} | BSI: {row['BSI']:.4f}"
                    f"</div></div>"
                )
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=marker_size, color=color, fill=True,
                    fill_color=color, fill_opacity=0.85, weight=1.5,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{icon} {kls} | NDVI: {row['NDVI']:.3f}",
                ).add_to(mc)
            mc.add_to(fg)
            fg.add_to(m)

        folium.LayerControl(collapsed=False).add_to(m)

        legend_html = (
            "<div style='position:fixed;bottom:30px;right:10px;z-index:1000;"
            "background:rgba(10,14,26,0.92);border:1px solid rgba(56,189,248,0.3);"
            "border-radius:12px;padding:14px 18px;font-family:Arial,sans-serif;'>"
            "<b style='color:#38bdf8;font-size:0.9rem;'>Legenda Kelas</b><br><br>"
        )
        for kls, color in CLASS_COLORS.items():
            legend_html += (
                f"<div style='display:flex;align-items:center;gap:8px;margin:5px 0;'>"
                f"<div style='width:14px;height:14px;background:{color};border-radius:50%;'></div>"
                f"<span style='color:#e2e8f0;font-size:0.82rem;'>{CLASS_ICONS.get(kls,'')} {kls}</span></div>"
            )
        legend_html += "</div>"
        m.get_root().html.add_child(folium.Element(legend_html))

        st_folium(m, width=None, height=580, returned_objects=[])

        st.markdown("#### Statistik Titik Sampel")
        if show_classes:
            cols = st.columns(len(show_classes))
            for i, kls in enumerate(show_classes):
                cnt = len(df_map[df_map["kelas"] == kls])
                color = CLASS_COLORS.get(kls, "#64748b")
                icon = CLASS_ICONS.get(kls, "")
                cols[i].markdown(
                    f"<div style='text-align:center;background:rgba(15,23,42,0.8);"
                    f"border:1px solid {color};border-radius:10px;padding:12px 8px;'>"
                    f"<div style='font-size:1.3rem;'>{icon}</div>"
                    f"<div style='color:{color};font-weight:700;font-size:1.1rem;'>{cnt}</div>"
                    f"<div style='color:#94a3b8;font-size:0.75rem;'>{kls}</div></div>",
                    unsafe_allow_html=True)

# ===============================================================
# PAGE 4 - EVALUASI MODEL
# ===============================================================
elif page == "Evaluasi Model":
    df = load_data()
    st.markdown("<div class='section-header'><h2>&#128200; Perbandingan & Evaluasi Model Klasifikasi</h2><p>Eksperimen 5 model ML untuk menemukan akurasi tertinggi pada dataset Sentinel-2A Jawa Timur</p></div>", unsafe_allow_html=True)

    with st.spinner("Melatih dan mengevaluasi semua model..."):
        results, le, X_train, X_test, y_train, y_test, scaler = run_models(df)

    acc_df = pd.DataFrame([
        {"Model": name, "Akurasi (%)": round(v["accuracy"]*100, 2)}
        for name, v in results.items()
    ]).sort_values("Akurasi (%)", ascending=False).reset_index(drop=True)

    best_model = acc_df.iloc[0]["Model"]
    best_acc   = acc_df.iloc[0]["Akurasi (%)"]
    st.success(f"Model Terbaik: **{best_model}** dengan Akurasi: **{best_acc:.2f}%**")

    cb, ct = st.columns([1.5, 1])
    with cb:
        bar_colors = ["#f59e0b" if m == best_model else "#0ea5e9" for m in acc_df["Model"]]
        fig_acc = go.Figure(go.Bar(
            x=acc_df["Akurasi (%)"], y=acc_df["Model"], orientation="h",
            marker_color=bar_colors,
            text=[f"{v:.2f}%" for v in acc_df["Akurasi (%)"]],
            textposition="outside",
        ))
        fig_acc.update_layout(**PLOTLY_LAYOUT, title="Perbandingan Akurasi Model",
                              xaxis_title="Akurasi (%)",
                              xaxis=dict(range=[0,115], showgrid=True, gridcolor="rgba(56,189,248,0.1)"),
                              yaxis=dict(showgrid=False), margin=dict(t=50,b=20,r=60), height=300)
        st.plotly_chart(fig_acc, use_container_width=True)
    with ct:
        st.markdown("#### Ranking Model")
        rank_icons = ["1st","2nd","3rd","4th","5th"]
        for i, row in acc_df.iterrows():
            bg = "rgba(245,158,11,0.1)" if row["Model"] == best_model else "rgba(15,23,42,0.6)"
            border = "#f59e0b" if row["Model"] == best_model else "rgba(56,189,248,0.2)"
            st.markdown(f"<div style='background:{bg};border:1px solid {border};border-radius:10px;padding:10px 16px;margin:6px 0;display:flex;align-items:center;gap:12px;'><span style='color:#94a3b8;font-size:0.85rem;min-width:30px;'>{rank_icons[i]}</span><span style='color:#e2e8f0;font-weight:600;flex:1;'>{row['Model']}</span><span style='color:#38bdf8;font-weight:700;'>{row['Akurasi (%)']:.2f}%</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    sel_model = st.selectbox("Pilih model untuk detail evaluasi:", list(results.keys()))
    res = results[sel_model]
    classes = le.classes_

    ccm, crep = st.columns([1, 1.2])
    with ccm:
        st.markdown("#### Confusion Matrix")
        fig_cm = px.imshow(res["cm"], labels=dict(x="Prediksi", y="Aktual", color="Count"),
                           x=classes, y=classes, text_auto=True, color_continuous_scale="Blues",
                           title=f"Confusion Matrix - {sel_model}")
        fig_cm.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_cm, use_container_width=True)
    with crep:
        st.markdown("#### Classification Report")
        report = res["report"]
        rows = []
        for cls in classes:
            if cls in report:
                r = report[cls]
                rows.append({"Kelas": f"{CLASS_ICONS.get(cls,'')} {cls}", "Precision": round(r["precision"],3),
                             "Recall": round(r["recall"],3), "F1-Score": round(r["f1-score"],3), "Support": int(r["support"])})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        macro = report.get("macro avg", {})
        st.markdown(f"<div style='background:rgba(14,165,233,0.1);border:1px solid rgba(14,165,233,0.3);border-radius:10px;padding:12px 16px;margin-top:12px;'><b style='color:#38bdf8;'>Macro Average</b><br><span style='color:#cbd5e1;font-size:0.9rem;'>Precision: {macro.get('precision',0):.3f} | Recall: {macro.get('recall',0):.3f} | F1-Score: {macro.get('f1-score',0):.3f}</span></div>", unsafe_allow_html=True)

    if sel_model in ["Random Forest", "Gradient Boosting", "Extra Trees"]:
        st.markdown("#### Feature Importance")
        importances = res["model"].feature_importances_
        fi_df = pd.DataFrame({"Fitur": FEATURES, "Importance": importances}).sort_values("Importance", ascending=False)
        fig_fi = px.bar(fi_df, x="Importance", y="Fitur", orientation="h",
                        title=f"Feature Importance - {sel_model}", color="Importance", color_continuous_scale="viridis")
        fig_fi.update_layout(**PLOTLY_LAYOUT, height=500, margin=dict(t=50,b=20))
        st.plotly_chart(fig_fi, use_container_width=True)

# ===============================================================
# PAGE 5 - JUPYTER BOOK EMBED
# ===============================================================
elif page == "Proses Analisis (Jupyter Book)":
    st.markdown("<div class='section-header'><h2>&#128218; Proses Analisis Lengkap - Jupyter Book</h2><p>Dokumentasi lengkap preprocessing, ekstraksi fitur, dan klasifikasi</p></div>", unsafe_allow_html=True)
    if os.path.isdir(BUILD_DIR):
        st.info("Menampilkan Jupyter Book yang di-build secara lokal.", icon="INFO")
        st.components.v1.iframe(f"http://localhost:{PORT}", height=850, scrolling=True)
    else:
        st.warning("Jupyter Book belum di-build. Jalankan: jupyter-book build .")
        st.markdown("<div class='info-card'><h4>Konten Jupyter Book</h4><ul><li>Business Understanding & Tujuan Analisis</li><li>Data Understanding & Eksplorasi Dataset</li><li>Preprocessing Citra Sentinel-2A</li><li>Ekstraksi Fitur Spektral (NDVI, NDWI, dll.)</li><li>Eksperimen Klasifikasi (KNN, RF, SVM, dll.)</li><li>Visualisasi Peta Hasil Klasifikasi</li><li>Analisis & Kesimpulan</li></ul></div>", unsafe_allow_html=True)
