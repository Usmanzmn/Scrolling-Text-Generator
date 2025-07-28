import streamlit as st
import time

# Page config
st.set_page_config(page_title="Looping Scrolling Text", layout="centered")

# CSS for 1280x720 black video-style layout
st.markdown("""
    <style>
    .scroll-box {
        width: 1280px;
        height: 720px;
        background-color: black;
        color: white;
        font-size: 28px;
        font-family: monospace;
        padding: 40px;
        overflow: hidden;
        line-height: 1.8;
    }
    .center-title {
        text-align: center;
        color: white;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h2 class='center-title'>📜 Looping Scrolling Text</h2>", unsafe_allow_html=True)

# Upload or manual entry
upload = st.file_uploader("Upload a .txt file", type="txt")
if upload:
    content = upload.read().decode("utf-8")
else:
    content = st.text_area("Or enter your text manually:", height=300)

scroll_speed = st.slider("Scroll speed (seconds per step)", 0.05, 1.0, 0.15)

# Start button
if st.button("Start Scrolling"):
    if not content.strip():
        st.warning("Please upload or enter text first.")
    else:
        lines = content.strip().split("\n")
        display = st.empty()
        i = 0

        # Simulate infinite loop (Streamlit doesn't support real infinite loops, so we scroll a lot)
        for _ in range(9999):
            window_lines = lines[i:i+20]
            if len(window_lines) < 20:
                window_lines += lines[:20 - len(window_lines)]  # loop back to beginning
            i = (i + 1) % len(lines)
            scroll_html = f"""
            <div class="scroll-box">
            {'<br>'.join(window_lines)}
            </div>
            """
            display.markdown(scroll_html, unsafe_allow_html=True)
            time.sleep(scroll_speed)
