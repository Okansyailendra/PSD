# 2. Data Understanding: Klasifikasi Sinyal Audio Lingkungan (Berisik vs Non-Berisik)

Dokumen ini merupakan bagian kedua dari metodologi CRISP-DM untuk klasifikasi sinyal audio lingkungan, yang menguraikan sumber data, pra-pemrosesan sinyal, landasan matematis fitur akustik, serta agregasi dan pembagian dataset.

- **Bagian Sebelumnya:** [Business Understanding](business_understanding.md)
- **Implementasi Notebook & Kode Eksperimen:** [Notebook Analisis & Klasifikasi Audio](audio)

---

## 2.1 Sumber dan Karakteristik Dataset

Dataset yang digunakan merupakan rekaman audio riil yang dikumpulkan dari berbagai skenario lingkungan ruang nyata. Seluruh rekaman disimpan ke dalam dua direktori kelas utama:

- **Direktori `berisik/`:** Berisi 100 berkas audio rekaman kondisi keramaian ruangan, percakapan banyak orang, suara gaduh, tawa, atau langkah kaki yang intens.
- **Direktori `non-berisik/`:** Berisi 98 berkas audio rekaman kondisi ruangan hening, sunyi, atau suara latar monoton seperti dengung kipas angin dan hembusan pendingin udara (AC).

**Ringkasan Karakteristik Populasi Data:**
- **Total Berkas Valid:** 198 berkas audio (format kompresi audio `.mp3` dan format linier `.wav`).
- **Keseimbangan Kelas (*Class Balance*):**
  - Kelas `berisik`: 100 sampel ($50{,}51\%$)
  - Kelas `non-berisik`: 98 sampel ($49{,}49\%$)
  - Rasio kelas mendekati 1:1, sehingga dataset berada dalam kondisi **seimbang sempurna (*balanced dataset*)**. Hal ini mengeliminasi potensi bias kelas mayoritas pada algoritma klasifikasi.

---

## 2.2 Alur Pra-Pemrosesan Sinyal Audio (*Audio Preprocessing*)

Sebelum sinyal audio diekstraksi ke dalam fitur numerik, terdapat tahapan pra-pemrosesan wajib untuk memastikan integritas dan konsistensi matematis data:

```
               TAHAPAN PRE-PEMROSESAN SINYAL AUDIO
┌───────────────────────┐
│ File Audio Mentah     │ ──► Format bervariasi (.mp3 / .wav), laju cuplik tidak seragam
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ 1. Resampling         │ ──► Diseragamkan ke 22.050 Hz (Konsistensi batas Nyquist 11.025 Hz)
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ 2. Buang Hening       │ ──► Librosa effects.trim (top_db = 25 dB di bawah magnitudo puncak)
│    (Silence Removal)  │     Membuang jeda senyap di awal/akhir rekaman
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ 3. Segmentasi Chunk   │ ──► Dipotong menjadi segmen berdurasi 3 detik (66.150 sampel/chunk)
└───────────────────────┘
```

1. **Resampling ($f_s = 22.050\text{ Hz}$):**
   Rekaman audio mentah memiliki frekuensi pencuplikan yang beragam ($44.100\text{ Hz}$, $48.000\text{ Hz}$, atau $16.000\text{ Hz}$). Penyeragaman ke frekuensi standar $22.050\text{ Hz}$ menjamin bahwa resolusi spektrogram dan batas frekuensi Nyquist ($f_{\text{Nyquist}} = f_s / 2 = 11.025\text{ Hz}$) identik untuk seluruh berkas.
2. **Pembuangan Hening (*Silence Removal* dengan $top\_db = 25\text{ dB}$):**
   Di awal atau akhir perekaman, sering terdapat jeda hening beberapa detik sebelum subjek mulai beraktivitas. Jeda ini dibuang menggunakan `librosa.effects.trim(y, top_db=25)` agar model tidak mempelajari representasi keheningan yang menyesatkan pada file yang seharusnya berlabel ramai.
