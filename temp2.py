from google.cloud import speech
import io

# Set up Google Cloud client
client = speech.SpeechClient()

# Path to your MP3 file
audio_file_path = r"C:\Users\Shani\Downloads\P\project\server\uploads\1744650810340.mp3"

# Read the MP3 file into memory
with io.open(audio_file_path, "rb") as audio_file:
    content = audio_file.read()

audio = speech.RecognitionAudio(content=content)

# Set the recognition configuration
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.MP3,  # MP3 encoding
    sample_rate_hertz=16000,  # Adjust if necessary
    language_code="en-US",  # Change to the appropriate language code
)

# Request speech recognition
response = client.recognize(config=config, audio=audio)

# Print the transcribed text
for result in response.results:
    print("Transcript: {}".format(result.alternatives[0].transcript))
