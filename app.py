import os
import tempfile
import time
import whisper
from flask import Flask, render_template, request, redirect, send_file
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

model = whisper.load_model("base")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video = request.files['video']
        if not video:
            return redirect(request.url)

        filename = secure_filename(video.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        video.save(video_path)

        # Create a temporary audio file
        audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        video_clip = VideoFileClip(video_path)
        video_clip.audio.write_audiofile(audio_temp.name)

        # Transcribe audio
        result = model.transcribe(audio_temp.name)
        segments = result['segments']

        # Overlay subtitles one line at a time
        clips = []
        for segment in segments:
            start, end, text = segment['start'], segment['end'], segment['text']
            txt_clip = TextClip(text, fontsize=50, color='white', font='Arial-Bold', method='caption', size=video_clip.size, align='center')
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(start).set_end(end)
            clips.append(txt_clip)

        final = CompositeVideoClip([video_clip, *clips])
        output_path = os.path.join(OUTPUT_FOLDER, f"subtitled_{filename}")
        final.write_videofile(output_path, codec='libx264', audio_codec='aac')

        os.remove(audio_temp.name)  # Clean up temp audio

        return send_file(output_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
