import streamlit as st
import time
import tempfile
import os
from moviepy.editor import TextClip, CompositeVideoClip

# Page settings
st.set_page_config(page_title="Scrolling Text Video Generator", layout="centered")
st.title("🎬 Scrolling Text to Video (1280x720)")

# User input
raw_text = st.text_area("Enter your scrolling text:", height=300)
scroll_speed = st.slider("Scroll speed (pixels/sec)", 20, 100, 50)
duration_limit = st.slider("Video length (seconds)", 10, 120, 60)

if st.button("Generate Scrolling Video"):
    with st.spinner("Creating video..."):

        # Create TextClip
        font_size = 48
        font = "Courier"  # Make sure it's installed
        video_width = 1280
        video_height = 720
        bg_color = "black"
        text_color = "white"

        text_clip = TextClip(
            raw_text.strip(),
            fontsize=font_size,
            font=font,
            color=text_color,
            size=(video_width, None),
            method="caption"
        )

        text_height = text_clip.h
        scroll_distance = text_height + video_height
        scroll_duration = scroll_distance / scroll_speed

        # Animation function
        def scroll_pos(t):
            y = video_height - (t * scroll_speed)
            return ("center", y)

        # Make scrolling clip
        scrolling_clip = (
            text_clip.set_position(scroll_pos)
            .set_duration(scroll_duration)
            .on_color(size=(video_width, video_height), color=bg_color, col_opacity=1)
        )

        # Loop to fit selected video duration
        final_clip = scrolling_clip.loop(duration=duration_limit)

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_path = temp_file.name
        final_clip.write_videofile(output_path, fps=24, codec="libx264", audio=False)

    st.success("✅ Video created!")
    st.video(output_path)
    st.download_button("📥 Download MP4", open(output_path, "rb"), file_name="scrolling_text.mp4")

