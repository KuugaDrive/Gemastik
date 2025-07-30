import azure.cognitiveservices.speech as speechsdk

def recognize_from_microphone_azure():
    AZURE_SPEECH_KEY = "API"
    AZURE_SERVICE_REGION = "southeastasia"  

    # Konfigurasi speech service
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SERVICE_REGION
    )
    speech_config.speech_recognition_language = "id-ID"  

    # Gunakan mikrofon sebagai input
    audio_config = speechsdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )

    print("Silakan bicara sekarang...")

    # Tunggu dan rekam input suara satu kali
    result = speech_recognizer.recognize_once()

    # Tampilkan hasil
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Anda mengucapkan:", result.text)
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("Maaf, tidak ada ucapan yang dikenali.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Pengenalan dibatalkan. Alasan:", cancellation_details.reason)
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Kode error:", cancellation_details.error_code)
            print("Detail error:", cancellation_details.error_details)

if __name__ == "__main__":
    recognize_from_microphone_azure()
