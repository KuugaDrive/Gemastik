import azure.cognitiveservices.speech as speechsdk
import time
import re

def recognize_interactive():
    """
    Menjalankan program pengenal dan sintesis suara interaktif.
    """
    try:
        with open("speech_api.txt", "r") as f:
            AZURE_SPEECH_KEY = f.read().strip()
        AZURE_SERVICE_REGION = "southeastasia"

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

        done = False

        def respond(text):
            """
            Menyuarakan teks yang diberikan, mencetaknya ke konsol, dan memberikan jeda.
            """
            print(f"Mikasa: {text}")
            result = speech_synthesizer.speak_text_async(text).get()
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"Gagal menyuarakan teks. Alasan: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print(f"ErrorDetails: {cancellation_details.error_details}")
            
            # Tambahkan jeda 1 detik di sini
            time.sleep(8)

        def recognized_handler(evt):
            """
            Menangani hasil ucapan yang dikenali.
            """
            nonlocal done
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                original_text = evt.result.text
                text = original_text.lower()
                print(f"Anda: {original_text}")

                if "keluar" in text or "selesai" in text:
                    respond("Baik, sampai jumpa.")
                    done = True
                elif "namaku adalah" in text:
                    match = re.search(r"namaku adalah ([\w\s]+)", text)
                    if match:
                        nama = match.group(1).strip().title()
                        respond(f"Halo {nama}, senang berkenalan denganmu. Namaku adalah Mikasa.")
                    else:
                        respond("Maaf, namamu kurang jelas. Bisa sebutkan lagi?")
                elif "apa kabar" in text:
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
            nonlocal done
            print("Sesi dihentikan.")
            done = True

        recognizer.recognized.connect(recognized_handler)
        recognizer.session_stopped.connect(stop_cb)
        recognizer.canceled.connect(stop_cb)

        print("Mulai mendengarkan... Ucapkan 'keluar' atau 'selesai' untuk berhenti.")
        recognizer.start_continuous_recognition()

        while not done:
            time.sleep(0.1)

        recognizer.stop_continuous_recognition()

    except FileNotFoundError:
        print("Error: File 'api.txt' tidak ditemukan. Pastikan file tersebut ada dan berisi kunci API.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    recognize_interactive()