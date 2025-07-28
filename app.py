import streamlit as st
from moviepy.editor import ImageSequenceClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import tempfile
import matplotlib.font_manager as fm
import textwrap

st.set_page_config(layout="centered")
st.title("🎞️ Scrolling Text Video Generator")

# Set defaults in session state
if "video_path" not in st.session_state:
    st.session_state.video_path = None

text = st.text_area("📜 Paste your text here", height=400)
font_size = st.slider("Font size", 20, 60, 40)
scroll_speed = st.slider("Scroll speed (lower = slower)", 1, 20, 5)

if st.button("🎬 Generate Scrolling Video"):
    with st.spinner("Creating video..."):

        # Video resolution
        W, H = 1280, 720
        side_margin = 60

        # Font setup
        font_path = fm.findfont(fm.FontProperties(family='DejaVu Sans'))
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        # Wrap long lines to fit within side margins
        max_chars = (W - 2 * side_margin) // (font_size // 2)
        wrapped_lines = []
        for line in text.split("\n"):
            wrapped_lines += textwrap.wrap(line, width=max_chars)

        # Estimate text height
        line_height = font.getbbox("A")[3] + 10
        total_text_height = line_height * len(wrapped_lines)
        img_height = max(total_text_height + H, H * 2)

        # Create full image
        img = Image.new("RGB", (W, img_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Start text from middle
        y = (img_height - total_text_height) // 2
        for line in wrapped_lines:
            w, _ = draw.textsize(line, font=font)
            x = max((W - w) // 2, side_margin)
            draw.text((x, y), line, font=font, fill="white")
            y += line_height

        # Generate frames
        scroll_range = img_height - H
        frames = []
        for offset in range(0, scroll_range, scroll_speed):
            crop = img.crop((0, offset, W, offset + H))
            frames.append(np.array(crop))

        # Pause at end
        for _ in range(20):
            frames.append(frames[-1])

        # Create video
        clip = ImageSequenceClip(frames, fps=24)
        tmp_path = os.path.join(tempfile.gettempdir(), "scrolling_text.mp4")
        clip.write_videofile(tmp_path, codec="libx264", audio=False)

        # Save to session state
        st.session_state.video_path = tmp_path
        st.success("✅ Video ready!")

# If video already created, show again
if st.session_state.video_path and os.path.exists(st.session_state.video_path):
    st.video(st.session_state.video_path)
    with open(st.session_state.video_path, "rb") as f:
        st.download_button("⬇️ Download MP4", f.read(), file_name="scrolling_text.mp4")
