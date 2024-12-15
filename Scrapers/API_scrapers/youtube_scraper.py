from googleapiclient.discovery import build
from pprint import pprint
from decouple import config 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from typing import List
from datetime import datetime


global API_Key 
API_Key = config("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_Key)

def scrape_youtube_content(
    part: str = "snippet",
    queries: List[str] = None,
    type="video",
    max_results=1, #limit is 80
    order="relevance",
    relevance_language="en",
    video_license=None,
    processed_video_ids=None
):
    if processed_video_ids is None:
        processed_video_ids = set()
    queries_to_retry = []
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
                videoLicense=video_license,
                eventType="completed"
            ).execute()

            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                if video_id in processed_video_ids:
                    continue
                
                processed_video_ids.add(video_id)
                video_link = f"https://www.youtube.com/watch?v={video_id}"
                upload_date = convert_to_giphy_format(item["snippet"].get("publishedAt", None))
                video_dictionary[video_id] = {
                        "video": 
                        {
                        "content_source" : "youtube",
                        "search_query" : query,
                        "url": video_link,
                        "url_to_view" : video_link,
                        "title": item["snippet"].get("title", None),
                        "description": item["snippet"].get("description", None),
                        "tags" : None,
                        "category": None,
                        "upload_date": upload_date
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

def scrape_with_retries(queries, max_retry_attempts=3, max_results=1):
    retry_order_sequence = ["relevance", "viewCount", "rating",  "date"]
    processed_video_ids = set()

    attempt_number = 0

    while attempt_number < max_retry_attempts:
        current_order = retry_order_sequence[attempt_number % len(retry_order_sequence)]
        print(f"Attempt {attempt_number + 1}: Using order '{current_order}'")
        
        queries_to_retry, video_dictionary, processed_video_ids = scrape_youtube_content(
            queries=queries,
            max_results=max_results,
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
    video_dictionary = get_video_info(processed_video_ids, video_dictionary)

    return video_dictionary

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

def convert_to_giphy_format(date_str):
    """
    Converts YouTube's publishedAt date format to Giphy's format.
    :param date_str: The date string from YouTube (ISO 8601 format).
    :return: A string in Giphy's date format ('YYYY-MM-DD HH:MM:SS') or None if invalid.
    """
    try:
        # YouTube's ISO 8601 format: '2023-12-13T15:21:00Z'
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        # Convert to Giphy's format: 'YYYY-MM-DD HH:MM:SS'
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error converting date: {e}")
        return None
    
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