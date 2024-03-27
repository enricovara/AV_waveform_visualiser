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
    ffmpeg -y -i "$file" -filter_complex "[0:a]aformat=channel_layouts=mono,volume=20.0,showwavespic=s=${width}x120:colors=white" -frames:v 1 "../temp_waveforms/${filename}_waveform.png"

    # 2. Convert waveform image to a static video of the same duration as the original video
    ffmpeg -y -loop 1 -i "../temp_waveforms/${filename}_waveform.png" -c:v libx264 -t ${duration} -pix_fmt yuv420p -vf "scale=${width}:-2, fps=${framerate}" "../temp_waveforms/${filename}_waveform.mp4"

    # 3. Paste waveform video onto the bottom of the original video
    ffmpeg -y -i "$file" -i "../temp_waveforms/${filename}_waveform.mp4" -filter_complex "[0:v][1:v] vstack=inputs=2" -r $framerate -codec:a copy "../temp_augmented/${filename}_with_waveform.mp4"

    # 4. Generate progress bar video with moving bar using FFmpeg's default font
    ffmpeg -y -i "../temp_augmented/${filename}_with_waveform.mp4" -vf "drawtext=text='|':fontcolor=red:fontsize=30:x=(t/${duration})*w:y=main_h-75" -codec:a copy "../temp_augmented/${filename}_with_progress.mp4"
	
    # 5. Loop over each second of the video and generate a waveform image for that individual second, then append it to the video above using the space generated in step 5
    dirChopped="../temp_waveforms/${filename}_chopped"
    dirChoppedVideos="../temp_waveforms/${filename}_chopped_videos"
    mkdir -p "$dirChopped"
    mkdir -p "$dirChoppedVideos"
    interval=1.5
    pc () { pyexpr="from math import *; print($@)"; python -c "$pyexpr"; }
    intervals_num=$(pc "floor($duration/$interval)")
    for ((i=0; i<intervals_num; i++)); do
        echo "------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
        start_time=$(printf "%.1f" $(echo "$i * $interval" | bc))
        end_time=$(printf "%.1f" $(echo "$start_time + $interval" | bc))
	echo ${start_time}
	echo ${end_time}
        ffmpeg -y -i "$file" -filter_complex "[0:a]atrim=start=${start_time}:end=${end_time},asetpts=PTS-STARTPTS,aformat=channel_layouts=mono,volume=20.0,showwavespic=s=${width}x120:colors=white" -frames:v 1 "${dirChopped}/${i}.png"

        # 6. in a new directory called filename_videos within temp_waveforms, save each of the above generated images as videos, with a step similar to step 2. The duration of each of these should be "interval"
	ffmpeg -y -loop 1 -i "${dirChopped}/${i}.png" -c:v libx264 -t ${interval} -pix_fmt yuv420p -vf "scale=${width}:-2, fps=${framerate}" "${dirChoppedVideos}/${i}.mp4"
	echo "file '${i}.mp4'" >> "${dirChoppedVideos}/filelist.txt"

    done

    # 7. Combine the videos generated in step 6
    ffmpeg -y -f concat -safe 0 -i "${dirChoppedVideos}/filelist.txt" -c copy "../temp_waveforms/${filename}_chopped.mp4"

    # 8. Paste the new waveform video (i.e. the one saved in temp_waveforms during the loop above) onto the bottom of the original video, as done in step 3.
    ffmpeg -y -i "../temp_augmented/${filename}_with_progress.mp4" -i "../temp_waveforms/${filename}_chopped.mp4" -filter_complex "[0:v][1:v] vstack=inputs=2" -r $framerate -codec:a copy "../temp_augmented/${filename}_with_chopped.mp4"

    # 9. Add a progress bar to each interval
    cp "../temp_augmented/${filename}_with_chopped.mp4" "../final_output/${filename}.mp4"
    for ((i=0; i<intervals_num; i++)); do
        start_time=$(printf "%.1f" $(echo "$i * $interval" | bc))
        end_time=$(printf "%.1f" $(echo "$start_time + $interval" | bc))
        echo "......................................................................................................................................................................................................................................................................................................................................................................................................................................................."
	echo ${start_time}
	echo ${end_time}
	ffmpeg -y -i "../final_output/${filename}.mp4" -vf "drawtext=text='|':fontcolor=red:fontsize=30:x='if(gte(t,${start_time}),min((t-${start_time})/(${end_time}-${start_time})*w,w),-w)':y=main_h-75" -codec:a copy "../final_output/${filename}_temp.mp4"
	cp "../final_output/${filename}_temp.mp4" "../final_output/${filename}.mp4"

    done


    echo "Finished processing $file."
done

echo "All videos processed."
