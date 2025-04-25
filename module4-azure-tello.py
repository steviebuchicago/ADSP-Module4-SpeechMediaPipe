import sounddevice as sd
import azure.cognitiveservices.speech as speechsdk
import time
import os
from djitellopy import Tello

# Azure Speech service key and region
speech_key = "your_actual_key_here"
service_region = "eastus2"

# Define verbal commands
COMMANDS = {
    "start": "start",
    "take off": "take off",
    "land": "land",
    "forward": "forward",
    "back": "back",
    "flip": "flip"
}

def list_microphones():
    """List all available microphones and their ID."""
    print("Available microphones:")
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        print(f"ID: {idx}, Name: {device['name']}, Samplerate: {device['default_samplerate']}")

def recognize_speech_realtime(device_id, tello):
    """Recognize speech in real-time from the specified microphone and control the Tello drone."""
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
                command = evt.result.text.lower()
                print(f"Recognized: {command}")
                execute_command(command, tello)
            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized.")
            elif evt.result.reason == speechsdk.ResultReason.Canceled:
                cancellation = evt.result.cancellation_details
                print(f"Speech recognition canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation.error_details}")

        # Connect the callback function to the recognizer
        speech_recognizer.recognized.connect(recognized_callback)

        print("Listening... Say 'start' to begin Tello commands.")
        speech_recognizer.start_continuous_recognition()

        # Keep the program running to listen for speech
        input("Press Enter to stop listening...\n")
        speech_recognizer.stop_continuous_recognition()
    except Exception as e:
        print(f"An error occurred: {e}")

def execute_command(command, tello):
    """Execute the given command on the Tello drone."""
    if command == COMMANDS["start"]:
        print("Ready for Tello commands.")
    elif command == COMMANDS["take off"]:
        if not tello.is_flying:
            print("Taking off...")
            tello.takeoff()
        else:
            print("Already in the air.")
    elif command == COMMANDS["land"]:
        if tello.is_flying:
            print("Landing...")
            tello.land()
        else:
            print("Already on the ground.")
    elif command == COMMANDS["forward"]:
        if tello.is_flying:
            print("Moving forward...")
            tello.move_forward(50)  # Example distance
        else:
            print("Cannot move forward, drone is on the ground.")
    elif command == COMMANDS["back"]:
        if tello.is_flying:
            print("Moving back...")
            tello.move_back(50)  # Example distance
        else:
            print("Cannot move back, drone is on the ground.")
    elif command == COMMANDS["flip"]:
        if tello.is_flying:
            print("Flipping...")
            tello.flip_forward()  # Example flip
        else:
            print("Cannot flip, drone is on the ground.")
    else:
        print("Unknown command.")

if __name__ == "__main__":
    list_microphones()
    device_id = int(input("Enter the ID of the microphone you want to test: "))

    # Initialize Tello drone
    tello = Tello()
    tello.connect()

    print("Say 'start' to begin Tello commands.")
    recognize_speech_realtime(device_id, tello)
