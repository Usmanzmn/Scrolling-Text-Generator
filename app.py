import streamlit as st
from moviepy.editor import ImageSequenceClip
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
import textwrap

# Constants
W, H = 1280, 720
FPS = 30
DURATION = 30  # video duration in seconds
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 40
SIDE_MARGIN = 60

st.title("🎞️ Scrolling Text Video Generator")
st.write("Paste your text below and download a video with smooth upward scrolling.")

text_input = st.text_area("✏️ Enter your text here:", height=300)
generate = st.button("🎬 Generate Scrolling Video")

if generate and text_input.strip():
    with st.spinner("Creating video..."):

        # Load font
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        # Wrap long lines considering horizontal margin
        max_chars = (W - 2 * SIDE_MARGIN) // (FONT_SIZE // 2)
        wrapped_lines = []
        for line in text_input.split("\n"):
            wrapped_lines += textwrap.wrap(line, width=max_chars)

        # Calculate height
        line_height = font.getbbox("A")[3] + 10
        total_text_height = line_height * len(wrapped_lines)
        img_height = max(total_text_height + H, H * 2)

        # Create full image with all text
        img = Image.new("RGB", (W, img_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        y = (img_height - total_text_height) // 2  # Start from middle
        for line in wrapped_lines:
            w, _ = draw.textsize(line, font=font)
            x = max((W - w) // 2, SIDE_MARGIN)
            draw.text((x, y), line, font=font, fill="white")
            y += line_height

        # Generate frames
        frames = []
        scroll_pixels = img_height - H
        pixels_per_frame = scroll_pixels / (FPS * DURATION)
        for i in range(int(FPS * DURATION)):
            top = int(i * pixels_per_frame)
            frame = img.crop((0, top, W, top + H))
            frames.append(frame)

        # Save video
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            clip = ImageSequenceClip([f for f in frames], fps=FPS)
            clip.write_videofile(tmpfile.name, codec="libx264", audio=False)

        # Display and allow download
        with open(tmpfile.name, "rb") as f:
            video_bytes = f.read()

        st.success("✅ Video ready!")
        st.video(video_bytes)
        st.download_button("⬇️ Download MP4", video_bytes, file_name="scrolling_text.mp4")
else:
    st.info("Please enter some text and click 'Generate Scrolling Video'.")
