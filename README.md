# Video Processing Toolkit

A Python script for embedding sound waveform visualization into videos. Useful for example to select start and end points based on video and audio, for later processing.

## Features

- **Extract Streams**: Splits the video into separate audio and video streams.
- **Audio Processing**: Downsamples and pads the audio stream.
- **Video Processing**: Downsamples video frames and extends them vertically to make space for sound visualization.
- **Sound Visualization**: Generates several sound wave visualizations (at different time-axis zoom levels) for each video frame and integrates them into the video.
- **Final Composition**: Combines the processed video with the original audio, incorporating the sound visualizations into the final video output.

![Example](examples/example.png "This is a screenshot of an example input.")

## Prerequisites

To run this script, you'll need:
- Python 3
- OpenCV (`cv2`) for video processing
- NumPy for numerical operations
- SciPy for audio file operations
- Matplotlib for generating sound visualizations
- FFmpeg installed on your system for handling video and audio stream extraction and merging

## How to Use

1. **Prepare Your Environment**: Ensure you have all the necessary libraries and FFmpeg installed.
2. **Structure Your Directories**: By default, the script expects a directory named `videos` in the script's root to contain your input `.mp4` videos.
3. **Generate Calibration Video (Optional)**: To test the script with a calibration video, first run the `generate_calibration_video.py` script. This will create a modulated sine wave audio file and a corresponding video displaying a pattern synchronized with the audio. Use the command:
  ```
  python calibration_creator.py
  ```
  The script generates a file named `test_video_with_sound.mp4` in the `videos/` directory.
4. **Run the Main Script**: Execute the main script with Python 3.
  ```
  python process_videos.py
  ```
  You can also call the `process_video` function directly with the filename of the generated calibration video (`test_video_with_sound.mp4`) or any other video file as an argument.
5. **Output**: The processed videos, including any calibration videos you generated and processed, will be saved in the `videos_with_sound_vis/` directory.

## Directory Structure

- `videos/`: Input directory for original videos.
- `temp_wavs/`: Temporary storage for extracted audio files. (auto-generated inside root)
- `temp_images/`: Temporary storage for processed frames with sound visualization. (auto-generated inside root)
- `temp_silent_videos/`: Temporary storage for video streams without audio. (auto-generated inside root)
- `videos_with_sound_vis/`: Output directory for videos processed with sound visualization. (auto-generated inside root)

## Customization

You can customize the behaviour by modifying parameters such as:
- `frame_audio_durations`: Durations of audio to visualize on each frame.
- `audio_ds_factor`, `image_ds_factor`: Downsampling factors for audio and video, respectively.

## Contributing

Contributions are welcome! If you'd like to improve the script or add new features, feel free to fork the repository and submit a pull request.

## Acknowledgments

- Creator: Enrico Varano
- This project is open-sourced.
- This script was created for educational and experimental purposes. It demonstrates how to integrate sound visualization into video processing workflows using Python.

## Contact

For any inquiries or contributions, please open an issue on the GitHub repository page.
