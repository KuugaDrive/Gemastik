import azure.cognitiveservices.speech as speechsdk
import time
import re

def recognize_for_berapa_seconds():
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
        speech_config=speech_config, audio_config=audio_config
    )

    done = False

    def recognized_handler(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            original_text = evt.result.text
            text = original_text.lower()
            print("Anda Mengatakan:", original_text)

            match = re.search(r"namaku adalah ([\w\s]+)", text)
            if match:
                nama = match.group(1).strip().title()
                
                response_text = f"Halo {nama}, senang berkenalan denganmu. Namaku adalah Mikasa"
                
                print("Mikasa:", response_text)
                result = speech_synthesizer.speak_text_async(response_text).get()
                
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = result.cancellation_details
                    print(f"Pembatalan sintesis suara: {cancellation_details.reason}")
                    if cancellation_details.error_details:
                        print(f"Detail kesalahan: {cancellation_details.error_details}")

        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("Tidak dapat mengenali ucapan.")
            
    def stop_cb(evt):
        nonlocal done
        print("Selesai!")
        done = True

    recognizer.recognized.connect(recognized_handler)
    recognizer.session_stopped.connect(stop_cb)
    recognizer.canceled.connect(stop_cb)

    print("Silakan bicara (rekaman 5 detik)...")
    recognizer.start_continuous_recognition()

    time.sleep(5)
    recognizer.stop_continuous_recognition()

    while not done:
        time.sleep(0.1)

if __name__ == "__main__":
    recognize_for_berapa_seconds()
