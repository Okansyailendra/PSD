# Analisis Time Series: Persiapan Data Polutan Gresik

Dalam proyek ini, kita menggunakan data historis kualitas udara (polutan) yang direkam berdasarkan urutan waktu. Sebelum melakukan pemodelan dan peramalan tren *time series*, data mentah dikelola di dalam *cloud database* agar proses penarikan data ke sistem analitik menjadi lebih efisien dan terpusat.

Dokumen ini mencakup alur lengkap mulai dari migrasi data awal hingga pengolahan dasar menggunakan KNIME Analytics Platform, termasuk penjelasan matematis di balik setiap fitur statistik yang dihasilkan.

## 1. Migrasi Data ke Aiven PostgreSQL (via DBeaver)

Tahap pertama bertujuan untuk memindahkan data historis (`polutan_gresik_2025_2026.csv`) ke dalam layanan *cloud database* Aiven agar siap diakses secara daring dari berbagai platform, termasuk DBeaver dan KNIME.

### 1.1. Pembuatan Struktur Tabel di Aiven
Langkah pertama sebelum memasukkan data adalah membuat penampung datanya, yaitu sebuah tabel. Karena ini adalah analisis runtun waktu, tipe data untuk kolom waktu (`time`) wajib didefinisikan sebagai `TIMESTAMP`.

Melalui fitur **PG Studio** di *dashboard* Aiven, kita dapat membuat tabel dengan menjalankan *query* SQL. Berikut adalah langkah-langkahnya:
1. Masuk ke *dashboard* Aiven dan pilih layanan PostgreSQL yang telah dibuat.
2. Buka menu **PG Studio**.
3. Pastikan *Database* diatur ke `defaultdb` dan *Schema* diatur ke `public`.
4. Ketikkan perintah SQL berikut pada editor:

```sql
CREATE TABLE polutan_gresik (
    time TIMESTAMP,
    "CO" NUMERIC,
    "NO2" NUMERIC,
    "O3" NUMERIC
);
```
5. Klik tombol **Run** untuk mengeksekusi *query*. Tabel `polutan_gresik` kini telah berhasil dibuat di *cloud*.

![Pembuatan Tabel di Aiven](images/gambar5.png)
*(Keterangan: Tampilan PG Studio di Aiven saat pembuatan tabel)*

### 1.2. Menghubungkan DBeaver dengan Aiven
Agar kita bisa mengelola data dan mengimpor file CSV dengan mudah, kita akan menggunakan aplikasi **DBeaver** yang ada di komputer lokal dan menghubungkannya ke *database* Aiven di *cloud*.

**Langkah-langkah koneksi:**
1. Di DBeaver, klik **New Database Connection** dan pilih **PostgreSQL**.
2. Masukkan parameter koneksi yang didapatkan dari halaman *Overview* di *dashboard* Aiven, meliputi:
   - **Host**: *Service URI* atau *Host* dari Aiven.
   - **Port**: *Port* PostgreSQL dari Aiven.
   - **Database**: `defaultdb`
   - **Username** & **Password**: *Kredensial* dari Aiven.
3. **Penting:** Buka tab **SSL** atau **Driver Properties**, pastikan parameter `sslmode` diatur menjadi `require`. Ini wajib dilakukan agar DBeaver dapat terhubung ke Aiven yang mewajibkan koneksi aman menggunakan SSL.
4. Klik **Test Connection** untuk memastikan koneksi berhasil, lalu klik **Finish**.

### 1.3. Import Data CSV ke DBeaver
Setelah DBeaver berhasil terhubung ke Aiven dan tabel `polutan_gresik` sudah terlihat di skema `public`, saatnya memasukkan data dari file CSV.

**Langkah-langkah import data:**
1. Pada *Database Navigator* di DBeaver, cari tabel `polutan_gresik` (`defaultdb` > `Schemas` > `public` > `Tables`).
2. Klik kanan pada tabel `polutan_gresik`, lalu pilih **Import Data**.
3. Pilih format **CSV** dan cari file `polutan_gresik_2025_2026.csv` di komputer lokal Anda.
4. Ikuti instruksi pada layar (pastikan pemisah kolom/delimeter sesuai, biasanya koma `,`).
5. Selesaikan proses import. Data dari CSV akan diunggah melalui DBeaver dan langsung masuk ke *cloud database* Aiven.

