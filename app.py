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

if st.button("🎬 Generate Scrolling Video"):
    with st.spinner("Creating video..."):

        # Video resolution
        W, H = 1280, 720
        side_margin = 60  # margin from left/right

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

        # Estimate total text height
        line_height = font.getbbox("A")[3] + 10
        total_text_height = line_height * len(wrapped_lines)
        img_height = max(total_text_height + H, H * 2)

        # Create full image with all text
        img = Image.new("RGB", (W, img_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        y = img_height - H
        for line in wrapped_lines:
            w, _ = draw.textsize(line, font=font)
            x = max((W - w) // 2, side_margin)
            draw.text((x, y), line, font=font, fill="white")
            y += line_height

        # Generate video frames
        scroll_range = img_height - H
        step = scroll_speed
        frames = []

        for offset in range(0, scroll_range, step):
            crop = img.crop((0, offset, W, offset + H))
            frames.append(np.array(crop))

        # Add pause at end
        for _ in range(20):
            frames.append(frames[-1])

        # Create video
        clip = ImageSequenceClip(frames, fps=24)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            clip.write_videofile(tmpfile.name, codec="libx264", audio=False)
            st.success("✅ Video ready!")
            st.video(tmpfile.name)
            st.download_button("⬇️ Download MP4", open(tmpfile.name, "rb").read(), file_name="scrolling_text.mp4")
