from moviepy.editor import TextClip, CompositeVideoClip
import moviepy.editor as mpe

# Parameters
video_width = 1280
video_height = 720
font_size = 48
duration_per_line = 0.5  # seconds per line
lines_visible = 15        # number of lines on screen at once
background_color = 'black'
text_color = 'white'
font = 'Courier'  # or any mono font installed (like 'DejaVu Sans Mono')

# Input your multiline text
raw_text = """
Welcome to the Scrolling Text Generator!
This is line 1.
This is line 2.
This is line 3.
This is line 4.
This is line 5.
This is line 6.
This is line 7.
This is line 8.
This is line 9.
This is line 10.
This is line 11.
This is line 12.
Enjoy the scroll!
"""

# Prepare lines
lines = raw_text.strip().split("\n")
total_lines = len(lines)
scroll_duration = duration_per_line * (total_lines + lines_visible)

# Create full text block
full_text = "\n".join(lines)
text_clip = TextClip(full_text, fontsize=font_size, font=font, color=text_color, size=(video_width, None), method='caption')

# Calculate scroll animation
def make_scroll_clip(text_clip):
    return text_clip.set_position(lambda t: ('center', video_height - (t * video_height / scroll_duration))) \
                    .set_duration(scroll_duration) \
                    .on_color(size=(video_width, video_height), color=background_color, col_opacity=1)

scrolling_clip = make_scroll_clip(text_clip)

# Export
output_file = "scrolling_text.mp4"
scrolling_clip.write_videofile(output_file, fps=24)
