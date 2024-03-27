#!/bin/bash

# Navigate to the videos directory
cd videos

# Create necessary directories if they don't exist
mkdir -p ../temp_waveforms ../temp_augmented ../final_output

# Process each video file in the directory
for file in *; do
    echo "Processing $file..."

    # Extract filename without extension
    filename="${file%.*}"

    # 0. Set variables
    eval $(ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height,width,nb_frames,duration,r_frame_rate "$file")
    width=${streams_stream_0_width}
    height=${streams_stream_0_height}
    frames=${streams_stream_0_nb_frames}
    duration=${streams_stream_0_duration}
    framerate=${streams_stream_0_r_frame_rate}

    echo ${width}
    echo ${height}
    echo ${frames}
    echo ${duration}
    echo ${framerate}

    # 1. Generate waveform image
    #ffmpeg -y -i "$file" -filter_complex "[0:a]aformat=channel_layouts=mono,volume=20.0,showwavespic=s=${width}x120:colors=white" -frames:v 1 "../temp_waveforms/${filename}_waveform.png"

    # 2. Convert waveform image to a static video of the same duration as the original video
    #ffmpeg -y -loop 1 -i "../temp_waveforms/${filename}_waveform.png" -c:v libx264 -t ${duration} -pix_fmt yuv420p -vf "scale=${width}:-2, fps=${framerate}" "../temp_waveforms/${filename}_waveform.mp4"

    # 3. Paste waveform video onto the bottom of the original video
    #ffmpeg -y -i "$file" -i "../temp_waveforms/${filename}_waveform.mp4" -filter_complex "[0:v][1:v] vstack=inputs=2" -r $framerate -codec:a copy "../temp_augmented/${filename}_with_waveform.mp4"

    # 4. Generate progress bar video with moving bar using FFmpeg's default font
    #ffmpeg -y -i "../temp_augmented/${filename}_with_waveform.mp4" -vf "drawtext=text='|':fontcolor=red:fontsize=30:x=(t/${duration})*w:y=main_h-75" -codec:a copy "../temp_augmented/${filename}_with_progress.mp4"
	
    # 5. Create a stretched version of the waveform so that we can then use it as a horizontally zoomed in, sliding version of the waveform
    stretch_factor=103
    new_width=$(echo "$width*$stretch_factor" | bc)  # Calculating new width
    ffmpeg -y -i "$file" -filter_complex "[0:a]aformat=channel_layouts=mono,volume=20.0,showwavespic=s=${new_width}x120:colors=white" -frames:v 1 "../temp_waveforms/${filename}_waveform_stretched.png"

    # 6. Apply crop and pan effect to the stretched waveform and save to a new file
    input="../temp_waveforms/${filename}_waveform_stretched.mp4"
    output="../temp_waveforms/${filename}_panned.mp4"
    original_width=$(echo "$width*$stretch_factor" | bc)
    crop_width=$width  # Keep the crop width equal to the original video width for a full-width view
    crop_height=120
    initial_offset_x=${duration}/${stretch_factor}
    # initial_offset_x=-$(echo "$crop_width / 2" | bc) # Center the crop at the beginning

    exit

    ffmpeg -y -i "$input" -filter_complex \
    "crop=${crop_width}:${crop_height}:((${original_width}-${crop_width})*t/${duration}+${initial_offset_x}):0" \
    -r $framerate -c:v libx264 -pix_fmt yuv420p "$output"

    # 7. Stack the panned waveform below the _with_progress video
    ffmpeg -y -i "../temp_augmented/${filename}_with_progress.mp4" -i "$output" -filter_complex \
    "[0:v][1:v] vstack=inputs=2" -r $framerate -codec:a copy "../temp_augmented/${filename}_with_progress_zoomed.mp4"

    # 8. Add a fixed progress bar on top of the sliding waveform.
    ffmpeg -y -i "../temp_augmented/${filename}_with_progress_zoomed.mp4" -vf "drawtext=text='|':fontcolor=red:fontsize=30:x=(w/2):y=main_h-75" -codec:a copy "../final_output/${filename}_augmented.mp4"


    

    echo "Finished processing $file."
done

echo "All videos processed."
