import streamlit as st
from moviepy.editor import ImageSequenceClip
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
import textwrap

# Constants
W, H = 1280, 720
FPS = 30
DURATION = 30  # seconds
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 40
SIDE_MARGIN = 60  # left/right padding

st.title("🖤 Scrolling Text Video Generator")
st.write("Enter any amount of text. It'll scroll slowly from the middle upwards in a 1280x720 video.")

text_input = st.text_area("✏️ Your Scrolling Text:", height=300)
generate = st.button("🎞️ Generate Video")

if generate and text_input.strip():
    with st.spinner("📽️ Generating video..."):

        # Load font
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        # Wrap long lines
        max_chars = (W - 2 * SIDE_MARGIN) // (FONT_SIZE // 2)
        lines = []
        for line in text_input.split("\n"):
            lines += textwrap.wrap(line, width=max_chars)

        # Calculate text block height
        line_height = font.getbbox("A")[3] + 10
        text_height = line_height * len(lines)
        total_height = max(text_height + H, H * 2)

        # Create full canvas image
        img = Image.new("RGB", (W, total_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Start Y from middle of canvas
        y = (total_height - text_height) // 2
        for line in lines:
            w, _ = draw.textsize(line, font=font)
            x = max((W - w) // 2, SIDE_MARGIN)
            draw.text((x, y), line, font=font, fill="white")
            y += line_height

        # Scroll: Create frame-by-frame video
        frames = []
        scroll_range = total_height - H
        px_per_frame = scroll_range / (FPS * DURATION)
        for i in range(int(FPS * DURATION)):
            top = int(i * px_per_frame)
            frame = img.crop((0, top, W, top + H))
            frames.append(frame)

        # Write video to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            clip = ImageSequenceClip([f for f in frames], fps=FPS)
            clip.write_videofile(tmpfile.name, codec="libx264", audio=False)

        # Display + Download
        with open(tmpfile.name, "rb") as f:
            video_bytes = f.read()

        st.success("✅ Done!")
        st.video(video_bytes)
        st.download_button("⬇️ Download Video", video_bytes, file_name="scrolling_text.mp4")
else:
    st.info("Enter some text and click the button to generate a video.")
