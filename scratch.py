import whisper
import pyaudio
import wave
import tempfile
import os
import ssl
import certifi
import urllib.request

# Set the default SSL context to use the certifi CA bundle
ssl_context = ssl.create_default_context(cafile=certifi.where())
urllib.request.urlopen = lambda *args, **kwargs: urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context)).open(*args, **kwargs)

def record_audio(filename, duration=5):
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 44100  # Record at 44100 samples per second

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for the specified duration
    for _ in range(0, int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))

def main():
    # Load Whisper model from the web, using certifi
    print('Loading Whisper model')
    model = whisper.load_model("base")

    # Record audio
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        record_audio(tmp_file.name, duration=10)  # Record for 10 seconds

        # Transcribe audio
        print('Transcribing audio')
        result = model.transcribe(tmp_file.name)
        text = result["text"]
        print("You said: " + text)

        # Clean up temporary file
        os.unlink(tmp_file.name)


if __name__ == "__main__":
    main()
