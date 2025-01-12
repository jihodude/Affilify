import sys
import os

# Add the parent directory of 'Scrapers' and 'NLP_Processing' to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Scrapers.filter_scrapers import filter_videos
from Scrapers.main_scraper import get_content
from Video.Video_Creater_Scripts.compilation import compilation_video
from NLP_Processing.prepare_scraping import generate_sub_queries_and_kws
from Video.video_downloader import download_videos  # Importing prepare_scraping from NLP_Processing
import math

from pprint import pprint
from Video.video_downloader import download_videos

def create_video():
    video_dictionary = {}
    subqueries, sub_kws= generate_sub_queries_and_kws(
        subquery_count=1, 
        subkeyword_count=1, 
        main_query="cute cat videos", 
        main_keywords="cute, adorable, animals, funny, cat, kitten"
    )
    print(f"subqueries: {subqueries}, sub_kws: {sub_kws}")


    video_dictionary = get_content(queries=subqueries, search_keywords=sub_kws, max_results=2, scrapers=["pexels"], filter_video_boolean={"pexels":True})
    pprint(video_dictionary)
    download_videos(video_dictionary, max_length=300)

    video_dictionary = get_content(queries=subqueries, search_keywords=sub_kws, max_results=2, scrapers=["giphy"], filter_video_boolean={"giphy":True})
    pprint(video_dictionary)
    download_videos(video_dictionary, max_length=300)

    compilation_video()

if __name__ == "__main__":
    create_video()