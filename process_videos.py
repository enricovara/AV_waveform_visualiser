#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 09:38:56 2024

@author: evaran
"""

import os
import cv2
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
import shutil

wavs_dir = "temp_wavs"
temp_images_dir = "temp_images"
silent_video_dir = "temp_silent_videos"
video_input_dir = "videos"
video_output_dir = "videos_with_sound_vis"

# Ensure matplotlib doesn't try to display plots in a window
# plt.switch_backend('agg')

def extract_streams(video_path, output_audio_path, output_video_path):
    os.system(f"ffmpeg -y -i '{video_path}' -q:a 0 -map a '{output_audio_path}'")
    os.system(f"ffmpeg -y -i '{video_path}' -an -c:v copy '{output_video_path}'")
    
# Parameters
frame_extension_pixels = 80*2  # Pixels to extend the frame by, vertically below
frame_audio_durations = [0.5, 30]   # Total duration of audio to associate with each frame, in seconds

audio_ds_factor = 4
image_ds_factor = 3

# def process_video(video_filename):
for video_filename in os.listdir(video_input_dir):
    print(video_filename)
    if video_filename.endswith('.mp4') and "sp14" not in video_filename:
        print("sp14" in video_filename)
        
        for _dir in [wavs_dir, temp_images_dir, silent_video_dir, video_input_dir, video_output_dir]:
            if not os.path.exists(_dir):
                os.makedirs(_dir)
        base_filename = os.path.splitext(video_filename)[0]
        video_input_path = os.path.join(video_input_dir, video_filename)
        temp_audio_path = os.path.join(wavs_dir, base_filename + '.wav')
        temp_silent_video_path = os.path.join(silent_video_dir, base_filename + '_silent.mp4')
    
        # Extract streams
        extract_streams(video_input_path, temp_audio_path, temp_silent_video_path)
    
        # Load audio and video
        samplerate, audio_data = wavfile.read(temp_audio_path)
        samplerate = samplerate/audio_ds_factor
        if audio_data.ndim == 2:
            audio_data = audio_data[::audio_ds_factor,0]
        else:
            audio_data = audio_data[::audio_ds_factor]
        
        # Pad audio data with zeros for the first and last 0.5 seconds
        padding_samples = int(np.max(frame_audio_durations)/2 * samplerate)
        padded_audio_data = np.pad(audio_data, (padding_samples, padding_samples), 'constant', constant_values=(0, 0))

        cap = cv2.VideoCapture(temp_silent_video_path)
        video_frame_rate = cap.get(cv2.CAP_PROP_FPS)
        samples_per_frame = samplerate / video_frame_rate
    
        frame_count = 0
        success = 1
        
        dpi = 100
        fig, ax = plt.subplots(dpi=dpi)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)        
    
        while 1:
            
            success, frame = cap.read()
            if not success:
                break
            frame = frame[::image_ds_factor, ::image_ds_factor, :]
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            ax.clear()
            plt.axis('off')
            fig.set_size_inches(frame.shape[1] / dpi, frame_extension_pixels / dpi)
                        
            # Extend frame vertically by frame_extension_pixels pixels
            extended_frame = np.zeros((frame.shape[0] + frame_extension_pixels, frame.shape[1], frame.shape[2]), dtype=np.uint8)
            extended_frame[:frame.shape[0], :, :] = frame
            
            for i, frame_audio_duration in enumerate(frame_audio_durations):
    
                # Audio adding logic
                half_samples_per_audio_duration = int(samplerate * frame_audio_duration/2)
                
                current_time = frame_count / video_frame_rate
                
                audio_start_sample = int(current_time*samplerate - half_samples_per_audio_duration + padding_samples)
                audio_end___sample = int(current_time*samplerate + half_samples_per_audio_duration + padding_samples)
        
                # Generate plot
                xx = np.linspace(0,1,audio_end___sample-audio_start_sample)
                
                # Create figure and axes with specified dimensions
                ax.plot(xx, padded_audio_data[audio_start_sample:audio_end___sample]+2*i*np.max(padded_audio_data), 'k', linewidth=0.6)
                
            ax.set_ylim((np.min(padded_audio_data), np.max(padded_audio_data)*3.5))
            ax.axvline(0.5, np.min(padded_audio_data), np.max(padded_audio_data)*3, color='b', linewidth=0.6)
            ax.text(0.7, 3.1*np.max(padded_audio_data), f"time:{current_time:.2f}   frame:{frame_count:06}")
            fig.canvas.draw()
                
            # Convert plot to image and insert into the frame
            plot_image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            plot_image = plot_image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            # plot_image = cv2.resize(plot_image, (frame.shape[1], frame_extension_pixels))
            
            
            extended_frame[frame.shape[0]:, :, :] = plot_image
                    
            # Save frame
            cv2.imwrite(os.path.join(temp_images_dir, f'frame_{frame_count:06d}.png'), extended_frame)
    
            frame_count += 1
            
        plt.close(fig)
        cap.release()

        # Generate video from frames
        os.system(f"ffmpeg -y -framerate {video_frame_rate} -i {temp_images_dir}/frame_%06d.png -c:v libx264 -pix_fmt yuv420p {temp_silent_video_path}")
        
        # Combine the silent video with the extracted audio
        final_video_path = os.path.join(video_output_dir, base_filename + '_with_sound_vis.mp4')
        os.system(f"ffmpeg -y -i {temp_silent_video_path} -i {temp_audio_path} -c:v copy -c:a aac -strict experimental {final_video_path}")
        
        shutil.rmtree(temp_images_dir)

# for video_filename in os.listdir(video_dir):
#     if video_filename.endswith('.mp4'):
#         process_video(video_filename)
