from flask import Flask, request, jsonify, render_template
from moviepy.video.io.VideoFileClip import VideoFileClip
import whisper
from translate import Translator
from gtts import gTTS
import os

import cloudinary

# Cloudinary configuration (replace with your credentials)
cloudinary.config(
    cloud_name="dsjjtnudl",
    api_key="272999119546813",
    api_secret="fBRJ8Dn3bAFLO42GuYajbD4AUds"
)

app = Flask(__name__)

def extract_audio(video_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio_path = "sample.mp3"
    audio.write_audiofile(audio_path)
    return audio_path

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcription = result["text"]
    return transcription

def translate_text(text, to_lang):
    translator = Translator(to_lang=to_lang)
    translation = translator.translate(text)
    return translation

def text_to_speech(text, language="es"):
    tts = gTTS(text=text, lang=language)
    audio_path = "generated_speech.mp3"
    tts.save(audio_path)
    return audio_path

def combine_video_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio = mp.AudioFileClip(audio_path)

    if video.duration < audio.duration:
        audio = audio.subclip(0, video.duration)

    final_clip = video.set_audio(audio)
    final_clip.write_videofile("final_video.mp4")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return "No video file provided", 400

    video = request.files['video']
    video_path = os.path.join("uploads", video.filename)
    video.save(video_path)

    target_language = request.form.get('language', 'es')

    # Extract audio from video
    audio_path = extract_audio(video_path)

    # Transcribe audio
    transcribed_text = transcribe_audio(audio_path)

    # Translate text
    translated_text = translate_text(transcribed_text, target_language)

    # Convert translated text to speech
    tts_audio_path = text_to_speech(translated_text, target_language)

    # Combine video and new audio
    combine_video_audio(video_path, tts_audio_path)


     # Upload the final video to Cloudinary
    response = cloudinary.uploader.upload("final_video.mp4")

    # Access the uploaded video URL from the response
    video_url = response["url"]

    # Clean up temporary files (optional)
    os.remove(audio_path)
    os.remove(tts_audio_path)
    os.remove("final_video.mp4")  # Consider alternative approach for efficiency

    return jsonify({"message": "Final video uploaded to Cloudinary!", "video_url": video_url})

    # return jsonify({"message": "Final video with translated audio created!", "video_path": "final_video.mp4"})

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=5000)
