import tkinter as tk
from tkinter import filedialog, messagebox
import moviepy.editor as mp
from moviepy.video.io.VideoFileClip import VideoFileClip
import openai_whisper as whisper
from translate import Translator
from gtts import gTTS
import os

# Function to extract audio from video
def extract_audio(video_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio_path = "sample.mp3"
    audio.write_audiofile(audio_path)
    return audio_path

# Function to transcribe audio using Whisper
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcription = result["text"]
    return transcription

# Function to translate text
def translate_text(text, to_lang):
    translator = Translator(to_lang=to_lang)
    translation = translator.translate(text)
    return translation

# Function to convert text to speech using gTTS
def text_to_speech(text, language="es"):
    tts = gTTS(text=text, lang=language)
    audio_path = "generated_speech.mp3"
    tts.save(audio_path)
    return audio_path

# Function to combine video and new audio
def combine_video_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio = mp.AudioFileClip(audio_path)

    if video.duration < audio.duration:
        audio = audio.subclip(0, video.duration)

    final_clip = video.set_audio(audio)
    final_clip.write_videofile("final_video.mp4")

# Function to handle the generation process
def generate_final_video():
    video_path = video_path_var.get()
    target_language = language_var.get()

    if not video_path:
        messagebox.showerror("Error", "Please select a video file.")
        return

    if not target_language:
        messagebox.showerror("Error", "Please select a target language.")
        return

    # Extract audio from video
    audio_path = extract_audio(video_path)

    # Transcribe audio
    transcribed_text = transcribe_audio(audio_path)
    print("Transcribed Text:", transcribed_text)

    # Translate text
    translated_text = translate_text(transcribed_text, target_language)
    print("Translated Text:", translated_text)

    # Convert translated text to speech
    tts_audio_path = text_to_speech(translated_text, target_language)

    # Combine video and new audio
    combine_video_audio(video_path, tts_audio_path)

    messagebox.showinfo("Success", "Final video with translated audio created!")

# Function to select a video file
def select_video_file():
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
    video_path_var.set(video_path)

# Create the GUI
root = tk.Tk()
root.title("Video Translation")

# Video selection
tk.Label(root, text="Select Video File:").pack(pady=5)
video_path_var = tk.StringVar()
tk.Entry(root, textvariable=video_path_var, width=50).pack(padx=10, pady=5)
tk.Button(root, text="Browse", command=select_video_file).pack(pady=5)

# Language selection
tk.Label(root, text="Select Target Language:").pack(pady=5)
language_var = tk.StringVar(value="es")  # Default to Spanish
tk.OptionMenu(root, language_var, "es", "fr", "de", "it", "pt", "zh", "ja", "ko").pack(pady=5)

# Generate button
tk.Button(root, text="Generate", command=generate_final_video).pack(pady=20)

# Run the GUI main loop
root.mainloop()
