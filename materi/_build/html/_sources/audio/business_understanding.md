# 1. Business Understanding: Klasifikasi Sinyal Audio Lingkungan (Berisik vs Non-Berisik)

Dokumen ini merupakan bagian pertama dari metodologi CRISP-DM untuk klasifikasi sinyal audio lingkungan, yang menguraikan konteks masalah, tujuan analitik, rumusan masalah, dan manfaat praktis proyek.

- **Bagian Selanjutnya:** [Data Understanding](data_understanding.md)
- **Implementasi Notebook & Kode Eksperimen:** [Notebook Analisis & Klasifikasi Audio](audio)

---

## 1.1 Latar Belakang

Kebisingan lingkungan (*environmental acoustic noise*) merupakan salah satu faktor krusial yang mempengaruhi kenyamanan, konsentrasi, produktivitas, serta kesehatan mental dan fisik manusia. Pada berbagai fasilitas umum dan ruang kerja—seperti ruang perpustakaan, ruang ujian, laboratorium riset, ruang kerja bersama (*co-working space*), ruang kelas, hingga ruang rapat perkantoran—kondisi ketenangan akustik menjadi persyaratan mendasar agar aktivitas intelektual dan komunikasi dapat berlangsung secara optimal.

Secara umum, kondisi akustik ruangan dapat dikategorisasikan menjadi dua kelas utama:
1. **Kelas Berisik (*Noisy / Crowded*):** Suasana ruangan yang dipenuhi oleh aktivitas percakapan banyak orang (*multi-speaker speech / babble noise*), gesekan perabotan, tawa, atau kegaduhan aktivitas fisik lainnya.
2. **Kelas Non-Berisik (*Quiet / Ambient Noise*):** Kondisi ruangan yang tenang atau hening, di mana sinyal suara yang tertangkap hanya berupa desis suara latar konstan (*background stationary noise*) seperti dengung pendingin udara (AC), putaran kipas angin, atau hembusan angin halus tanpa adanya percakapan yang dominan.

Secara konvensional, pemantauan kebisingan dilakukan secara manual melalui patroli petugas atau menggunakan alat pengukur level tekanan suara analog/digital (*Sound Level Meter* / desibel meter). Namun, pengukuran berbasis desibel (dB) semata memiliki kelemahan mendasar:
- **Ketidakmampuan Mengenali Konteks Suara:** Desibel meter hanya mengukur magnitudo tekanan suara sesaat (*instantaneous Sound Pressure Level*), bukan konteks atau karakteristik psikoakustik suara. Lonjakan sesaat akibat pintu tertutup atau batuk sekilas dapat memicu alarm kebisingan palsu (*false positive*), padahal ruangan secara umum dalam kondisi tenang.
- **Keterbatasan Skalabilitas:** Pemantauan manusia bersifat subjektif, melelahkan, dan tidak memungkinkan pemantauan berkelanjutan di banyak ruangan secara serentak (skala 24/7).

Oleh karena itu, diperlukan pendekatan cerdas berbasis **Sains Data dan Machine Learning** yang memanfaatkan ekstraksi fitur akustik digital (domain waktu dan domain frekuensi) untuk mengklasifikasikan status kebisingan ruangan secara objektif, otomatis, dan akurat.

```
                    ALUR SISTEM KLASIFIKASI AUDIO
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Rekaman Suara  │ ───► │ Pra-Pemrosesan  │ ───► │ Ekstraksi Fitur │
│  (WAV / MP3)    │      │ Resample, Trim, │      │ RMS, Centroid,  │
└─────────────────┘      │ Chunking 3 Detik│      │ ZCR, MFCC (1-13)│
                         └─────────────────┘      └────────┬────────┘
                                                           │
┌─────────────────┐      ┌─────────────────┐               ▼
│ Inferensi Suara │ ◄─── │ Model ML Terbaik│ ◄─── ┌─────────────────┐
│ Baru (Uji Coba) │      │ (Random Forest/ │      │ Seleksi Fitur   │
└─────────────────┘      │ SVM Terpilih)   │      │ (MDI & F-Score) │
                         └─────────────────┘      └─────────────────┘
```

