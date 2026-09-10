# Analisis Time Series: Persiapan Data Polutan Manyar

Dalam proyek ini, kita menggunakan data historis kualitas udara (polutan) yang direkam berdasarkan urutan waktu. Sebelum melakukan pemodelan dan peramalan tren _time series_, data mentah dikelola di dalam _cloud database_ agar proses penarikan data ke sistem analitik menjadi lebih efisien dan terpusat.

Dokumen ini mencakup alur lengkap mulai dari migrasi data awal hingga pengolahan dasar menggunakan KNIME Analytics Platform, termasuk penjelasan matematis di balik setiap fitur statistik yang dihasilkan.

## 1. Migrasi Data ke Aiven PostgreSQL (via DBeaver)

Tahap pertama bertujuan untuk memindahkan data historis (`polutan_Manyar_2025_2026.csv`) ke dalam layanan _cloud database_ Aiven agar siap diakses secara daring dari berbagai platform, termasuk DBeaver dan KNIME.

### 1.1. Pembuatan Struktur Tabel di Aiven

Langkah pertama sebelum memasukkan data adalah membuat penampung datanya, yaitu sebuah tabel. Karena ini adalah analisis runtun waktu, tipe data untuk kolom waktu (`time`) wajib didefinisikan sebagai `TIMESTAMP`.

Melalui fitur **PG Studio** di _dashboard_ Aiven, kita dapat membuat tabel dengan menjalankan _query_ SQL. Berikut adalah langkah-langkahnya:

1. Masuk ke _dashboard_ Aiven dan pilih layanan PostgreSQL yang telah dibuat.
2. Buka menu **PG Studio**.
3. Pastikan _Database_ diatur ke `defaultdb` dan _Schema_ diatur ke `public`.
4. Ketikkan perintah SQL berikut pada editor:

```sql
CREATE TABLE polutan_Manyar (
    time TIMESTAMP,
    "CO" NUMERIC,
    "NO2" NUMERIC,
    "O3" NUMERIC
);
```

5. Klik tombol **Run** untuk mengeksekusi _query_. Tabel `polutan_Manyar` kini telah berhasil dibuat di _cloud_.

![Pembuatan Tabel di Aiven](images/gambar5.png)
_(Keterangan: Tampilan PG Studio di Aiven saat pembuatan tabel)_

### 1.2. Menghubungkan DBeaver dengan Aiven

Agar kita bisa mengelola data dan mengimpor file CSV dengan mudah, kita akan menggunakan aplikasi **DBeaver** yang ada di komputer lokal dan menghubungkannya ke _database_ Aiven di _cloud_.

**Langkah-langkah koneksi:**

1. Di DBeaver, klik **New Database Connection** dan pilih **PostgreSQL**.
2. Masukkan parameter koneksi yang didapatkan dari halaman _Overview_ di _dashboard_ Aiven, meliputi:
   - **Host**: _Service URI_ atau _Host_ dari Aiven.
   - **Port**: _Port_ PostgreSQL dari Aiven.
   - **Database**: `defaultdb`
   - **Username** & **Password**: _Kredensial_ dari Aiven.
3. **Penting:** Buka tab **SSL** atau **Driver Properties**, pastikan parameter `sslmode` diatur menjadi `require`. Ini wajib dilakukan agar DBeaver dapat terhubung ke Aiven yang mewajibkan koneksi aman menggunakan SSL.
4. Klik **Test Connection** untuk memastikan koneksi berhasil, lalu klik **Finish**.

### 1.3. Import Data CSV ke DBeaver

Setelah DBeaver berhasil terhubung ke Aiven dan tabel `polutan_Manyar` sudah terlihat di skema `public`, saatnya memasukkan data dari file CSV.

**Langkah-langkah import data:**

1. Pada _Database Navigator_ di DBeaver, cari tabel `polutan_Manyar` (`defaultdb` > `Schemas` > `public` > `Tables`).
2. Klik kanan pada tabel `polutan_Manyar`, lalu pilih **Import Data**.
3. Pilih format **CSV** dan cari file `polutan_Manyar_2025_2026.csv` di komputer lokal Anda.
4. Ikuti instruksi pada layar (pastikan pemisah kolom/delimeter sesuai, biasanya koma `,`).
5. Selesaikan proses import. Data dari CSV akan diunggah melalui DBeaver dan langsung masuk ke _cloud database_ Aiven.