![Data di DBeaver](images/gambar6.png)
*(Keterangan: Tampilan DBeaver dengan data polutan_gresik yang berhasil diimport)*

**Verifikasi:**
Anda bisa mengecek total baris data yang berhasil diunggah dengan menjalankan query SQL ini di DBeaver:

```sql
SELECT COUNT(*) FROM polutan_gresik;
```

---

## 2. Integrasi dan Pengolahan Time Series di KNIME
Setelah data siap dan tersimpan dengan aman di *cloud database* Aiven, tahapan selanjutnya adalah menarik data tersebut ke ruang kerja lokal (KNIME Analytics Platform) untuk pra-pemrosesan dan analisis tren.

### Menghubungkan Aiven ke KNIME
Proses menghubungkan KNIME ke Aiven pada prinsipnya mirip dengan menghubungkan DBeaver. KNIME akan mengambil data secara langsung dari *cloud*. Alur koneksinya (*workflow*) dibangun menggunakan beberapa node utama secara berurutan:

* **PostgreSQL Connector**: Diatur menggunakan detail host, port, dan kredensial server Aiven. Pada tab JDBC Parameters, properti tambahan `sslmode` dengan nilai `require` dikonfigurasi agar node dapat terhubung. Hal ini penting karena Aiven menuntut koneksi SSL.

  ![Konfigurasi PostgreSQL Connector](images/gambar1.png)
  *(Keterangan: Jendela konfigurasi PostgreSQL Connector di mana kredensial database dimasukkan)*

* **DB Table Selector**: Diarahkan ke skema `public` untuk menyeleksi tabel `polutan_gresik`.

  ![DB Table Selector](images/gambar2.png)
  *(Keterangan: Keseluruhan workflow KNIME beserta cuplikan hasil pemilihan tabel)*

* **DB Reader**: Mengeksekusi penarikan data dari database ke dalam memori KNIME agar siap diolah lebih lanjut. Total data yang berhasil ditarik berjumlah 366 baris.

  ![Hasil DB Reader](images/gambar3.png)
  *(Keterangan: Cuplikan data polutan yang berhasil ditarik ke dalam KNIME melalui node DB Reader)*

* **Statistics**: Node ini ditambahkan setelah `DB Reader` dan berfungsi sebagai langkah awal yang sangat krusial untuk **Eksplorasi Data (Exploratory Data Analysis)**.
  Alih-alih mengecek polutan satu per satu, node *Statistics* akan secara otomatis memproses seluruh kolom numerik (PM10, PM2.5, CO, NO2, O3) secara bersamaan dan menghasilkan ringkasan statistik deskriptif.

  ![Ringkasan Statistik](images/gambar4.png)
  *(Keterangan: Output tabel dari node Statistics yang merangkum perhitungan statistik deskriptif untuk seluruh kolom polutan secara bersamaan dalam satu tampilan)*

### 2.1. Penjelasan Rumus dan Contoh Perhitungan Fitur pada Node Statistics

Bagian ini menjelaskan makna, rumus matematis, dan contoh perhitungan manual untuk tiap fitur statistik yang muncul di output node *Statistics*. Sebagai contoh perhitungan, digunakan 5 data PM10 pertama dari file `polutan_gresik_2025_2026.csv` yang sebenarnya dipakai pada proyek ini (tanggal 2025-08-31 s.d. 2025-09-04):

| Tanggal | Nilai PM10 |
|---|---|
| 2025-08-31 | 32.87 |
| 2025-09-01 | 23.47 |
| 2025-09-02 | 16.35 |
| 2025-09-03 | 21.00 |
| 2025-09-04 | 31.20 |

Jumlah data $n = 5$, dan setelah diurutkan: **16.35, 21.00, 23.47, 31.20, 32.87**

---

**a) Missing Values (Jumlah Data Kosong)**

