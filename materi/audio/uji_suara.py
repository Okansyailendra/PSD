"""
================================================================================
SKRIP PENGUJIAN KLASIFIKASI AUDIO (BERISIK vs NON-BERISIK)
================================================================================
Skrip mandiri untuk menguji klasifikasi file suara secara instan lewat terminal.
Waktu eksekusi: ~2-3 detik.

Cara menjalankan:
    python uji_suara.py
Atau tentukan file sendiri:
    python uji_suara.py "path/ke/file_audio.mp3"
"""

import os
import sys
import time
import joblib
import librosa
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Direktori utama
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, 'model_klasifikasi_audio.pkl')

def uji_suara(audio_path):
    print("=" * 70)
    print("      DIAGNOSIS KLASIFIKASI AUDIO (BERISIK vs NON-BERISIK)      ")
    print("=" * 70)
    
    if not os.path.exists(audio_path):
        print(f"[ERROR] File audio tidak ditemukan: {audio_path}")
        return
        
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model tidak ditemukan di: {MODEL_PATH}")
        return
        
    print(f"File Audio  : {os.path.basename(audio_path)}")
    print("Memproses dan mengekstrak fitur (13 MFCC + Akustik)...")
    
    t_start = time.time()
    
    # 1. Load model bundle
    bundle = joblib.load(MODEL_PATH)
    model = bundle['model']
    selected_features = bundle['selected_features']
    sr_target = bundle.get('target_sr', 22050)
    db_trim = bundle.get('top_db', 20)
    chunk_dur = bundle.get('chunk_duration', 3)
    
    # 2. Preprocessing Audio
    y_raw, sr = librosa.load(audio_path, sr=sr_target)
    durasi_awal = len(y_raw) / sr
    y_clean, _ = librosa.effects.trim(y_raw, top_db=db_trim)
    durasi_bersih = len(y_clean) / sr
    
    # 3. Chunking (3 detik)
    samples_per_chunk = sr_target * chunk_dur
    if len(y_clean) < samples_per_chunk:
        chunks = [y_clean] if len(y_clean) > 0 else [y_raw]
    else:
        num_ch = len(y_clean) // samples_per_chunk
        chunks = [y_clean[i*samples_per_chunk:(i+1)*samples_per_chunk] for i in range(num_ch)]
        
    # 4. Ekstraksi Fitur
    rms_list, cent_list, zcr_list, mfcc_list = [], [], [], []
    for ch in chunks:
        rms_list.append(librosa.feature.rms(y=ch))
        cent_list.append(librosa.feature.spectral_centroid(y=ch, sr=sr))
        zcr_list.append(librosa.feature.zero_crossing_rate(y=ch))
        mfcc_list.append(librosa.feature.mfcc(y=ch, sr=sr, n_mfcc=13))
        
    cat_rms = np.hstack(rms_list)
    cat_cent = np.hstack(cent_list)
    cat_zcr = np.hstack(zcr_list)
    cat_mfcc = np.hstack(mfcc_list)
    
    feature_dict = {
        'rms_mean': float(np.mean(cat_rms)),
        'rms_std': float(np.std(cat_rms)),
        'centroid_mean': float(np.mean(cat_cent)),
        'centroid_std': float(np.std(cat_cent)),
        'zcr_mean': float(np.mean(cat_zcr)),
        'zcr_std': float(np.std(cat_zcr))
    }
    for k in range(13):
        feature_dict[f'mfcc{k+1}_mean'] = float(np.mean(cat_mfcc[k, :]))
        
    df_sample = pd.DataFrame([feature_dict])[selected_features]
    
    # 5. Prediksi
    prediksi = model.predict(df_sample)[0]
    probabilitas = model.predict_proba(df_sample)[0]
    classes = list(model.classes_)
    prob_dict = {cls: float(probabilitas[idx]) for idx, cls in enumerate(classes)}
    
    t_end = time.time()
    
    badge = "[BERISIK / RAMAI]" if prediksi == 'berisik' else "[NON-BERISIK / TENANG]"
    confidence = prob_dict[prediksi] * 100
    
    print("-" * 70)
    print(f"Hasil Diagnosis    : {badge}")
    print(f"Tingkat Keyakinan  : {confidence:.2f}%")
    print(f"Peluang Berisik    : {prob_dict['berisik']*100:.2f}%")
    print(f"Peluang Non-Berisik: {prob_dict['non-berisik']*100:.2f}%")
    print(f"Durasi Rekaman     : Awal {durasi_awal:.2f}s -> Pasca Trim {durasi_bersih:.2f}s ({len(chunks)} segmen)")
    print(f"Energi RMS Rerata  : {feature_dict['rms_mean']:.5f}")
    print(f"Centroid Frekuensi : {feature_dict['centroid_mean']:.1f} Hz")
    print(f"Waktu Komputasi    : {t_end - t_start:.2f} detik")
    print("-" * 70)

if __name__ == '__main__':
    default_test = os.path.join(CURRENT_DIR, 'non-berisik', '24-179 sepi 2.mp3')
    target_file = sys.argv[1] if len(sys.argv) > 1 else default_test
    uji_suara(target_file)
