import streamlit as st
from moviepy.editor import VideoClip, AudioFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tempfile
import matplotlib.font_manager as fm
import textwrap
from gtts import gTTS
import os

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

# ————— Feature 1: Scrolling Video —————
if st.button("🎬 Generate Scrolling Video"):
    with st.spinner("Creating video..."):

        W, H = 1280, 720
        side_margin = 60

        font_path = fm.findfont(fm.FontProperties(family='DejaVu Sans'))
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        max_chars = (W - 2 * side_margin) // (font_size // 2)
        wrapped_lines = []
        for line in text.split("\n"):
            wrapped_lines += textwrap.wrap(line, width=max_chars)

        line_height = font.getbbox("A")[3] + 10
        total_text_height = line_height * len(wrapped_lines)
        img_height = total_text_height + H
        y_start = (img_height - total_text_height) // 2

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
        duration = total_lines * 0.5
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

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            clip.write_videofile(tmpfile.name, codec="libx264", audio=False)
            st.success("✅ Video created!")
            st.video(tmpfile.name)
            st.download_button("⬇️ Download MP4", open(tmpfile.name, "rb").read(), file_name="scrolling_highlight_video.mp4")

# ————— Feature 2: Sync Highlight with Audio —————
if st.button("🟡 Generate Sync Video (Highlight While Speaking)"):
    with st.spinner("Creating synchronized video..."):
        try:
            tts = gTTS(text)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audiofile:
                tts.save(audiofile.name)

                W, H = 1280, 720
                side_margin = 60
                font_path = fm.findfont(fm.FontProperties(family='DejaVu Sans'))
                font = ImageFont.truetype(font_path, font_size)

                wrapped_lines = []
                for line in text.split("\n"):
                    wrapped_lines += textwrap.wrap(line, width=(W - 2 * side_margin) // (font_size // 2))

                line_height = font.getbbox("A")[3] + 10
                total_lines = len(wrapped_lines)

                audio = AudioFileClip(audiofile.name)
                audio_duration = audio.duration
                duration_per_line = audio_duration / total_lines

                def make_sync_frame(t):
                    current_line_index = int(t / duration_per_line)
                    if current_line_index >= total_lines:
                        current_line_index = total_lines - 1

                    img = Image.new("RGB", (W, H), color=(0, 0, 0))
                    draw = ImageDraw.Draw(img)
                    start_line = max(0, current_line_index - 3)
                    end_line = min(total_lines, current_line_index + 4)

                    y = H // 2 - (line_height * (current_line_index - start_line))

                    for i in range(start_line, end_line):
                        line = wrapped_lines[i]
                        w, _ = draw.textsize(line, font=font)
                        x = max((W - w) // 2, side_margin)
                        color = "yellow" if i == current_line_index else "white"
                        draw.text((x, y), line, font=font, fill=color)
                        y += line_height

                    return np.array(img)

                sync_clip = VideoClip(make_sync_frame, duration=audio_duration)
                sync_clip = sync_clip.set_audio(audio).set_fps(24)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
                    sync_clip.write_videofile(tmpfile.name, codec="libx264", audio_codec="aac")
                    st.success("✅ Sync Video created!")
                    st.video(tmpfile.name)
                    st.download_button("⬇️ Download Sync Video", open(tmpfile.name, "rb").read(), file_name="sync_highlight_video.mp4")

        except Exception as e:
            st.error(f"❌ Failed to generate synchronized video: {e}")

# ————— Feature 3: Text to Audio Only —————
if st.button("🔊 Generate Audio (MP3)"):
    with st.spinner("Generating audio..."):
        try:
            tts = gTTS(text)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audiofile:
                tts.save(audiofile.name)
                st.success("✅ Audio ready!")
                st.audio(audiofile.name)
                st.download_button("⬇️ Download MP3", open(audiofile.name, "rb").read(), file_name="text_audio.mp3")
        except Exception as e:
            st.error(f"❌ Failed to generate audio: {e}")

# ————— Feature 4: Replace Background with Images —————
st.header("📽 Replace Background in Existing Video")
uploaded_video = st.file_uploader("Upload scrolling text video (MP4)", type=["mp4"])
uploaded_images = st.file_uploader("Upload background images (JPG or PNG)", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_video and uploaded_images:
    if st.button("🎨 Generate New Video with Replaced Background"):
        with st.spinner("Processing background replacement..."):

            from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
            import random

            video = VideoFileClip(uploaded_video.name)
            bg_images = [Image.open(img).resize((1280, 720)) for img in uploaded_images]
            bg_nps = [np.array(img) for img in bg_images]
            num_images = len(bg_nps)

            def generate_video_with_images():
                bg_index = 0  # Now properly scoped

                def make_frame(t):
                    nonlocal bg_index
                    bg_index = int(t // 1) % num_images  # change background every second
                    bg = bg_nps[bg_index]
                    frame = video.get_frame(t)
                    frame_rgba = np.dstack((frame, np.full((frame.shape[0], frame.shape[1]), 255, dtype=np.uint8)))
                    result = Image.alpha_composite(Image.fromarray(bg).convert("RGBA"), Image.fromarray(frame_rgba).convert("RGBA"))
                    return np.array(result.convert("RGB"))

                new_clip = VideoClip(make_frame, duration=video.duration).set_fps(video.fps)
                return new_clip

            final_video = generate_video_with_images()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as out_file:
                final_video.write_videofile(out_file.name, codec="libx264", audio=False)
                st.success("✅ Video with new background created!")
                st.video(out_file.name)
                st.download_button("⬇️ Download Video with New Background", open(out_file.name, "rb").read(), file_name="background_replaced_video.mp4")
