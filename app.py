import streamlit as st
from moviepy.editor import VideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import matplotlib.font_manager as fm
import textwrap
from gtts import gTTS

st.set_page_config(layout="centered")
st.title("📜 Scrolling Text Video with Center Highlight + Audio")

text = st.text_area("Paste your text here", height=400)
font_size = st.slider("Font size", 20, 60, 40)
highlight_lines = st.checkbox("✅ Highlight center line while reading", value=True)

MAX_CHARS = 20000
if len(text) > MAX_CHARS:
    st.warning(f"⚠️ Text too long. Only first {MAX_CHARS} characters used.")
    text = text[:MAX_CHARS]

st.caption(f"{len(text)}/{MAX_CHARS} characters")

# ------------------- Feature 1: Scrolling Video -------------------
if st.button("🎬 Generate Scrolling Video"):
    with st.spinner("Creating video..."):

        W, H = 1280, 720
        side_margin = 60

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

        line_height = font.getbbox("A")[3] + 10
        total_text_height = line_height * len(wrapped_lines)
        img_height = total_text_height + H
        y_start = (img_height - total_text_height) // 2

        # Render full image and store line positions
        line_positions = []
        img = Image.new("RGB", (W, img_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        y = y_start
        for line in wrapped_lines:
            w, _ = draw.textsize(line, font=font)
            x = max((W - w) // 2, side_margin)
            draw.text((x, y), line, font=font, fill="white")
            line_positions.append((x, y, line))
            y += line_height

        full_img_np = np.array(img)
        total_lines = len(wrapped_lines)
        duration = total_lines * 0.5  # 0.5s per line
        scroll_range = img_height - H

        def make_frame(t):
            current_line_index = int(t / 0.5)
            if current_line_index >= total_lines:
                current_line_index = total_lines - 1

            center_y_abs = line_positions[current_line_index][1]
            offset = center_y_abs - H // 2 + line_height // 2
            offset = np.clip(offset, 0, scroll_range)

            frame_img = Image.fromarray(full_img_np[offset:offset + H, :, :])
            draw_frame = ImageDraw.Draw(frame_img)

            if highlight_lines:
                for x, y_abs, line in line_positions:
                    y_rel = y_abs - offset
                    if 0 <= y_rel <= H - line_height:
                        color = "yellow" if y_abs == center_y_abs else "white"
                        draw_frame.text((x, y_rel), line, font=font, fill=color)

            return np.array(frame_img)

        clip = VideoClip(make_frame, duration=duration + 0.5)
        clip = clip.set_fps(24)

        # Save to persistent location (Downloads folder)
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", "scrolling_highlight_video.mp4")
        clip.write_videofile(downloads_path, codec="libx264", audio=False)

        st.success("✅ Video created!")
        st.video(downloads_path)
        with open(downloads_path, "rb") as f:
            st.download_button("⬇️ Download MP4", f.read(), file_name="scrolling_highlight_video.mp4")

# ------------------- Feature 2: Text to Audio -------------------
if st.button("🔊 Generate Audio (MP3)"):
    with st.spinner("Generating audio..."):
        try:
            tts = gTTS(text)
            downloads_audio_path = os.path.join(os.path.expanduser("~"), "Downloads", "text_audio.mp3")
            tts.save(downloads_audio_path)

            st.success("✅ Audio ready!")
            st.audio(downloads_audio_path)
            with open(downloads_audio_path, "rb") as f:
                st.download_button("⬇️ Download MP3", f.read(), file_name="text_audio.mp3")
        except Exception as e:
            st.error(f"❌ Failed to generate audio: {e}")
