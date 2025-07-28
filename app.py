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
    font_size = st.slider("Font size", 20, 80, 50)
    one_line_mode = st.checkbox("✅ Show one line at a time with yellow highlight (Reading Mode)", value=True)
    per_line_duration = st.select_slider("⏱️ Highlight duration per line (seconds)", options=[0.5, 1.0, 1.5, 2.0], value=1.0)

    MAX_CHARS = 20000
    if len(text) > MAX_CHARS:
        st.warning(f"⚠️ Text is too long ({len(text)} characters). Only the first {MAX_CHARS} will be used.")
        text = text[:MAX_CHARS]

    st.caption(f"🧮 {len(text)}/{MAX_CHARS} characters")

    if st.button("🎬 Generate Video"):
        with st.spinner("Creating video..."):

            W, H = 1280, 720
            font_path = fm.findfont(fm.FontProperties(family='DejaVu Sans'))
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()

            # Wrap text
            max_chars = W // (font_size // 2)
            wrapped_lines = []
            for line in text.split("\n"):
                wrapped_lines += textwrap.wrap(line, width=max_chars)

            line_height = font.getbbox("A")[3] + 20  # Line spacing
            total_duration = len(wrapped_lines) * per_line_duration
            fps = 24

            def make_frame(t):
                current_line = int(t // per_line_duration)
                current_line = min(current_line, len(wrapped_lines) - 1)

                img = Image.new("RGB", (W, H), color="black")
                draw = ImageDraw.Draw(img)

                if one_line_mode:
                    # One-line-at-a-time
                    line = wrapped_lines[current_line]
                    w, _ = draw.textsize(line, font=font)
                    x = max((W - w) // 2, 50)
                    y = (H - line_height) // 2
                    draw.text((x, y), line, font=font, fill="yellow")
                else:
                    # Scroll mode
                    total_text_height = len(wrapped_lines) * line_height
                    img_height = total_text_height + H
                    scroll_range = img_height - H
                    full_img = Image.new("RGB", (W, img_height), color="black")
                    full_draw = ImageDraw.Draw(full_img)
                    y_pos = (img_height - total_text_height) // 2

                    for i, line in enumerate(wrapped_lines):
                        fill = "white"
                        w, _ = full_draw.textsize(line, font=font)
                        x = max((W - w) // 2, 50)
                        full_draw.text((x, y_pos), line, font=font, fill=fill)
                        y_pos += line_height

                    offset = int((t / total_duration) * scroll_range)
                    offset = min(offset, scroll_range)
                    img = full_img.crop((0, offset, W, offset + H))

                return np.array(img)

            clip = VideoClip(make_frame, duration=total_duration + 0.1).set_fps(fps)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
                clip.write_videofile(tmpfile.name, codec="libx264", audio=False)
                st.success("✅ Video ready!")
                st.video(tmpfile.name)
                st.download_button("⬇️ Download MP4", open(tmpfile.name, "rb").read(), file_name="reading_video.mp4")

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