![Data di DBeaver](images/gambar6.png)
_(Keterangan: Tampilan DBeaver dengan data polutan_Manyar yang berhasil diimport)_

**Verifikasi:**
Anda bisa mengecek total baris data yang berhasil diunggah dengan menjalankan query SQL ini di DBeaver:

```sql
SELECT COUNT(*) FROM polutan_Manyar;
```

---

## 2. Integrasi dan Pengolahan Time Series di KNIME

Setelah data siap dan tersimpan dengan aman di _cloud database_ Aiven, tahapan selanjutnya adalah menarik data tersebut ke ruang kerja lokal (KNIME Analytics Platform) untuk pra-pemrosesan dan analisis tren.

### Menghubungkan Aiven ke KNIME

Proses menghubungkan KNIME ke Aiven pada prinsipnya mirip dengan menghubungkan DBeaver. KNIME akan mengambil data secara langsung dari _cloud_. Alur koneksinya (_workflow_) dibangun menggunakan beberapa node utama secara berurutan:

- **PostgreSQL Connector**: Diatur menggunakan detail host, port, dan kredensial server Aiven. Pada tab JDBC Parameters, properti tambahan `sslmode` dengan nilai `require` dikonfigurasi agar node dapat terhubung. Hal ini penting karena Aiven menuntut koneksi SSL.

  ![Konfigurasi PostgreSQL Connector](images/gambar1.png)
  _(Keterangan: Jendela konfigurasi PostgreSQL Connector di mana kredensial database dimasukkan)_

- **DB Table Selector**: Diarahkan ke skema `public` untuk menyeleksi tabel `polutan_Manyar`.

  ![DB Table Selector](images/gambar2.png)
  _(Keterangan: Keseluruhan workflow KNIME beserta cuplikan hasil pemilihan tabel)_

- **DB Reader**: Mengeksekusi penarikan data dari database ke dalam memori KNIME agar siap diolah lebih lanjut. Total data yang berhasil ditarik berjumlah 365 baris, dengan rentang waktu 2025-08-31 sampai 2026-08-30.

  ![Hasil DB Reader](images/gambar3.png)
  _(Keterangan: Cuplikan data polutan yang berhasil ditarik ke dalam KNIME melalui node DB Reader)_

- **Statistics**: Node ini ditambahkan setelah `DB Reader` dan berfungsi sebagai langkah awal yang sangat krusial untuk **Eksplorasi Data (Exploratory Data Analysis)**.
  Alih-alih mengecek polutan satu per satu, node _Statistics_ akan secara otomatis memproses seluruh kolom numerik (CO, NO2, O3) secara bersamaan dan menghasilkan ringkasan statistik deskriptif.

  ![Ringkasan Statistik](images/gambar4.png)
  _(Keterangan: Output tabel dari node Statistics yang merangkum perhitungan statistik deskriptif untuk seluruh kolom polutan secara bersamaan dalam satu tampilan)_

### 2.1. Penjelasan Rumus dan Contoh Perhitungan Fitur pada Node Statistics

Bagian ini menjelaskan makna, rumus matematis, dan contoh perhitungan manual untuk tiap fitur statistik yang muncul di output node _Statistics_. Sebagai contoh perhitungan, digunakan 5 data NO2 pertama dari file `polutan_Manyar_2025_2026.csv` (tanggal 2025-08-31 s.d. 2025-09-04):

| Tanggal    | Nilai NO2     |
| ---------- | ------------- |
| 2025-08-31 | 0.00004948597 |
| 2025-09-01 | 0.00004543574 |
| 2025-09-02 | 0.00003819312 |
| 2025-09-03 | 0.00007869070 |
| 2025-09-04 | 0.00006042393 |

Jumlah data $n = 5$, dan setelah diurutkan: **0.00003819312, 0.00004543574, 0.00004948597, 0.00006042393, 0.00007869070**

---

**a) Missing Values (Jumlah Data Kosong)**

Menghitung berapa baris data yang bernilai kosong (`NULL`) pada suatu kolom. Berguna untuk menentukan strategi imputasi (misalnya interpolasi linear) sebelum data dianalisis lebih lanjut, karena data kosong bisa terjadi akibat kegagalan sensor pada hari tertentu.

$$\text{Missing Values} = \text{jumlah baris dengan nilai kosong pada kolom tersebut}$$

