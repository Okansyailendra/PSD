# Data Preparation

Sebelum kita dapat mengekstrak pola atau fitur yang bermakna dari data deret waktu (time-series) kualitas udara, data mentah yang diperoleh dari sensor harus melalui serangkaian tahapan persiapan. Tahap persiapan ini sangat krusial; data yang kotor atau tidak terstruktur dapat menyebabkan algoritma machine learning atau ekstraksi fitur gagal berjalan, atau lebih buruk lagi, menghasilkan kesimpulan yang salah (Garbage In, Garbage Out).

Pada proyek ini, proses persiapan data berfokus pada pengondisian dataset `polutan_Manyar_2025_2026.csv` agar siap diserap oleh algoritma ekstraksi fitur **TSFEL** (Time Series Feature Extraction Library). 

Berikut adalah tahapan umum yang dilakukan pada masing-masing variabel polutan (seperti SO2, NO2, dan CO):

## 1. Pemuatan dan Format Data
Langkah pertama adalah memuat dataset ke dalam struktur tabel (DataFrame) dan memastikan setiap kolom memiliki tipe data yang tepat.
*   **Waktu sebagai Fondasi:** Kolom `time` diubah secara eksplisit menjadi tipe `datetime`. Hal ini memungkinkan kita untuk mengurutkan data secara presisi berdasarkan kronologi waktu. Data *time-series* kehilangan maknanya jika urutan waktunya acak.
*   **Standardisasi Numerik:** Kolom target polutan dipaksa untuk menjadi tipe data numerik. Data yang berasal dari sensor terkadang tercampur dengan teks atau kode *error* tertentu. Proses ini secara otomatis akan menyapu bersih karakter yang tidak valid tersebut.

## 2. Pengondisian Data Bersih
Dalam *pipeline* aslinya, data mentah harus melalui tahap pembersihan yang berat, meliputi:
*   **Penyaringan Pencilan (Outlier):** Menggunakan metode statistik *Interquartile Range* (IQR) untuk membuang lonjakan nilai yang tidak masuk akal akibat *noise* pada sensor.
*   **Imputasi Missing Value:** Menambal kekosongan data akibat sensor yang mati atau data *outlier* yang dihapus, menggunakan teknik Interpolasi Waktu.

Namun, pada tahap ini, kita telah menggunakan dataset sekunder (`polutan_Manyar_2025_2026_bersih.csv`) yang **sudah melalui seluruh proses pembersihan tersebut**. Oleh karena itu, kita dapat langsung melompat ke tahap persiapan ekstraksi dengan jaminan bahwa data sudah 100% utuh tanpa *missing value* maupun nilai pencilan yang mengganggu.

## 3. Transformasi untuk Algoritma TSFEL
Algoritma komputasi di balik pustaka TSFEL tidak memproses data dalam bentuk tabel Pandas, melainkan membutuhkan struktur matematis berupa *array* satu dimensi.
*   Data polutan target (misalnya SO2) diekstrak dan diubah menjadi rentetan angka murni (*numpy array*).
*   Kita mendefinisikan *Sampling Frequency* (`fs = 1`) yang berfungsi sebagai parameter acuan bagi beberapa perhitungan fitur yang berkaitan dengan domain waktu dan frekuensi.

Setelah data berubah wujud menjadi sinyal satu dimensi yang mulus, barulah kita siap untuk membongkarnya dan mengekstrak puluhan fitur statistik, temporal, dan spektral pada tahap selanjutnya.