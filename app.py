from flask import Flask, request, jsonify, render_template
from moviepy.editor import VideoFileClip
import io
import tempfile
import requests
import cloudinary
import cloudinary.uploader
import secrets
import logging
import faster_whisper  # Import the faster-whisper library

# Cloudinary configuration (replace with your credentials)
cloudinary.config(
    cloud_name="dsjjtnudl",
    api_key="272999119546813",
    api_secret="fBRJ8Dn3bAFLO42GuYajbD4AUds"
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Setup logging
logging.basicConfig(level=logging.INFO)

def extract_audio(video_data):
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video_file:
            temp_video_file.write(video_data)
            temp_video_file.flush()
            temp_video_path = temp_video_file.name

        video = VideoFileClip(temp_video_path)
        
        if not video.audio:
            raise ValueError("The video file has no audio track.")
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
            audio_path = temp_audio_file.name
            video.audio.write_audiofile(audio_path, codec='libmp3lame')

        with open(audio_path, 'rb') as f:
            audio_data = f.read()

        return io.BytesIO(audio_data)

    except Exception as e:
        logging.error(f"Error extracting audio: {e}")
        raise

def transcribe_audio(audio_data):
    try:
        # Load the faster-whisper model
        model = faster_whisper.WhisperModel("base")
        audio_data.seek(0)
        result = model.transcribe(audio_data)
        transcription = result["text"]
        return transcription
    except Exception as e:
        logging.error(f"Error transcribing audio: {e}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/videotoaudio', methods=['POST'])
def video_to_audio():
    if not request.is_json or 'video_url' not in request.json:
        return jsonify({"error": "No video URL provided"}), 400

    video_url = request.json['video_url']

    try:
        logging.info(f"Downloading video from URL: {video_url}")
        video_response = requests.get(video_url)
        video_response.raise_for_status()
        video_data = video_response.content

        logging.info("Extracting audio from video")
        audio_data = extract_audio(video_data)

        audio_data_bytes = audio_data.getvalue()

        logging.info("Uploading audio to Cloudinary")
        response = cloudinary.uploader.upload(io.BytesIO(audio_data_bytes), resource_type="video", format="mp3")
        audio_url = response["url"]

        return jsonify({"audio_url": audio_url})

    except requests.RequestException as e:
        logging.error(f"Error downloading video: {e}")
        return jsonify({"error": "Failed to download video"}), 500
    except cloudinary.exceptions.Error as e:
        logging.error(f"Error uploading audio to Cloudinary: {e}")
        return jsonify({"error": "Failed to upload audio to Cloudinary"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/audioTotranscription', methods=['POST'])
def audio_to_transcription():
    if not request.is_json or 'audio_url' not in request.json:
        return jsonify({"error": "No audio URL provided"}), 400

    audio_url = request.json['audio_url']

    try:
        logging.info(f"Downloading audio from URL: {audio_url}")
        audio_response = requests.get(audio_url)
        audio_response.raise_for_status()
        audio_data = io.BytesIO(audio_response.content)

        logging.info("Transcribing audio")
        transcription = transcribe_audio(audio_data)

        return jsonify({"transcription": transcription})

    except requests.RequestException as e:
        logging.error(f"Error downloading audio: {e}")
        return jsonify({"error": "Failed to download audio"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
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


