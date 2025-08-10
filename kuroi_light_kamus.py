# kuroi_light_final_v5.py - Dengan Output Instruksi Pertama yang Lebih Jelas

import requests
import json

# ... (Semua fungsi lain seperti get_routable_location, cari_poi_dengan_nama, dll tetap sama persis)
def get_routable_location(lat_lon_str, subscription_key):
    print(f"Mencari jalan terdekat untuk koordinat awal: {lat_lon_str}...")
    try:
        url = f"https://atlas.microsoft.com/search/address/reverse/json?api-version=1.0&query={lat_lon_str}&subscription-key={subscription_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('addresses'):
            position_str = data['addresses'][0]['position']
            print(f"Jalan terdekat untuk titik awal ditemukan di: {position_str}")
            return position_str
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None

def cari_poi_dengan_nama(nama_tempat, subscription_key, lat_konteks, lon_konteks):
    print(f"\nMencari POI untuk '{nama_tempat}' via Azure Fuzzy Search...")
    try:
        url = (f"https://atlas.microsoft.com/search/fuzzy/json"
               f"?api-version=1.0&query={requests.utils.quote(nama_tempat)}"
               f"&subscription-key={subscription_key}&lat={lat_konteks}&lon={lon_konteks}&limit=1")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('results'):
            result = data['results'][0]
            pos = result['position']
            coord_str = f"{pos['lat']},{pos['lon']}"
            print(f"POI ditemukan: '{result.get('poi', {}).get('name', nama_tempat)}' di koordinat {coord_str}")
            return coord_str
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None


# --- HANYA FUNGSI INI YANG BERUBAH ---
def get_pedestrian_route_with_instructions(start_lat_lon, end_lat_lon, subscription_key):
    """
    Menghitung rute pejalan kaki dengan instruksi dan jarak yang dihitung
    dan membuat instruksi pertama lebih jelas.
    """
    try:
        query_coords = f"{start_lat_lon}:{end_lat_lon}"
        url = (f"https://atlas.microsoft.com/route/directions/json"
               f"?api-version=1.0&query={query_coords}&travelMode=pedestrian"
               f"&instructionsType=text&language=id-ID&subscription-key={subscription_key}")

        print("\nMenghitung rute pejalan kaki dengan instruksi (Bahasa Indonesia)...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('routes'):
            route = data['routes'][0]
            summary = route['summary']
            print(f"\n--- Rute Pejalan Kaki Ditemukan ---")
            print(f"Jarak Total  : {summary['lengthInMeters'] / 1000:.2f} km")
            print(f"Waktu Tempuh : {summary['travelTimeInSeconds'] / 60:.0f} menit")
            print("------------------------------------")
            print("\nPETUNJUK ARAH:")
            
            if route.get('guidance') and route['guidance'].get('instructions'):
                instructions = route['guidance']['instructions']
                
                for i, step in enumerate(instructions):
                    message = step.get('message', 'Instruksi tidak tersedia')
                    distance = 0
                    
                    if i + 1 < len(instructions):
                        current_offset = step.get('routeOffsetInMeters', 0)
                        next_offset = instructions[i+1].get('routeOffsetInMeters', 0)
                        distance = next_offset - current_offset
                    
                    # --- PERUBAHAN LOGIKA PRESENTASI ---
                    # Jika ini adalah langkah pertama (i == 0) dan pesannya "Berangkat"
                    if i == 0 and "berangkat" in message.lower():
                        # Ganti pesan menjadi lebih deskriptif
                        print(f"1. Mulai dengan berjalan lurus sejauh {distance}m")
                    else:
                        # Untuk semua langkah lain, gunakan format biasa
                        print(f"{i+1}. {message} ({distance}m)")
            return route
        else:
            print("Tidak ada rute yang ditemukan antara dua titik tersebut.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Terjadi error saat menghubungi Azure Maps: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error saat mem-parsing respons rute: '{e}'")
        return None

# --- Fungsi-fungsi lainnya tetap sama ---
def muat_kamus_lokasi(file_path='kamus_lokasi.json'):
    try:
        with open(file_path, 'r') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}
def cari_nama_panjang_dari_kamus(nama_panggilan, kamus):
    return kamus.get(nama_panggilan.lower())

# --- Program Utama (tidak ada perubahan di sini) ---
if __name__ == "__main__":
    try:
        with open("maps_api.txt", "r") as f: azure_key = f.read().strip()
        kamus_lokasi = muat_kamus_lokasi()
        
        input_pengguna = "aku ingin ke rumah"
        nama_panggilan_tujuan = input_pengguna.replace("aku ingin ke ", "").strip()
        print(f"\nPengguna ingin pergi ke: '{nama_panggilan_tujuan}'")

        nama_lengkap_tujuan = cari_nama_panjang_dari_kamus(nama_panggilan_tujuan, kamus_lokasi)

        if nama_lengkap_tujuan:
            print(f"Nama lengkap tujuan dari kamus: '{nama_lengkap_tujuan}'")
            raw_start_coords = "-6.1750,106.8275"
            clean_start_coords = get_routable_location(raw_start_coords, azure_key)

            if clean_start_coords:
                start_lat, start_lon = clean_start_coords.split(',')
                clean_dest_coords = cari_poi_dengan_nama(nama_lengkap_tujuan, azure_key, start_lat, start_lon)

                if clean_dest_coords:
                    get_pedestrian_route_with_instructions(clean_start_coords, clean_dest_coords, azure_key)
    except Exception as e:
        print(f"Terjadi error tak terduga: {e}")