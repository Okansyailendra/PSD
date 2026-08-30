# 2. Data Understanding

## 2.1 Sumber Data

Data diperoleh dari **Open-Meteo Air Quality API**, yaitu layanan open data yang menyediakan estimasi konsentrasi polutan udara berbasis model reanalisis atmosfer (mengombinasikan data satelit, model kimia atmosfer CAMS milik Copernicus, dan data stasiun pemantauan darat). Data yang diambil berupa data per jam (*hourly*) selama satu tahun ke belakang, dibatasi pada satu titik koordinat yang mewakili pusat wilayah kajian (Gresik), yang diperoleh dari titik tengah (*centroid*) poligon GeoJSON batas wilayah yang telah ditentukan.

Karena sifatnya berbasis model estimasi (bukan pengukuran langsung dari satu alat sensor fisik di lokasi), nilai yang dihasilkan bisa dianggap sebagai representasi kondisi udara di area tersebut, bukan pengukuran presisi pada satu titik geografis yang sangat spesifik.

## 2.2 Struktur Data

Data yang digunakan merupakan rangkaian *time-series* polutan udara per jam, dengan kolom sebagai berikut:

| Kolom | Tipe Data | Keterangan |
|---|---|---|
| `time` | datetime | Waktu pencatatan (tanggal dan jam) |
| `CO` | float | Konsentrasi Karbon Monoksida (μg/m³) |
| `NO2` | float | Konsentrasi Nitrogen Dioksida (μg/m³) |
| `PM10` | float | Konsentrasi partikel < 10 mikrometer (μg/m³) |
| `PM2.5` | float | Konsentrasi partikel < 2.5 mikrometer (μg/m³) |
| `O3` | float | Konsentrasi Ozon permukaan (μg/m³) |

## 2.3 Deskripsi Fitur (Polutan) & Baku Mutu

Tabel berikut merangkum sumber, dampak kesehatan, dan baku mutu udara ambien nasional (PP No. 22 Tahun 2021) untuk tiap polutan. Baku mutu ini nantinya dipakai kembali di Bagian 4.D untuk menghitung seberapa sering tiap polutan melewati ambang batas aman.

| Polutan | Deskripsi Singkat | Sumber Utama | Dampak Kesehatan | Baku Mutu (PP No. 22/2021) |
|---|---|---|---|---|
| **CO** (Karbon Monoksida) | Gas beracun, tidak berwarna maupun berbau, dihasilkan dari pembakaran bahan bakar fosil yang tidak sempurna | Asap knalpot kendaraan bermotor, pembakaran industri, pembakaran biomassa | Mengikat hemoglobin dalam darah menggantikan oksigen; pusing, mual, hingga keracunan fatal pada konsentrasi tinggi | 10.000 μg/m³ (rata-rata 1 jam) |
| **NO2** (Nitrogen Dioksida) | Gas berwarna cokelat kemerahan dengan bau tajam menyengat | Mesin kendaraan bermotor (terutama diesel), pembangkit listrik berbahan bakar fosil, cerobong asap pabrik | Mengiritasi saluran pernapasan, memperparah asma, menurunkan fungsi paru-paru jangka panjang | 200 μg/m³ (rata-rata 1 jam) |
| **PM10** (Particulate Matter ≤10 µm) | Partikel debu/asap yang dapat masuk ke saluran pernapasan atas | Debu jalan, aktivitas konstruksi, asap cerobong pabrik | Iritasi saluran pernapasan atas, memperparah gangguan paru | 75 μg/m³ (rata-rata 24 jam) |
| **PM2.5** (Particulate Matter ≤2.5 µm) | Partikel jauh lebih halus, dapat menembus alveolus paru bahkan masuk aliran darah | Pembakaran bahan bakar fosil, asap kendaraan diesel, pembakaran terbuka (sampah/lahan) | Paling banyak dikaitkan dengan risiko penyakit jantung dan kanker paru dalam studi epidemiologi | 55 μg/m³ (rata-rata 24 jam) |
| **O3** (Ozon Permukaan) | Berbeda dari lapisan ozon stratosfer; ozon permukaan berbahaya bagi kesehatan, terbentuk dari reaksi fotokimia sinar matahari dengan NO2 dan VOC, sehingga cenderung lebih tinggi di siang hari cerah | Reaksi fotokimia sekunder (bukan emisi langsung) | Mengiritasi saluran pernapasan, memperparah asma | 150 μg/m³ (rata-rata 1 jam) |

