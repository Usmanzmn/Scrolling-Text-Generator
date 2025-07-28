import streamlit as st
from moviepy.editor import VideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tempfile
import matplotlib.font_manager as fm
import textwrap
import pyttsx3

st.set_page_config(layout="centered")
st.title("🛠️ Text Media Generator (Video + Audio)")

# User Input
text = st.text_area("📜 Paste your text here", height=400)
font_size = st.slider("🎨 Font size", 20, 60, 40)
scroll_speed = st.slider("🚀 Scroll speed (lower = slower)", 1, 20, 5)
highlight_lines = st.checkbox("✅ Highlight line while reading", value=True)

# Character limit
MAX_CHARS = 20000
if len(text) > MAX_CHARS:
    st.warning(f"⚠️ Text is too long ({len(text)} characters). Only the first {MAX_CHARS} will be used.")
    text = text[:MAX_CHARS]

st.caption(f"🧮 {len(text)}/{MAX_CHARS} characters")

# ===============================
# 📽️ Feature 1: Text to Scrolling Video
# ===============================
if st.button("🎬 Generate Scrolling Video"):
    with st.spinner("Creating video..."):

        # Setup
        W, H = 1280, 720
        side_margin = 60

        # Font
        font_path = fm.findfont(fm.FontProperties(family='DejaVu Sans'))
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        # Wrap text
        max_chars = (W - 2 * side_margin) // (font_size // 2)
        wrapped_lines = []
        for line in text.split("\n"):
            wrapped_lines += textwrap.wrap(line, width=max_chars)

        # Line height and total image height
        line_height = font.getbbox("A")[3] + 10
        total_text_height = line_height * len(wrapped_lines)
        img_height = total_text_height + H

        # Line positions
        line_positions = []
        img = Image.new("RGB", (W, img_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        y = (img_height - total_text_height) // 2
        for line in wrapped_lines:
            w, _ = draw.textsize(line, font=font)
            x = max((W - w) // 2, side_margin)
            draw.text((x, y), line, font=font, fill="white")
            line_positions.append((x, y, line))
            y += line_height

        full_img_np = np.array(img)
        scroll_range = img_height - H
        duration = len(wrapped_lines)  # 1 second per line

        def make_frame(t):
            offset = int(t * scroll_speed * 24)
            offset = min(offset, scroll_range)

            img_frame = Image.new("RGB", (W, H), color=(0, 0, 0))
            draw_frame = ImageDraw.Draw(img_frame)

            # Highlight index based on time
            current_line_idx = int(t // 1)
            highlight_line_y_abs = line_positions[current_line_idx][1] if current_line_idx < len(line_positions) else -1

            for x, y_abs, line in line_positions:
                if offset <= y_abs <= offset + H - line_height:
                    y_rel = y_abs - offset
                    color = "yellow" if (highlight_lines and y_abs == highlight_line_y_abs) else "white"
                    draw_frame.text((x, y_rel), line, font=font, fill=color)

            return np.array(img_frame)

        clip = VideoClip(make_frame, duration=duration + 1)
        clip = clip.set_fps(24)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            clip.write_videofile(tmpfile.name, codec="libx264", audio=False)
            st.success("✅ Video ready!")
            st.video(tmpfile.name)
            st.download_button("⬇️ Download MP4", open(tmpfile.name, "rb").read(), file_name="scrolling_text.mp4")

# ===============================
# 🔊 Feature 2: Text to Audio
# ===============================
if st.button("🔉 Generate Audio (Text to Speech)"):
    with st.spinner("Creating audio..."):

        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            engine.save_to_file(text, tmp_audio.name)
            engine.runAndWait()
            st.success("✅ Audio ready!")
            st.audio(tmp_audio.name)
            st.download_button("⬇️ Download MP3", open(tmp_audio.name, "rb").read(), file_name="text_audio.mp3")
