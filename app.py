import streamlit as st
import time

st.set_page_config(page_title="Scrolling Text Generator", layout="centered")

st.title("🌀 Scrolling Text Generator")

text = st.text_input("Enter your text:")
speed = st.slider("Scroll speed (seconds per step)", 0.01, 0.3, 0.1)
direction = st.selectbox("Scroll Direction", ["Left", "Right"])

if st.button("Start Scrolling"):
    placeholder = st.empty()
    while True:
        if direction == "Left":
            text = text[1:] + text[0]
        else:
            text = text[-1] + text[:-1]
        placeholder.markdown(f"### {text}")
        time.sleep(speed)
