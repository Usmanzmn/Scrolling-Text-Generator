import streamlit as st
from moviepy.editor import ImageClip, ImageSequenceClip
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile

st.set_page_config(page_title="Scrolling Text Generator", layout="centered")
st.title("📜 Scrolling Text to Video Generator")

uploaded_file = st.file_uploader("📄 Upload a .txt file", type=["txt"])
scroll_speed = st.slider("🌀 Scroll Speed (pixels per frame)", 1, 10, 2)

if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
else:
    text = st.text_area("Or enter text manually:")

if st.button("🎥 Generate Video") and text.strip():
    with st.spinner("Generating video..."):

        width, height = 1280, 720
        bg_color = (0, 0, 0)
        text_color = (255, 255, 255)
        font_size = 36
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"  # Works on Streamlit Cloud

        lines = text.splitlines()
        line_height = font_size + 10
        total_text_height = line_height * len(lines)
        image_height = total_text_height + height  # extra space for scroll-in

        # Create a tall image with all the text
        img = Image.new("RGB", (width, image_height), color=bg_color)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, font_size)

        y = height  # start below the visible frame
        for line in lines:
            draw.text((40, y), line, font=font, fill=text_color)
            y += line_height

        tmp_dir = tempfile.mkdtemp()
        image_path = os.path.join(tmp_dir, "scroll.png")
        img.save(image_path)

        base_clip = ImageClip(image_path)
        frames = []

        for y in range(0, image_height - height, scroll_speed):
            cropped = base_clip.crop(y1=y, y2=y + height).get_frame(0)
            frames.append(cropped)

        clip = ImageSequenceClip(frames, fps=24)
        video_path = os.path.join(tmp_dir, "scrolling_text.mp4")
        clip.write_videofile(video_path, codec='libx264', audio=False)

        st.video(video_path)
        with open(video_path, "rb") as f:
            st.download_button("📥 Download MP4", f, file_name="scrolling_text.mp4")
