# Selamat Datang di Mata Kuliah Proyek Sains Data (PSD)

```{raw} html
<style>
/* Sembunyikan h1 bawaan markdown agar desain kustom dapat ditampilkan */
h1:first-of-type { 
  display: none !important; 
}

.intro-container {
  /* Light Mode Variables */
  --nature-dark: #2C5F2D; /* Forest Green */
  --nature-light: #97BC62; /* Light Green */
  --nature-bg: #F9FCF9; /* Mint light background */
  --nature-text: #1E392A; /* Dark green text */
  --nature-card: #FFFFFF; /* White cards */
  --nature-border: #E2EFE2;
  --nature-shadow: rgba(44, 95, 45, 0.08);
  --nature-shadow-header: rgba(44, 95, 45, 0.2);
  --nature-shadow-card: rgba(44, 95, 45, 0.06);
  --nature-shadow-card-hover: rgba(44, 95, 45, 0.15);
  --nature-shadow-list: rgba(0, 0, 0, 0.1);
  --nature-list-text: #334B3D;
  --nature-card-text: #4A5D52;
  --nature-logo-bg: rgba(151, 188, 98, 0.2);
  --header-grad-start: var(--nature-light);
  --header-grad-end: var(--nature-dark);
  
  color: var(--nature-text);
  background: var(--nature-bg);
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 10px 40px var(--nature-shadow);
  position: relative;
  overflow: hidden;
  line-height: 1.6;
  transition: all 0.3s ease;
}

/* Dark Mode Variables (Jupyter Book uses html[data-theme="dark"]) */
html[data-theme="dark"] .intro-container,
html[data-mode="dark"] .intro-container {
  --nature-dark: #81C784; 
  --nature-light: #4CAF50; 
  --nature-bg: #121E14; 
  --nature-text: #E8F5E9; 
  --nature-card: #1B2B20; 
  --nature-border: #2E4C36; 
  --nature-shadow: rgba(0, 0, 0, 0.4);
  --nature-shadow-header: rgba(0, 0, 0, 0.5);
  --nature-shadow-card: rgba(0, 0, 0, 0.3);
  --nature-shadow-card-hover: rgba(0, 0, 0, 0.6);
  --nature-shadow-list: rgba(0, 0, 0, 0.4);
  --nature-list-text: #C8E6C9; 
  --nature-card-text: #A5D6A7;
  --nature-logo-bg: rgba(76, 175, 80, 0.2);
  --header-grad-start: var(--nature-dark);
  --header-grad-end: var(--nature-light);
}

/* Fallback for system dark mode if data-theme is not applied explicitly */
@media (prefers-color-scheme: dark) {
  html:not([data-theme="light"]):not([data-mode="light"]) .intro-container {
    --nature-dark: #81C784; 
    --nature-light: #4CAF50; 
    --nature-bg: #121E14; 
    --nature-text: #E8F5E9; 
    --nature-card: #1B2B20; 
    --nature-border: #2E4C36; 
    --nature-shadow: rgba(0, 0, 0, 0.4);
    --nature-shadow-header: rgba(0, 0, 0, 0.5);
    --nature-shadow-card: rgba(0, 0, 0, 0.3);
    --nature-shadow-card-hover: rgba(0, 0, 0, 0.6);
    --nature-shadow-list: rgba(0, 0, 0, 0.4);
    --nature-list-text: #C8E6C9; 
    --nature-card-text: #A5D6A7;
    --nature-logo-bg: rgba(76, 175, 80, 0.2);
    --header-grad-start: var(--nature-dark);
    --header-grad-end: var(--nature-light);
  }
}

/* Animasi mengambang / float */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-12px); }
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Bagian Header */
.hero-header {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, var(--header-grad-start), var(--header-grad-end));
  color: white;
  border-radius: 16px;
  margin-bottom: 3rem;
  animation: fadeUp 1s cubic-bezier(0.2, 0.8, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 15px 30px var(--nature-shadow-header);
  transition: all 0.3s ease;
}

.hero-header h1 {
  color: white !important;
  font-size: 2.5em;
  margin-bottom: 1.5rem;
  animation: float 5s ease-in-out infinite;
  position: relative;
  z-index: 2;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.hero-header p {
  font-size: 1.15em;
  opacity: 0.95;
  max-width: 700px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

/* Animasi partikel daun (hanya menggunakan CSS murni) */
.leaf-particle {
  position: absolute;
  background-color: rgba(255,255,255,0.15);
  border-radius: 50% 0 50% 50%;
  transform: rotate(-45deg);
  animation: floating-leaf 12s linear infinite;
  pointer-events: none;
}

@keyframes floating-leaf {
  0% { transform: translateY(-20px) rotate(-45deg) translateX(0); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(200px) rotate(45deg) translateX(100px); opacity: 0; }
}

.lp-1 { top: -10%; left: 15%; width: 25px; height: 25px; animation-duration: 9s; }
.lp-2 { top: -5%; left: 40%; width: 15px; height: 15px; animation-duration: 14s; animation-delay: 2s; }
.lp-3 { top: 10%; left: 75%; width: 35px; height: 35px; animation-duration: 11s; animation-delay: 1s; }
.lp-4 { top: 0%; left: 90%; width: 20px; height: 20px; animation-duration: 13s; animation-delay: 4s; }
.lp-5 { top: -15%; left: 60%; width: 18px; height: 18px; animation-duration: 10s; animation-delay: 3s; }

/* Bagian / Section */
.nature-section {
  margin-bottom: 3.5rem;
  animation: fadeUp 1s cubic-bezier(0.2, 0.8, 0.2, 1) both;
}
.nature-section:nth-child(2) { animation-delay: 0.2s; }
.nature-section:nth-child(3) { animation-delay: 0.4s; }
.nature-section:nth-child(4) { animation-delay: 0.6s; }
.nature-section:nth-child(5) { animation-delay: 0.8s; }

.section-title {
  display: flex;
  align-items: center;
  gap: 15px;
  color: var(--nature-dark) !important;
  border-bottom: 3px solid var(--nature-border);
  padding-bottom: 0.8rem;
  margin-bottom: 2rem;
  font-weight: 700;
  margin-top: 0;
  transition: all 0.3s ease;
}

/* Tempat untuk Logo */
.logo-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: var(--nature-logo-bg);
  color: var(--nature-dark);
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
  text-align: center;
  border: 2px dashed var(--nature-light);
  padding: 5px;
  box-sizing: border-box;
  transition: transform 0.3s ease, background-color 0.3s ease, border-color 0.3s ease;
}
.logo-box:hover {
  transform: scale(1.1) rotate(5deg);
}

.logo-small {
  width: 45px;
  height: 45px;
}
.logo-large {
  width: 70px;
  height: 70px;
  margin: 0 auto 1.5rem;
  border-radius: 20px;
  background-color: var(--nature-light);
  color: white;
  border: 2px dashed white;
  transition: background-color 0.3s ease;
}

/* Layout Grid untuk Card */
.nature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 2rem;
}

.nature-card {
  background: var(--nature-card);
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 25px var(--nature-shadow-card);
  border-bottom: 5px solid var(--nature-light);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  text-align: center;
  height: 100%;
}
.nature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 35px var(--nature-shadow-card-hover);
  border-bottom-color: var(--nature-dark);
}

.nature-card h3 {
  color: var(--nature-dark) !important;
  margin-bottom: 1rem;
  font-size: 1.25em;
  font-weight: 600;
  transition: color 0.3s ease;
}
.nature-card p {
  color: var(--nature-card-text);
  font-size: 0.95em;
  margin-bottom: 0;
  transition: color 0.3s ease;
}

/* Layout List (Daftar) */
.nature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.nature-list li {
  position: relative;
  padding-left: 35px;
  margin-bottom: 1.2rem;
  color: var(--nature-list-text);
  transition: color 0.3s ease;
}
.nature-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 6px;
  width: 14px;
  height: 14px;
  background-color: var(--nature-light);
  border-radius: 50% 0 50% 50%; /* Bentuk daun murni CSS */
  transform: rotate(-45deg);
  box-shadow: 2px 2px 4px var(--nature-shadow-list);
  transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
}
.nature-list li:hover::before {
  transform: rotate(-45deg) scale(1.2);
  background-color: var(--nature-dark);
}

.intro-container a {
  color: var(--nature-dark);
  font-weight: bold;
  text-decoration: none;
  transition: color 0.3s ease;
}
.intro-container a:hover {
  color: var(--nature-light);
  text-decoration: underline;
}

</style>

<div class="intro-container">

  <!-- HEADER UTAMA -->
  <div class="hero-header">
    <div class="leaf-particle lp-1"></div>
    <div class="leaf-particle lp-2"></div>
    <div class="leaf-particle lp-3"></div>
    <div class="leaf-particle lp-4"></div>
    <div class="leaf-particle lp-5"></div>
    
    <img src="_images/tree.svg" alt="Logo Pohon" class="logo-large" style="border: none; background: transparent;">
    
    <h1>Selamat Datang di Mata Kuliah Proyek Sains Data (PSD)</h1>
    <p>Buku panduan dan materi interaktif yang dirancang untuk membantu memahami, merancang, dan mengimplementasikan proyek sains data.</p>
  </div>


  <!-- BAGIAN 1: CAPAIAN PEMBELAJARAN -->
  <div class="nature-section">
    <h2 class="section-title">
      <img src="_images/target.svg" alt="Logo Target" class="logo-small" style="border: none; background: transparent;">
      Capaian Pembelajaran
    </h2>
    <ul class="nature-list">
      <li><strong>Memahami</strong> siklus hidup proyek sains data, mulai dari pemahaman bisnis (business understanding) hingga <i>deployment</i>.</li>
      <li><strong>Mengumpulkan dan Membersihkan</strong> data dari berbagai sumber (API, web scraping, database).</li>
      <li><strong>Mengeksplorasi</strong> data menggunakan teknik Exploratory Data Analysis (EDA) yang mendalam.</li>
      <li><strong>Membangun</strong> model prediktif atau deskriptif menggunakan algoritma Machine Learning yang tepat.</li>
      <li><strong>Menyajikan</strong> hasil analisis dalam bentuk visualisasi data yang komunikatif dan interaktif.</li>
      <li><strong>Mendeploy</strong> model ke dalam aplikasi berbasis web untuk dapat digunakan oleh pengguna (end-user).</li>
    </ul>
  </div>


  <!-- BAGIAN 2: PRASYARAT -->
  <div class="nature-section">
    <h2 class="section-title">
      <img src="_images/gear.svg" alt="Logo Peralatan" class="logo-small" style="border: none; background: transparent;">
      Prasyarat
    </h2>
    <ul class="nature-list">
      <li><strong>Pemrograman Python</strong> (terutama penggunaan <i>library</i> <code>pandas</code>, <code>numpy</code>, dan <code>matplotlib</code> / <code>seaborn</code>).</li>
      <li><strong>Statistika & Probabilitas</strong> (konsep dasar distribusi, uji hipotesis, dan korelasi).</li>
      <li><strong>Dasar Machine Learning</strong> (pemahaman konsep regresi dan klasifikasi).</li>
    </ul>
  </div>


  <!-- BAGIAN 3: STRUKTUR PEMBELAJARAN -->
  <div class="nature-section">
    <h2 class="section-title">
      <img src="_images/book.svg" alt="Logo Buku" class="logo-small" style="border: none; background: transparent;">
      Struktur Pembelajaran
    </h2>
    
    <div class="nature-grid">
      <!-- KARTU 1 -->
      <div class="nature-card">
        <img src="_images/database.svg" alt="Logo Database" class="logo-large" style="border: none; background: transparent;">
        <h3>Tahap 1: Pengumpulan & Persiapan Data</h3>
        <p>Mempelajari teknik akuisisi data, penanganan <i>missing values</i>, <i>outliers</i>, dan transformasi data.</p>
      </div>
      
      <!-- KARTU 2 -->
      <div class="nature-card">
        <img src="_images/magnifying-glass.svg" alt="Logo Analisis" class="logo-large" style="border: none; background: transparent;">
        <h3>Tahap 2: Exploratory Data Analysis (EDA)</h3>
        <p>Teknik visualisasi data dan penggalian <i>insight</i> (wawasan) menggunakan berbagai plot statistik.</p>
      </div>
      
      <!-- KARTU 3 -->
      <div class="nature-card">
        <img src="_images/brain.svg" alt="Logo AI" class="logo-large" style="border: none; background: transparent;">
        <h3>Tahap 3: Pemodelan Machine Learning</h3>
        <p>Implementasi model cerdas serta evaluasi dan optimasi model (hyperparameter tuning).</p>
      </div>
      
      <!-- KARTU 4 -->
      <div class="nature-card">
        <img src="_images/cloud-filled.svg" alt="Logo Server" class="logo-large" style="border: none; background: transparent;">
        <h3>Tahap 4: Deployment & Presentasi</h3>
        <p>Mengemas hasil analisis ke dalam <i>dashboard</i> interaktif dan presentasi proyek.</p>
      </div>
    </div>
  </div>


  <!-- BAGIAN 4: CARA MENGGUNAKAN BUKU INI -->
  <div class="nature-section">
    <h2 class="section-title">
      <img src="_images/compass.svg" alt="Logo Kompas" class="logo-small" style="border: none; background: transparent;">
      Cara Menggunakan Buku Ini
    </h2>
    <p>Buku ini dibuat menggunakan <a href="https://jupyterbook.org">Jupyter Book</a>. Beberapa hal yang dapat Anda lakukan:</p>
    <ul class="nature-list">
      <li><strong>Membaca materi</strong> secara terstruktur dari panel navigasi di sebelah kiri.</li>
      <li><strong>Berinteraksi dengan kode</strong>: Anda dapat menjalankan <i>notebook</i> di awan (cloud) pada halaman tertentu.</li>
      <li><strong>Mengunduh</strong>: Anda dapat mengunduh halaman dalam format <code>.ipynb</code> (Jupyter Notebook) atau <code>.pdf</code>.</li>
    </ul>
  </div>

</div>
```

<div style="display: none;">

![Logo](images/tree.svg)
![Logo](images/target.svg)
![Logo](images/gear.svg)
![Logo](images/book.svg)
![Logo](images/database.svg)
![Logo](images/magnifying-glass.svg)
![Logo](images/brain.svg)
![Logo](images/cloud-filled.svg)
![Logo](images/compass.svg)

</div>
