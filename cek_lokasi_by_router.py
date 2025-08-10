# cek_lokasi_ip.py
# Tujuan: Program mandiri untuk mengecek dan menampilkan lokasi
#         berdasarkan alamat IP publik saat ini.

import requests
import json

def cek_lokasi_via_ip():
    """
    Menghubungi layanan IP Geolocation dan menampilkan hasilnya.
    """
    # URL ke layanan gratis ipinfo.io
    url = "https://ipinfo.io/json"
    
    print("Mencoba mendeteksi lokasi Anda berdasarkan alamat IP...")
    
    try:
        # Mengirim permintaan ke server dengan timeout 10 detik
        response = requests.get(url, timeout=10)
        
        # Jika ada error jaringan atau server, hentikan program
        response.raise_for_status()
        
        # Ubah data JSON dari server menjadi format yang bisa dibaca Python
        data = response.json()
        
        # Ekstrak semua informasi yang relevan
        ip_address = data.get('ip', 'Tidak tersedia')
        city = data.get('city', 'Tidak tersedia')
        region = data.get('region', 'Tidak tersedia')
        country = data.get('country', 'Tidak tersedia')
        coordinates = data.get('loc', 'Tidak tersedia')
        isp = data.get('org', 'Tidak tersedia')
        
        # Tampilkan hasil dengan format yang rapi
        print("\n--- LOKASI TERDETEKSI ---")
        print(f"Alamat IP       : {ip_address}")
        print(f"Provider (ISP)  : {isp}")
        print(f"Kota            : {city}")
        print(f"Wilayah         : {region}")
        print(f"Negara          : {country}")
        print(f"Koordinat (lat,lon): {coordinates}")
        print("--------------------------")
        
    except requests.exceptions.RequestException as e:
        print(f"\nError: Gagal terhubung ke layanan lokasi.")
        print(f"Pastikan Anda terhubung ke internet.")
        print(f"Detail error teknis: {e}")
    except json.JSONDecodeError:
        print("\nError: Gagal membaca respons dari server. Coba lagi nanti.")
    except Exception as e:
        print(f"Terjadi error tak terduga: {e}")

# --- Jalankan program utama ---
if __name__ == "__main__":
    cek_lokasi_via_ip()