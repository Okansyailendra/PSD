# Pipeline Lengkap: Time Series → Ekstraksi Fitur → PCA → K-Means Clustering

## Latar Belakang

User memiliki data 3 polutan (NO2, CO, SO2) di Manyar (365 hari, kolom densitas mol/m²). Sudah ada notebook `Ekstraksi_Fitur_NO2.ipynb` yang melakukan ekstraksi 68 fitur TSFEL untuk NO2 saja. Tugas ini memperluas pipeline untuk **ketiga polutan** dan menambahkan tahap PCA + K-Means Clustering.

## Status Saat Ini (Apa yang Sudah Ada)

| Poin Tugas | Status | Lokasi |
|---|---|---|
| Time series per polutan (eksplorasi) | ✅ **Sudah ada** | [perhitungan.md](file:///c:/Users/OKAN/OneDrive/Dokumen/PSD/materi/perhitungan.md) (Bagian 4.A–4.E) |
| Konsep dasar statistik + contoh hitung | ✅ **Sudah ada** | [time_series.md](file:///c:/Users/OKAN/OneDrive/Dokumen/PSD/materi/time_series.md) (Bagian 2.1) |
| Ekstraksi fitur NO2 (68 fitur TSFEL) | ✅ **Sudah ada** | [Ekstraksi_Fitur_NO2.ipynb](file:///c:/Users/OKAN/OneDrive/Dokumen/PSD/materi/Ekstraksi_Fitur_NO2.ipynb) |
| Deskripsi fitur + contoh perhitungan manual | ❌ Belum ada | — |
| Ekstraksi fitur CO & SO2 | ❌ Belum ada | — |
| PCA (reduksi dimensi ke 37) | ❌ Belum ada | — |
| K-Means Clustering (68 fitur & 37 PCA) | ❌ Belum ada | — |
| Evaluasi jumlah cluster terbaik | ❌ Belum ada | — |

## Open Questions

> [!IMPORTANT]
> **Tentang "membagi ekstraksi fitur untuk 1 kelas"**: 
> Apakah yang dimaksud adalah bahwa seluruh sinyal 365 hari satu polutan dianggap sebagai **1 kelas** (1 baris fitur), sehingga ketika digabung 3 polutan menjadi **3 baris × 68 kolom fitur**? Saya mengasumsikan demikian berdasarkan notebook yang sudah ada (`Ekstraksi_Fitur_NO2.ipynb` menghasilkan 1 baris).

> [!IMPORTANT]
> **Tentang "Analisis K-Means Clustering"**: 
> Dengan hanya 3 sampel (3 polutan), jumlah cluster maksimal adalah 2. Apakah user menginginkan skenario pembagian segmen waktu (misal bulanan) untuk mendapat lebih banyak sampel? Saya akan mengimplementasikan pendekatan **segmentasi bulanan** (12 bulan × 3 polutan = 36 sampel) agar K-Means bermakna, sambil tetap menyediakan analisis 3-sampel sebagai perbandingan awal.

> [!IMPORTANT]
> **Tentang "Reduksi dimensi menjadi 37"**:
> Dari 68 fitur, PCA akan mereduksi ke 37 komponen. Ini akan diterapkan pada matriks fitur hasil segmentasi.

## Proposed Changes

### Notebook 1: Deskripsi Fitur & Perhitungan Manual

#### [NEW] `Deskripsi_Fitur_TSFEL.ipynb`

Notebook penjelasan **68 fitur TSFEL** yang mencakup:

1. **Pengelompokan fitur** ke dalam 4 domain: Statistik, Temporal, Spektral, Fraktal/Kompleksitas
2. **Tabel deskripsi** setiap fitur: nama, domain, satuan, interpretasi
3. **Rumus matematika** (LaTeX) untuk setiap fitur yang memiliki formula eksplisit
4. **Contoh perhitungan manual** menggunakan 5 data NO2 pertama (data yang sama dengan `time_series.md`)
5. **Verifikasi TSFEL**: membandingkan hasil manual vs output `tsfel` pada 5 data yang sama

Fitur akan dikelompokkan, misalnya:
- **Statistik dasar**: `calc_mean`, `calc_median`, `calc_std`, `calc_var`, `calc_min`, `calc_max`, `skewness`, `kurtosis`, `interq_range`, `mean_abs_deviation`, `median_abs_deviation`
- **Energi/Power**: `abs_energy`, `average_power`, `rms`, `mse`
- **Temporal**: `zero_cross`, `mean_diff`, `mean_abs_diff`, `median_diff`, `median_abs_diff`, `slope`, `autocorr`, `negative_turning`, `positive_turning`, `distance`, `pk_pk_distance`, `sum_abs_diff`
- **Entropi/Kompleksitas**: `entropy`, `lempel_ziv`, `dfa`, `hurst_exponent`, `higuchi_fractal_dimension`, `petrosian_fractal_dimension`, `maximum_fractal_length`
- **Spektral**: `spectral_centroid`, `spectral_entropy`, `spectral_kurtosis`, `spectral_skewness`, `spectral_spread`, `spectral_slope`, `spectral_distance`, `spectral_decrease`, `spectral_roll_off`, `spectral_roll_on`, `spectral_variation`, `spectral_positive_turning`, `fundamental_frequency`, `max_frequency`, `median_frequency`, `max_power_spectrum`, `power_bandwidth`, `human_range_energy`, `spectrogram_mean_coeff`
- **Wavelet**: `wavelet_abs_mean`, `wavelet_energy`, `wavelet_entropy`, `wavelet_std`, `wavelet_var`
- **Lainnya**: `auc`, `ecdf`, `ecdf_percentile`, `ecdf_percentile_count`, `ecdf_slope`, `hist_mode`, `calc_centroid`, `lpcc`, `mfcc`, `neighbourhood_peaks`

---

### Notebook 2: Ekstraksi Fitur Semua Polutan

#### [MODIFY] `Ekstraksi_Fitur_NO2.ipynb` → Tetap ada, tapi perlu update output O3→SO2

#### [NEW] `Ekstraksi_Fitur_Lengkap.ipynb`

Pipeline lengkap untuk **ketiga polutan** (NO2, CO, SO2):

1. **Muat data** dari `polutan_Manyar_2025_2026.csv`
2. **Preprocessing** per polutan: outlier IQR, interpolasi, ffill/bfill
3. **Ekstraksi 68 fitur TSFEL** per polutan → matriks 3 × 68
4. **Segmentasi bulanan** (12 bulan) per polutan → matriks 36 × 68
5. **Simpan CSV** hasil: `fitur_3polutan_global.csv` (3×68) dan `fitur_3polutan_bulanan.csv` (36×68)
6. **Visualisasi heatmap** fitur per polutan untuk eksplorasi awal

---

### Notebook 3: PCA & K-Means Clustering

#### [NEW] `PCA_KMeans_Clustering.ipynb`

Pipeline analisis unsupervised learning:

**Bagian A: Analisis pada 37 Komponen PCA**
1. **Standardisasi** fitur (StandardScaler)
2. **PCA** dari 68 → 37 komponen
3. **Explained Variance Ratio**: berapa % varians ditangkap oleh PCA 1–37
4. **Visualisasi Scree Plot & Cumulative Variance**
5. **Elbow Method** (WCSS/Inertia) untuk menentukan jumlah cluster optimal
6. **Silhouette Analysis** untuk evaluasi kualitas cluster
7. **K-Means** dengan jumlah cluster terbaik
8. **Visualisasi** cluster pada PCA-1 vs PCA-2 (scatter plot 2D)
9. **Interpretasi**: polutan/bulan mana yang masuk cluster yang sama

**Bagian B: Analisis pada 68 Fitur Asli (Tanpa PCA)**
1. **Standardisasi** fitur
2. **Elbow Method + Silhouette** pada 68 fitur langsung
3. **K-Means** dengan jumlah cluster terbaik
4. **Visualisasi** menggunakan PCA 2D (hanya untuk plot, bukan untuk clustering)
5. **Perbandingan** hasil cluster: 37 PCA vs 68 fitur — apakah hasilnya sama?

---

### Update TOC

#### [MODIFY] `_toc.yml`

Menambahkan 3 notebook baru ke table of contents:

```yaml
format: jb-book
root: intro
chapters:
- file: polutan
  sections:
  - file: business_understanding
  - file: data_understanding
  - file: perhitungan
- file: time_series
- file: Ekstraksi_Fitur_NO2
- file: Deskripsi_Fitur_TSFEL
- file: Ekstraksi_Fitur_Lengkap
- file: PCA_KMeans_Clustering
```

---

### Update Dependencies

#### [MODIFY] `requirements.txt`

Menambahkan library baru:
```
tsfel
scikit-learn
```

---

## Verification Plan

### Automated Tests
- Setiap notebook akan dicek cell-by-cell bahwa output sesuai harapan
- Verifikasi manual vs TSFEL pada fitur-fitur kunci (mean, std, skewness dll)
- Clustering: Silhouette Score > 0 menunjukkan cluster bermakna

### Manual Verification
- `jupyter-book build .` harus sukses tanpa error
- CSV output fitur harus memiliki dimensi yang benar (3×68, 36×68)
- Scree plot dan elbow plot harus menunjukkan titik siku yang jelas
