import requests
import json

def get_location_from_ip():
    """
    Mengambil data geolokasi berdasarkan alamat IP publik.
    """
    try:
        # URL ke layanan IP Geolocation (ipinfo.io tidak butuh API key untuk penggunaan dasar)
        url = "https://ipinfo.io/json"
        
        print("Mencari lokasi berdasarkan alamat IP publik...")
        
        # Mengirim permintaan GET ke server
        response = requests.get(url, timeout=5) # Timeout 5 detik
        
        # Memeriksa apakah permintaan berhasil (status code 200)
        response.raise_for_status()
        
        # Mengubah respons JSON menjadi dictionary Python
        data = response.json()
        
        # Ekstrak data yang kita inginkan
        ip = data.get('ip')
        city = data.get('city', 'N/A')
        region = data.get('region', 'N/A')
        country = data.get('country', 'N/A')
        # Koordinat dalam format "latitude,longitude"
        loc = data.get('loc', 'N/A,N/A').split(',')
        
        latitude = loc[0]
        longitude = loc[1]
        
        # Tampilkan hasil
        print("\n--- Hasil Geolokasi IP ---")
        print(f"Alamat IP: {ip}")
        print(f"Kota     : {city}, {region}, {country}")
        print(f"Koordinat: Latitude={latitude}, Longitude={longitude}")
        print("--------------------------")
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "city": city
        }

    except requests.exceptions.RequestException as e:
        print(f"Terjadi error saat menghubungi layanan geolokasi: {e}")
        return None
    except json.JSONDecodeError:
        print("Gagal mem-parsing respons dari server.")
        return None

if __name__ == "__main__":
    location_data = get_location_from_ip()
    
    if location_data:
        print("\nData berhasil didapatkan dan bisa digunakan di program utama.")
    else:
        print("\nGagal mendapatkan data lokasi.")