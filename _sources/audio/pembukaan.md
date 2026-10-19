# Klasifikasi Sinyal Audio: Suara Berisik vs Non-Berisik

Bab ini menyajikan implementasi lengkap siklus sains data (*Data Science Lifecycle*) berbasis metodologi **CRISP-DM** untuk mengklasifikasikan kondisi kebisingan ruangan berdasarkan sinyal audio digital menjadi dua kategori: **`berisik`** (ramai / gaduh / banyak percakapan) dan **`non-berisik`** (tenang / hening / suara latar konstan).

---

## 📌 Gambaran Umum

Dalam era *Smart Building* dan otomatisasi fasilitas umum (perpustakaan, ruang ujian, laboratorium, dan ruang kerja), pemantauan tingkat kebisingan secara objektif dan *real-time* menjadi kebutuhan esensial. Berbeda dengan sensor desibel konvensional yang hanya mengukur amplitudo sesaat, pendekatan berbasis **Machine Learning dan Pemrosesan Sinyal Audio Digital** mampu mengidentifikasi karakteristik psikoakustik suara (energi, timbre percakapan manusia, dan pusat spektrum frekuensi).

Data yang diolah terdiri dari **198 rekaman audio aktual** yang seimbang:
- **Kelas `berisik`:** 100 file rekaman aktivitas ruangan ramai dan percakapan banyak orang.
- **Kelas `non-berisik`:** 98 file rekaman suasana tenang, hening, atau dengung latar kipas/AC.

---

## 🧭 Struktur dan Alur Pembahasan Bab

Bab ini disusun secara modular ke dalam 3 sub-bagian terpadu yang dapat diakses melalui panel navigasi atau tautan berikut:

| No | Sub-Bagian | Format | Deskripsi & Cakupan |
|:---:|---|:---:|---|
| **1** | [1. Business Understanding](business_understanding) | `.md` | Latar belakang masalah kebisingan lingkungan, tujuan analitik, rumusan masalah, dan manfaat praktis sistem klasifikasi audio. |
| **2** | [2. Data Understanding](data_understanding) | `.md` | Karakteristik dataset, metodologi pra-pemrosesan (resampling 22.050 Hz, buang hening, chunking 3 detik), formula matematis fitur akustik (RMS, Centroid, ZCR, MFCC 1–13), dan agregasi 19 fitur tabular (13 koefisien MFCC). |
| **3** | [3. Pemrosesan & Pemodelan Audio](audio) | `.ipynb` | Implementasi kode teknis lengkap: ekstraksi fitur Librosa, seleksi fitur (Random Forest Importance & ANOVA F-Score), komparasi 6 model klasifikasi machine learning, leaderboard, confusion matrix, ROC-AUC, dan pengujian inferensi audio baru secara interaktif. |

---

## 🔄 Alur Kerja Sistem (*End-to-End Pipeline*)

```
┌─────────────────────────┐
│ 1. Data Audio Mentah    │ ──► Rekaman WAV / MP3 (Kelas Berisik vs Non-Berisik)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 2. Pra-Pemrosesan       │ ──► Resample 22.050 Hz ➔ Trim Hening (25 dB) ➔ Chunking 3 Detik
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 3. Ekstraksi Fitur      │ ──► Librosa: RMS Energy, Spectral Centroid, ZCR, MFCC 1-13
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 4. Agregasi Statistik   │ ──► Menghitung Nilai Statistik ➔ Matriks Tabular 19 Fitur Numerik (13 MFCC)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 5. Seleksi Fitur        │ ──► MDI Random Forest & ANOVA F-Score ➔ Terpilih 10 Fitur Inti
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 6. Komparasi Model ML   │ ──► Random Forest, SVM (RBF & Linear), KNN, LogReg, Gradient Boosting
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 7. Model Terbaik        │ ──► Random Forest (Akurasi Uji: 82.50% | F1: 0.8293 | ROC-AUC: 0.8663)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 8. Pipeline Inferensi   │ ──► Fungsi Pengujian File Suara Baru Real-time & Persistensi PKL
└─────────────────────────┘
```

---

## 🛠️ Pustaka dan Teknologi Utama

- **`librosa`** & **`soundfile`** — *Digital Signal Processing (DSP)*, manipulasi audio, spektrogram STFT, dan ekstraksi fitur psikoakustik.
- **`scikit-learn`** — Pembagian data terstratifikasi (*train-test split*), seleksi fitur (ANOVA F-Score), *standardization pipeline*, pemodelan klasifikasi, *cross-validation*, dan metrik evaluasi.
- **`pandas`** & **`numpy`** — Komputasi array numerik multidimensi dan manipulasi matriks dataset tabular.
- **`matplotlib`** & **`seaborn`** — Visualisasi bentuk gelombang sinyal (*waveform*), boxplot distribusi fitur, heatmap korelasi, confusion matrix, dan kurva ROC.
- **`joblib`** — Serialisasi dan persistensi artefak model klasifikasi untuk kebutuhan penerapan (*deployment*).
