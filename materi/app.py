import os
import warnings
warnings.filterwarnings("ignore")

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

# ===============================================================
# PAGE CONFIGURATION
# ===============================================================
st.set_page_config(
    page_title="SIG Klasifikasi Lahan Jawa Timur",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===============================================================
# CLEAN, PROFESSIONAL DESIGN SYSTEM (NO AI SLOP / NO NEON GLOW)
# ===============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Background & Surface */
.stApp {
    background-color: #0b0f17;
    color: #e2e8f0;
}

[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
}

/* Clean Metrics */
[data-testid="stMetric"] {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-size: 0.8rem;
    font-weight: 500;
}
[data-testid="stMetricValue"] {
    color: #38bdf8 !important;
    font-weight: 700;
}

/* Clean Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #0f172a;
    border-radius: 8px;
    padding: 4px;
    border: 1px solid #1e293b;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    color: #94a3b8;
    font-weight: 500;
    font-size: 0.85rem;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background-color: #2563eb !important;
    color: #ffffff !important;
}

/* Section Headers */
.section-header {
    border-left: 3px solid #3b82f6;
    padding: 8px 14px;
    margin: 18px 0 14px 0;
    background-color: rgba(30, 41, 59, 0.4);
    border-radius: 0 6px 6px 0;
}
.section-header h2 {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 600;
    color: #f1f5f9;
}
.section-header p {
    margin: 2px 0 0 0;
    color: #94a3b8;
    font-size: 0.82rem;
}

/* Informational Cards */
.info-card {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.info-card h4 {
    color: #60a5fa;
    margin: 0 0 6px 0;
    font-size: 0.95rem;
    font-weight: 600;
}
.info-card p, .info-card li {
    color: #cbd5e1;
    font-size: 0.85rem;
    line-height: 1.55;
    margin-bottom: 4px;
}

/* Header Banner */
.page-header {
    padding: 14px 0 18px 0;
    border-bottom: 1px solid #1e293b;
    margin-bottom: 20px;
}
.page-header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f8fafc;
    margin: 0 0 4px 0;
}
.page-header p {
    color: #94a3b8;
    font-size: 0.875rem;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)

# ===============================================================
# CONSTANTS & CONFIGURATION
# ===============================================================
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "klasifikasi_jawa_timur", "dataset_sentinel2_jatim.csv")
MAP_HTML_PATH = os.path.join(BASE_DIR, "klasifikasi_jawa_timur", "hasil_klasifikasi_svm.html")

CLASS_COLORS = {
    "Sawah":                   "#F7E331",
    "Bangunan":                "#E53935",
    "Mangrove":                "#8E24AA",
    "Lahan Hijau":             "#2E7D32",
    "Perairan Terbuka (Laut)": "#1565C0",
    "Danau":                   "#4FC3F7",
}

CLASS_ICONS = {
    "Sawah":                   "🌾",
    "Bangunan":                "🏢",
    "Mangrove":                "🌿",
    "Lahan Hijau":             "🌲",
    "Perairan Terbuka (Laut)": "🌊",
    "Danau":                   "💧",
}

FEATURES = [
    "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12",
    "NDVI", "NDWI", "MNDWI", "NDBI", "NDRE", "EVI", "SAVI", "BSI"
]

