import os
import librosa
import numpy as np
import speech_recognition as sr
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize
import re
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required

nltk.download("punkt")

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key
jwt = JWTManager(app)

def analyze_audio(audio_path):
    # Load audio
    y, sr = librosa.load(audio_path)

    # 1. Extract Pitch (Average Fundamental Frequency)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    avg_pitch = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0

    # 2. Speech Tempo (Words per Minute)
    duration = librosa.get_duration(y=y, sr=sr)
    speech_tempo = "Normal" if 120 <= (len(y) / duration) <= 180 else "Fast" if (len(y) / duration) > 180 else "Slow"

    # 3. Speech-to-Text Conversion
    recognizer = sr.Recognizer()
    text = ""
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError:
        return {"error": "Speech recognition service unavailable"}

    # 4. Word Count & Filler Words
    words = word_tokenize(text)
    word_count = len(words)
    filler_words = [word for word in words if word.lower() in ["um", "like", "you know", "uh"]]

    # 5. Sentiment Analysis
    sentiment_score = TextBlob(text).sentiment.polarity
    sentiment = "Positive" if sentiment_score > 0.2 else "Negative" if sentiment_score < -0.2 else "Neutral"

    # 6. Stress Level (Amplitude Variation)
    stress_level = "High" if np.std(y) > 0.05 else "Moderate" if np.std(y) > 0.02 else "Low"

    # 7. Clarity (Pause Detection)
    silence_count = len(re.findall(r"\.\.\.|-", text))
    clarity = "High" if silence_count < 3 else "Moderate" if silence_count < 6 else "Low"

    # 8. Fluency (Word per Second Ratio)
    fluency = "Good" if word_count / duration > 2 else "Moderate" if word_count / duration > 1 else "Poor"

    # 9. Keyword Matching (Based on Job Interviews)
    keywords = ["interview", "experience", "skills", "position", "team", "work"]
    relevant_keywords = [word for word in words if word.lower() in keywords]

    # 10. Bias Detection (Simple Example: Detecting Gendered Words)
    gendered_words = ["he", "she", "his", "hers", "man", "woman"]
    bias_detection = "Bias Detected" if any(word in words for word in gendered_words) else "None"

    # 11. Speaker Profiling (Basic)
    speaker_profile = "Professional" if sentiment == "Positive" and fluency == "Good" else "Casual"

    # Prepare Results
    results = {
        "sentiment": sentiment,
        "average_pitch": f"{avg_pitch:.2f} Hz" if avg_pitch else "N/A",
        "speech_tempo": speech_tempo,
        "word_count": word_count,
        "relevant_keywords": relevant_keywords,
        "stress_level": stress_level,
        "clarity": clarity,
        "fluency": fluency,
        "filler_words": filler_words,
        "speaker_profile": speaker_profile,
        "bias_detection": bias_detection
    }

    return results

@app.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_audio_route():
    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Invalid or missing audio file."}), 400

    results = analyze_audio(file_path)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
