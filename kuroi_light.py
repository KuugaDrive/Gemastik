# kuroi_light.py - Versi Final (Perbaikan Format Koordinat) 2025-08-09

import requests

def get_routable_location(lat_lon_str, subscription_key):
    """
    Langkah 1: Mengambil koordinat mentah dan menemukan lokasi/jalan terdekat
    yang dapat dirutekan. Mengembalikan string "latitude,longitude".
    """
    print(f"Mencari jalan terdekat untuk koordinat: {lat_lon_str}...")
    try:
        url = (f"https://atlas.microsoft.com/search/address/reverse/json"
               f"?api-version=1.0"
               f"&query={lat_lon_str}"  # Langsung gunakan format "lat,lon"
               f"&subscription-key={subscription_key}")
               
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('addresses'):
            position_str = data['addresses'][0]['position']
            print(f"Jalan terdekat ditemukan di: {position_str}")
            return position_str
        else:
            print("Tidak bisa menemukan jalan terdekat.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error saat mencari jalan terdekat: {e}")
        return None

def get_pedestrian_route_with_instructions(start_lat_lon, end_lat_lon, subscription_key):
    """
    Langkah 2: Menghitung rute pejalan kaki lengkap dengan instruksi.
    """
    if not all([start_lat_lon, end_lat_lon, subscription_key]):
        print("Error: Informasi tidak lengkap untuk menghitung rute.")
        return None
    try:
        # --- PERBAIKAN FINAL: Gunakan format "lat,lon" secara langsung ---
        query_coords = f"{start_lat_lon}:{end_lat_lon}"

        url = (f"https://atlas.microsoft.com/route/directions/json"
               f"?api-version=1.0"
               f"&query={query_coords}"
               f"&travelMode=pedestrian"
               f"&instructionsType=text"   # Mengembalikan parameter instruksi
               f"&subscription-key={subscription_key}")

        print("\nMenghitung rute pejalan kaki dengan instruksi...")
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            print(f"Error: Menerima status {response.status_code}")
            print(f"Pesan dari server: {response.text}")
            response.raise_for_status()

        data = response.json()

        if data.get('routes'):
            route = data['routes'][0]
            summary = route['summary']
            
            distance_km = summary['lengthInMeters'] / 1000
            duration_min = summary['travelTimeInSeconds'] / 60
            
            print(f"\n--- Rute Pejalan Kaki Ditemukan ---")
            print(f"Jarak      : {distance_km:.2f} km")
            print(f"Waktu Tempuh: {duration_min:.0f} menit")
            print("------------------------------------")
            
            print("\nPETUNJUK ARAH:")
            if route.get('guidance') and route['guidance'].get('instructions'):
                for i, step in enumerate(route['guidance']['instructions']):
                    print(f"{i+1}. {step['message']}")
            else:
                print("Instruksi detail tidak tersedia.")
            
            return route
        else:
            print("Tidak ada rute pejalan kaki yang ditemukan.")
            return None
            
    except requests.exceptions.RequestException:
        print(f"\nTerjadi error saat menghubungi Azure Maps. Silakan periksa detail di atas.")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error saat mem-parsing respons rute: {e}")
        return None

# --- Program Utama ---
if __name__ == "__main__":
    try:
        with open("maps_api.txt", "r") as f:
            azure_key = f.read().strip()

        # Gunakan format "latitude,longitude" secara konsisten
        raw_start_coords = "-6.1750,106.8275"
        destination_coords = "-6.234727,106.747345"

        # Langkah 1: Dapatkan titik awal yang bersih
        clean_start_coords = get_routable_location(raw_start_coords, azure_key)
        
        if clean_start_coords:
            # Langkah 2: Hitung rute menggunakan koordinat yang sudah bersih
            # Tidak perlu lagi membolak-balik urutan lat/lon
            get_pedestrian_route_with_instructions(clean_start_coords, destination_coords, azure_key)

    except FileNotFoundError:
        print("Error: Pastikan file 'maps_api.txt' ada dan berisi kunci Azure Maps Anda.")
    except Exception as e:
        print(f"Terjadi error tak terduga: {e}")
