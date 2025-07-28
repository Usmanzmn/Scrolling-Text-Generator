import streamlit as st
import time

# Configure Streamlit to simulate 1280x720 frame
st.set_page_config(
    page_title="Scrolling Text Generator",
    layout="centered"
)

st.markdown("<h1 style='text-align: center;'>🎬 1280x720 Scrolling Text</h1>", unsafe_allow_html=True)

# Input text and speed
raw_text = st.text_area("Enter your text (each line will scroll):", height=300)
speed = st.slider("Scroll speed (seconds per line)", 0.1, 1.0, 0.3)

# Video-style font and dimensions
video_frame_style = """
<style>
.scroll-box {
    width: 1280px;
    height: 720px;
    background-color: black;
    color: white;
    font-size: 32px;
    font-family: monospace;
    padding: 30px;
    overflow: hidden;
    line-height: 1.6;
}
</style>
"""

# Apply style
st.markdown(video_frame_style, unsafe_allow_html=True)

# Start scrolling
start = st.button("Start Scrolling")

if start and raw_text.strip():
    lines = raw_text.strip().split("\n")
    display = st.empty()
    
    for i in range(len(lines) + 20):  # extra space for smooth ending
        visible_lines = lines[max(0, i - 20):i]  # show last 20 lines max
        scroll_html = f"""
        <div class="scroll-box">
        {"<br>".join(visible_lines)}
        </div>
        """
        display.markdown(scroll_html, unsafe_allow_html=True)
        time.sleep(speed)
