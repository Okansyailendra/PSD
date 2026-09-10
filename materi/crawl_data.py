import pandas as pd
from shapely.geometry import Polygon
import openeo

geojson_coords = [
    [112.6124555, -7.1337934],
    [112.6033317, -7.1496527],
    [112.6203805, -7.1596966],
    [112.63683, -7.1370975],
    [112.6124555, -7.1337934],
]

area_polygon = Polygon(geojson_coords)
centroid_lon = area_polygon.centroid.x
centroid_lat = area_polygon.centroid.y
print(f"Titik Pusat Penarikan Data -> Latitude: {centroid_lat:.5f}, Longitude: {centroid_lon:.5f}")

print("Menghubungkan ke OpenEO CDSE...")
connection = openeo.connect("https://openeo.dataspace.copernicus.eu")
connection.authenticate_oidc()
print("Koneksi berhasil.")
start_date = "2025-08-31"
end_date = "2026-08-31"

# PENTING: spatial_extent di load_collection() harus berupa bounding box
# (bukan Polygon penuh), sedangkan geometries di aggregate_spatial() memakai
# poligon presisi asli. Bounding box dihitung otomatis dari area_polygon.
west, south, east, north = area_polygon.bounds
spatial_extent = {"west": west, "south": south, "east": east, "north": north}
geometries = {"type": "Polygon", "coordinates": [geojson_coords]}

daftar_band = ["NO2", "CO", "O3"]
hasil_per_gas = {}

for band in daftar_band:
    print(f"\nMemuat & menarik data Sentinel-5P untuk band: {band} ...")

    datacube = connection.load_collection(
        "SENTINEL_5P_L2",
        spatial_extent=spatial_extent,
        temporal_extent=[start_date, end_date],
        bands=[band],
    )

    timeseries = datacube.aggregate_spatial(
        geometries=geometries,
        reducer="mean",
    )

    # Batch job asinkron (bukan execute() sinkron) karena rentang 1 tahun
    # berisiko timeout kalau diproses secara synchronous.
    job = timeseries.create_job(out_format="JSON", title=f"Manyar_{band.lower()}")
    job.start_and_wait()

    results = job.get_results()
    hasil_per_gas[band] = results.get_asset().load_json()

    print(f"Data band {band} berhasil ditarik! ({len(hasil_per_gas[band])} entri tanggal)")

print("\nSemua band (NO2, CO, O3) berhasil ditarik dari OpenEO.")

# Konversi JSON -> DataFrame per gas, lalu gabungkan jadi satu DataFrame

def json_ke_dataframe(data_json, nama_kolom):
    """Mengubah hasil JSON aggregate_spatial (satu band) menjadi DataFrame [time, nama_kolom]."""
    records = []
    for date_str, values in data_json.items():
        if len(values) > 0 and len(values[0]) >= 1:
            records.append({"time": date_str, nama_kolom: values[0][0]})
    df_hasil = pd.DataFrame(records)
    if not df_hasil.empty:
        df_hasil["time"] = pd.to_datetime(df_hasil["time"]).dt.tz_localize(None)
    return df_hasil


df_no2 = json_ke_dataframe(hasil_per_gas["NO2"], "NO2")
df_co = json_ke_dataframe(hasil_per_gas["CO"], "CO")
df_o3 = json_ke_dataframe(hasil_per_gas["O3"], "O3")

print(f"\nJumlah baris -> NO2: {len(df_no2)}, CO: {len(df_co)}, O3: {len(df_o3)}")

# outer join supaya tanggal yang datanya hilang di salah satu gas tetap
# tercatat (nanti diisi NaN & diinterpolasi di notebook perhitungan.md)
df = df_no2.merge(df_co, on="time", how="outer").merge(df_o3, on="time", how="outer")
df = df.sort_values("time").reset_index(drop=True)


csv_filename = "polutan_Manyar_2025_2026.csv"
df.to_csv(csv_filename, index=False)
print(f"\nData mentah disimpan ke: {csv_filename}")
print("Selesai! File CSV ini siap dipakai di perhitungan.md.")