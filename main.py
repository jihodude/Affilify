import sys
import os

# Add the parent directory of 'Scrapers' and 'NLP_Processing' to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Audio.tts import generate_tts
from Scrapers.filter_scrapers import filter_videos
from Scrapers.main_scraper import get_content
from Video.Video_Creater_Scripts.informative_video import informative_video
from NLP_Processing.prepare_scraping import generate_sub_queries_and_kws
from NLP_Processing.script_generator import generate_script
from Video.video_downloader import download_videos
from Video.video_deleter import delete_all_files  # Importing prepare_scraping from NLP_Processing
import math

from pprint import pprint
from Video.video_downloader import download_videos
from pydub import AudioSegment
def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000

def create_video(video_templet,impersonation, clip_legnth, main_query, main_keywords, voice, pitch, rate, video_count, query_diversity, scrapers, video_length):
    video_length = video_length * rate
    video_dictionary = {}
    subqueries, sub_kws= generate_sub_queries_and_kws(
        subquery_count=video_count*query_diversity, 
        subkeyword_count=video_count*query_diversity, 
        main_query=main_query,
        main_keywords=main_keywords
    )
    print(f"subqueries: {subqueries}, sub_kws: {sub_kws}")
    video_number = 0
    index = 0
    while video_number < video_count:
        local_subqueries = []
        local_subkeywords = []
        video_number += 1

        while index < query_diversity * video_number and index < len(subqueries):
            local_subqueries.append(subqueries[index])
            local_subkeywords.append(sub_kws[index])
            index += 1
        #generate script: generate a 1m script for a video_templet(informative, fictional story time, motivation, life hack) video about 
        script = generate_script(video_templet, impersonation, local_subqueries, local_subkeywords ,video_count=video_count, video_length=video_length)
        tts_file_path = f"./Affilify/Audio/TTS Audio/{video_number}.mp3"
        generate_tts(text=script[video_number-1], output_file=tts_file_path, voice=voice, rate=str(rate), pitch=pitch, volume="default")
        #transcript it using assembly
        #scrape videos for the video using the templet and the length of the audio. If the templete is short, then there must be more clips. EX, audio = 60s, templete is story time and is short, then 60/3 = 20 video clips.
        tts_duration = get_audio_duration(tts_file_path)
        result_count = math.ceil(tts_duration/clip_legnth/len(scrapers))
        for scraper in scrapers:#max result is the legnth of the script/clip length/scraper count
            video_dictionary = get_content(queries=local_subqueries, search_keywords=local_subkeywords, max_results=result_count, scrapers=[f"{scraper}"], filter_video_boolean={f"{scraper}":True})
            download_videos(video_dictionary, max_length=300)
        
        #create video to the length of the audio and the clip length
        #burn the text into the video
        #add bgm using templete and audio
        #create 
        informative_video(video_number=video_number, video_length=tts_duration, clip_length=clip_legnth, audio_path=tts_file_path, main_query=main_query)
        delete_all_files()


if __name__ == "__main__":

    create_video(
        video_templet="INFORMATIVE", 
        impersonation="rapping kanye west with rhymes", 
        voice="en-US-AndrewNeural",
        rate=1.2,
        pitch="low",
        main_query="kanye west and his albums", 
        main_keywords="hip-pop, kanye west, kanye, music", 
        clip_legnth=2.5, 
        video_count=2,
        query_diversity=2,
        video_length=20, 
        scrapers=["pexels", "giphy"]
        )
    create_video(
        video_templet="INFORMATIVE", 
        impersonation="Joe Biden", 
        voice="en-US-AndrewNeural",
        rate=1.2,
        pitch="default",
        main_query="Joe Biden", 
        main_keywords="Joe Biden, USA, President", 
        clip_legnth=3, 
        video_count=2,
        query_diversity=2,
        video_length=20, 
        scrapers=["pexels", "giphy"]
        )