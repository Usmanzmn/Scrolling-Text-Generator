import streamlit as st
import time

# Page setup
st.set_page_config(page_title="Scrolling Text", layout="centered")

# Custom CSS to simulate 1280x720 video style
st.markdown("""
    <style>
    .scroll-box {
        width: 1280px;
        height: 720px;
        background-color: black;
        color: white;
        font-size: 32px;
        font-family: monospace;
        padding: 40px;
        overflow: hidden;
        line-height: 1.6;
    }
    .center-title {
        text-align: center;
        color: white;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# App title
st.markdown("<h2 class='center-title'>🎞️ Scrolling Text Generator</h2>", unsafe_allow_html=True)

# Text input and settings
raw_text = st.text_area("Enter your scrolling text (one line per row):", height=300)
speed = st.slider("Scroll speed (seconds per line)", 0.1, 1.0, 0.3)

# Start scrolling
start = st.button("Start Scrolling")

if start and raw_text.strip():
    lines = raw_text.strip().split("\n")
    display = st.empty()

    for i in range(len(lines) + 25):  # +25 for smooth scroll off screen
        visible = lines[max(0, i - 20):i]  # show last 20 lines (720p frame)
        html = f"""
        <div class="scroll-box">
        {'<br>'.join(visible)}
        </div>
        """
        display.markdown(html, unsafe_allow_html=True)
        time.sleep(speed)
