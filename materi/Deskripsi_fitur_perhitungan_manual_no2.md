# Deskripsi Fitur & Perhitungan Manual

Sesuai pembagian tugas kelas (lihat kolom **Pembagian Fitur**), bagian ini mencakup **2 fitur**:

| Fitur | Nama Fungsi TSFEL |
|---|---|
| Fitur 1 | `calc_centroid(signal, fs)` |
| Fitur 2 | `calc_max(signal)` |

**Sinyal contoh yang dipakai (ilustrasi):**
`signal = [2, 4, 3, 6, 5, 7, 4, 8]`, `fs = 1` (1 sampel/hari)

> Catatan: data time series harian yang sesungguhnya untuk lokasi ini tidak tersedia (hanya tersedia hasil akhir 68 fitur), sehingga perhitungan manual di bawah menggunakan sinyal ilustrasi di atas. Hasilnya diverifikasi langsung memakai fungsi TSFEL asli (`tsfel.feature_extraction.features`) pada sinyal yang sama.

---

## Fitur 1: `calc_centroid(signal, fs)`

**Deskripsi:**
`calc_centroid` menghitung **titik pusat massa sinyal dalam domain waktu** (weighted mean of time, dengan bobot berupa energi/kuadrat sinyal pada tiap titik). Fitur ini menunjukkan pada "waktu" mana, dalam satu periode pengamatan, energi sinyal (di sini: konsentrasi polutan) paling terkonsentrasi. Jika nilai konsentrasi cenderung tinggi di akhir periode, centroid akan bergeser mendekati akhir; jika merata, centroid berada di tengah.

**Rumus:**

$$C = \frac{\sum_{i} t_i \cdot x_i^2}{\sum_{i} x_i^2}, \qquad t_i = \frac{i}{f_s}$$

di mana $x_i$ adalah nilai sinyal ke-$i$, dan $t_i$ adalah waktu (dalam detik/hari, tergantung satuan $f_s$) pada indeks tersebut.

**Perhitungan manual:**

Sinyal: `signal = [2, 4, 3, 6, 5, 7, 4, 8]`, `fs = 1` → `n = 8`

1. Hitung waktu tiap titik: $t_i = i / f_s$

   | i | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
   |---|---|---|---|---|---|---|---|---|
   | $x_i$ | 2 | 4 | 3 | 6 | 5 | 7 | 4 | 8 |
   | $t_i$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
   | $x_i^2$ | 4 | 16 | 9 | 36 | 25 | 49 | 16 | 64 |
   | $t_i \cdot x_i^2$ | 0 | 16 | 18 | 108 | 100 | 245 | 96 | 448 |

2. Jumlahkan:

   $\sum x_i^2 = 4+16+9+36+25+49+16+64 = 219$

   $\sum t_i x_i^2 = 0+16+18+108+100+245+96+448 = 1031$

3. Bagi:

   $$C = \frac{1031}{219} = 4.7078$$

**Verifikasi dengan TSFEL:**

```python
import tsfel.feature_extraction.features as F
signal = [2, 4, 3, 6, 5, 7, 4, 8]
fs = 1
F.calc_centroid(signal, fs)   # -> 4.7078
```

Hasil manual (4.7078) **cocok** dengan hasil fungsi TSFEL asli. ✅

---

## Fitur 2: `calc_max(signal)`

**Deskripsi:**
`calc_max` adalah fitur statistik dasar yang sangat sederhana: mengambil **nilai maksimum** dari keseluruhan sinyal. Untuk data kualitas udara, fitur ini merepresentasikan **puncak konsentrasi polutan tertinggi** yang pernah tercatat di suatu lokasi selama periode pengamatan — berguna untuk mendeteksi lokasi yang pernah mengalami lonjakan polusi ekstrem, meskipun rata-ratanya mungkin tidak terlalu tinggi.

**Rumus:**

$$\text{calc\_max}(x) = \max\{x_1, x_2, \dots, x_n\}$$

**Perhitungan manual:**

Sinyal: `signal = [2, 4, 3, 6, 5, 7, 4, 8]`

Bandingkan seluruh nilai satu per satu:

$2 \to 4 \to (4 \text{ vs } 3 \to 4) \to (4 \text{ vs } 6 \to 6) \to (6 \text{ vs } 5 \to 6) \to (6 \text{ vs } 7 \to 7) \to (7 \text{ vs } 4 \to 7) \to (7 \text{ vs } 8 \to 8)$

Nilai terbesar yang ditemukan = **8.0**

**Verifikasi dengan TSFEL:**

```python
import tsfel.feature_extraction.features as F
signal = [2, 4, 3, 6, 5, 7, 4, 8]
F.calc_max(signal)   # -> 8.0000
```

Hasil manual (8.0) **cocok** dengan hasil fungsi TSFEL asli. ✅

---

## Ringkasan

| Fitur | Rumus Singkat | Hasil (sinyal contoh) |
|---|---|---|
| `calc_centroid(signal, fs)` | $\sum t_i x_i^2 / \sum x_i^2$ | 4.7078 |
| `calc_max(signal)` | $\max(x)$ | 8.0 |