3. **Segmentasi Berdurasi Seragam (*Chunking* 3 Detik):**
   Durasi total rekaman antar file bervariasi (mulai dari beberapa detik hingga hitungan menit). Sinyal dipartisi menjadi segmen *chunk* berdurasi seragam $3\text{ detik}$ ($3 \times 22.050 = 66.150\text{ sampel}$). Pendekatan ini menjamin bahwa setiap jendela analisis memiliki bobot durasi yang setara.

---

## 2.3 Landasan Teori Fitur Akustik dan Formula Matematika

Untuk menangkap karakteristik pembeda antara suara gaduh dan suara sunyi, diekstraksi 4 kategori fitur akustik fundamental melalui pustaka `librosa`:

### 1. Root Mean Square (RMS) Energy
RMS merepresentasikan kekuatan energi atau volume rata-rata dari sinyal suara dalam satu jendela waktu (*frame*). Ruangan yang ramai dengan aktivitas vokal manusia memiliki energi amplitudo yang jauh lebih tinggi dan berfluktuasi dibandingkan ruangan hening.

$$\text{RMS} = \sqrt{\frac{1}{N}\sum_{n=1}^{N} x[n]^2}$$

di mana $N$ adalah panjang sampel dalam satu frame dan $x[n]$ adalah nilai amplitudo sinyal digital pada titik cuplik ke-$n$.

### 2. Spectral Centroid (Pusat Spektrum Frekuensi)
Spectral Centroid menunjukkan "titik tengah" atau pusat gravitasi dari spektrum frekuensi audio, yang secara psikoakustik dipersepsikan manusia sebagai tingkat "kecerahan" (*brightness*) suara. Sinyal suara percakapan manusia umumnya memiliki konsentrasi frekuensi menengah-tinggi yang bervariasi, sedangkan suara mesin/AC cenderung terpusat pada frekuensi rendah yang stabil.

$$\text{Centroid} = \frac{\sum_{k=1}^{K} f_k \cdot |X[k]|}{\sum_{k=1}^{K} |X[k]|}$$

di mana $f_k$ adalah frekuensi pada bin ke-$k$, dan $|X[k]|$ adalah magnitudo spektrum hasil transformasi Fourier cepat (*Short-Time Fourier Transform* / STFT).

### 3. Zero Crossing Rate (ZCR)
ZCR mengukur laju seberapa sering sinyal audio berubah tanda (dari positif ke negatif atau sebaliknya) per satuan waktu. ZCR memberikan estimasi kasar mengenai dominasi komponen frekuensi tinggi dan suara frikatif/vokal tak bersuara (*unvoiced speech*) dalam percakapan:

$$\text{ZCR} = \frac{1}{2N} \sum_{n=1}^{N-1} |\text{sgn}(x[n]) - \text{sgn}(x[n-1])|$$

di mana fungsi tanda (*sign function*) didefinisikan sebagai:
$$\text{sgn}(x) = \begin{cases} 1, & x \ge 0 \\ -1, & x < 0 \end{cases}$$

### 4. Mel-Frequency Cepstral Coefficients (MFCC 1-13)
MFCC merupakan fitur paling krusial dalam pemrosesan suara manusia (*speech processing*). Sinyal dipetakan ke dalam **skala Mel**, yaitu skala frekuensi non-linear yang meniru respons koklea telinga manusia (sangat peka pada frekuensi rendah di bawah $1.000\text{ Hz}$, dan kurang peka pada frekuensi tinggi):

$$m = 2595 \cdot \log_{10}\left(1 + \frac{f}{700}\right)$$

Tahapan ekstraksi MFCC meliputi:
1. Menghitung magnitudo STFT dari sinyal.
2. Mengalikan spektrum daya dengan kumpulan filter segitiga (*Mel filter bank*).
3. Mengambil nilai logaritma dari energi tiap filter bank.
4. Menerapkan *Discrete Cosine Transform* (DCT) untuk mendekorelasikan koefisien spektral.

Dalam proyek ini, diambil **13 koefisien pertama** ($n\_mfcc = 13$), yang secara presisi menangkap amplop spektral (*spectral envelope*) dan timbre suara manusia.

---

## 2.4 Agregasi Fitur (*Feature Aggregation*)

