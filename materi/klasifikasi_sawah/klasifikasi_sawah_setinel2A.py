# =============================================================================
# KLASIFIKASI SAWAH vs NON-SAWAH - Sentinel-2A (Copernicus Data Space)
#
#   - 50 sampel sawah (kelas 1) + 50 sampel non-sawah (kelas 0)
#   - 2 kelas: sawah dan non-sawah
#   - Data  : Sentinel-2A L2A, diunduh otomatis dari Copernicus sebagai GeoTIFF
#   - Model : Random Forest (scikit-learn)
#   - Output: klasifikasi_sawah_s2a.tif
#
# Install:
#   pip install requests rasterio scikit-learn numpy matplotlib geopandas
#
# Sebelum dijalankan (sekali saja):
#   1. Buka https://shapps.dataspace.copernicus.eu/dashboard  (login akun Copernicus)
#   2. User settings -> OAuth clients -> Create -> salin Client ID & Client Secret
#   3. Isi CLIENT_ID & CLIENT_SECRET di bawah (atau lewat environment variable
#      CDSE_CLIENT_ID / CDSE_CLIENT_SECRET). Jangan upload secret ke GitHub.
#
# Struktur folder yang diperlukan:
#   klasifikasi_sawah/
#     datasawah50/  -> sawah.shp  (.dbf .shx .prj)
#     nonsawah/     -> nonsawah.shp  (.dbf .shx .prj)
# =============================================================================

import datetime as dt
import json
import math
import os
from pathlib import Path

import geopandas as gpd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import requests
from matplotlib.colors import ListedColormap
from rasterio import features
from rasterio.warp import transform_bounds, transform_geom
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                             cohen_kappa_score, confusion_matrix)

try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path(os.getcwd())

# %% [1] PARAMETER -------------------------------------------------------------
# --- Akun Copernicus (OAuth client dari dashboard Sentinel Hub) ---
CLIENT_ID = os.environ.get("CDSE_CLIENT_ID", "sh-ce8718c2-d115-4655-b456-15ef4e621c3b")
CLIENT_SECRET = os.environ.get("CDSE_CLIENT_SECRET", "4IcGDU0dfrjdGNSXnUqeefPIJgUvHA3i")

# --- Pencarian citra ---
START_DATE = "2026-06-01"      # rentang tanggal pencarian citra
END_DATE = "2026-09-30"
PLATFORM_PREFIX = "S2A"        # hanya Sentinel-2A. Isi None untuk semua satelit Sentinel-2
MAX_CLOUD = 30                 # % awan maksimum (level tile) untuk kandidat scene
MAX_TRIES = 5                  # coba maks. N scene terbaik sampai area sampel cukup bersih
MIN_VALID = 0.90               # minimal fraksi piksel bebas awan di area unduhan
MASK_CLOUD = True              # buang awan/bayangan awan/salju memakai band SCL
BUFFER_M = 1500                # margin area unduhan di sekeliling sampel (meter)

# --- Sampel & model ---
N_SAMPLE = 50                  # jumlah poligon sampel PER KELAS
FILE_SAWAH    = BASE_DIR / "datasawah50" / "sawah.shp"      # kelas = 1
FILE_NONSAWAH = BASE_DIR / "nonsawah"    / "nonsawah.shp"  # kelas = 0
TRAIN_FRAC = 0.7               # porsi poligon untuk training (sisanya testing)
N_TREES = 200
SEED = 42

# --- File ---
# Jika file ini sudah ada, unduhan dilewati (boleh juga diisi TIF manual dari
# Copernicus Browser dengan band B02,B03,B04,B08,B11,B12 berurutan).
TIF_IN = BASE_DIR / "sentinel2a_aoi.tif"
INFO_TXT = BASE_DIR / "sentinel2a_aoi_info.txt"
OUT_TIF = BASE_DIR / "klasifikasi_sawah_s2a.tif"
OUT_PNG = BASE_DIR / "peta_klasifikasi.png"
OUT_TXT = BASE_DIR / "hasil_evaluasi.txt"

