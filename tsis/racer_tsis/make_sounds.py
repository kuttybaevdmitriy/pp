import wave, struct, math, random

def create_sound(filename, duration, freq=1000, is_noise=False):
    # Setup WAV file parameters
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            if is_noise:
                # Generate static/noise for crash
                value = random.randint(-32767, 32767)
            else:
                # Generate sine wave for coin
                value = int(32767 * math.sin(2 * math.pi * freq * (i / sample_rate)))
            wav_file.writeframesraw(struct.pack('<h', value))

print("Generating sounds...")
# Coin: 0.1 seconds, 1200 Hz tone
create_sound('coin.wav', duration=0.1, freq=1200, is_noise=False)
# Crash: 0.3 seconds, pure noise
create_sound('crash.wav', duration=0.3, is_noise=True)
print("Sounds created successfully! You can now run your games.")