from moviepy import VideoFileClip, concatenate_videoclips, vfx, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import os
from moviepy.video.fx.Crop import Crop
import math
import random
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Current script's directory
PARENT_DIR = os.path.dirname(BASE_DIR)  # One level up
VIDEO_DIR = os.path.join(PARENT_DIR, "Content Download")
OUTPUT_DIR = os.path.join(PARENT_DIR, "Content Output")
folder_path = VIDEO_DIR

def load_video_clips(content_folder, clip_length, video_length):
    clips = []  # List to store video clips
    clips_sum = 0  # Total duration of clips added so far
    file_paths = []
    for root, _, files in os.walk(content_folder):
        for file in files:
            file_paths.append(os.path.join(root, file))
    # Iterate through video paths
    for video_path in file_paths:
        myclip = VideoFileClip(video_path)

        # Determine the duration of the clip to add
        if "giphy" in video_path:  # Handle GIFs differently if needed
            duration = min(myclip.duration, clip_length)
        else:
            duration = min(myclip.duration, clip_length)  # Use the shorter of the two

        # Add the subclip to the list
        clips.append(myclip.subclipped(0, duration))
        
        clips_sum += duration

        # Stop if the total duration meets or exceeds the desired video length
        if clips_sum >= video_length:
            break
         
    return clips

def crop_videos(clips, aspect_ratio=(9, 16)):
    cropped_clips = []
    for idx, clip in enumerate(clips):
        video_dimensions = clip.size
        width = video_dimensions[0]
        height = video_dimensions[1]
        
        width_aspect_ratio = aspect_ratio[0]
        height_aspect_ratio = aspect_ratio[1]
        x_midpoint = width / 2
        y_midpoint = height / 2

        if width > height:  # Landscape video
            new_width = height / height_aspect_ratio * width_aspect_ratio
            new_height = height
        elif height > width:  # Portrait video
            new_width = width
            new_height = width / width_aspect_ratio * height_aspect_ratio
        else:  # Square video
            new_width = height / height_aspect_ratio * width_aspect_ratio
            new_height = height

        # Ensure dimensions do not exceed video size
        new_width = min(new_width, width)
        new_height = min(new_height, height)

        # Calculate crop coordinates
        x1 = int(x_midpoint - (new_width / 2))
        y1 = int(y_midpoint + (new_height / 2))
        x2 = int(x_midpoint + (new_width / 2))
        y2 = int(y_midpoint - (new_height / 2))

        # Debugging
        print(f"Cropping: x1={x1}, y1={y1}, x2={x2}, y2={y2}, og: width={width}, height={height} to {new_width}, {new_height}")

        cropped_video = clip.cropped(x_center=x_midpoint, y_center=y_midpoint, width=new_width, height=new_height)
        cropped_clips.append(cropped_video)
    return cropped_clips

def resize_videos(clips, width, length):
    resized_clips = []
    for clip in clips:
        resized_clip = clip.with_effects([vfx.Resize((width,length))])
        resized_clips.append(resized_clip)
    return resized_clips

def concatenate_videos(clips):
    concatenated_videos = concatenate_videoclips(clips=clips, method="compose")
    return concatenated_videos

def export(video, output_path):
    video.write_videofile(output_path, codec="libx264", audio_codec="aac", bitrate="5000k", fps=30)


def informative_video(video_number=1, width=1080, height=1920, aspect_ratio=(9, 16), 
                      output_folder=OUTPUT_DIR, content_folder=VIDEO_DIR, 
                      video_length=60, clip_length=3, audio_path=None, main_query=None):

    output_path = os.path.join(output_folder, f"compilation_output_video{str(video_number)}.mp4")

    loaded_videos = load_video_clips(content_folder, video_length=video_length, clip_length=clip_length)
    cropped_clips = crop_videos(loaded_videos, aspect_ratio=aspect_ratio)
    resized_clips = resize_videos(cropped_clips, width, height)
    concatenated_videos = concatenate_videos(resized_clips)
    temp_video_path_1 = output_path.replace(".mp4", "_temp1.mp4")
    srt_path = audio_path.replace(".mp3", ".srt")
    export(concatenated_videos, output_path=temp_video_path_1)
    temp_video_path_2 = output_path.replace("_temp1.mp4", "_temp2.mp4")
    burn_subtitles(temp_video_path_1, srt_path, temp_video_path_2)
    final_output_path = output_path.replace(".mp4", f"{main_query}_final.mp4")
    merge_audio_video(video_path=temp_video_path_2, audio_path=audio_path, output_path=final_output_path)

    os.remove(temp_video_path_1)  # Clean temp file
    os.remove(temp_video_path_2)

def burn_subtitles(video_path, srt_path, output_path):
    """Burn subtitles into the video."""    
    video = VideoFileClip(video_path)
    font_path = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
    generator = lambda txt: TextClip(
    text=txt,
    font=font_path,
    font_size=80,
    color="white",
    method='caption',
    size=video.size
)
    sub_clip = SubtitlesClip(srt_path, make_textclip=generator)

    result = CompositeVideoClip((video, sub_clip), size=video.size)
    result.write_videofile(output_path, fps=video.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")

def merge_audio_video(video_path, audio_path, output_path):
    """Merges audio with the video."""
    
    video_clip = VideoFileClip(video_path)
    
    if audio_path and os.path.exists(audio_path):
        try:
            audio_clip = AudioFileClip(audio_path)
            video_clip = video_clip.with_audio(audio_clip)
        except Exception as e:
            print(f"⚠️ Error loading audio: {e}. Proceeding with video only.")

    video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", bitrate="5000k", fps=30)
    print(f"✅ Final video saved: {output_path}")



if __name__ == "__main__":
    informative_video(video_length=60, clip_length=3)