BAND_INFO = [
    {"Band": "B2 (Blue)",       "Panjang Gelombang": "490 nm",  "Resolusi": "10 m", "Karakteristik": "Penetrasi air dan pembedaan vegetasi bawah air"},
    {"Band": "B3 (Green)",      "Panjang Gelombang": "560 nm",  "Resolusi": "10 m", "Karakteristik": "Puncak reflektansi vegetasi sehat dan perairan dangkal"},
    {"Band": "B4 (Red)",        "Panjang Gelombang": "665 nm",  "Resolusi": "10 m", "Karakteristik": "Absorpsi klorofil, pembeda utama vegetasi vs tanah"},
    {"Band": "B5 (Red Edge 1)", "Panjang Gelombang": "705 nm",  "Resolusi": "20 m", "Karakteristik": "Batas tepi absorbsi klorofil (kondisi kanopi)"},
    {"Band": "B6 (Red Edge 2)", "Panjang Gelombang": "740 nm",  "Resolusi": "20 m", "Karakteristik": "Sensitif terhadap biomassa vegetasi"},
    {"Band": "B7 (Red Edge 3)", "Panjang Gelombang": "783 nm",  "Resolusi": "20 m", "Karakteristik": "Transisi menuju inframerah dekat"},
    {"Band": "B8 (NIR)",        "Panjang Gelombang": "842 nm",  "Resolusi": "10 m", "Karakteristik": "Reflektansi tinggi struktur seluler daun vegetasi"},
    {"Band": "B8A (Narrow NIR)","Panjang Gelombang": "865 nm",  "Resolusi": "20 m", "Karakteristik": "Estimasi kandungan air dan biomassa tanpa gangguan uap air"},
    {"Band": "B11 (SWIR 1)",    "Panjang Gelombang": "1610 nm", "Resolusi": "20 m", "Karakteristik": "Kandungan kelembapan tanah, deteksi lahan terbangun"},
    {"Band": "B12 (SWIR 2)",    "Panjang Gelombang": "2190 nm", "Resolusi": "20 m", "Karakteristik": "Pembeda formasi batuan, tanah terbuka, dan permukiman"},
]

FEATURE_INFO = [
    {"Indeks": "NDVI",  "Nama Lengkap": "Normalized Difference Vegetation Index", "Rumus": "(B8 - B4) / (B8 + B4)", "Fungsi": "Kerapatan dan biomassa hijau daun"},
    {"Indeks": "NDWI",  "Nama Lengkap": "Normalized Difference Water Index",      "Rumus": "(B3 - B8) / (B3 + B8)", "Fungsi": "Kelembapan vegetasi dan badan air"},
    {"Indeks": "MNDWI", "Nama Lengkap": "Modified NDWI",                           "Rumus": "(B3 - B11) / (B3 + B11)", "Fungsi": "Pemisah perairan terbuka dari lahan terbangun"},
    {"Indeks": "NDBI",  "Nama Lengkap": "Normalized Difference Built-up Index",   "Rumus": "(B11 - B8) / (B11 + B8)", "Fungsi": "Pembeda lahan terbangun dan permukiman"},
    {"Indeks": "NDRE",  "Nama Lengkap": "Normalized Difference Red Edge",         "Rumus": "(B8 - B5) / (B8 + B5)", "Fungsi": "Kandungan klorofil pada fase kanopi rapat"},
    {"Indeks": "EVI",   "Nama Lengkap": "Enhanced Vegetation Index",              "Rumus": "2.5 * (B8 - B4) / (B8 + 6*B4 - 7.5*B2 + 1)", "Fungsi": "Kehijauan vegetasi pada area aerosol tinggi"},
    {"Indeks": "SAVI",  "Nama Lengkap": "Soil-Adjusted Vegetation Index",         "Rumus": "1.5 * (B8 - B4) / (B8 + B4 + 0.5)", "Fungsi": "Koreksi pengaruh latar belakang tanah"},
    {"Indeks": "BSI",   "Nama Lengkap": "Bare Soil Index",                        "Rumus": "((B11+B4) - (B8+B2)) / ((B11+B4) + (B8+B2))", "Fungsi": "Deteksi tanah terbuka dan lahan garapan"},
]

PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#cbd5e1", family="Inter, sans-serif"),
    title_font=dict(color="#f1f5f9", size=14),
    margin=dict(l=40, r=20, t=40, b=30),
)