BAND_NAMES = ["B02", "B03", "B04", "B08", "B11", "B12"]

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
CATALOG_URL = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"

LOG = []


def log(*args):
    s = " ".join(str(a) for a in args)
    print(s)
    LOG.append(s)


# %% [2] SAMPEL: baca SHP dan pilih 50 poligon per kelas -----------------------
def load_samples_shp(path, n):
    """
    Membaca file Shapefile (.shp) menggunakan GeoPandas,
    memproyeksikan ke WGS-84 (EPSG:4326) agar konsisten,
    lalu mengambil maksimum n poligon secara acak.
    Mengembalikan list geometri dalam format GeoJSON-dict (koordinat lon/lat).
    """
    gdf = gpd.read_file(path)
    total = len(gdf)

    # Hanya simpan fitur yang memiliki geometri
    gdf = gdf[gdf.geometry.notna()].copy()

    # Proyeksikan ke WGS-84 jika belum
    if gdf.crs is None:
        log(f"PERINGATAN: {Path(path).name} tidak memiliki CRS. Diasumsikan EPSG:4326.")
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    if len(gdf) > n:
        idx = np.random.default_rng(SEED).choice(len(gdf), n, replace=False)
        gdf = gdf.iloc[sorted(idx)].copy()
    elif len(gdf) < n:
        log(f"PERINGATAN: {Path(path).name} hanya berisi {total} poligon (< {n}).")

    log(f"{Path(path).name}: {total} poligon di file -> dipakai {len(gdf)}")

    # Kembalikan geometri sebagai list dict GeoJSON
    from shapely.geometry import mapping
    return [mapping(g) for g in gdf.geometry]


def iter_xy(c):
    if isinstance(c[0], (int, float)):
        yield c[0], c[1]
    else:
        for s in c:
            yield from iter_xy(s)


geoms_sawah = load_samples_shp(FILE_SAWAH, N_SAMPLE)
geoms_non   = load_samples_shp(FILE_NONSAWAH, N_SAMPLE)

xy = [p for g in geoms_sawah + geoms_non for p in iter_xy(g["coordinates"])]
pad = BUFFER_M / 111000.0
BBOX = (min(x for x, _ in xy) - pad, min(y for _, y in xy) - pad,
        max(x for x, _ in xy) + pad, max(y for _, y in xy) + pad)
log("BBox area (lon/lat):", tuple(round(v, 5) for v in BBOX))


# %% [3] UNDUH SENTINEL-2A (GeoTIFF) DARI COPERNICUS ---------------------------
def get_token():
    r = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }, timeout=60)
    if r.status_code != 200:
        raise SystemExit(f"Gagal mengambil token ({r.status_code}): {r.text[:300]}\n"
                         "Cek CLIENT_ID dan CLIENT_SECRET (dashboard Sentinel Hub).")
    return r.json()["access_token"]


def search_scenes(token):
    body = {
        "collections": ["sentinel-2-l2a"],
        "datetime": f"{START_DATE}T00:00:00Z/{END_DATE}T23:59:59Z",
        "bbox": list(BBOX),
        "limit": 100,
    }
    headers = {"Authorization": f"Bearer {token}"}
    feats = []
    while True:
        r = requests.post(CATALOG_URL, json=body, headers=headers, timeout=120)
        if r.status_code != 200:
            raise SystemExit(f"Pencarian katalog gagal ({r.status_code}): {r.text[:300]}")
        js = r.json()
        feats += js.get("features", [])
        nxt = js.get("context", {}).get("next")
        if not nxt:
            break
        body["next"] = nxt

    cand = []
    for it in feats:
        p = it.get("properties", {})
        cc = p.get("eo:cloud_cover")
        if cc is None or cc > MAX_CLOUD:
            continue
        if PLATFORM_PREFIX and not it["id"].upper().startswith(PLATFORM_PREFIX):
            continue
        cand.append((cc, p["datetime"], it["id"]))
    cand.sort()
    log(f"Scene ditemukan: {len(feats)} | lolos filter ({PLATFORM_PREFIX or 'semua'}, "
        f"awan <= {MAX_CLOUD}%): {len(cand)}")
    return cand


