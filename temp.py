import whisper

# Load the Whisper model
model = whisper.load_model("base")  # You can also use 'small', 'medium', or 'large' for different trade-offs

# Path to your MP3 file
audio_file_path = r"C:\Users\Shani\Downloads\P\project\server\uploads\1744650810340.mp3"

# Transcribe the MP3 file
result = model.transcribe(audio_file_path)

# Print the transcribed text
print("Text extracted from audio: ", result['text'])
print(type(result['text']))
