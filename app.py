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

text = st.text_area("📜 Paste your text here", height=400)
font_size = st.slider("Font size", 20, 60, 40)
scroll_speed = st.slider("Scroll speed (lower = slower)", 1, 20, 5)

# Show warning for heavy settings
if font_size >= 50 and scroll_speed <= 2:
    st.warning("⚠️ High font size with low speed can crash the app. Increase scroll speed or reduce font size.")

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

        # Wrap long lines
        max_chars = (W - 2 * side_margin) // (font_size // 2)
        wrapped_lines = []
        for line in text.split("\n"):
            wrapped_lines += textwrap.wrap(line, width=max_chars)

        # Line and image height
        line_height = font.getbbox("A")[3] + 10
        total_text_height = line_height * len(wrapped_lines)
        img_height = max(total_text_height + H, H * 2)

        # Frame limit check
        scroll_range = img_height - H
        MAX_FRAMES = 3000
        if scroll_range // scroll_speed > MAX_FRAMES:
            st.error("🚫 Too much text or speed too slow. Try increasing scroll speed or lowering font size.")
            st.stop()

        # Create full image
        img = Image.new("RGB", (W, img_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        y = (img_height // 2) - (total_text_height // 2)  # Start from middle
        for line in wrapped_lines:
            w, _ = draw.textsize(line, font=font)
            x = max((W - w) // 2, side_margin)
            draw.text((x, y), line, font=font, fill="white")
            y += line_height

        # Generate frames
        frames = []
        for offset in range(0, scroll_range, scroll_speed):
            crop = img.crop((0, offset, W, offset + H))
            frames.append(np.array(crop))

        # Pause at end
        for _ in range(20):
            frames.append(frames[-1])

        # Create video
        clip = ImageSequenceClip(frames, fps=24)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            clip.write_videofile(tmpfile.name, codec="libx264", audio=False)
            video_path = tmpfile.name

    st.success("✅ Video ready!")
    st.video(video_path)
    with open(video_path, "rb") as f:
        st.download_button("⬇️ Download MP4", f.read(), file_name="scrolling_text.mp4")