_Contoh:_ Berdasarkan pengecekan langsung pada file `polutan_Manyar_2025_2026.csv` (365 baris), terdapat missing values pada kolom `NO2` sebanyak 177, `CO` sebanyak 165, dan `O3` sebanyak 4. Karena itu, node _Missing Value_ dan strategi imputasi perlu dijalankan sebelum analisis lanjutan.

---

**b) Minimum & Maximum**

Nilai terkecil dan terbesar dalam suatu kolom. Digunakan untuk mendeteksi anomali/outlier, misalnya memastikan tidak ada nilai polutan yang negatif atau nilai yang jauh di luar kewajaran.

$$\text{Min} = \min(x_1, x_2, \dots, x_n) \qquad \text{Max} = \max(x_1, x_2, \dots, x_n)$$

_Contoh (5 data NO2 di atas):_
$$\text{Min} = 0.00003819312 \qquad \text{Max} = 0.00007869070$$

---

**c) Mean (Rata-rata)**

Nilai tengah dari seluruh data, dihitung dengan menjumlahkan semua nilai lalu membaginya dengan jumlah data.

$$\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i$$

_Contoh:_
$$\bar{x} = \frac{0.00004948597+0.00004543574+0.00003819312+0.00007869070+0.00006042393}{5} = 0.00005444589$$

---

**d) Median (50% Quantile)**

Nilai tengah setelah data diurutkan. Lebih tahan terhadap outlier dibanding Mean, karena tidak terpengaruh oleh nilai ekstrem.

$$\text{Median} = x_{\left(\frac{n+1}{2}\right)} \quad \text{(untuk } n \text{ ganjil)}$$

_Contoh:_ Data terurut: 0.00003819312, 0.00004543574, **0.00004948597**, 0.00006042393, 0.00007869070 → nilai tengah (posisi ke-3) adalah **0.00004948597**.

---

**e) Overall Sum (Jumlah Total)**

Total penjumlahan seluruh nilai dalam kolom.

$$\text{Sum} = \sum_{i=1}^{n} x_i$$

_Contoh:_
$$\text{Sum} = 0.00004948597+0.00004543574+0.00003819312+0.00007869070+0.00006042393 = 0.00027222946$$

---

**f) Variance (Varians)**

Mengukur seberapa jauh sebaran data dari nilai rata-ratanya. Semakin besar variance, semakin bervariasi/tersebar datanya.

$$s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2$$

_Contoh (menggunakan $\bar{x}=0.00005444589$):_

| $x_i$         | $x_i - \bar{x}$ | $(x_i-\bar{x})^2$ |
| ------------- | --------------- | ----------------- |
| 0.00004948597 | -0.00000495992  | 0.00000000002460  |
| 0.00004543574 | -0.00000901055  | 0.00000000008119  |
| 0.00003819312 | -0.00001625277  | 0.00000000026415  |
| 0.00007869070 | 0.00002424481   | 0.00000000058781  |
| 0.00006042393 | 0.00000597804   | 0.00000000003574  |

$$s^2 = \frac{0.00000000002460+0.00000000008119+0.00000000026415+0.00000000058781+0.00000000003574}{5-1} \approx 0.00000000024837$$

---

**g) Standard Deviation (Simpangan Baku)**

Akar kuadrat dari variance. Satuannya sama dengan satuan data asli (µg/m³), sehingga lebih mudah diinterpretasikan dibanding variance.

$$s = \sqrt{s^2}$$

_Contoh:_
$$s = \sqrt{0.00000000024837} \approx 0.00001575979$$

Artinya, secara rata-rata nilai NO2 menyimpang sekitar **0.00001575979** dari rata-ratanya (0.00005444589) pada contoh lima data tersebut.

---

**h) Skewness (Kemencengan Distribusi)**

Mengukur simetri sebaran data. Bila skewness ≈ 0, distribusi cenderung simetris. Bila positif, ekor distribusi condong ke kanan (banyak nilai kecil, sedikit nilai sangat besar). Bila negatif, ekor condong ke kiri.

$$\text{Skewness} = \frac{\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^3}{\sigma^3}$$

_Contoh (menggunakan simpangan baku populasi $\sigma \approx 0.000014096$):_

Menghitung $(x_i-\bar{x})^3$ untuk tiap data, dijumlahkan, dibagi $n$, lalu dibagi $\sigma^3$, menghasilkan:

$$\text{Skewness} \approx 0.67$$

Nilai positif ini menunjukkan bahwa lima data contoh tersebut sedikit condong ke kanan.

---

**i) Kurtosis (Keruncingan Distribusi)**

Mengukur seberapa "runcing" atau "landai" distribusi data dibandingkan distribusi normal. Kurtosis > 0 berarti distribusi lebih runcing (banyak nilai ekstrem/outlier), kurtosis < 0 berarti lebih landai/merata.

$$\text{Kurtosis} = \frac{\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^4}{\sigma^4} - 3$$

_Contoh:_
$$\text{Kurtosis} \approx -0.85$$

Nilai negatif menunjukkan sebaran 5 data contoh ini lebih landai (lebih merata, tidak ada nilai yang terlalu ekstrem) dibanding distribusi normal.

> **Catatan:** Contoh perhitungan di atas disederhanakan dengan 5 data agar mudah dipahami langkah demi langkah. Berikut adalah ringkasan hasil aktual dari **365 baris** pada file `polutan_Manyar_2025_2026.csv`, sebagai pembanding terhadap output node _Statistics_ di KNIME (Gambar 4). Nilai statistik dihitung dari data yang tersedia pada masing-masing kolom; missing values tidak dihitung dalam Min, Max, Mean, Median, Variance, Skewness, Kurtosis, dan Overall Sum:

| Fitur              | NO2 (188 tersedia) | CO (200 tersedia) | O3 (361 tersedia) |
| ------------------ | -----------------: | ----------------: | ----------------: |
| Missing Values     |                177 |               165 |                 4 |
| Minimum            |      0.00001543805 |        0.01133146 |        0.11028662 |
| Maximum            |         0.00063134 |        0.04372259 |        0.12317621 |
| Mean               |         0.00008140 |        0.02915624 |        0.11584706 |
| Median             |         0.00006687 |        0.02911604 |        0.11571048 |
| Standard Deviation |         0.00006376 |        0.00424835 |        0.00243485 |
| Variance           |   0.00000000406541 |     0.00001804847 |     0.00000592852 |
| Skewness           |               4.60 |              0.21 |              0.33 |
| Kurtosis (excess)  |              32.84 |              2.30 |             -0.01 |
| Overall Sum        |         0.01528314 |        5.83124857 |       41.82078750 |

Data NO2 memiliki skewness **4.60** dan kurtosis excess **32.84**, yang menunjukkan ekor kanan sangat kuat dan adanya nilai ekstrem. CO dan O3 lebih mendekati distribusi simetris, dengan skewness masing-masing **0.21** dan **0.33**.

---

## 3. Kesimpulan & Hasil Pre-processing

Dari tahapan pengumpulan data ke database _cloud_ (Aiven) hingga proses transformasi di dalam KNIME, kita telah berhasil mempersiapkan data mentah menjadi himpunan data (dataset) runtun waktu yang berkualitas tinggi. Berikut adalah rangkuman dari hasil _pre-processing_ ini:

1. **Sentralisasi Data yang Aman**: Data historis polutan Manyar kini tersimpan dengan aman di Aiven PostgreSQL dan diakses menggunakan enkripsi SSL, memungkinkan kolaborasi atau penarikan data dari berbagai platform kapan saja tanpa harus memindahkan _file_ CSV secara manual.
2. **Integrasi ke KNIME Berhasil**: Melalui 4 node (PostgreSQL Connector, DB Table Selector, DB Reader, Statistics), seluruh 365 baris data polutan berhasil ditarik dari _cloud database_ ke ruang kerja lokal KNIME tanpa kendala. Data terdiri atas kolom `time`, `NO2`, `CO`, dan `O3`, dengan missing values yang perlu ditangani sebelum analisis lanjutan.
3. **Pemahaman Statistik yang Terukur**: Setiap fitur pada node Statistics (Min, Max, Mean, Median, Standard Deviation, Variance, Skewness, Kurtosis, dan Overall Sum) telah dijelaskan lengkap dengan rumus dan contoh perhitungan manual, sehingga hasil eksplorasi data tidak hanya dibaca sebagai angka, tapi juga dipahami maknanya. Dari hasil ini juga diketahui kolom `time` masih bertipe String dan perlu dikonversi pada tahap berikutnya.