Ekstraksi fitur pada tingkat frame menghasilkan deret matriks deret waktu (*time-series matrix*) yang panjangnya bergantung pada durasi audio. Karena algoritma machine learning standar membutuhkan masukan berupa vektor berdimensi tetap, dilakukan agregasi statistik.

Sesuai dengan acuan pada **md.pdf**, fitur MFCC yang digunakan adalah **13 koefisien MFCC** (`mfcc1_mean` hingga `mfcc13_mean`) untuk merepresentasikan spektrum timbre vokal secara efisien tanpa pembengkakan dimensi:
- **Fitur Domain Waktu & Spektral (6 Fitur):** RMS (`rms_mean`, `rms_std`), Spectral Centroid (`centroid_mean`, `centroid_std`), dan Zero Crossing Rate (`zcr_mean`, `zcr_std`).
- **Fitur Mel-Frequency Cepstral Coefficients (13 Fitur):** Koefisien Mel 1 s.d. 13 (`mfcc1_mean` s.d. `mfcc13_mean`).

**Daftar Lengkap 19 Fitur Numerik yang Dihasilkan:**

| No | Nama Kolom Fitur | Deskripsi Singkat Fitur | Tipe Data |
|:---:|---|---|:---:|
| 1 | `rms_mean` | Rata-rata energi RMS sinyal suara | `float64` |
| 2 | `rms_std` | Standar deviasi (fluktuasi) energi RMS | `float64` |
| 3 | `centroid_mean` | Rata-rata pusat massa spektrum frekuensi (Hz) | `float64` |
| 4 | `centroid_std` | Fluktuasi pergeseran pusat massa frekuensi | `float64` |
| 5 | `zcr_mean` | Rata-rata laju perubahan tanda amplitudo nol | `float64` |
| 6 | `zcr_std` | Fluktuasi laju perubahan tanda amplitudo nol | `float64` |
| 7–19 | `mfcc1_mean` s.d. `mfcc13_mean` | 13 Koefisien MFCC rata-rata (timbre suara manusia) | `float64` |

Seluruh 19 fitur akustik tersebut disimpan bersama atribut identitas `filename` dan label target `label` ke dalam berkas **`fitur_audio.csv`** (198 baris $\times$ 21 kolom).

---

## 2.5 Eksplorasi Awal & Karakteristik Daya Pembeda

Berdasarkan analisis statistik eksploratif awal (EDA):
1. **Daya Pembeda RMS:** Kelas `berisik` menunjukkan nilai `rms_mean` dan `rms_std` yang secara signifikan lebih tinggi dibanding kelas `non-berisik`. Ruangan yang ramai memiliki fluktuasi energi yang dinamis.
2. **Daya Pembeda MFCC:** Koefisien `mfcc1_mean`, `mfcc3_mean`, dan `mfcc5_mean` menunjukkan disparitas nilai rata-rata yang sangat tegas antara kedua kelas, membuktikan bahwa 13 spektrum Mel sangat efektif menangkap kehadiran suara vokal manusia.
3. **Kebutuhan Seleksi Fitur:** Dari 19 fitur yang ada, dilakukan seleksi fitur terstruktur (Random Forest Importance & ANOVA F-Score) untuk mengekstrak subset fitur inti yang paling berpengaruh sebelum proses pemodelan.

---

## 2.6 Pembagian Data Terstratifikasi (*Train / Test Split*)

Untuk menguji kemampuan generalisasi model terhadap data baru (*unseen data*), dataset populasi 198 sampel dibagi menggunakan kaidah pembagian terstratifikasi (*Stratified Split* 80:20):

- **Data Latih (*Train Set*) - 80%:** 158 sampel (80 kelas `berisik`, 78 kelas `non-berisik`), disimpan pada berkas **`train_data.csv`**.
- **Data Uji (*Test Set*) - 20%:** 40 sampel (20 kelas `berisik`, 20 kelas `non-berisik`), disimpan pada berkas **`test_data.csv`**.

Keseimbangan proporsi 50:50 pada kedua himpunan menjamin evaluasi pengujian terbebas dari bias distribusi kelas.