# ===============================================================
# DATA & MODEL FUNCTIONS
# ===============================================================
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
        "SVM (RBF)":         SVC(kernel="rbf", C=10, gamma="scale", probability=True, random_state=42),
        "Extra Trees":       ExtraTreesClassifier(n_estimators=200, random_state=42, n_jobs=-1),
        "Random Forest":     RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=150, random_state=42),
        "KNN (k=5)":         KNeighborsClassifier(n_neighbors=5),
        "Decision Tree":     DecisionTreeClassifier(max_depth=8, random_state=42),
    }
    results = {}
    for name, clf in models.items():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        results[name] = {
            "model": clf,
            "accuracy": accuracy_score(y_test, y_pred),
            "report": classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True, zero_division=0),
            "cm": confusion_matrix(y_test, y_pred),
            "y_test": y_test,
            "y_pred": y_pred,
        }
    return results, le, X_train, X_test, y_train, y_test, scaler

# ===============================================================
# SIDEBAR NAVIGATION
# ===============================================================
with st.sidebar:
    st.markdown("""
    <div style='padding: 6px 0 16px 0;'>
        <div style='font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; color:#64748b; font-weight:600;'>Sistem Informasi Geografis</div>
        <div style='font-weight:700; font-size:1.15rem; color:#f8fafc; margin-top:2px;'>LULC Jawa Timur</div>
        <div style='font-size:0.8rem; color:#94a3b8;'>Sentinel-2A &middot; Proyek Saint Data</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.selectbox(
        "Menu Navigasi",
        [
            "Beranda & Tujuan",
            "Data Understanding",
            "Peta Klasifikasi Interaktif",
            "Evaluasi Model",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem; font-weight:600; text-transform:uppercase; color:#64748b; margin-bottom:8px;'>Kelas Tutupan Lahan</div>", unsafe_allow_html=True)
    for kls, color in CLASS_COLORS.items():
        icon = CLASS_ICONS.get(kls, "")
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:10px;margin:4px 0;'>"
            f"<div style='width:10px;height:10px;background:{color};border-radius:2px;flex-shrink:0;'></div>"
            f"<span style='font-size:0.82rem;color:#cbd5e1;'>{icon} {kls}</span></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("<div style='font-size:0.72rem;color:#475569;line-height:1.4;'>Tugas UTS Data Mining<br>Analisis Spasial Penggunaan Lahan</div>", unsafe_allow_html=True)

# ===============================================================
# PAGE 1 - BERANDA & TUJUAN
# ===============================================================
if page == "Beranda & Tujuan":
    st.markdown("""
    <div class='page-header'>
        <h1>Sistem Informasi Geografis: Klasifikasi Tutupan Lahan Jawa Timur</h1>
        <p>Analisis spasial penggunaan dan tutupan lahan (LULC) berbasis citra Sentinel-2A dan Support Vector Machine (SVM)</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Citra Sumber", "Sentinel-2A L2A")
    c2.metric("Total Sampel", "285 Poligon")
    c3.metric("Kelas Lahan", "6 Kategori")
    c4.metric("Model Terpilih", "SVM (RBF)")

    st.markdown("<div class='section-header'><h2>Tujuan Analisis Land Use & Land Cover (LULC)</h2><p>Tujuan strategis analisis tutupan lahan di wilayah Provinsi Jawa Timur</p></div>", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("""
        <div class='info-card'>
            <h4>1. Perlindungan Lahan Pertanian Pangan</h4>
            <p>Jawa Timur merupakan lumbung beras nasional. Analisis ini mendeteksi alih fungsi lahan sawah produktif menjadi kawasan industri atau permukiman untuk mendukung penetapan Lahan Pertanian Pangan Berkelanjutan (LP2B).</p>
        </div>
        <div class='info-card'>
            <h4>2. Konservasi Ekosistem Pesisir & Mangrove</h4>
            <p>Mengidentifikasi sebaran hutan mangrove di sepanjang garis pantai utara dan selatan Jawa Timur sebagai penahan abrasi alami dan kawasan penyerap karbon.</p>
        </div>
        <div class='info-card'>
            <h4>3. Pemantauan Daerah Tangkapan Air (Watershed)</h4>
            <p>Memetakan tutupan danau, waduk, dan ranu di Jawa Timur untuk inventarisasi ketersediaan cadangan air baku, irigasi, dan pencegahan degradasi hidrologi darat.</p>
        </div>
        """, unsafe_allow_html=True)

    with c_right:
        st.markdown("""
        <div class='info-card'>
            <h4>4. Acuan Kebijakan Tata Ruang di Indonesia</h4>
            <ul>
                <li><b>SNI 7645:2014</b>: Standar Nasional Indonesia untuk klasifikasi penutup lahan skala 1:25.000 (Badan Informasi Geospasial).</li>
                <li><b>Perpres No. 88/2017</b>: Penyelesaian penguasaan tanah dalam kawasan hutan dan perlindungan sawah lestari.</li>
                <li><b>PP No. 16/2004</b>: Penatagunaan tanah yang mensyaratkan inventarisasi data spasial aktual sebelum penetapan izin lokasi.</li>
                <li><b>PermenLHK No. P.12/2023</b>: Standar teknis penafsiran citra satelit optik untuk pemantauan tutupan lahan kehutanan.</li>
            </ul>
        </div>
        <div class='info-card'>
            <h4>5. Alur Pemrosesan Data</h4>
            <p>Data diekstraksi dari citra Sentinel-2A level 2A bebas awan. Dilakukan pembentukan 8 indeks spektral komposit, normalisasi standar (StandardScaler), pelatihan model klasifikasi, dan validasi menggunakan cross-validation berulang.</p>
        </div>
        """, unsafe_allow_html=True)

# ===============================================================
# PAGE 2 - DATA UNDERSTANDING
# ===============================================================
elif page == "Data Understanding":
    df = load_data()
    st.markdown("""
    <div class='page-header'>
        <h1>Data Understanding & Eksplorasi Fitur</h1>
        <p>Distribusi sampel, karakteristik band multispektral Sentinel-2A, dan matriks korelasi</p>
    </div>
    """, unsafe_allow_html=True)

    n_total = len(df)
    n_class = df["kelas"].nunique()
    X_tr, X_te, _, _ = train_test_split(df[FEATURES], df["kelas"], test_size=0.2, random_state=42, stratify=df["kelas"])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Sampel", f"{n_total}")
    c2.metric("Data Training (80%)", f"{len(X_tr)}")
    c3.metric("Data Testing (20%)", f"{len(X_te)}")
    c4.metric("Jumlah Kelas", f"{n_class}")
    c5.metric("Jumlah Fitur", f"{len(FEATURES)}")

    tab1, tab2, tab3, tab4 = st.tabs(["Distribusi Kelas", "Band Sentinel-2A", "Fitur Spektral", "Tabel Sampel"])

    with tab1:
        cc = df["kelas"].value_counts().reset_index()
        cc.columns = ["Kelas", "Jumlah"]
        
        col_bar, col_pie = st.columns([1.3, 1])
        with col_bar:
            fig_bar = px.bar(
                cc, x="Kelas", y="Jumlah", color="Kelas",
                color_discrete_map=CLASS_COLORS, text="Jumlah",
                title="Jumlah Sampel per Kelas"
            )
            fig_bar.update_traces(textposition="outside", textfont_size=12)
            fig_bar.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                                  yaxis=dict(gridcolor="#1e293b", range=[0, max(cc["Jumlah"]) * 1.2]))
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_pie:
            fig_pie = px.pie(
                cc, names="Kelas", values="Jumlah", color="Kelas",
                color_discrete_map=CLASS_COLORS, hole=0.5,
                title="Proporsi Kelas Sampel"
            )
            fig_pie.update_layout(**PLOTLY_LAYOUT, legend=dict(font=dict(size=11)))
            st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.markdown("<div class='info-card'><h4>Karakteristik Sensor MSI (MultiSpectral Instrument) Sentinel-2A</h4><p>10 band reflektansi digunakan untuk membedakan karakteristik fisik permukaan. Band B2, B3, B4, B8 memiliki resolusi 10 meter, sedangkan band Red Edge dan SWIR memiliki resolusi 20 meter.</p></div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(BAND_INFO), use_container_width=True, hide_index=True)

        band_cols = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]
        fig_spec = go.Figure()
        for kls, col in CLASS_COLORS.items():
            mean_vals = df[df["kelas"] == kls][band_cols].mean().values
            fig_spec.add_trace(go.Scatter(
                x=band_cols, y=mean_vals, name=kls,
                mode="lines+markers", line=dict(color=col, width=2.2),
                marker=dict(size=6)
            ))
        fig_spec.update_layout(**PLOTLY_LAYOUT, title="Profil Reflektansi Spektral Rata-rata per Kelas",
                               xaxis_title="Band Sentinel-2A", yaxis_title="Nilai Reflektansi Rata-rata",
                               yaxis=dict(gridcolor="#1e293b"))
        st.plotly_chart(fig_spec, use_container_width=True)

    with tab3:
        st.markdown("<div class='info-card'><h4>Deskripsi 8 Indeks Spektral Turunan</h4><p>Indeks spektral dibentuk melalui rasio band matematis untuk menonjolkan fitur spesifik seperti klorofil, kelembapan air, dan kerapatan bangunan.</p></div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(FEATURE_INFO), use_container_width=True, hide_index=True)

        st.markdown("#### Distribusi Nilai Fitur")
        sel_feat = st.selectbox("Pilih fitur untuk diinspeksi:", FEATURES, index=10)
        fig_v = px.violin(
            df, x="kelas", y=sel_feat, color="kelas",
            color_discrete_map=CLASS_COLORS, box=True, points="all",
            title=f"Distribusi Nilai {sel_feat} per Kelas"
        )
        fig_v.update_layout(**PLOTLY_LAYOUT, showlegend=False, yaxis=dict(gridcolor="#1e293b"))
        st.plotly_chart(fig_v, use_container_width=True)

        st.markdown("#### Matriks Korelasi Antar Fitur")
        corr = df[FEATURES].corr()
        fig_corr = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            title="Korelasi Linier Pearson (18 Fitur)",
            color_continuous_scale="RdBu_r"
        )
        fig_corr.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_corr, use_container_width=True)

    with tab4:
        st.markdown("#### Eksplorasi Data Tabular")
        filter_kls = st.multiselect("Filter Kelas:", df["kelas"].unique().tolist(), default=df["kelas"].unique().tolist())
        d_filtered = df[df["kelas"].isin(filter_kls)]
        st.dataframe(d_filtered.reset_index(drop=True), use_container_width=True)
        st.caption(f"Menampilkan {len(d_filtered)} dari total {len(df)} baris data.")

