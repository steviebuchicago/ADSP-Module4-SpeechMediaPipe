import sounddevice as sd
import azure.cognitiveservices.speech as speechsdk
import os

# Azure Speech service key and region
speech_key = ""
service_region = "eastus2"

def list_microphones():
    """List all available microphones and their ID."""
    print("Available microphones:")
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        print(f"ID: {idx}, Name: {device['name']}, Samplerate: {device['default_samplerate']}")

def recognize_speech_realtime(device_id):
    """Recognize speech in real-time from the specified microphone."""
    try:
        # Set the device configuration for recording
        samplerate = int(sd.query_devices(device_id, 'input')['default_samplerate'])

        # Initialize speech recognition
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        def recognized_callback(evt):
            """Callback function for recognized speech."""
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(f"Recognized: {evt.result.text}")
            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized.")
            elif evt.result.reason == speechsdk.ResultReason.Canceled:
                cancellation = evt.result.cancellation_details
                print(f"Speech recognition canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation.error_details}")

        # Connect the callback function to the recognizer
        speech_recognizer.recognized.connect(recognized_callback)

        print("Listening... Speak into the microphone.")
        speech_recognizer.start_continuous_recognition()

        # Keep the program running to listen for speech
        input("Press Enter to stop listening...\n")
        speech_recognizer.stop_continuous_recognition()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_microphones()
    device_id = int(input("Enter the ID of the microphone you want to test: "))
    recognize_speech_realtime(device_id)
