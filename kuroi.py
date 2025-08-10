# kuroi_navigator_lengkap_v2.py - Versi Final
# Program navigator berbasis suara untuk kacamata pintar tunanetra.

import requests
import json
import gps
import azure.cognitiveservices.speech as speechsdk
import time
import requests.utils
import re

# --- BAGIAN 1: FUNGSI-FUNGSI INTI ---

def speak_text(text_to_speak, speech_key, speech_region):
    try:
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        speech_config.speech_synthesis_voice_name = 'id-ID-GadisNeural'
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        print(f"SPEAKING: \"{text_to_speak}\"")
        result = speech_synthesizer.speak_text_async(text_to_speak).get()
        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Sintesis suara dibatalkan: {cancellation_details.reason.name}")
    except Exception as e:
        print(f"Error pada fungsi speak_text: {e}")

def get_location_from_ip():
    print("Mencoba mendapatkan lokasi dari IP Geolocation...")
    try:
        response = requests.get("https://ipinfo.io/json", timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'loc' in data:
            print(f"Sukses! Lokasi IP terdeteksi di {data['loc']}")
            return data['loc']
        return None
    except Exception as e:
        print(f"Gagal mendapatkan lokasi dari IP. Error: {e}")
        return None

def get_best_available_location():
    """Menggunakan IP Geolocation sebagai sumber lokasi utama."""
    print("\nMenggunakan IP Geolocation sebagai sumber lokasi utama.")
    location = get_location_from_ip()
    return location

def cari_poi_dengan_nama(nama_tempat, maps_key, lat_konteks, lon_konteks):
    print(f"\nMencari POI untuk '{nama_tempat}' via Azure Fuzzy Search...")
    try:
        url = (f"https://atlas.microsoft.com/search/fuzzy/json?api-version=1.0"
               f"&query={requests.utils.quote(nama_tempat)}&subscription-key={maps_key}"
               f"&lat={lat_konteks}&lon={lon_konteks}&limit=1")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('results'):
            result = data['results'][0]
            pos = result['position']
            coord_str = f"{pos['lat']},{pos['lon']}"
            print(f"POI ditemukan: '{result.get('poi', {}).get('name', nama_tempat)}' di koordinat {coord_str}")
            return coord_str
        return None
    except requests.exceptions.RequestException:
        return None

def get_pedestrian_route_with_instructions(start_lat_lon, end_lat_lon, maps_key, speech_key, speech_region):
    """Menghitung rute, lalu menampilkan dan mengucapkan setiap instruksi."""
    try:
        query_coords = f"{start_lat_lon}:{end_lat_lon}"
        url = f"https://atlas.microsoft.com/route/directions/json?api-version=1.0&query={query_coords}&travelMode=pedestrian&instructionsType=text&language=id-ID&subscription-key={maps_key}"
        print("\nMenghitung rute pejalan kaki...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if data.get('routes'):
            route = data['routes'][0]
            summary = route['summary']
            summary_text = (f"Rute ditemukan. Jarak total {summary['lengthInMeters'] / 1000:.1f} kilometer, "
                            f"dengan perkiraan waktu tempuh {summary['travelTimeInSeconds'] / 60:.0f} menit.")
            print(f"\n--- RANGKUMAN ---\n{summary_text}\n-------------------\n")
            speak_text(summary_text, speech_key, speech_region)
            time.sleep(1)
            print("PETUNJUK ARAH:")
            
            if route.get('guidance') and route['guidance'].get('instructions'):
                instructions = route['guidance']['instructions']
                
                for i, step in enumerate(instructions):
                    message = step.get('message', 'Instruksi tidak tersedia')
                    distance = 0
                    
                    if i + 1 < len(instructions):
                        current_offset = step.get('routeOffsetInMeters', 0)
                        next_offset = instructions[i+1].get('routeOffsetInMeters', 0)
                        distance = next_offset - current_offset
                    
                    unit = "meter"
                    full_instruction_text = f"{message} ({distance} {unit})"
                    
                    if i == 0 and "berangkat" in message.lower():
                        full_instruction_text = f"Mulai dengan berjalan lurus sejauh {distance} {unit}"
                    elif i == len(instructions) - 1:
                        full_instruction_text = "Anda telah sampai di tujuan."

                    print(f"{i+1}. {full_instruction_text}")
                    speak_text(full_instruction_text, speech_key, speech_region)
                    time.sleep(1) 

            return route
    except Exception as e:
        print(f"Error di get_pedestrian_route_with_instructions: {e}")
        return None

def muat_kamus_lokasi(file_path='kamus_lokasi.json'):
    try:
        with open(file_path, 'r') as f: return json.load(f)
    except Exception: return {}

def cari_nama_panjang_dari_kamus(nama_panggilan, kamus):
    return kamus.get(nama_panggilan.lower())

def recognize_from_microphone(speech_key, speech_region):
    """Mendengarkan perintah dari mikrofon dan mengubahnya menjadi teks."""
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language="id-ID"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    print("\nSilakan berbicara ke mikrofon...")
    speak_text("Silakan sebutkan tujuan anda", speech_key, speech_region)
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Saya mendengar: \"{speech_recognition_result.text}\"")
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        speak_text("Maaf, saya tidak mendengar apapun.", speech_key, speech_region)
        return None
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print(f"Sintesis suara dibatalkan. Alasan: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error Code: {cancellation_details.error_code}")
            print(f"Error Details: {cancellation_details.error_details}")
            speak_text("Maaf, terjadi masalah saat terhubung ke layanan.", speech_key, speech_region)
        return None
    return None

# --- BAGIAN 2: PROGRAM UTAMA ---
if __name__ == "__main__":
    try:
        # Muat semua kredensial
        with open("maps_api.txt", "r") as f: maps_key = f.read().strip()
        with open("speech_api.txt", "r") as f:
            speech_key = f.readline().strip()
            speech_region = f.readline().strip()
        
        kamus_lokasi = muat_kamus_lokasi()
        print("Kunci API dan kamus berhasil dimuat.")

        input_pengguna_suara = recognize_from_microphone(speech_key, speech_region)
        
        if input_pengguna_suara:
            raw_start_coords = get_best_available_location()

            if raw_start_coords:
                nama_panggilan_tujuan = None
                for kunci in kamus_lokasi:
                    if kunci in input_pengguna_suara.lower():
                        nama_panggilan_tujuan = kunci
                        break
                
                if nama_panggilan_tujuan is None:
                    nama_panggilan_tujuan = input_pengguna_suara.lower()

                nama_lengkap_tujuan = cari_nama_panjang_dari_kamus(nama_panggilan_tujuan, kamus_lokasi)
                
                if nama_lengkap_tujuan is None:
                    nama_lengkap_tujuan = nama_panggilan_tujuan
                
                start_lat, start_lon = raw_start_coords.split(',')
                clean_dest_coords = cari_poi_dengan_nama(nama_lengkap_tujuan, maps_key, start_lat, start_lon)
                if clean_dest_coords:
                    get_pedestrian_route_with_instructions(raw_start_coords, clean_dest_coords, maps_key, speech_key, speech_region)
    except FileNotFoundError as e:
        print(f"CRITICAL ERROR: File API tidak ditemukan. Pastikan 'maps_api.txt' dan 'speech_api.txt' ada. Detail: {e}")
    except Exception as e:
        print(f"CRITICAL ERROR: Terjadi error tak terduga di program utama: {e}")
