#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 09:38:56 2024

@author: evaran

This Python script automates the process of adding visualized sound waves to
video files. It is designed to work with video files stored in a specified
directory, processing each by extracting the audio track, visualizing the audio
as waveforms, and then overlaying these visualizations onto the original video
frames. The script outputs the modified video with the integrated sound
visualization appended to each frame.

Dependencies:
- OpenCV: For video processing and image manipulation.
- NumPy: For efficient array operations, especially for audio signal processing.
- SciPy: Specifically, scipy.io.wavfile for reading WAV files.
- Matplotlib: For generating plots of the audio waveforms.
- FFmpeg: Command-line tool (not a Python package) used for audio and video
          processing tasks like extracting audio streams and recombining them with video.

Workflow Overview:
1. Set up directories for processing and output.
2. Iterate over videos in a specified directory, excluding specific patterns
3. Extract audio and silent video streams from each video file using FFmpeg.
4. Downsample audio data for manageable processing and overlay preparation.
5. For each video frame, extend the frame vertically and overlay a waveform
   visualization of the surrounding audio.
6. Reconstruct a video from these processed frames.
7. Combine the new video with the original audio track to produce the final
   output.

Please ensure FFmpeg is installed and accessible in your system's PATH for this
script to function correctly.
"""


import os
import cv2
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
import shutil

def extract_streams(video_path, output_audio_path, output_video_path):
    os.system(f"ffmpeg -y -i '{video_path}' -q:a 0 -map a '{output_audio_path}' > /dev/null 2>&1")
    os.system(f"ffmpeg -y -i '{video_path}' -an -c:v copy '{output_video_path}' > /dev/null 2>&1")
    

def process_video(video_filename,
                  frame_audio_durations=[0.5, 5, 20],
                  frame_extension_pixels=80,
                  audio_ds_factor=4, image_ds_factor=3,
                  video_input_dir="videos", video_output_dir="videos_with_sound_vis"):
    """
    Processes a given video file by overlaying visualized sound waveforms onto
    vertically stretched video frames. This function automates the enhancement
    of video files, creating a visual representation of the audio track
    alongside the original video content. The processed video is saved in an
    output directory with the sound visualization integrated into each frame.
    
    Parameters:
        video_filename (str): Name of the video file to process.
        frame_audio_durations (list of floats, optional): Durations in seconds
        for different lengths of audio to visualize on each frame.
            Defaults to [0.5, 5, 20].
        frame_extension_pixels (int, optional): Number of pixels to extend each
        frame vertically for the waveform visualization.
            Defaults to 80.
        audio_ds_factor (int, optional): Factor by which the audio data is
        downsampled to reduce processing load.
            Defaults to 4.
        image_ds_factor (int, optional): Factor by which the video frames are
        downsampled to reduce computational requirements.
            Defaults to 3.
        video_input_dir (str, optional): Directory containing the input video
        files.
            Defaults to "videos".
        video_output_dir (str, optional): Directory where the processed videos
        are saved.
            Defaults to "videos_with_sound_vis".
    
    Returns:
        None. The processed video file is saved in the specified output
        directory.
    
    Usage:
        process_video("example_video.mp4")
        This will process 'example_video.mp4' from the 'videos' directory,
        overlaying sound wave visualizations onto each frame, and save the
        enhanced video to 'videos_with_sound_vis' directory.
    """

    
    # directory and file naming management
    wavs_dir = "temp_wavs"
    temp_images_dir = "temp_images"
    silent_video_dir = "temp_silent_videos"
    
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
    audio_data = (audio_data - np.mean(audio_data))/np.max(np.abs(audio_data))
        
    cap = cv2.VideoCapture(temp_silent_video_path)
    video_frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Pad audio data with zeros for the first and last 0.5 seconds
    padding_samples = int(np.max(frame_audio_durations)/2 * samplerate)
    padded_audio_data = np.pad(audio_data, (padding_samples, padding_samples), 'constant', constant_values=(0, 0))
    
    # visualisation parameters
    frame_extension_pixels = frame_extension_pixels * len(frame_audio_durations)
    max_audio_ampl = np.max(np.abs(padded_audio_data))
    
    dpi = 100
    
    fig, ax = plt.subplots(dpi=dpi)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)        
    
    # for every frame
    frame_count = 0
    percent_complete = 0
    success = 1
    while 1:
        
        success, frame = cap.read()
        if not success:
            break
        frame = frame[::image_ds_factor, ::image_ds_factor, :]
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        ax.clear()
        plt.axis('off')
        fig.set_size_inches(frame.shape[1] / dpi, (frame_extension_pixels) / dpi)
                    
        # Extend frame vertically by frame_extension_pixels pixels
        extended_frame = np.zeros((frame.shape[0] + frame_extension_pixels, frame.shape[1], frame.shape[2]), dtype=np.uint8)
        extended_frame[:frame.shape[0], :, :] = frame
        
        for i, frame_audio_duration in enumerate(frame_audio_durations):

            # Audio adding logic
            half_samples_per_audio_duration = int(samplerate * frame_audio_duration/2)
            
            current_time = frame_count / video_frame_rate
            
            audio_start_sample = int(np.round(current_time*samplerate - half_samples_per_audio_duration + padding_samples))
            audio_end___sample = int(np.round(current_time*samplerate + half_samples_per_audio_duration + padding_samples))
            
            # Generate plot
            xx = np.linspace(0,1,audio_end___sample-audio_start_sample)
            
            # Create figure and axes with specified dimensions
            ax.plot(xx, padded_audio_data[audio_start_sample:audio_end___sample]+2*i*max_audio_ampl, 'k', linewidth=0.6)
            
        ax.set_ylim((-max_audio_ampl, max_audio_ampl*(2*i+1+1.5)))
        ax.plot([0.5, 0.5], [-max_audio_ampl, max_audio_ampl*(2*i+1)], color='b', linewidth=0.6)
        # ax.axvline(0.5, -max_audio_ampl, max_audio_ampl*(i-1), color='b', linewidth=0.6) # old
        ax.text(0.5, max_audio_ampl*(2*i+1.5), f"time:{current_time:.2f}\nframe:{frame_count:06}", ha='center')
        fig.canvas.draw()
            
        # Convert plot to image and insert into the frame
        plot_image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        plot_image = plot_image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        # plot_image = cv2.resize(plot_image, (frame.shape[1], frame_extension_pixels)) # old
        
        extended_frame[frame.shape[0]:, :, :] = plot_image
                
        # Save frame
        cv2.imwrite(os.path.join(temp_images_dir, f'frame_{frame_count:06d}.png'), extended_frame)

        frame_count += 1
        perc = int(np.round(frame_count/total_frames*100))
        if perc > percent_complete and perc % 5 == 0:
            print(f"{perc}%")
            percent_complete = perc
        
    plt.close(fig)
    cap.release()

    # Generate video from frames
    os.system(f"ffmpeg -y -framerate {video_frame_rate} -i {temp_images_dir}/frame_%06d.png -c:v libx264 -pix_fmt yuv420p {temp_silent_video_path} > /dev/null 2>&1")
    
    # Combine the silent video with the extracted audio
    final_video_path = os.path.join(video_output_dir, base_filename + '_with_sound_vis.mp4')
    os.system(f"ffmpeg -y -i {temp_silent_video_path} -i {temp_audio_path} -c:v copy -c:a aac -strict experimental {final_video_path} > /dev/null 2>&1")
    
    # nuke contents of the temp image dir
    shutil.rmtree(temp_images_dir); os.makedirs(temp_images_dir)
        
#%%

if __name__ == "__main__":
    video_input_dir = "videos"
    video_output_dir = "videos_with_sound_vis"
    
    # Ensure matplotlib doesn't try to display plots in a window
    plt.switch_backend('agg')
    # do plt.switch_backend('Qt5Agg') to bring back to normal after
            
    # Parameters
    frame_audio_durations = [0.5, 5, 20] # Total duration of audio to associate with each frame, in seconds
    frame_extension_pixels = 80 # Pixels to extend the frame by, vertically below
    
    # downsampling factors to reduce computation time and storage requirements
    # keep high for speed and lightness, keep low for latency accuracy etc
    audio_ds_factor = 4
    image_ds_factor = 3
    
    for video_filename in os.listdir(video_input_dir):
        if video_filename.endswith('.MTS'):
        # if video_filename == "output.mp4": # debug
            print(video_filename)
            process_video(video_filename, frame_audio_durations, frame_extension_pixels,
                          audio_ds_factor, image_ds_factor,
                          video_input_dir, video_output_dir)
