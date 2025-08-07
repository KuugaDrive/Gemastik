import geocoder

def get_coordinates():
    try:
        # Menggunakan IP publik untuk mendapatkan lokasi
        g = geocoder.ip('me')

        # Memeriksa apakah lokasi ditemukan
        if g.ok:
            latitude = g.latlng[0]
            longitude = g.latlng[1]

            print("Koordinat perangkat Anda:")
            print(f"Lintang (Latitude): {latitude}")
            print(f"Bujur (Longitude): {longitude}")
        else:
            print("Gagal mendapatkan koordinat. Pastikan Anda terhubung ke internet.")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    get_coordinates()