# ===============================================================
# PAGE 3 - PETA KLASIFIKASI INTERAKTIF
# ===============================================================
elif page == "Peta Klasifikasi Interaktif":
    df = load_data()
    st.markdown("""
    <div class='page-header'>
        <h1>Peta Interaktif Klasifikasi Penggunaan Lahan</h1>
        <p>Visualisasi poligon shapefile sampel, hasil raster SVM, dan sebaran spasial tutupan lahan</p>
    </div>
    """, unsafe_allow_html=True)

    tab_map1, tab_map2 = st.tabs(["🗺️ Peta Klasifikasi SVM & Poligon Shapefile", "📍 Eksplorasi Titik & Indeks Spektral"])

    with tab_map1:
        st.markdown("<div class='info-card'><h4>Peta Hasil Klasifikasi SVM (Vektor Poligon & Raster Spasial)</h4><p>Peta di bawah memuat poligon shapefile asli untuk 6 kelas tutupan lahan, layer evaluasi (Sorot Data Uji dan Salah Klasifikasi dengan pin info oranye), serta overlay raster hasil prediksi SVM berlatar Google Satellite.</p></div>", unsafe_allow_html=True)

        if os.path.exists(MAP_HTML_PATH):
            with open(MAP_HTML_PATH, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=680, scrolling=False)
        else:
            st.warning("File hasil_klasifikasi_svm.html belum ditemukan di folder klasifikasi_jawa_timur.")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Model Klasifikasi", "SVM (RBF)")
        m2.metric("Total Poligon Sampel", "285 Poligon")
        m3.metric("Data Uji (Testing)", "57 Poligon")
        m4.metric("Akurasi Testing", "82.46%")

    with tab_map2:
        ctrl1, ctrl2, ctrl3 = st.columns(3)
        with ctrl1:
            show_classes = st.multiselect("Tampilkan Kelas:", df["kelas"].unique().tolist(), default=df["kelas"].unique().tolist(), key="tab2_cls")
        with ctrl2:
            map_style = st.selectbox("Peta Dasar:", ["Google Satellite", "Google Hybrid", "OpenStreetMap", "CartoDB Dark"], key="tab2_base")
        with ctrl3:
            marker_size = st.slider("Ukuran Titik:", 4, 14, 7, key="tab2_sz")

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
                    f"<div style='font-family:Arial,sans-serif;min-width:200px;'>"
                    f"<div style='background:{color};color:white;padding:6px 10px;"
                    f"border-radius:6px 6px 0 0;font-weight:600;font-size:13px;'>{icon} {kls}</div>"
                    f"<div style='padding:8px 10px;background:#1e293b;color:#e2e8f0;"
                    f"border-radius:0 0 6px 6px;font-size:12px;line-height:1.5;'>"
                    f"<b>Koordinat:</b> {row['lat']:.5f}, {row['lon']:.5f}<br>"
                    f"<b>NDVI:</b> {row['NDVI']:.4f} | <b>NDWI:</b> {row['NDWI']:.4f}<br>"
                    f"<b>MNDWI:</b> {row['MNDWI']:.4f} | <b>NDBI:</b> {row['NDBI']:.4f}<br>"
                    f"<b>EVI:</b> {row['EVI']:.4f} | <b>BSI:</b> {row['BSI']:.4f}"
                    f"</div></div>"
                )
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=marker_size, color=color, fill=True,
                    fill_color=color, fill_opacity=0.85, weight=1.5,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{icon} {kls} (NDVI: {row['NDVI']:.3f})",
                ).add_to(mc)
            mc.add_to(fg)
            fg.add_to(m)

        folium.LayerControl(collapsed=False).add_to(m)
        st_folium(m, width=None, height=580, returned_objects=[])

