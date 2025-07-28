import streamlit as st
import time

st.set_page_config(page_title="Vertical Scrolling Text", layout="centered")
st.title("🔼 Vertical Scrolling Text Generator")

# Text input and settings
raw_text = st.text_area("Enter your text (multiple lines):", height=200)
speed = st.slider("Scroll speed (seconds per line)", 0.1, 1.0, 0.3)

# Split the text into lines
lines = raw_text.split("\n")

# Display area
start_scroll = st.button("Start Scrolling")
if start_scroll and lines:
    display = st.empty()
    # Scroll one line at a time
    for i in range(len(lines) + 10):  # +10 adds some blank space at the end
        current_display = "\n".join(lines[max(0, i - 10):i])
        display.markdown(f"```text\n{current_display}\n```")
        time.sleep(speed)