## 2.4 Eksplorasi Data & Pengecekan Anomali

Sebelum data dibersihkan, penting untuk melakukan eksplorasi awal guna mengetahui kondisi data secara umum: tipe data, jumlah baris, rentang nilai, serta indikasi anomali seperti data kosong (*missing values*), nilai negatif, atau outlier ekstrem.

```{note}
Kode di bawah ini hanya **contoh ilustrasi** cara melakukan pengecekan (belum dieksekusi di sini karena `df` belum tersedia — variabel `df` baru terbentuk setelah proses crawling di Bagian 3.B). Kode yang benar-benar dijalankan (executable) ada di **Bagian 3.C**, tepat setelah data hasil crawling dimasukkan ke DataFrame.
```

```python
# Informasi umum struktur data: tipe kolom, jumlah non-null, penggunaan memori
df.info()

# Statistik deskriptif untuk melihat rentang nilai (min, max, mean, std) tiap polutan
# Berguna untuk mendeteksi kejanggalan, misalnya nilai minimum yang negatif
df.describe()

# Cek jumlah missing values (NaN) di setiap kolom
print("Jumlah data kosong (missing values) per kolom:")
print(df.isna().sum())

# Cek jumlah nilai negatif per kolom SEBELUM dibersihkan
# Nilai negatif secara logika fisika tidak mungkin terjadi pada konsentrasi gas/partikel
kolom_polutan = ['pm10', 'pm2_5', 'carbon_monoxide', 'nitrogen_dioxide', 'ozone']
for col in kolom_polutan:
    jumlah_negatif = (df[col] < 0).sum()
    print(f"Jumlah nilai negatif pada {col}: {jumlah_negatif}")

# Deteksi outlier ekstrem menggunakan visualisasi boxplot per kolom polutan
fig, axes = plt.subplots(1, 5, figsize=(20, 5))
for i, col in enumerate(kolom_polutan):
    sns.boxplot(y=df[col], ax=axes[i], color='#3498db')
    axes[i].set_title(col)
plt.suptitle('Deteksi Outlier per Jenis Polutan (Sebelum Dibersihkan)', fontweight='bold')
plt.tight_layout()
plt.show()
```

Dari eksplorasi di atas, kita bisa memutuskan tiga jenis penanganan anomali:
1.  **Missing Values (NaN):** Data kosong pada jam tertentu, biasanya terjadi saat sensor atau model reanalisis sedang tidak memiliki data (*gap*) untuk lokasi/waktu tersebut.
2.  **Nilai Negatif:** Secara logika, konsentrasi gas atau partikel di udara tidak mungkin bernilai di bawah 0. Jika ditemukan, nilai tersebut merupakan *error* numerik model/sensor dan harus ditangani (diubah menjadi NaN, lalu dapat diisi ulang dengan interpolasi jika diperlukan).
3.  **Lonjakan Ekstrem (Outlier):** Nilai yang mendadak sangat tinggi dibanding nilai di sekitarnya dalam rentang waktu singkat. Outlier tidak selalu berarti error — bisa juga mengindikasikan kejadian nyata seperti kebakaran lahan atau kemacetan ekstrem — sehingga perlu diverifikasi lebih lanjut sebelum dihapus. Pada Bagian 3.C, boxplot juga akan dibandingkan **sebelum vs sesudah** pembersihan untuk melihat apakah sebaran outlier berkurang setelah nilai negatif ditangani.

---
