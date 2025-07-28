import streamlit as st
import tempfile
from moviepy.editor import TextClip

# UI Settings
st.set_page_config(page_title="Scrolling Text to Video", layout="centered")
st.title("🎬 Scrolling Text to MP4 (1280x720)")

# Input
raw_text = st.text_area("Enter text to scroll from bottom to top:", height=300)
scroll_speed = st.slider("Scroll speed (pixels/sec)", 20, 100, 50)
video_duration = st.slider("Video duration (seconds)", 10, 120, 60)

# Generate video
if st.button("🎥 Generate Video"):
    if not raw_text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Generating video..."):

            # Video settings
            video_width = 1280
            video_height = 720
            font_size = 48
            font = "Courier"
            bg_color = "black"
            text_color = "white"

            # Create text clip
            text_clip = TextClip(
                raw_text.strip(),
                fontsize=font_size,
                font=font,
                color=text_color,
                size=(video_width, None),
                method="caption"
            )

            # Scroll animation
            text_height = text_clip.h
            scroll_distance = text_height + video_height
            single_duration = scroll_distance / scroll_speed

            def scroll_position(t):
                y = video_height - (t * scroll_speed)
                return ("center", y)

            scrolling_clip = (
                text_clip.set_position(scroll_position)
                .set_duration(single_duration)
                .on_color(size=(video_width, video_height), color=bg_color, col_opacity=1)
            )

            # Loop the clip to match full video duration
            final_clip = scrolling_clip.loop(duration=video_duration)

            # Save to temporary file
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            output_path = temp_video.name
            final_clip.write_videofile(output_path, fps=24, codec="libx264", audio=False)

        st.success("✅ Video created!")
        st.video(output_path)
        st.download_button("📥 Download MP4", open(output_path, "rb"), file_name="scrolling_text.mp4")