Menghitung berapa baris data yang bernilai kosong (`NULL`) pada suatu kolom. Berguna untuk menentukan strategi imputasi (misalnya interpolasi linear) sebelum data dianalisis lebih lanjut, karena data kosong bisa terjadi akibat kegagalan sensor pada hari tertentu.

$$\text{Missing Values} = \text{jumlah baris dengan nilai kosong pada kolom tersebut}$$

*Contoh:* Berdasarkan pengecekan langsung pada file `polutan_gresik_2025_2026.csv` (366 baris), **tidak ditemukan nilai kosong** pada kolom manapun — PM10, PM2.5, CO, NO2, maupun O3 sama-sama memiliki Missing Values = 0. Artinya sensor tidak pernah gagal mencatat data selama periode tersebut, sehingga node *Missing Value* untuk data historis ini sebenarnya tidak wajib dijalankan (tetap berguna sebagai antisipasi jika suatu saat ada data baru yang kosong).

---

**b) Minimum & Maximum**

Nilai terkecil dan terbesar dalam suatu kolom. Digunakan untuk mendeteksi anomali/outlier, misalnya memastikan tidak ada nilai polutan yang negatif atau nilai yang jauh di luar kewajaran.

$$\text{Min} = \min(x_1, x_2, \dots, x_n) \qquad \text{Max} = \max(x_1, x_2, \dots, x_n)$$

*Contoh (5 data di atas):*
$$\text{Min} = 16.35 \qquad \text{Max} = 32.87$$

---

**c) Mean (Rata-rata)**

Nilai tengah dari seluruh data, dihitung dengan menjumlahkan semua nilai lalu membaginya dengan jumlah data.

$$\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i$$

*Contoh:*
$$\bar{x} = \frac{32.87+23.47+16.35+21.00+31.20}{5} = \frac{124.89}{5} = 24.98$$

---

**d) Median (50% Quantile)**

Nilai tengah setelah data diurutkan. Lebih tahan terhadap outlier dibanding Mean, karena tidak terpengaruh oleh nilai ekstrem.

$$\text{Median} = x_{\left(\frac{n+1}{2}\right)} \quad \text{(untuk } n \text{ ganjil)}$$

*Contoh:* Data terurut: 16.35, 21.00, **23.47**, 31.20, 32.87 → nilai tengah (posisi ke-3) adalah **23.47**.

---

**e) Overall Sum (Jumlah Total)**

Total penjumlahan seluruh nilai dalam kolom.

$$\text{Sum} = \sum_{i=1}^{n} x_i$$

*Contoh:*
$$\text{Sum} = 32.87+23.47+16.35+21.00+31.20 = 124.89$$

---

**f) Variance (Varians)**

Mengukur seberapa jauh sebaran data dari nilai rata-ratanya. Semakin besar variance, semakin bervariasi/tersebar datanya.

$$s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2$$

*Contoh (menggunakan $\bar{x}=24.98$):*

| $x_i$ | $x_i - \bar{x}$ | $(x_i-\bar{x})^2$ |
|---|---|---|
| 32.87 | 7.89 | 62.25 |
| 23.47 | -1.51 | 2.28 |
| 16.35 | -8.63 | 74.48 |
| 21.00 | -3.98 | 15.84 |
| 31.20 | 6.22 | 38.69 |

$$s^2 = \frac{62.25+2.28+74.48+15.84+38.69}{5-1} = \frac{193.54}{4} = 48.39$$

---

**g) Standard Deviation (Simpangan Baku)**

Akar kuadrat dari variance. Satuannya sama dengan satuan data asli (µg/m³), sehingga lebih mudah diinterpretasikan dibanding variance.

$$s = \sqrt{s^2}$$

*Contoh:*
$$s = \sqrt{48.39} = 6.96$$

Artinya, secara rata-rata nilai PM10 menyimpang sekitar **6.96 µg/m³** dari rata-ratanya (24.98).

---

**h) Skewness (Kemencengan Distribusi)**

Mengukur simetri sebaran data. Bila skewness ≈ 0, distribusi cenderung simetris. Bila positif, ekor distribusi condong ke kanan (banyak nilai kecil, sedikit nilai sangat besar). Bila negatif, ekor condong ke kiri.