def utm_epsg(lon, lat):
    return (32700 if lat < 0 else 32600) + int((lon + 180) // 6) + 1


def build_evalscript():
    mask = " || [0,1,3,8,9,10,11].indexOf(s.SCL) >= 0" if MASK_CLOUD else ""
    return ('//VERSION=3\n'
            'function setup() {\n'
            '  return {\n'
            '    input: [{bands: ["B02","B03","B04","B08","B11","B12","SCL","dataMask"]}],\n'
            '    output: {bands: 6, sampleType: "FLOAT32"}\n'
            '  };\n'
            '}\n'
            'function evaluatePixel(s) {\n'
            f'  var bad = (s.dataMask == 0){mask};\n'
            '  if (bad) return [0,0,0,0,0,0];\n'
            '  return [s.B02, s.B03, s.B04, s.B08, s.B11, s.B12];\n'
            '}\n')


def download_scene(token, when):
    """Unduh area sampel dari satu scene: UTM, 10 m, 6 band reflektansi (float32)."""
    epsg = utm_epsg((BBOX[0] + BBOX[2]) / 2, (BBOX[1] + BBOX[3]) / 2)
    minx, miny, maxx, maxy = transform_bounds("EPSG:4326", f"EPSG:{epsg}", *BBOX)
    minx, miny = math.floor(minx / 10) * 10, math.floor(miny / 10) * 10
    maxx, maxy = math.ceil(maxx / 10) * 10, math.ceil(maxy / 10) * 10
    w, h = (maxx - minx) // 10, (maxy - miny) // 10
    if w > 2500 or h > 2500:
        raise SystemExit(f"Area terlalu besar ({w}x{h} piksel, maks 2500). "
                         "Kecilkan BUFFER_M.")

    t = dt.datetime.fromisoformat(when.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    body = {
        "input": {
            "bounds": {
                "bbox": [minx, miny, maxx, maxy],
                "properties": {"crs": f"http://www.opengis.net/def/crs/EPSG/0/{epsg}"},
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {"from": (t - dt.timedelta(minutes=1)).strftime(fmt),
                                  "to": (t + dt.timedelta(minutes=1)).strftime(fmt)},
                    "mosaickingOrder": "leastCC",
                },
            }],
        },
        "output": {
            "resx": 10, "resy": 10,
            "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}],
        },
        "evalscript": build_evalscript(),
    }
    r = requests.post(PROCESS_URL, json=body, timeout=300, headers={
        "Authorization": f"Bearer {token}", "Accept": "image/tiff"})
    if r.status_code != 200:
        raise SystemExit(f"Unduhan gagal ({r.status_code}): {r.text[:400]}")
    return r.content, epsg


def valid_fraction(tif_bytes):
    from rasterio.io import MemoryFile
    with MemoryFile(tif_bytes) as mf, mf.open() as src:
        arr = src.read()
    return float((np.any(arr != 0, axis=0) & np.isfinite(arr).all(axis=0)).mean())


def fetch_sentinel2a():
    token = get_token()
    cand = search_scenes(token)
    if not cand:
        raise SystemExit(
            f"Tidak ada scene {PLATFORM_PREFIX or ''} dengan awan <= {MAX_CLOUD}% pada "
            f"{START_DATE} s/d {END_DATE}. Perlebar START_DATE/END_DATE atau naikkan "
            "MAX_CLOUD (atau PLATFORM_PREFIX=None untuk semua satelit).")

    best = None
    for cc, when, sid in cand[:MAX_TRIES]:
        data, epsg = download_scene(token, when)
        frac = valid_fraction(data)
        log(f"  {sid[:40]}... | {when} | awan tile {cc:.1f}% | piksel valid {frac:.1%}")
        if best is None or frac > best["frac"]:
            best = dict(frac=frac, data=data, when=when, sid=sid, cc=cc, epsg=epsg)
        if frac >= MIN_VALID:
            break

    TIF_IN.write_bytes(best["data"])
    INFO_TXT.write_text(
        f"Scene    : {best['sid']}\nAkuisisi : {best['when']}\n"
        f"Awan tile: {best['cc']:.1f}%\nPiksel valid di AOI: {best['frac']:.1%}\n"
        f"CRS      : EPSG:{best['epsg']}\nResolusi : 10 m\n"
        f"Band     : {', '.join(BAND_NAMES)} (reflektansi 0-1)\n"
        f"Masking awan (SCL): {MASK_CLOUD}\n", encoding="utf-8")
    log(f"Scene dipakai: {best['sid']} ({best['when']}), valid {best['frac']:.1%}")
    log("Tersimpan:", TIF_IN, "dan", INFO_TXT)


