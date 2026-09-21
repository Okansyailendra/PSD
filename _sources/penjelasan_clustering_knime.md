# Penjelasan Proses Clustering Menggunakan KNIME

Dokumen ini menjelaskan proses clustering pada data polutan (NO2, SO2, dan CO) menggunakan tools KNIME. Terdapat 3 file CSV yang mewakili masing-masing polutan dari direktori `Data_Polutan_Sekelas`, dan ketiganya diproses menggunakan alur kerja (workflow) yang identik.

## Alur Kerja (Workflow) KNIME

Secara umum, workflow clustering dibagi menjadi dua jalur untuk membandingkan proses pengelompokan data dengan dan tanpa reduksi dimensi (PCA):
1. **Jalur Atas (Dengan PCA)**: Data dari CSV Reader diproses terlebih dahulu melalui node PCA untuk reduksi dimensi, kemudian masuk ke node k-Means, dan hasilnya divisualisasikan dengan Scatter Plot.
2. **Jalur Bawah (Tanpa PCA)**: Data dari CSV Reader langsung dimasukkan ke node k-Means tanpa reduksi dimensi, lalu divisualisasikan dengan Scatter Plot.

### Konfigurasi Node

Berikut adalah rincian konfigurasi untuk masing-masing node yang digunakan pada workflow:

- **CSV Reader**: 
  - Berfungsi untuk membaca dataset polutan.
  - Terdapat 3 variasi workflow yang membedakan hanyalah input file CSV-nya (NO2, SO2, dan CO).
  
- **PCA (Principal Component Analysis)**:
  - Dibatasi hanya menggunakan **37 dimensi**.
  - Opsi **"remove original data columns"** diaktifkan sehingga kolom data asli digantikan dengan hasil dimensi PCA.

- **k-Means**:
  - Dikonfigurasi untuk membentuk maksimal **3 cluster**.
  - Konfigurasi node k-Means ini diterapkan sama persis, baik untuk jalur atas (yang melewati PCA) maupun jalur bawah.

- **Scatter Plot**:
  - Memvisualisasikan hasil dari proses clustering.
  - **Horizontal dimension (Sumbu X)** diatur menggunakan kolom `nama`.
  - **Vertical dimension (Sumbu Y)** diatur menggunakan kolom `Cluster`.
  - Konfigurasi scatter plot ini sama untuk semua visualisasi.

---

## Visualisasi Workflow dan Scatter Plot

Berikut adalah gambar dari masing-masing workflow dan hasil scatter plot untuk ketiga dataset polutan (NO2, SO2, dan CO). Pastikan gambar-gambar di bawah ini sudah disimpan di dalam folder `images` dengan nama yang sesuai.

### 1. Polutan NO2
![Workflow NO2](images/workflow_1.png)
*Gambar 1: Workflow KNIME untuk file CSV NO2.*

![Scatter Plot NO2](images/scatter_plot_1.png)
*Gambar 2: Hasil Scatter Plot untuk NO2 (Jalur atas dengan PCA / Jalur bawah tanpa PCA).*

### 2. Polutan SO2
![Workflow SO2](images/workflow_2.png)
*Gambar 3: Workflow KNIME untuk file CSV SO2.*

![Scatter Plot SO2](images/scatter_plot_2.png)
*Gambar 4: Hasil Scatter Plot untuk SO2.*

### 3. Polutan CO
![Workflow CO](images/workflow_3.png)
*Gambar 5: Workflow KNIME untuk file CSV CO.*

![Scatter Plot CO](images/scatter_plot_3.png)
*Gambar 6: Hasil Scatter Plot untuk CO.*
