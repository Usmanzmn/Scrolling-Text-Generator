import streamlit as st
from moviepy.editor import ImageSequenceClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import tempfile
import matplotlib.font_manager as fm
import textwrap
from gtts import gTTS

st.set_page_config(layout="centered")
st.title("🎞️ Scrolling Text & 🔊 Audio Generator")

text = st.text_area("📜 Paste your text here", height=400)
font_size = st.slider("Font size", 20, 60, 40)
scroll_speed = st.slider("Scroll speed (lower = slower)", 1, 20, 5)

# Shared parameters
W, H = 1280, 720
side_margin = 60  # side margins for video text

# Font setup
font_path = fm.findfont(fm.FontProperties(family='DejaVu Sans'))
try:
    font = ImageFont.truetype(font_path, font_size)
except:
    font = ImageFont.load_default()

# TEXT WRAPPING
def wrap_text(text, max_chars):
    wrapped = []
    for line in text.split("\n"):
        wrapped += textwrap.wrap(line, width=max_chars)
    return wrapped

# 🎬 VIDEO GENERATION
if st.button("🎬 Generate Scrolling Video"):
    with st.spinner("Creating video..."):
        max_chars = (W - 2 * side_margin) // (font_size // 2)
        wrapped_lines = wrap_text(text, max_chars)

        # Prepare image
        line_height = font.getbbox("A")[3] + 10
        total_text_height = line_height * len(wrapped_lines)
        img_height = max(total_text_height + H, H * 2)

        img = Image.new("RGB", (W, img_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        y = (img_height // 2) - (total_text_height // 2)
        for line in wrapped_lines:
            w, _ = draw.textsize(line, font=font)
            x = max((W - w) // 2, side_margin)
            draw.text((x, y), line, font=font, fill="white")
            y += line_height

        scroll_range = img_height - H
        frames = []
        for offset in range(0, scroll_range, scroll_speed):
            crop = img.crop((0, offset, W, offset + H))
            frames.append(np.array(crop))

        for _ in range(20):
            frames.append(frames[-1])

        clip = ImageSequenceClip(frames, fps=24)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            clip.write_videofile(tmpfile.name, codec="libx264", audio=False)
            st.success("✅ Video ready!")
            st.video(tmpfile.name)
            st.download_button("⬇️ Download MP4", open(tmpfile.name, "rb").read(), file_name="scrolling_text.mp4")

# 🔊 AUDIO GENERATION
if st.button("🔊 Generate Audio from Text"):
    with st.spinner("Generating audio..."):
        try:
            tts = gTTS(text)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
                tts.save(audio_file.name)
                st.success("✅ Audio ready!")
                st.audio(audio_file.name)
                st.download_button("⬇️ Download MP3", open(audio_file.name, "rb").read(), file_name="text_audio.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
