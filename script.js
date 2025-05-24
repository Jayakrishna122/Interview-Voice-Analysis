document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('analysis-form').addEventListener('submit', async function(event) {
        event.preventDefault();

        const formData = new FormData();
        const audioInput = document.getElementById('audio-file');
        const audioFile = audioInput ? audioInput.files[0] : null;

        if (!audioFile) {
            alert("Please upload an audio file.");
            return;
        }

        formData.append('audio', audioFile);

        try {
            console.log('Form data:', formData);
            
            const xamppBaseURL = "http://localhost/audio_analysis";
            const flaskBaseURL = "http://127.0.0.1:5000";

            console.log("Uploading file to PHP server...");

            const uploadResponse = await fetch(`${xamppBaseURL}/upload.php`, {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                throw new Error('Failed to upload audio file.');
            }

            const uploadData = await uploadResponse.json();
            console.log("Upload Data:", uploadData);

            if (uploadData.error) {
                alert(uploadData.error);
                return;
            }

            const filePath = uploadData.file_path.startsWith("http") ? uploadData.file_path : `http://localhost/${uploadData.file_path}`;
            console.log("Uploaded file path: ", filePath);

            console.log("Sending file path to Flask for analysis...");

            const analysisResponse = await fetch(`${flaskBaseURL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ file_path: filePath })
            });

            if (!analysisResponse.ok) {
                throw new Error('Failed to fetch analysis results.');
            }

            const results = await analysisResponse.json();
            console.log("Analysis Results: ", results);

            // Ensure all result elements exist before setting values
            const resultElements = {
                sentiment: document.getElementById('sentiment'),
                avgPitch: document.getElementById('avg-pitch'),
                tempo: document.getElementById('tempo'),
                wordCount: document.getElementById('word-count'),
                keywordsMatch: document.getElementById('keywords-match'),
                stressLevel: document.getElementById('stress-level'),
                clarity: document.getElementById('clarity'),
                resultsSection: document.getElementById('results')
            };

            for (let key in resultElements) {
                if (!resultElements[key]) {
                    console.error(`Element with ID '${key}' is missing in the DOM.`);
                    return;
                }
            }

            resultElements.sentiment.innerText = results.Sentiment?.compound || "N/A";
            resultElements.avgPitch.innerText = results["Audio Features"]?.["Average Pitch"] || "N/A";
            resultElements.tempo.innerText = results["Audio Features"]?.["Speech Tempo"] || "N/A";
            resultElements.wordCount.innerText = results["Transcription"] ? results["Transcription"].split(" ").length : "N/A";
            resultElements.keywordsMatch.innerText = results["Relevant Keywords"] ? results["Relevant Keywords"].join(', ') : "N/A";
            resultElements.stressLevel.innerText = results["Stress Level"] || "N/A";
            resultElements.clarity.innerText = results["Clarity"] || "N/A";

            resultElements.resultsSection.style.display = 'block';

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while processing the audio. Please check the console for details.');
        }
    });
});
