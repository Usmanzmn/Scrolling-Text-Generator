import streamlit as st
import re
from gtts import gTTS
import tempfile
import os
from moviepy.editor import *
from num2words import num2words
from pydub import AudioSegment

# === FUNCTIONS ===

# Convert numbers like 2023 to words (two thousand twenty-three)
def convert_year_to_words(text):
    pattern = r'\b(1\d{3}|20\d{2}|2100)\b'  # matches years from 1000 to 2100
    return re.sub(pattern, lambda x: num2words(int(x.group())), text)

# Convert general numbers to words
def convert_numbers_to_words(text):
    pattern = r'\b\d+\b'
    return re.sub(pattern, lambda x: num2words(int(x.group())), text)

# Create TTS audio from text
def generate_tts(text, lang='en'):
    tts = gTTS(text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(temp_audio.name)
    return temp_audio.name

# Convert uploaded MP3 to compatible format
def convert_uploaded_audio(file):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    audio = AudioSegment.from_file(file)
    audio.export(temp.name, format="mp3")
    return temp.name

# Create video with highlighted text lines
def create_video(text, audio_path, font_size=32, highlight_lines=True):
    lines = text.split('\n')
    font = "DejaVu-Sans"
    clips = []
    audio = AudioFileClip(audio_path)
    duration_per_line = audio.duration / len(lines)

    for i, line in enumerate(lines):
        txt = ""
        for j, l in enumerate(lines):
            if highlight_lines and j == i:
                txt += f"<span style='color:red;'>{l}</span><br>"
            else:
                txt += f"{l}<br>"

        txt_clip = TextClip(txt, fontsize=font_size, color='white', font=font, method='caption', size=(720, 1280), bg_color='black')
        txt_clip = txt_clip.set_duration(duration_per_line)
        clips.append(txt_clip)

    final = concatenate_videoclips(clips).set_audio(audio)
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    final.write_videofile(temp_video.name, fps=24)
    return temp_video.name

# === STREAMLIT APP ===

st.set_page_config(layout="centered", page_title="Cartoon Video Generator")
st.title("🎬 Cartoon-style Scrolling Video Generator")

# Text input
text = st.text_area("Enter your story/text:", height=300)

# Font size
font_size = st.slider("Font Size", min_value=24, max_value=64, value=32)

# Highlight option
highlight_lines = st.checkbox("Highlight Center Line While Reading", value=True)

# Audio source
voice_option = st.radio("Voice Option", ["Default Voice (TTS)", "Upload MP3"])

# Year & number to word conversion
if text:
    text = convert_year_to_words(text)
    text = convert_numbers_to_words(text)

# Generate on button click
if st.button("Generate Video"):
    with st.spinner("Generating audio and video..."):
        if voice_option == "Default Voice (TTS)":
            audio_path = generate_tts(text)
        else:
            uploaded_file = st.file_uploader("Upload MP3 Audio", type=["mp3"])
            if uploaded_file is not None:
                audio_path = convert_uploaded_audio(uploaded_file)
            else:
                st.warning("Please upload an MP3 file.")
                st.stop()

        video_path = create_video(text, audio_path, font_size, highlight_lines)

        st.success("✅ Video Generated!")
        st.video(video_path)

        with open(video_path, "rb") as f:
            st.download_button("📥 Download Video", f, file_name="generated_video.mp4")

        with open(audio_path, "rb") as f:
            st.download_button("🔊 Download Audio", f, file_name="generated_audio.mp3")