# ===============================================================
# PAGE 4 - EVALUASI MODEL
# ===============================================================
elif page == "Evaluasi Model":
    df = load_data()
    st.markdown("""
    <div class='page-header'>
        <h1>Perbandingan & Evaluasi Model Machine Learning</h1>
        <p>Eksperimen 6 model klasifikasi pada dataset Sentinel-2A Jawa Timur</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Melatih dan mengevaluasi model..."):
        results, le, X_train, X_test, y_train, y_test, scaler = run_models(df)

    acc_df = pd.DataFrame([
        {"Model": name, "Akurasi (%)": round(v["accuracy"] * 100, 2)}
        for name, v in results.items()
    ]).sort_values("Akurasi (%)", ascending=False).reset_index(drop=True)

    best_model = acc_df.iloc[0]["Model"]
    best_acc   = acc_df.iloc[0]["Akurasi (%)"]

    st.markdown(
        f"<div style='background-color:#14532d;border:1px solid #16a34a;border-radius:8px;padding:12px 18px;margin-bottom:16px;'>"
        f"<span style='color:#bbf7d0;font-weight:600;'>Model Terbaik:</span> "
        f"<span style='color:#ffffff;font-weight:700;'>{best_model}</span> "
        f"<span style='color:#86efac;margin-left:8px;'>(Akurasi Pengujian: {best_acc:.2f}%)</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    cb, ct = st.columns([1.5, 1])
    with cb:
        bar_colors = ["#22c55e" if m == best_model else "#3b82f6" for m in acc_df["Model"]]
        fig_acc = go.Figure(go.Bar(
            x=acc_df["Akurasi (%)"], y=acc_df["Model"], orientation="h",
            marker_color=bar_colors,
            text=[f"{v:.2f}%" for v in acc_df["Akurasi (%)"]],
            textposition="outside",
        ))
        fig_acc.update_layout(**PLOTLY_LAYOUT, title="Perbandingan Akurasi Model",
                              xaxis_title="Akurasi (%)",
                              xaxis=dict(range=[0, 115], gridcolor="#1e293b"),
                              yaxis=dict(autorange="reversed"),
                              height=320)
        st.plotly_chart(fig_acc, use_container_width=True)

    with ct:
        st.markdown("#### Peringkat Akurasi Model")
        for i, row in acc_df.iterrows():
            is_best = (row["Model"] == best_model)
            bg = "rgba(34, 197, 94, 0.12)" if is_best else "rgba(30, 41, 59, 0.5)"
            border = "#22c55e" if is_best else "#334155"
            rank_str = f"#{i+1}"
            st.markdown(
                f"<div style='background:{bg};border:1px solid {border};border-radius:8px;"
                f"padding:10px 14px;margin:6px 0;display:flex;align-items:center;gap:12px;'>"
                f"<span style='color:{'#86efac' if is_best else '#94a3b8'};font-weight:700;font-size:0.85rem;min-width:28px;'>{rank_str}</span>"
                f"<span style='color:#f8fafc;font-weight:500;flex:1;'>{row['Model']}</span>"
                f"<span style='color:{'#86efac' if is_best else '#cbd5e1'};font-weight:700;'>{row['Akurasi (%)']:.2f}%</span>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("### Detail Evaluasi per Model")
    sel_model = st.selectbox("Pilih model untuk inspeksi rincian:", list(results.keys()))
    res = results[sel_model]
    classes = le.classes_

    col_cm, col_rep = st.columns([1, 1.2])
    with col_cm:
        st.markdown("#### Confusion Matrix")
        fig_cm = px.imshow(
            res["cm"], labels=dict(x="Prediksi", y="Aktual", color="Jumlah"),
            x=classes, y=classes, text_auto=True, color_continuous_scale="Blues",
            title=f"Confusion Matrix ({sel_model})"
        )
        fig_cm.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_cm, use_container_width=True)

    with col_rep:
        st.markdown("#### Classification Report")
        report = res["report"]
        rep_rows = []
        for cls in classes:
            if cls in report:
                r = report[cls]
                rep_rows.append({
                    "Kelas": cls,
                    "Precision": round(r["precision"], 3),
                    "Recall": round(r["recall"], 3),
                    "F1-Score": round(r["f1-score"], 3),
                    "Support": int(r["support"])
                })
        st.dataframe(pd.DataFrame(rep_rows), use_container_width=True, hide_index=True)

        macro = report.get("macro avg", {})
        st.markdown(
            f"<div style='background-color:#1e293b;border:1px solid #334155;border-radius:8px;padding:12px 16px;margin-top:10px;'>"
            f"<div style='font-weight:600;color:#94a3b8;font-size:0.8rem;'>Rata-rata Makro (Macro Average)</div>"
            f"<div style='color:#f8fafc;font-size:0.9rem;margin-top:2px;'>"
            f"Precision: <b>{macro.get('precision', 0):.3f}</b> &middot; "
            f"Recall: <b>{macro.get('recall', 0):.3f}</b> &middot; "
            f"F1-Score: <b>{macro.get('f1-score', 0):.3f}</b>"
            f"</div></div>",
            unsafe_allow_html=True
        )

    if sel_model in ["Random Forest", "Gradient Boosting", "Extra Trees"]:
        st.markdown("#### Tingkat Kepentingan Fitur (Feature Importance)")
        importances = res["model"].feature_importances_
        fi_df = pd.DataFrame({"Fitur": FEATURES, "Importance": importances}).sort_values("Importance", ascending=True)
        fig_fi = px.bar(
            fi_df, x="Importance", y="Fitur", orientation="h",
            title=f"Feature Importance ({sel_model})",
            color="Importance", color_continuous_scale="Viridis"
        )
        fig_fi.update_layout(**PLOTLY_LAYOUT, height=480)
        st.plotly_chart(fig_fi, use_container_width=True)
