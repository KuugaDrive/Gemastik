# navigator.py
# Program navigator berbasis suara untuk Raspberry Pi yang menggunakan modul GPS.
# Program ini menggunakan Azure Speech SDK untuk input/output suara,
# modul GPS untuk mendapatkan lokasi, dan OpenStreetMap Nominatim/OSRM untuk rute.

# Pastikan Anda telah menginstal pustaka berikut:
# pip install azure-cognitiveservices-speech pyserial pynmea2 requests geocoder

import azure.cognitiveservices.speech as speechsdk
import time
import re
import requests
import geocoder # Tambahkan geocoder untuk fallback
import serial
import pynmea2

# Konfigurasi API
try:
    with open("speech_api.txt", "r") as f:
        AZURE_SPEECH_KEY = f.read().strip()
    AZURE_SERVICE_REGION = "southeastasia"
except FileNotFoundError:
    print("Error: File 'api.txt' tidak ditemukan. Pastikan file tersebut ada dan berisi kunci API.")
    exit()

# Konfigurasi Azure Speech
speech_config = speechsdk.SpeechConfig(
    subscription=AZURE_SPEECH_KEY,
    region=AZURE_SERVICE_REGION
)
speech_config.speech_recognition_language = "id-ID"
speech_config.speech_synthesis_voice_name = "id-ID-GadisNeural"

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
audio_config = speechsdk.AudioConfig(use_default_microphone=True)
recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config,
    audio_config=audio_config
)

# Variabel untuk menyimpan status navigasi
current_route = []
current_step_index = 0
done = False

# Konfigurasi port serial untuk modul GPS
# Sesuaikan port ini jika modul GPS Anda terhubung ke port lain.
# Contoh lain: '/dev/ttyAMA0'
SERIAL_PORT = '/dev/serial0' 
BAUD_RATE = 9600

def respond(text):
    """
    Menyuarakan teks yang diberikan dan mencetaknya ke konsol.
    """
    print(f"Mikasa: {text}")
    result = speech_synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.Canceled:
        print("Gagal menyuarakan teks.")

def get_current_location():
    """
    Mendapatkan koordinat lintang dan bujur dari modul GPS (fallback ke IP jika gagal).
    """
    respond("Mendapatkan lokasi saat ini, mohon tunggu...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        start_time = time.time()
        while time.time() - start_time < 30: # Coba selama 30 detik untuk mendapatkan sinyal GPS
            line = ser.readline().decode('ascii', errors='ignore')
            if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                try:
                    msg = pynmea2.parse(line)
                    if msg.gps_qual > 0: # Cek apakah ada sinyal GPS
                        lat = msg.latitude
                        lon = msg.longitude
                        print(f"Lokasi GPS ditemukan: Lintang={lat}, Bujur={lon}")
                        ser.close()
                        return [lat, lon]
                except pynmea2.ParseError as e:
                    print(f"Gagal memparsing NMEA: {e}")
        
        ser.close()
        print("Timeout: Gagal mendapatkan lokasi GPS.")
        raise serial.SerialException("Gagal membaca dari port serial.")
        
    except serial.SerialException as e:
        print(f"Error mengakses port serial: {e}. Mencoba mendapatkan lokasi dari IP.")
        # Fallback ke geocoder.ip jika GPS gagal
        g = geocoder.ip('me')
        if g.ok:
            lat, lon = g.latlng
            print(f"Lokasi IP ditemukan: Lintang={lat}, Bujur={lon}")
            return [lat, lon]
        else:
            print("Gagal mendapatkan lokasi dari IP. Menggunakan koordinat default (Jakarta).")
            return [-6.2088, 106.8456]

def get_coordinates_from_query(query):
    """
    Mengubah nama tempat menjadi koordinat menggunakan Nominatim.
    """
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={requests.utils.quote(query)}"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            return None
    except Exception as e:
        print(f"Error geocoding: {e}")
        return None

def get_route(start_coords, end_coords):
    """
    Mendapatkan petunjuk rute dari Open Source Routing Machine (OSRM).
    """
    profile = "driving" # driving, cycling, or walking
    url = f"http://router.project-osrm.org/route/v1/{profile}/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&steps=true"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['code'] == 'Ok':
            return data['routes'][0]['legs'][0]['steps']
        else:
            return None
    except Exception as e:
        print(f"Error getting route: {e}")
        return None

def recognized_handler(evt):
    """
    Menangani hasil ucapan yang dikenali.
    """
    global done, current_route, current_step_index
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        original_text = evt.result.text
        text = original_text.lower()
        print(f"Anda: {original_text}")

        # Perintah untuk keluar
        if "keluar" in text or "selesai" in text or "berhenti navigasi" in text:
            respond("Baik, navigasi dihentikan. Sampai jumpa.")
            current_route = []
            done = True
            return

        # Perintah untuk mulai navigasi
        # Pola regex yang lebih fleksibel untuk berbagai variasi perintah
        match_start_nav = re.search(r"(mulai navigasi ke|aku ingin pergi ke|bawa aku ke) (.+)", text)
        if match_start_nav:
            destination = match_start_nav.group(2).strip()
            
            start_coords = get_current_location() # Mendapatkan lokasi dari GPS
            
            if start_coords:
                respond(f"Lokasi saat ini ditemukan. Mencari rute ke {destination}, mohon tunggu.")
                end_coords = get_coordinates_from_query(destination)
                
                if end_coords:
                    route_steps = get_route(start_coords, end_coords)
                    if route_steps:
                        current_route = route_steps
                        current_step_index = 0
                        respond(f"Rute ditemukan. {current_route[current_step_index]['instruction']}")
                        print(f"Instruksi: {current_route[current_step_index]['instruction']}")
                    else:
                        respond("Maaf, tidak dapat menemukan rute ke tujuan.")
                else:
                    respond("Maaf, tidak dapat menemukan tujuan yang Anda sebutkan.")
            else:
                respond("Gagal mendapatkan lokasi saat ini. Silakan coba lagi.")
            return

        # Perintah untuk langkah selanjutnya
        if ("langkah selanjutnya" in text or "next" in text) and current_route:
            current_step_index += 1
            if current_step_index < len(current_route):
                respond(current_route[current_step_index]['instruction'])
                print(f"Instruksi: {current_route[current_step_index]['instruction']}")
            else:
                respond("Anda telah sampai di tujuan. Navigasi selesai.")
                current_route = []
            return
        
        # Sapaan dan percakapan dasar
        if "apa kabar" in text:
            respond("Aku baik-baik saja, terima kasih sudah bertanya.")
        elif "kamu siapa" in text or "siapa namamu" in text:
            respond("Namaku adalah Mikasa, asisten suaramu.")
        else:
            respond("Maaf, aku belum mengerti maksudmu. Bisa diulangi?")
    
    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
        print("Tidak dapat mengenali ucapan.")

def stop_cb(evt):
    """
    Menangani peristiwa sesi dihentikan atau dibatalkan.
    """
    global done
    print("Sesi dihentikan.")
    done = True

def main():
    recognizer.recognized.connect(recognized_handler)
    recognizer.session_stopped.connect(stop_cb)
    recognizer.canceled.connect(stop_cb)

    print("Mulai mendengarkan... Ucapkan 'mulai navigasi ke [tujuan]' untuk memulai.")
    recognizer.start_continuous_recognition()

    while not done:
        time.sleep(0.1)

    recognizer.stop_continuous_recognition()

if __name__ == "__main__":
    main()