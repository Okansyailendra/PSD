# Analisis Clustering & Segmentasi Wilayah Polutan

Bagian ini membahas proses **segmentasi wilayah berdasarkan karakteristik polutan udara** menggunakan teknik *machine learning* tidak terawasi (*unsupervised learning*) yaitu **K-Means Clustering**.

## Gambaran Umum

Data yang digunakan berasal dari hasil ekstraksi fitur time-series polutan udara di **37 lokasi wilayah** Indonesia. Fitur diekstraksi dari tiga polutan utama:

| Polutan | Nama Lengkap | Jumlah Fitur |
|:-------:|:------------|:------------:|
| **NO₂** | Nitrogen Dioksida | 68 |
| **SO₂** | Sulfur Dioksida | 68 |
| **CO**  | Karbon Monoksida | 68 |
| | **Total** | **204** |

Ekstraksi fitur dilakukan dengan dua metode berbeda (linear & polinomial), menghasilkan dua tabel terpisah di database yang masing-masing memiliki struktur **207 kolom × 37 baris**.

---

## Alur Analisis (4 Tahap)

```{mermaid}
flowchart LR
    A["📦 Tahap 1\nData & EDA"] --> B["📉 Tahap 2\nReduksi Dimensi\n204 → 203 → 74 → 37"]
    B --> C["🔬 Tahap 3\nEksperimen Clustering\nSilhouette Analysis"]
    C --> D["🗺️ Tahap 4\nVisualisasi Peta\nSegmentasi Wilayah"]

    style A fill:#1565C0,color:#fff
    style B fill:#6A1B9A,color:#fff
    style C fill:#2E7D32,color:#fff
    style D fill:#E65100,color:#fff
```

| Tahap | Judul | Deskripsi |
|:-----:|:------|:----------|
| **1** | [Data & EDA](01_Data_dan_EDA/data_dan_eda) | Pengambilan data dari database MySQL, eksplorasi dan analisis deskriptif |
| **2** | [Reduksi Dimensi](02_Reduksi_Dimensi/reduksi_dimensi) | PCA bertahap: 204 → 203 → 74 → 37 komponen |
| **3** | [Eksperimen Clustering](03_Eksperimen_Clustering/eksperimen_clustering) | K-Means dengan berbagai nilai *k*, evaluasi Silhouette Coefficient pada 8 representasi × 9 nilai k = **72 eksperimen** |
| **4** | [Visualisasi Peta](04_Visualisasi_Peta/visualisasi_peta) | Peta interaktif segmentasi wilayah dengan Folium |

---

## Pipeline Reduksi Dimensi

| Tahap PCA | Dimensi Input | Dimensi Output | Tujuan |
|:---------:|:-------------:|:--------------:|:-------|
| PCA-1 | 204 | **203** | Buang 1 komponen noise terendah |
| PCA-2 | 203 | **74** | Kompresi ke ≈ n_fitur/3, pertahankan mayoritas variansi |
| PCA-3 | 74  | **37** | Kompresi ke = n_sampel, clustering lebih stabil |

Setiap tahap PCA didahului oleh **StandardScaler** untuk menormalisasi skala komponen.

---

## Teknologi yang Digunakan

- **pymysql** — Koneksi ke database MySQL
- **pandas / numpy** — Manipulasi data
- **scikit-learn** — PCA, K-Means, Silhouette
- **matplotlib / seaborn** — Visualisasi statis
- **folium** — Peta interaktif berbasis Leaflet.js
- **geopy** — Geocoding nama daerah ke koordinat
