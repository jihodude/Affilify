import os
import requests
import subprocess
import tempfile
from yt_dlp import YoutubeDL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "Content Download")

def get_video_duration(video_url):
    """
    Fetches the duration of the video using yt-dlp for YouTube URLs or FFprobe for direct video files.
    Parameters:
    - video_url (str): URL of the video.
    Returns:
    - duration (float): Duration of the video in seconds, or None if an error occurs.
    """
    try:
        if "youtube.com" in video_url or "youtu.be" in video_url:
            # Use yt-dlp to fetch YouTube video metadata
            with YoutubeDL({"quiet": True}) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                duration = info_dict.get("duration")  # Duration in seconds
                print(f"yt-dlp duration: {duration} seconds for {video_url}")
                return duration
        else:
            # Use FFprobe for other video sources
            ffprobe_path = "/opt/homebrew/bin/ffprobe"  # Explicit path to ffprobe
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as temp_file:
                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                        temp_file.write(chunk)
                        break
                    temp_file.flush()

                    result = subprocess.run(
                        [
                            ffprobe_path,
                            "-v", "error",
                            "-show_entries", "format=duration",
                            "-of", "default=noprint_wrappers=1:nokey=1",
                            temp_file.name,
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    output = result.stdout.strip()
                    if not output:
                        print(f"FFprobe failed for {video_url}")
                        return None
                    return float(output)
    except Exception as e:
        print(f"Error fetching video duration: {e}")
        return None


def download_video(video_url, output_file):
    """
    Downloads the video using requests for direct URLs or yt-dlp for YouTube.
    """
    try:
        if "youtube.com" in video_url or "youtu.be" in video_url:
            # Use yt-dlp for YouTube videos
            ydl_opts = {"quiet": True, "outtmpl": output_file, "format": "best"}
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        else:
            # Use requests for direct video links
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                with open(output_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
    except Exception as e:
        print(f"Error downloading video: {e}")


def download_videos(data_dict, max_length=300, output_dir=None):
    """
    Downloads videos from a data dictionary and saves them to a specified directory,
    with a maximum allowed duration.
    """
    if output_dir is None:
        output_dir = VIDEO_DIR

    os.makedirs(output_dir, exist_ok=True)

    for video_id, video_data in data_dict.items():
        try:
            video_info = video_data.get("video", {})
            video_url = video_info.get("url")
            video_title = video_info.get("title", f"video_{video_id}")
            content_source = video_info.get("content_source", "unknown")

            if not video_url:
                print(f"Skipping {video_title} (ID: {video_id}): No URL provided.")
                continue

            # Get video duration
            print(f"Checking duration for {video_title}...")
            duration = get_video_duration(video_url)
            if duration is None:
                print(f"Skipping {video_title} (ID: {video_id}): Could not determine duration.")
                continue
            if duration > max_length:
                print(f"Skipping {video_title} (ID: {video_id}): Duration exceeds {max_length} seconds.")
                continue

            # Sanitize title for filename
            safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in video_title)
            output_file = os.path.join(output_dir, f"{safe_title}_{content_source}.mp4")

            # Download the video
            print(f"Downloading: {video_title} from {content_source} ({video_url})")
            download_video(video_url, output_file)
            print(f"Saved: {output_file}")

        except Exception as e:
            print(f"Error processing video {video_title} (ID: {video_id}): {e}")


# Example usage
if __name__ == "__main__":
    scraped_data = {
        "lwXBNQ276dk": {
            "video": {
                "content_source": "youtube",
                "title": "Funny frogs catching 🐸🐸 #reptiles #frogs",
                "url": "https://www.youtube.com/watch?v=lwXBNQ276dk",
            }
        },
        "3042473": {
            "video": {
                "content_source": "pexels",
                "title": "A dog fights with his reflection in the mirror",
                "url": "https://videos.pexels.com/video-files/3042473/3042473-hd_1280_720_30fps.mp4",
            }
        },
    }
    download_videos(scraped_data, max_length=60)





# import os
# import requests
# import subprocess
# import tempfile

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# VIDEO_DIR = os.path.join(BASE_DIR, "Content Download")

# def get_video_duration(video_url):
#     """
#     Fetches the duration of the video using FFprobe without downloading the entire file.
#     Parameters:
#     - video_url (str): URL of the video.
#     Returns:
#     - duration (float): Duration of the video in seconds, or None if an error occurs.
#     """
#     try:
#         ffprobe_path = "/opt/homebrew/bin/ffprobe"  # Explicitly define the path to ffprobe
#         # Create a temporary file to download part of the video
#         with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as temp_file:
#             response = requests.get(video_url, stream=True)
#             if response.status_code == 200:
#                 # Write a small portion of the video to extract metadata
#                 for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
#                     temp_file.write(chunk)
#                     break
#                 temp_file.flush()

#                 # Use ffprobe to get duration
#                 result = subprocess.run(
#                     [
#                         ffprobe_path,
#                         "-v", "error",
#                         "-show_entries", "format=duration",
#                         "-of", "default=noprint_wrappers=1:nokey=1",
#                         temp_file.name,
#                     ],
#                     stdout=subprocess.PIPE,
#                     stderr=subprocess.PIPE,
#                     text=True,
#                 )
#                 return float(result.stdout.strip())
#     except Exception as e:
#         print(f"Error fetching video duration: {e}")
#         return None


# def download_videos(data_dict, max_length=300, output_dir=None):
#     """
#     Downloads videos from a data dictionary and saves them to a specified directory,
#     with a maximum allowed duration.
#     Parameters:
#     - data_dict (dict): The scraped data dictionary containing video metadata.
#     - max_length (int): Maximum allowed video length in seconds.
#     - output_dir (str): The directory where the videos will be saved.
#     """

#     if output_dir is None:
#         output_dir = VIDEO_DIR

#     os.makedirs(output_dir, exist_ok=True)

#     for video_id, video_data in data_dict.items():
#         try:
#             video_info = video_data.get("video", {})
#             video_url = video_info.get("url")
#             video_title = video_info.get("title", f"video_{video_id}")
#             content_source = video_info.get("content_source", "unknown")

#             if not video_url:
#                 print(f"Skipping {video_title} (ID: {video_id}): No URL provided.")
#                 continue

#             # Get video duration
#             print(f"Checking duration for {video_title}...")
#             duration = get_video_duration(video_url)
#             if duration is None or duration > max_length:
#                 print(f"Skipping {video_title} (ID: {video_id}): Duration exceeds {max_length} seconds.")
#                 continue

#             # Sanitize title for filename
#             safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in video_title)
#             output_file = os.path.join(output_dir, f"{safe_title}_{content_source}.mp4")

#             # Download the video
#             print(f"Downloading: {video_title} from {content_source} ({video_url})")
#             response = requests.get(video_url, stream=True)
#             if response.status_code == 200:
#                 with open(output_file, "wb") as f:
#                     for chunk in response.iter_content(chunk_size=1024):
#                         if chunk:
#                             f.write(chunk)
#                 print(f"Saved: {output_file}")
#             else:
#                 print(f"Failed to download {video_title} (ID: {video_id}): HTTP {response.status_code}")

#         except Exception as e:
#             print(f"Error downloading video {video_title} (ID: {video_id}): {e}")

# # Example usage
# if __name__ == "__main__":
#     scraped_data = {
#         7204507: {
#             "video": {
#                 "content_source": "pexels",
#                 "title": "A woman trying to pet a cat",
#                 "url": "https://videos.pexels.com/video-files/7204507/7204507-sd_960_540_24fps.mp4",
#             }
#         },
#         "WjldrOwZZ3EpW": {
#             "video": {
#                 "content_source": "giphy",
#                 "title": "Funny Gif Awww GIF",
#                 "url": "https://media0.giphy.com/media/WjldrOwZZ3EpW/giphy.mp4",
#             }
#         },
#     }
#     download_videos(scraped_data, max_length=60)