$$\text{Skewness} = \frac{\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^3}{\sigma^3}$$

*Contoh (menggunakan simpangan baku populasi $\sigma = 6.22$):*

Menghitung $(x_i-\bar{x})^3$ untuk tiap data, dijumlahkan, dibagi $n$, lalu dibagi $\sigma^3$, menghasilkan:

$$\text{Skewness} \approx 0.02$$

Nilai yang sangat dekat dengan 0 ini menunjukkan 5 data contoh di atas tersebar hampir simetris, tidak condong ke kiri maupun ke kanan.

---

**i) Kurtosis (Keruncingan Distribusi)**

Mengukur seberapa "runcing" atau "landai" distribusi data dibandingkan distribusi normal. Kurtosis > 0 berarti distribusi lebih runcing (banyak nilai ekstrem/outlier), kurtosis < 0 berarti lebih landai/merata.

$$\text{Kurtosis} = \frac{\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^4}{\sigma^4} - 3$$

*Contoh:*
$$\text{Kurtosis} \approx -1.51$$

Nilai negatif menunjukkan sebaran 5 data contoh ini lebih landai (lebih merata, tidak ada nilai yang terlalu ekstrem) dibanding distribusi normal.

> **Catatan:** Contoh perhitungan di atas disederhanakan dengan 5 data agar mudah dipahami langkah demi langkah. Berikut adalah hasil perhitungan **aktual** untuk kolom PM10 dari **keseluruhan 366 baris** pada file `polutan_gresik_2025_2026.csv`, sebagai pembanding terhadap output node *Statistics* di KNIME (Gambar 4):

| Fitur | Nilai Aktual (PM10, 366 data) |
|---|---|
| Missing Values | 0 |
| Minimum | 13.30 |
| Maximum | 121.85 |
| Mean | 42.58 |
| Median | 36.66 |
| Standard Deviation | 19.10 |
| Variance | 364.66 |
| Skewness | 1.21 |
| Kurtosis (excess) | 1.40 |
| Overall Sum | 15,585.53 |

Berbeda dengan contoh 5 data di atas (yang hampir simetris), skewness PM10 pada keseluruhan 366 data bernilai **positif (1.21)**, artinya distribusinya condong ke kanan — sebagian besar hari memiliki PM10 rendah-sedang, namun ada beberapa hari dengan lonjakan PM10 sangat tinggi (hingga 121.85) yang menarik ekor distribusi ke kanan. Kurtosis positif (1.40) juga menguatkan hal ini: distribusi lebih "runcing" dari normal karena adanya beberapa nilai ekstrem tersebut.

---

## 3. Kesimpulan & Hasil Pre-processing

Dari tahapan pengumpulan data ke database *cloud* (Aiven) hingga proses transformasi di dalam KNIME, kita telah berhasil mempersiapkan data mentah menjadi himpunan data (dataset) runtun waktu yang berkualitas tinggi. Berikut adalah rangkuman dari hasil *pre-processing* ini:

1. **Sentralisasi Data yang Aman**: Data historis polutan Gresik kini tersimpan dengan aman di Aiven PostgreSQL dan diakses menggunakan enkripsi SSL, memungkinkan kolaborasi atau penarikan data dari berbagai platform kapan saja tanpa harus memindahkan *file* CSV secara manual.
2. **Integrasi ke KNIME Berhasil**: Melalui 4 node (PostgreSQL Connector, DB Table Selector, DB Reader, Statistics), seluruh 366 baris data polutan berhasil ditarik dari *cloud database* ke ruang kerja lokal KNIME tanpa kendala.
3. **Pemahaman Statistik yang Terukur**: Setiap fitur pada node Statistics (Min, Max, Mean, Median, Standard Deviation, Variance, Skewness, Kurtosis, dan Overall Sum) telah dijelaskan lengkap dengan rumus dan contoh perhitungan manual, sehingga hasil eksplorasi data tidak hanya dibaca sebagai angka, tapi juga dipahami maknanya. Dari hasil ini juga diketahui kolom `time` masih bertipe String dan perlu dikonversi pada tahap berikutnya.
