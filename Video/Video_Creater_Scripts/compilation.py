from moviepy import VideoFileClip, concatenate_videoclips, vfx
import os
from moviepy.video.fx.Crop import Crop
import math
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Current script's directory
PARENT_DIR = os.path.dirname(BASE_DIR)  # One level up
VIDEO_DIR = os.path.join(PARENT_DIR, "Content Download")
OUTPUT_DIR = os.path.join(PARENT_DIR, "Content Output")
folder_path = VIDEO_DIR

def load_videos(content_folder_path):
    clips = []
    video_paths = []

    for item in os.listdir(content_folder_path):
        if os.path.isfile(os.path.join(content_folder_path, item)):
            video_paths.append(os.path.join(content_folder_path, item))


    for video_path in video_paths:
        print("loading video", video_path)
        myclip = VideoFileClip(video_path)
        if myclip.duration > 2:
            duration = myclip.duration * 0.2
        else:
            duration = myclip.duration
        clips.append(myclip.subclipped(0, duration))
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

def concatenate_videos(clips, output_path=OUTPUT_DIR):
    final_video = concatenate_videoclips(clips=clips, method="compose", )
    final_video.write_videofile(output_path, codec="libx264")

def compilation_video(video_count=1, width=1080, height=1920, aspect_ratio=(9, 16), output_folder=OUTPUT_DIR, content_folder=VIDEO_DIR):
    
    output_path = os.path.join(output_folder, f"compilation_output_video{str(video_count)}.mp4")
    loaded_videos = load_videos(content_folder)
    cropped_clips = crop_videos(loaded_videos, aspect_ratio=aspect_ratio)
    resized_clips = resize_videos(cropped_clips, width, height)
    concatenate_videos(resized_clips, output_path)

if __name__ == "__main__":
    compilation_video()