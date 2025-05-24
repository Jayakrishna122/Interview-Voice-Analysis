import os
import uuid
from flask import Flask, request, jsonify
import librosa
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
import nltk
from collections import Counter
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import speech_recognition as sr
from pydub import AudioSegment
import whisper
app = Flask(__name__)


CORS(app)
# File Upload Configuration
UPLOAD_FOLDER = 'server\\uploads' # You can set your own folder
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the Spacy NLP model
nlp = spacy.load("en_core_web_sm")

# Sentiment Analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_audio(file_path):
    model = whisper.load_model("base")  # You can also use 'small', 'medium', or 'large' for different trade-offs

    # Path to your MP3 file
    audio_file_path = file_path

    # Transcribe the MP3 file
    resultText = model.transcribe(audio_file_path)
    print("Text extracted from audio: ", resultText['text'])
    
    # 1. Load the audio file
    audio, sr = librosa.load(file_path, sr=None)
    
    # 2. Analyze Audio Features
    # Pitch (average pitch)
    pitches, magnitudes = librosa.core.piptrack(y=audio, sr=sr)
    pitch = np.mean(pitches[pitches > 0])  # Average pitch
    
    # Tempo (Speech Rate)
    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    
    # 3. Extract the transcribed text (not the entire result object)
    text = resultText['text']  # Extract the actual transcribed text
    
    # 4. Sentiment Analysis
    sentiment_score = sentiment_analyzer.polarity_scores(text)
    sentiment = "Positive" if sentiment_score['compound'] > 0.1 else "Negative" if sentiment_score['compound'] < -0.1 else "Neutral"
    
    # 5. Word Count and Relevant Keywords Extraction
    doc = nlp(text)
    word_count = len([token.text for token in doc if token.is_alpha])  # Word count excluding punctuation
    nltk.download('stopwords')
    stop_words = set(nltk.corpus.stopwords.words("english"))
    relevant_keywords = [word.text for word in doc if word.text.lower() not in stop_words and len(word.text) > 2]
    relevant_keywords = [item for item, _ in Counter(relevant_keywords).most_common(10)]  # Top 10 keywords
    
    # 6. Stress Level (Example: analyzing sentence complexity)
    stress_level = "High" if len([token for token in doc if token.dep_ in ['nsubj', 'dobj']]) > 3 else "Moderate"
    
    # 7. Clarity and Fluency Analysis (simple heuristic)
    clarity = "High" if word_count > 100 else "Low"
    
    # 8. Filler Words Detection (example with "um", "uh", etc.)
    filler_words = ["um", "uh", "like", "you know"]
    detected_fillers = [filler for filler in filler_words if filler in text.lower()]
    
    # Return analysis results
    # Check if tempo is a numpy array
    if isinstance(tempo, np.ndarray):
        # For example, get the mean of the tempo array, or use a specific index
        tempo_value = np.mean(tempo)  # or tempo[0], depending on your use case
    else:
        tempo_value = tempo

    # Now you can safely format the value
    results = {
        "sentiment": sentiment,
        "average_pitch": f"{pitch:.2f} Hz",
        "speech_tempo": f"{tempo_value:.2f} BPM",  # Use tempo_value here
        "word_count": word_count,
        "relevant_keywords": relevant_keywords,
        "stress_level": stress_level,
        "clarity": clarity,
        "filler_words": detected_fillers
    }

    return results



# Function to analyze audio using ML
def analyze_audio1(file_path):
    # Load the audio file
    audio, sr = librosa.load(file_path, sr=None)
    
    # Example analysis: Get the duration of the audio
    duration = librosa.get_duration(y=audio, sr=sr)
    
    # Return some results (you can customize this)
    return {
        "duration": duration,
        "sample_rate": sr,
        "file_path": file_path
    }

# File upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    
    if audio_file and allowed_file(audio_file.filename):
        # Save the file with a unique name to prevent overwriting
        filename = secure_filename(audio_file.filename)
        unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]  # Adding unique ID
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        print(file_path)
        # Create uploads folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        audio_file.save(file_path)

        return jsonify({'success': True, 'file_path': file_path})
    else:
        return jsonify({'error': 'Invalid file type. Only mp3, wav, or m4a are allowed.'}), 400

# Audio analysis route
@app.route('/analyze', methods=['POST'])
def analyze_audio_route():
    # Get the filename from the JSON body
    filename = request.json.get('file_path')
    print(filename)
    # Check if the filename is provided
    if not filename:
        return jsonify({"error": "Filename is missing in the request body"}), 400
    
    print(f"Received filename: {filename}")

    # Get the current working directory
    current_directory = os.getcwd()

    # Construct the file path for the audio file
    file_path = os.path.join(current_directory, 'server', 'uploads', filename)
    print(f"Constructed file path: {file_path}")

    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({"error": "Audio file not found"}), 404

    # Analyze the audio file
    results = analyze_audio(file_path)
    
    return jsonify(results)

def analyze_audio_route1():
    # Get the file path from the JSON body
    file_path = request.json.get('file_path')
    print(file_path)

    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({"error": "Audio file not found"}), 404

    # Analyze the audio file
    results = analyze_audio(file_path)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
