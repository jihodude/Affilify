from googleapiclient.discovery import build
from pprint import pprint
from decouple import config 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from typing import List

def initialize_selenium():
    profile_path = "/Users/jihobae/Library/Application Support/Google/Chrome/Default"  # Replace with your profile path
    chromedriver_path = "/Users/jihobae/Documents/Programming/Selenium Tiktok Manager/Tiktok-Web-Scraping/Untitled/chromedriver"  # Replace with your chromedriver path

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument(f"user-data-dir={profile_path}")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

global API_Key 
API_Key = config("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_Key)
driver = initialize_selenium()

def scrape_youtube_content(
    part: str = "snippet",
    queries: List[str] = None,
    type="video",
    max_results=1,
    order="relevance",
    relevance_language="en",
    video_license=None,
    processed_video_ids=None
):
    if processed_video_ids is None:
        processed_video_ids = set()
    queries_to_retry = []
    videos_data = {}
    bad_videos_data = {}
    video_dictionary = {}
    for query in queries:
        try:
            print(f"Processing query '{query}' with order '{order}'...")
            response = youtube.search().list(
                part=part,
                q=query,
                type=type,
                maxResults=max_results,
                order=order,
                relevanceLanguage=relevance_language,
                videoLicense=video_license
            ).execute()

            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                if video_id in processed_video_ids:
                    continue
                
                processed_video_ids.add(video_id)
                video_link = f"https://www.youtube.com/watch?v={video_id}"

                video_dictionary[video_id] = {
                        "video": 
                        {
                        "search query" : query,
                        "url": video_link,
                        "url to view" : None,
                        "title": item["snippet"].get("title", None),
                        "description": item["snippet"].get("description", None),
                        "tags" : None,
                        "category": None,
                        "upload_date": item["snippet"].get("publishedAt", None)
                        },

                        "keywords": 
                        {
                            "entities": None,
                            "adjectives": None,
                            "verbs": None,
                            "nouns": None
                        },

                        "sentiment": 
                        {
                            "polarity": None,
                            "adjectives": None,
                        },

                        "summary":
                        {
                            "summary": None,
                            "rating_score": None,
                            "suggested_content_type": None
                        }

                    }
  
        except Exception as e:
            print(f"An error occurred with query '{query}': {e}")
            queries_to_retry.append(query)
    
    return queries_to_retry, video_dictionary, processed_video_ids

def scrape_with_retries(queries, max_retry_attempts=3):
    retry_order_sequence = ["relevance", "viewCount", "rating",  "date"]
    processed_video_ids = set()

    attempt_number = 0

    while attempt_number < max_retry_attempts:
        current_order = retry_order_sequence[attempt_number % len(retry_order_sequence)]
        print(f"Attempt {attempt_number + 1}: Using order '{current_order}'")
        
        queries_to_retry, video_dictionary, processed_video_ids= scrape_youtube_content(
            queries=queries,
            max_results=1,
            order=current_order,
            relevance_language="en",
            video_license=None,
            processed_video_ids=processed_video_ids
        )

        if not queries_to_retry:
            print("All queries processed successfully.")
            break

        queries = queries_to_retry
        attempt_number += 1
    video_dictionary = get_video_info(processed_video_ids,video_dictionary)

    good_videos = {}
    bad_videos = {}

    for video_id, data in video_dictionary.items():
        url = data["video"]["url"]
        driver.get(url)
        user_input = input("Is this video good? (answer: y or n): ").lower()
        if user_input == "y":
            good_videos[video_id] = data
        elif user_input == "n":
            bad_videos[video_id] = data
        else:
            print("please type valid entry")
    return good_videos, bad_videos, video_dictionary

def get_video_info(processed_video_ids, video_dictionary):
    video_id_list = ",".join(processed_video_ids)

    try:
        response = youtube.videos().list(part="snippet", id=video_id_list).execute()
    except Exception as e:
        print(f"Error fetching video info: {e}")
    try:
        for item in response["items"]:
            video_id = item["id"]
            snippet = item["snippet"]
            tags = snippet.get("tags", [])
            
            # Get categoryId and map to category name
            category_id = snippet.get("categoryId", "Unknown")
            category_mapping = get_youtube_video_category_mapping(API_Key)
            category_name = category_mapping.get(category_id, "Unknown")
            
            video_dictionary[video_id]["video"]["tags"] = ",".join(tags)
            video_dictionary[video_id]["video"]["category"] = category_name
    except Exception as e:
        print(f"Error{e}")
    return video_dictionary

import json
import os

CACHE_FILE = "category_cache.json"

def get_youtube_video_category_mapping(api_key):
    # Check if the cache file exists
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)


    category_mapping = {}

    try:
        response = youtube.videoCategories().list(part="snippet", regionCode="US").execute()
        for item in response["items"]:
            category_id = item["id"]
            category_name = item["snippet"]["title"]
            category_mapping[category_id] = category_name
    except Exception as e:
        print(f"Error fetching category mapping: {e}")
        return {}

    # Save to cache file
    with open(CACHE_FILE, "w") as f:
        json.dump(category_mapping, f)

    return category_mapping

queries = ["video of someone smelling stinky clothes", "stock video of dirty clothes"]

good_videos, bad_videos, video_dictionary = scrape_with_retries(queries=queries)

print("good dictionaries")
pprint(good_videos)