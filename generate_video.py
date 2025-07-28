from moviepy.editor import TextClip, CompositeVideoClip
import moviepy.editor as mpe

# Settings
video_width = 1280
video_height = 720
font_size = 48
scroll_speed = 50  # pixels per second
font = "Courier"  # Use a monospaced font installed on your system
text_color = "white"
bg_color = "black"
loop_duration = 60  # Total output video length in seconds

# Input your multiline text here
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

# Create the text clip
text_clip = TextClip(
    raw_text.strip(),
    fontsize=font_size,
    font=font,
    color=text_color,
    size=(video_width, None),
    method="caption",
)

# Calculate duration of one scroll cycle
text_height = text_clip.h
scroll_distance = text_height + video_height
single_scroll_duration = scroll_distance / scroll_speed

# Define scroll animation (from bottom to top)
def scrolling_position(t):
    y = video_height - (t * scroll_speed)
    return ("center", y)

# Scrolling clip for one cycle
scrolling_clip = (
    text_clip.set_position(scrolling_position)
    .set_duration(single_scroll_duration)
    .on_color(size=(video_width, video_height), color=bg_color, col_opacity=1)
)

# Loop to match the desired duration
looped_clip = scrolling_clip.loop(duration=loop_duration)

# Export final video
output_file = "scrolling_text_looped.mp4"
looped_clip.write_videofile(output_file, fps=24)
