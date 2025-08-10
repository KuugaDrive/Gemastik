import gps
import time

# Membuat sesi koneksi ke daemon gpsd
# gpsd biasanya berjalan di localhost port 2947
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

print("Mencari sinyal GPS... (Tekan Ctrl+C untuk berhenti)")

try:
    while True:
        # Ambil laporan data terbaru dari gpsd
        report = session.next()

        # TPV (Time-Position-Velocity) adalah jenis laporan yang berisi data lokasi
        if report['class'] == 'TPV':
            if hasattr(report, 'time'):
                print(f"Waktu       : {report.time}")
            if hasattr(report, 'lat'):
                print(f"Latitude    : {report.lat}")
            if hasattr(report, 'lon'):
                print(f"Longitude   : {report.lon}")
            if hasattr(report, 'speed'):
                # Konversi dari meter/detik ke km/jam
                speed_kmh = report.speed * 3.6
                print(f"Kecepatan   : {speed_kmh:.2f} km/jam")
            if hasattr(report, 'alt'):
                print(f"Altitude    : {report.alt} meter")

            print("-" * 20)

        time.sleep(3) # Tunggu 3 detik sebelum mengambil data lagi

except KeyboardInterrupt:
    print("Program dihentikan.")
except Exception as e:
    print(f"Terjadi error: {e}")