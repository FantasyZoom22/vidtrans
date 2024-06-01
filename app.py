from flask import Flask, request, jsonify, render_template, flash
from moviepy.editor import VideoFileClip
import whisper
from translate import Translator
from gtts import gTTS
import io
import tempfile
import requests
import cloudinary
import cloudinary.uploader
import moviepy.audio.io.AudioFileClip as mp
import secrets  # Import the secrets module for generating the secret key

# Cloudinary configuration (replace with your credentials)
cloudinary.config(
    cloud_name="dsjjtnudl",
    api_key="272999119546813",
    api_secret="fBRJ8Dn3bAFLO42GuYajbD4AUds"
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Automatically generate a secure random secret key

def extract_audio(video_data):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video_file:
        temp_video_file.write(video_data)
        temp_video_file.flush()
        video = VideoFileClip(temp_video_file.name)
        audio = video.audio
        audio_data = io.BytesIO()
        audio.write_audiofile(audio_data, codec='pcm_s16le')
        audio_data.seek(0)
    return audio_data

def transcribe_audio(audio_data):
    model = whisper.load_model("base")
    audio_data.seek(0)
    result = model.transcribe(audio_data)
    transcription = result["text"]
    return transcription

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/videotoaudioandtranscription', methods=['POST'])
def video_to_audio_and_transcription():
    if not request.is_json or 'video_url' not in request.json:
        return "No video URL provided", 400

    video_url = request.json['video_url']
    webhook_url = "https://n8n-manager.onrender.com/webhook-test/e8b55785-8786-44c5-85a8-56cd0d51823a"

    try:
        # Step 1: Download the video from the provided URL
        video_response = requests.get(video_url)
        video_data = video_response.content

        # Step 2: Extract audio from the downloaded video
        audio_data = extract_audio(video_data)

        # Step 3: Read audio data as bytes for Cloudinary upload
        audio_data.seek(0)
        audio_data_bytes = audio_data.read()

        # Step 4: Upload the extracted audio to Cloudinary
        response = cloudinary.uploader.upload(io.BytesIO(audio_data_bytes), resource_type="raw")
        audio_url = response["url"]

        # Step 5: Transcribe the audio
        transcription = transcribe_audio(io.BytesIO(audio_data_bytes))

        # Step 6: Send the transcription to the webhook URL
        webhook_response = requests.post(webhook_url, json={"transcription": transcription})
        if webhook_response.status_code != 200:
            return jsonify({"error": "Failed to send transcription to webhook"}), 500

        return jsonify({"audio_url": audio_url, "transcription": transcription})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)





# from flask import Flask, request, jsonify, render_template, flash
# from moviepy.editor import VideoFileClip  # Use VideoFileClip from moviepy.editor
# import whisper
# from translate import Translator
# from gtts import gTTS
# import io
# import tempfile

# import cloudinary

# # Cloudinary configuration (replace with your credentials)
# cloudinary.config(
#     cloud_name="dsjjtnudl",
#     api_key="272999119546813",
#     api_secret="fBRJ8Dn3bAFLO42GuYajbD4AUds"
# )

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Add a secret key for flash messages

# def extract_audio(video_data):  # Access the uploaded video data directly
#     # Replace with your audio extraction logic (e.g., using libraries like moviepy)
#     audio_data = video_data  # Placeholder, implement audio extraction here
#     return audio_data


# def transcribe_audio(audio_data):
#     model = whisper.load_model("base")
#     result = model.transcribe(audio_data)
#     transcription = result["text"]
#     return transcription


# def translate_text(text, to_lang):
#     translator = Translator(to_lang=to_lang)
#     translation = translator.translate(text)
#     return translation


# def text_to_speech(text, language="es"):
#     tts = gTTS(text=text, lang=language)
#     # Create an in-memory buffer to hold the generated audio data
#     audio_data = io.BytesIO()
#     tts.write_to_fp(audio_data)
#     audio_data.seek(0)  # Reset the buffer position
#     return audio_data


# def combine_video_audio(video_data, audio_data):
#     # Create a temporary video file for processing
#     with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_video_file:
#         temp_video_file.write(video_data)
#         video = VideoFileClip(temp_video_file.name)

#         audio = mp.AudioFileClip(io.BytesIO(audio_data.read()))  # Create AudioFileClip from in-memory data

#         if video.duration < audio.duration:
#             audio = audio.subclip(0, video.duration)

#         final_clip = video.set_audio(audio)
#         final_clip_data = io.BytesIO()
#         final_clip.write_videofile(final_clip_data, fps=video.fps)
#         final_clip_data.seek(0)  # Reset the buffer position
#         return final_clip_data


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'video' not in request.files:
#         return "No video file provided", 400

#     video = request.files['video']

#     target_language = request.form.get('language', 'es')

#     try:
#         # Access uploaded video data
#         video_data = video.read()

#         # Extract audio data from video
#         audio_data = extract_audio(video_data)

#         # Transcribe audio
#         transcribed_text = transcribe_audio(audio_data)

#         # Translate text
#         translated_text = translate_text(transcribed_text, target_language)

#         # Convert translated text to speech
#         tts_audio_data = text_to_speech(translated_text, target_language)

#         # Combine video and new audio (in-memory data)
#         combined_video_data = combine_video_audio(video_data, tts_audio_data)

#         # Upload the combined video data to Cloudinary
#         response = cloudinary.uploader.upload(combined_video_data.read(), public_id=f"processed_video_{video.filename}")

#         # Access the uploaded video URL from the response
#         video_url = response["url"]

#         flash("Final video uploaded to Cloudinary successfully!", 'success')
#         return render_template('index.html', video_url=video_url)  # Redirect to index with video URL

#     except Exception as e:
#         flash


