import streamlit as st
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile

# Streamlit UI
st.set_page_config(page_title="Scrolling Text Video Generator", layout="centered")
st.title("📜 Scrolling Text to Video Generator")

uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
scroll_speed = st.slider("Scroll speed (pixels per frame)", 1, 10, 2)

if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
else:
    text = st.text_area("Or enter text manually:")

if st.button("Generate Video") and text.strip():
    with st.spinner("Rendering video..."):

        # Set video dimensions
        width, height = 1280, 720
        bg_color = (0, 0, 0)
        text_color = (255, 255, 255)
        font_size = 32
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"  # safe on Streamlit Cloud

        # Create long text image
        lines = text.strip().split("\n")
        line_height = font_size + 10
        img_height = line_height * len(lines) + height  # enough for scrolling
        img = Image.new("RGB", (width, img_height), color=bg_color)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, font_size)

        y = img_height - height  # start from bottom
        for line in lines:
            draw.text((40, y), line, font=font, fill=text_color)
            y += line_height

        # Save temp image
        tmp_dir = tempfile.mkdtemp()
        img_path = os.path.join(tmp_dir, "text_image.png")
        img.save(img_path)

        # Create video by moving crop window up
        clip = ImageClip(img_path)
        frames = []
        for y in range(0, img_height - height, scroll_speed):
            frame = clip.crop(y1=y, y2=y + height).get_frame(0)
            frames.append(frame)

        video = ImageSequenceClip(frames, fps=24)

        # Save video
        video_path = os.path.join(tmp_dir, "scrolling_text.mp4")
        video.write_videofile(video_path, codec='libx264')

        # Show + download
        st.video(video_path)
        with open(video_path, "rb") as f:
            st.download_button("📥 Download MP4", f, file_name="scrolling_text.mp4")
