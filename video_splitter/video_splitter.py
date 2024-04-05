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

import subprocess
import os
import csv
import numpy as np

#%% General Parameters

video_folder = os.path.join(os.path.dirname(os.getcwd()), "videos")
csv_folder = os.getcwd()
output_folder = os.path.join(os.getcwd(), "audio_start_end")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
start_buffer = 1
end___buffer = 1
    
#%%

for file in os.listdir(csv_folder):
    if file.endswith(".csv"):
        with open(file, mode='r', encoding='utf-8') as csv_file:
            
            reader = csv.reader(csv_file)
            next(reader, None)  # Skip the first empty row
            next(reader, None)  # Skip the header
            for line in reader:
                
                input_video_name = line[0] + ".mp4"
                output_video_name = line[1] + "_" + line[2] + "_" + line[3] + "_str" + line[4] + "_snt" + str(line[5]).zfill(2) + ".mp4"
                
                start_time = float(line[7]) # audio
                end___time = float(line[9]) # audio
                
                # start_time = float(line[8]) # video
                # end___time = float(line[10]) # video
                
                start_time = start_time - start_buffer
                end___time = end___time + end___buffer
                
                duration = str(np.round(end___time - start_time, 2))
                print(output_video_name, duration)
                
                subprocess.run([
                    "ffmpeg", "-y",
                    "-ss", str(start_time),
                    "-i", os.path.join(video_folder, input_video_name),
                    "-t", duration,  # Calculate duration and convert to string
                    "-c:v", "copy", "-c:a", "copy",
                    os.path.join(output_folder, output_video_name)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)