import streamlit as st
from moviepy.editor import VideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import tempfile
import matplotlib.font_manager as fm
import textwrap

st.set_page_config(layout="centered")
st.title("🎞️ Scrolling Text Video Generator (20,000+ characters supported)")

text = st.text_area("📜 Paste your text here", height=400)
font_size = st.slider("Font size", 20, 60, 40)
scroll_speed = st.slider("Scroll speed (lower = slower)", 1, 20, 5)

MAX_CHARS = 20000
if len(text) > MAX_CHARS:
    st.warning(f"⚠️ Text is too long ({len(text)} characters). Only the first {MAX_CHARS} will be used.")
    text = text[:MAX_CHARS]

st.caption(f"🧮 {len(text)}/{MAX_CHARS} characters")

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

        # Line height & total height
        line_height = font.getbbox("A")[3] + 10
        total_text_height = line_height * len(wrapped_lines)
        img_height = total_text_height + H  # Enough room to scroll

        # Create full text image
        img = Image.new("RGB", (W, img_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Start from middle upward
        y = (img_height - total_text_height) // 2
        for line in wrapped_lines:
            w, _ = draw.textsize(line, font=font)
            x = max((W - w) // 2, side_margin)
            draw.text((x, y), line, font=font, fill="white")
            y += line_height

        full_img_np = np.array(img)
        scroll_range = img_height - H
        step = scroll_speed
        duration = scroll_range / step / 24  # total video time

        def make_frame(t):
            offset = int(t * scroll_speed * 24)
            offset = min(offset, scroll_range)
            frame = full_img_np[offset:offset + H, :, :]
            return frame

        clip = VideoClip(make_frame, duration=duration + 1)
        clip = clip.set_fps(24)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            clip.write_videofile(tmpfile.name, codec="libx264", audio=False)
            st.success("✅ Video ready!")
            st.video(tmpfile.name)
            st.download_button("⬇️ Download MP4", open(tmpfile.name, "rb").read(), file_name="scrolling_text.mp4")