---

## 1.2 Tujuan Proyek

Proyek ini bertujuan untuk:
1. **Mengakuisisi dan Mengintegrasikan Dataset Audio:** Menggabungkan rekaman suara lingkungan kelas `berisik` dan `non-berisik` ke dalam satu kesatuan populasi data yang representatif dan seimbang.
2. **Menerapkan Standar Pra-Pemrosesan Akustik:** Menyeragamkan laju cuplik (*sample rate*), memotong interval hening yang tidak informatif (*silence removal*), serta membagi sinyal menjadi segmen waktu berdurasi konsisten (*chunking*).
3. **Mengekstraksi Fitur Psikoakustik:** Menghitung fitur representatif domain waktu dan frekuensi (`RMS Energy`, `Spectral Centroid`, `Zero Crossing Rate`, dan `MFCC 13 Koefisien`) serta mengagregasikannya secara statistik (Mean dan Standard Deviation) menjadi matriks tabular berdimensi 32 fitur.
4. **Melakukan Seleksi Fitur (*Feature Selection*):** Menganalisis tingkat kepentingan fitur (*feature importance*) dan korelasi statistik guna menyaring fitur-fitur yang paling relevan dan membuang redundansi dimensi.
5. **Melakukan Pelatihan dan Komparasi Model:** Menguji performa berbagai algoritma machine learning (Random Forest, Support Vector Machine, K-Nearest Neighbors, Logistic Regression, dan Gradient Boosting) untuk menemukan model klasifikasi terbaik berdasarkan metrik akurasi, presisi, recall, F1-score, dan ROC-AUC.
6. **Membangun Fungsi Inferensi Pengujian Suara Baru:** Mengembangkan sistem pengujian yang siap pakai (*ready-to-use testing function*) yang mampu menerima masukan berkas audio sembarang dan mengeluarkan prediksi kelas beserta tingkat keyakinan probabilitasnya.

---

## 1.3 Rumusan Masalah

Berdasarkan tujuan di atas, rumusan masalah yang ingin dijawab melalui analisis dan eksperimen ini adalah:
1. Bagaimana mengonversi sinyal audio mentah yang berdurasi tidak seragam menjadi deret vektor fitur numerik statis yang merepresentasikan karakteristik suara secara utuh?
2. Fitur psikoakustik manakah yang memiliki daya beda (*discriminative power*) paling signifikan antara ruangan berisik (ramai percakapan) dan non-berisik (tenang/dengung mesin)?
3. Apakah pemangkasan jumlah fitur melalui seleksi fitur dapat mempertahankan atau bahkan meningkatkan kinerja model machine learning dibandingkan menggunakan seluruh 32 fitur mentah?
4. Algoritma klasifikasi machine learning mana yang memberikan performa generalisasi terbaik dan paling konsisten pada data uji independen?
5. Bagaimana merancang alur inferensi end-to-end yang mampu menguji berkas audio baru dan menyajikan hasil diagnosis kebisingan secara real-time?

---

## 1.4 Manfaat Proyek

Hasil dari proyek ini memberikan manfaat aplikatif pada berbagai aspek:

- **Bagi Pengelola Fasilitas & Smart Building:** Memungkinkan otomatisasi pemantauan kebisingan ruang perpustakaan, ruang rapat, dan laboratorium tanpa perlu pengawasan fisik petugas, serta memicu sistem pengingat otomatis jika ruangan terdeteksi ramai.
- **Bagi Integrasi Sistem IoT & Edge Devices:** Vektor fitur yang telah dirampingkan melalui seleksi fitur memungkinkan model dijalankan pada perangkat keras mikro (*edge computing* seperti Raspberry Pi / ESP32) dengan konsumsi daya dan memori yang sangat efisien.
- **Bagi Pengembangan Riset Sains Data:** Memberikan kerangka kerja terstruktur mengenai implementasi pemrosesan sinyal digital (*Digital Signal Processing* / DSP) dan *Supervised Machine Learning* pada data multimodal non-tekstual.
