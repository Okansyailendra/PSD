# Analisis Time Series: Persiapan Data Polutan Gresik

Dalam proyek ini, kita menggunakan data historis kualitas udara (polutan) yang direkam berdasarkan urutan waktu. Sebelum melakukan pemodelan dan peramalan tren *time series*, data mentah dikelola di dalam *cloud database* agar proses penarikan data ke sistem analitik menjadi lebih efisien dan terpusat.

Dokumen ini mencakup alur lengkap mulai dari migrasi data awal hingga pengolahan dasar menggunakan KNIME Analytics Platform.

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
    "PM10" NUMERIC,
    "PM2.5" NUMERIC,
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
  
  ![Konfigurasi PostgreSQL Connector](images/gambar2.png)
  *(Keterangan: Jendela konfigurasi PostgreSQL Connector di mana kredensial database dimasukkan)*

* **DB Table Selector**: Diarahkan ke skema `public` untuk menyeleksi tabel `polutan_gresik`.
  
  ![DB Table Selector](images/gambar1.png)
  *(Keterangan: Keseluruhan workflow KNIME beserta cuplikan hasil pemilihan tabel)*

* **DB Reader**: Mengeksekusi penarikan data dari database ke dalam memori KNIME agar siap diolah lebih lanjut.
  
  ![Hasil DB Reader](images/gambar3.png)
  *(Keterangan: Cuplikan data polutan yang berhasil ditarik ke dalam KNIME melalui node DB Reader)*

* **Statistics**: Node ini ditambahkan setelah `DB Reader` dan berfungsi sebagai langkah awal yang sangat krusial untuk **Eksplorasi Data (Exploratory Data Analysis)**. 
  Alih-alih mengecek polutan satu per satu, node *Statistics* akan secara otomatis memproses seluruh kolom numerik (PM10, PM2.5, CO, NO2, O3) secara bersamaan dan menghasilkan ringkasan statistik deskriptif. 
  Beberapa hal penting yang bisa kita amati dari output node ini meliputi:
  - **Min & Max**: Memeriksa apakah ada nilai anomali (outlier). Misalnya, memastikan tidak ada nilai konsentrasi polutan yang minus/negatif.
  - **Mean & Median**: Melihat nilai rata-rata konsentrasi polutan secara keseluruhan untuk memahami tingkat dasar polusi di Gresik.
  - **Missing Values**: Mengetahui dengan cepat persisnya berapa jumlah baris data yang kosong (hilang) pada setiap jenis polutan, sehingga kita bisa menentukan strategi penanganan (*imputation*) yang tepat pada tahap selanjutnya.
  
  ![Ringkasan Statistik](images/gambar4.png)
  *(Keterangan: Output tabel dari node Statistics yang merangkum perhitungan statistik deskriptif untuk seluruh kolom polutan secara bersamaan dalam satu tampilan)*

### Pra-pemrosesan Time Series
Setelah data berhasil ditarik, langkah pra-pemrosesan yang dilakukan untuk menyesuaikan format runtun waktu meliputi:
* String to Date&Time: Digunakan untuk memastikan kolom time dikenali sebagai format waktu yang valid oleh KNIME, sehingga pengurutan kronologis data tetap konsisten.
* Missing Value: Menangani data polutan yang mungkin kosong akibat kegagalan sensor pada hari-hari tertentu, umumnya menggunakan metode interpolasi linear agar pola data tidak terputus.
* Time Series Aggregation / GroupBy: Mengelompokkan data berskala harian menjadi rata-rata mingguan atau bulanan untuk mempermudah pengamatan tren jangka panjang.

---

## 3. Kesimpulan & Hasil Pre-processing

Dari tahapan pengumpulan data ke database *cloud* (Aiven) hingga proses transformasi di dalam KNIME, kita telah berhasil mempersiapkan data mentah menjadi himpunan data (dataset) runtun waktu yang berkualitas tinggi. Berikut adalah rangkuman dari hasil *pre-processing* ini:

1. **Sentralisasi Data yang Aman**: Data historis polutan Gresik kini tersimpan dengan aman di Aiven PostgreSQL dan diakses menggunakan enkripsi SSL, memungkinkan kolaborasi atau penarikan data dari berbagai platform kapan saja tanpa harus memindahkan *file* CSV secara manual.
2. **Kualitas Data Terjamin (Bebas Outlier/Gap)**: Berkat node *Statistics* dan *Missing Value* di KNIME, anomali seperti nilai negatif (jika ada) dan kekosongan data akibat kegagalan sensor harian telah diatasi menggunakan metode interpolasi linear. Rangkaian waktu (time-series) sekarang menjadi utuh dan tidak terputus.
3. **Format Waktu yang Valid**: Transformasi menggunakan node *String to Date&Time* memastikan KNIME dan algoritma analitik lainnya menganggap kolom waktu secara kronologis yang benar, bukan sekadar teks (*string*).
4. **Siap untuk Analisis Lanjutan**: Dengan selesainya tahap integrasi dan pra-pemrosesan ini, dataset sudah berada dalam kondisi yang sangat bersih (konsisten dan terstruktur). Data ini kini sepenuhnya siap digunakan untuk tugas *machine learning* seperti pemodelan peramalan (*forecasting*) kualitas udara di periode mendatang, ataupun analisis korelasi silang antar polutan.