import streamlit as st
from moviepy.editor import VideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import tempfile
import matplotlib.font_manager as fm
import textwrap
import pyttsx3

st.set_page_config(layout="centered")
st.title("🎞️ Scrolling Text & Audio Generator (20,000+ characters supported)")

tab1, tab2 = st.tabs(["📽️ Text to Video", "🔊 Text to Audio"])

with tab1:
    text = st.text_area("📜 Paste your text here", height=400)
    font_size = st.slider("Font size", 20, 60, 40)
    scroll_speed = st.slider("Scroll speed (lower = slower)", 1, 20, 5)
    highlight_lines = st.checkbox("✅ Show highlighted line reading", value=True)

    MAX_CHARS = 20000
    if len(text) > MAX_CHARS:
        st.warning(f"⚠️ Text is too long ({len(text)} characters). Only the first {MAX_CHARS} will be used.")
        text = text[:MAX_CHARS]

    st.caption(f"🧮 {len(text)}/{MAX_CHARS} characters")

    if st.button("🎬 Generate Scrolling Video"):
        with st.spinner("Creating video..."):

            W, H = 1280, 720
            side_margin = 60

            font_path = fm.findfont(fm.FontProperties(family='DejaVu Sans'))
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()

            max_chars = (W - 2 * side_margin) // (font_size // 2)
            wrapped_lines = []
            for line in text.split("\n"):
                wrapped_lines += textwrap.wrap(line, width=max_chars)

            line_height = font.getbbox("A")[3] + 10
            total_text_height = line_height * len(wrapped_lines)
            img_height = total_text_height + H

            y_positions = []
            y = (img_height - total_text_height) // 2
            for _ in wrapped_lines:
                y_positions.append(y)
                y += line_height

            full_img_np = np.zeros((img_height, W, 3), dtype=np.uint8)

            scroll_range = img_height - H
            highlight_duration = 1  # seconds
            fps = 24
            total_duration = len(wrapped_lines) * highlight_duration

            def make_frame(t):
                current_line = int(t // highlight_duration)
                current_line = min(current_line, len(wrapped_lines) - 1)

                img = Image.new("RGB", (W, img_height), color=(0, 0, 0))
                draw = ImageDraw.Draw(img)

                for i, line in enumerate(wrapped_lines):
                    fill = "yellow" if highlight_lines and i == current_line else "white"
                    w, _ = draw.textsize(line, font=font)
                    x = max((W - w) // 2, side_margin)
                    draw.text((x, y_positions[i]), line, font=font, fill=fill)

                offset = int(t * scroll_speed * fps)
                offset = min(offset, scroll_range)
                frame = img.crop((0, offset, W, offset + H))
                return np.array(frame)

            clip = VideoClip(make_frame, duration=total_duration + 1).set_fps(fps)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
                clip.write_videofile(tmpfile.name, codec="libx264", audio=False)
                st.success("✅ Video ready!")
                st.video(tmpfile.name)
                st.download_button("⬇️ Download MP4", open(tmpfile.name, "rb").read(), file_name="scrolling_text.mp4")

with tab2:
    st.header("🔊 Convert Text to Audio")
    tts_text = st.text_area("🗣️ Paste your text to convert to audio", height=300)
    voice_rate = st.slider("🌀 Voice Speed", 100, 250, 150)
    if st.button("🎧 Generate Audio"):
        with st.spinner("Generating audio..."):
            engine = pyttsx3.init()
            engine.setProperty('rate', voice_rate)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
                engine.save_to_file(tts_text, audio_file.name)
                engine.runAndWait()
                st.success("✅ Audio ready!")
                st.audio(audio_file.name)
                st.download_button("⬇️ Download MP3", open(audio_file.name, "rb").read(), file_name="text_audio.mp3")
