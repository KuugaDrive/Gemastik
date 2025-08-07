import sounddevice as sd

print("Daftar perangkat audio yang terdeteksi:")
for i, device in enumerate(sd.query_devices()):
    if device['max_input_channels'] > 0:
        print(f"[{i}] {device['name']}")
