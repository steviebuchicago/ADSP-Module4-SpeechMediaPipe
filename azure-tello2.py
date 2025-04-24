import sounddevice as sd
import azure.cognitiveservices.speech as speechsdk
import time
import os

# Azure Speech service key and region from environment variables
speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SERVICE_REGION")

def list_microphones():
    """List all available microphones and their ID."""
    print("Available microphones:")
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        print(f"ID: {idx}, Name: {device['name']}, Samplerate: {device['default_samplerate']}")

def record_and_recognize_audio(device_id):
    """Record audio from the specified microphone, play it back, and recognize the speech."""
    try:
        # Set the device configuration for recording
        samplerate = int(sd.query_devices(device_id, 'input')['default_samplerate'])
        duration = 5  # Duration in seconds

        print("Please speak clearly into the microphone after the beep.")
        time.sleep(1)  # Short pause before recording
        print('\a')  # System beep
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, device=device_id, dtype='float32')
        sd.wait()  # Wait until the recording is finished
        print("Recording complete.")

        print("Playback the recorded audio...")
        sd.play(recording, samplerate)
        sd.wait()  # Wait until the playback is finished
        print("Playback complete.")

        # Initialize speech recognition
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=False)
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # Push the recorded audio to the recognizer
        stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=stream)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        print("Starting speech recognition...")
        stream.write(recording.tobytes())
        stream.close()

        result = speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognized: {result.text}")
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized.")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            print(f"Speech recognition canceled: {cancellation.reason}")
            if cancellation.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation.error_details}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_microphones()
    device_id = int(input("Enter the ID of the microphone you want to test: "))
    record_and_recognize_audio(device_id)
