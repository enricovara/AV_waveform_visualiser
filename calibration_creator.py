#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 16:04:20 2024

@author: evaran

This script generates a modulated sine wave audio file and a corresponding
video displaying a pattern synchronized with the audio. The pattern alternates
between a high and low state in sync with the modulated sine wave. The final
output is a video file with the modulated sine wave as its audio track.


"""

import numpy as np
import os
import cv2
from scipy.io.wavfile import write

#%% General Parameters

duration = 10  # Duration of the signal in seconds
pattern_duration = 1  # Duration of each high/low pattern in seconds
output_subfolder = "videos/"


#%% Audio Parameters
sample_rate = 48000  # Audio sample rate
frequency = 440  # Frequency of the sine wave

# Generate time array
t = np.linspace(0, duration, int(sample_rate * duration), False)

# Generate sine wave
sine_wave = 0.5 * np.sin(2 * np.pi * frequency * t)

# Generate high and low pattern
pattern = np.tile(np.concatenate((np.ones(sample_rate * pattern_duration // 2), np.zeros(sample_rate * pattern_duration // 2))), duration // pattern_duration)

# Modulate sine wave with the pattern
modulated_sine_wave = sine_wave * pattern

# Save modulated sine wave as a WAV file
audio_temp_path = output_subfolder+'/modulated_sine_wave.wav'
write(audio_temp_path, sample_rate, modulated_sine_wave.astype(np.float32))


#%% Video Parameters
fps = 50
frame_count = duration * fps
frame_width, frame_height = 1000, 1000
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_temp_path = output_subfolder+'pattern_video.mp4'
video_writer = cv2.VideoWriter(video_temp_path, fourcc, fps, (frame_width, frame_height))

# Create frames and write to the video
for i in range(int(frame_count)):
    # Determine the color based on the pattern
    color = 255 if pattern[int(i * sample_rate / fps)] > 0 else 0
    frame = np.full((frame_height, frame_width, 3), color, dtype=np.uint8)
    video_writer.write(frame)

video_writer.release()


video_output_path = output_subfolder+'test_video_with_sound.mp4'
os.system(f"ffmpeg -y -i {video_temp_path} -i {audio_temp_path} -c:v copy -c:a aac -strict experimental {video_output_path}")
os.remove(audio_temp_path)
os.remove(video_temp_path)