if TIF_IN.exists():
    log(f"{TIF_IN.name} sudah ada -> langkah unduh dilewati.")
else:
    fetch_sentinel2a()

# %% [4] BACA CITRA ------------------------------------------------------------
with rasterio.open(TIF_IN) as src:
    stack = src.read().astype("float32")
    crs, transform = src.crs, src.transform
if stack.shape[0] != len(BAND_NAMES):
    raise SystemExit(f"TIF punya {stack.shape[0]} band, harus {len(BAND_NAMES)} "
                     f"({', '.join(BAND_NAMES)}).")
invalid = np.all(stack == 0, axis=0) | ~np.isfinite(stack).all(axis=0)
stack[:, invalid] = np.nan
H, W = stack.shape[1:]
log(f"Ukuran citra: {W} x {H} piksel | CRS: {crs} | piksel tanpa data: {invalid.mean():.1%}")
B = dict(zip(BAND_NAMES, stack))

# %% [5] FITUR: band + indeks spektral -----------------------------------------
def nd(a, b):
    return (a - b) / (a + b + 1e-10)

ndvi = nd(B["B08"], B["B04"])
ndwi = nd(B["B03"], B["B08"])
ndbi = nd(B["B11"], B["B08"])
evi = 2.5 * (B["B08"] - B["B04"]) / (B["B08"] + 6 * B["B04"] - 7.5 * B["B02"] + 1)

feats = np.concatenate([stack, np.stack([ndvi, ndwi, ndbi, evi])]).astype("float32")
FEATURE_NAMES = BAND_NAMES + ["NDVI", "NDWI", "NDBI", "EVI"]
F = feats.shape[0]

# %% [6] RASTERISASI POLIGON SAMPEL --------------------------------------------
poly_label, shapes, pid = {}, [], 0
for geoms, kelas in ((geoms_non, 0), (geoms_sawah, 1)):
    for g in geoms:
        pid += 1
        poly_label[pid] = kelas
        shapes.append((transform_geom("EPSG:4326", crs, g), pid))

poly_raster = features.rasterize(shapes, out_shape=(H, W), transform=transform,
                                 fill=0, dtype="int32")
labeled = (poly_raster > 0) & np.isfinite(feats).all(axis=0)
present = np.unique(poly_raster[labeled])

for k, nama in ((0, "non-sawah"), (1, "sawah")):
    ids = [p for p in present if poly_label[p] == k]
    npx = int(np.isin(poly_raster, ids).sum())
    log(f"Kelas {k} ({nama}): {len(ids)} poligon terpakai, {npx} piksel bebas awan")
if len(present) < len(poly_label):
    log(f"PERINGATAN: {len(poly_label) - len(present)} poligon tidak punya piksel valid "
        "(tertutup awan atau di luar citra).")

# %% [7] SPLIT PER POLIGON (hindari data leakage spasial) ----------------------
rng = np.random.default_rng(SEED)
train_ids = []
for k in (0, 1):
    ids = [p for p in present if poly_label[p] == k]
    rng.shuffle(ids)
    train_ids += ids[:max(1, int(round(len(ids) * TRAIN_FRAC)))]

m_train = labeled & np.isin(poly_raster, train_ids)
m_test = labeled & ~m_train
lab_map = np.zeros(poly_raster.max() + 1, dtype="uint8")
for p, k in poly_label.items():
    lab_map[p] = k

