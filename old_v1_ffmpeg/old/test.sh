#!/bin/bash

# Input video file
input="/Users/evaran/Desktop/process_videos/waveforms/IMG_3232_waveform_stretched.mp4"
# Output video file
output="/Users/evaran/Desktop/process_videos/waveforms/IMG_3232_panned.mp4"


# Video duration in seconds (ffprobe is part of the ffmpeg package)
duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$input")
# Original video's width
original_width=3840
# Desired crop size (width and height)
crop_width=1200
crop_height=120
# Initial horizontal offset
initial_offset_x=-600 # Adjust this to set the starting point of the crop

# Apply crop and pan effect using ffmpeg
ffmpeg -i "$input" -filter_complex \
"crop=${crop_width}:${crop_height}:((${original_width}-${crop_width})*t/${duration}+${initial_offset_x}):0" \
-y "$output"