X_train, y_train = feats[:, m_train].T, lab_map[poly_raster[m_train]]
X_test, y_test = feats[:, m_test].T, lab_map[poly_raster[m_test]]
log(f"Poligon training: {len(train_ids)} | testing: {len(present) - len(train_ids)}")
log(f"Piksel training: {len(y_train)} | testing: {len(y_test)}")

# %% [8] LATIH & EVALUASI ------------------------------------------------------
rf = RandomForestClassifier(n_estimators=N_TREES, random_state=SEED, n_jobs=-1)
rf.fit(X_train, y_train)
pred_test = rf.predict(X_test)

log("\nConfusion matrix (baris=aktual, kolom=prediksi; urutan 0=non-sawah, 1=sawah):")
log(confusion_matrix(y_test, pred_test, labels=[0, 1]))
log(f"Overall Accuracy : {accuracy_score(y_test, pred_test):.4f}")
log(f"Kappa            : {cohen_kappa_score(y_test, pred_test):.4f}")
log(classification_report(y_test, pred_test, labels=[0, 1],
                          target_names=["non-sawah", "sawah"], digits=3))
log("Kepentingan fitur:")
for n, v in sorted(zip(FEATURE_NAMES, rf.feature_importances_), key=lambda x: -x[1]):
    log(f"  {n:5s} {v:.3f}")

# %% [9] KLASIFIKASI SELURUH CITRA ---------------------------------------------
# Model akhir dilatih ulang dengan SEMUA sampel; akurasi di atas tetap dari data uji.
rf_final = RandomForestClassifier(n_estimators=N_TREES, random_state=SEED, n_jobs=-1)
rf_final.fit(feats[:, labeled].T, lab_map[poly_raster[labeled]])

flat = feats.reshape(F, -1).T
ok = np.isfinite(flat).all(axis=1)
pred = np.full(flat.shape[0], 255, dtype="uint8")
pred[ok] = rf_final.predict(flat[ok]).astype("uint8")
classified = pred.reshape(H, W)

if crs.is_projected:
    px_area = abs(transform.a * transform.e)
    log(f"\nLuas sawah    : {(classified == 1).sum() * px_area / 10000:.1f} ha")
    log(f"Luas non-sawah: {(classified == 0).sum() * px_area / 10000:.1f} ha")

# %% [10] SIMPAN GEOTIFF, PNG, DAN RINGKASAN -----------------------------------
with rasterio.open(OUT_TIF, "w", driver="GTiff", height=H, width=W, count=1,
                   dtype="uint8", crs=crs, transform=transform,
                   nodata=255, compress="lzw") as dst:
    dst.write(classified, 1)
    dst.set_band_description(1, "kelas (1=sawah, 0=non-sawah)")
    dst.write_colormap(1, {0: (215, 25, 28, 255), 1: (26, 150, 65, 255),
                           255: (0, 0, 0, 0)})

rgb = np.dstack([B["B04"], B["B03"], B["B02"]])
lo, hi = np.nanpercentile(rgb, 2), np.nanpercentile(rgb, 98)
rgb = np.nan_to_num(np.clip((rgb - lo) / (hi - lo + 1e-10), 0, 1))

fig, ax = plt.subplots(1, 2, figsize=(13, 6))
ax[0].imshow(rgb)
ax[0].set_title("Sentinel-2A (RGB)")
ax[1].imshow(np.ma.masked_equal(classified, 255),
             cmap=ListedColormap(["#d7191c", "#1a9641"]), vmin=0, vmax=1,
             interpolation="nearest")
ax[1].set_title("Klasifikasi (hijau = sawah, merah = non-sawah)")
for a in ax:
    a.axis("off")
plt.tight_layout()
plt.savefig(OUT_PNG, dpi=150)

OUT_TXT.write_text("\n".join(LOG), encoding="utf-8")
log("\nSelesai. Output:")
log("  GeoTIFF  :", OUT_TIF)
log("  Pratinjau:", OUT_PNG)
log("  Evaluasi :", OUT_TXT)