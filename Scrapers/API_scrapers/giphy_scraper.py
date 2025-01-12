import requests
from pprint import pprint
from decouple import config 
import datetime
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json

API_Key = config("GIPHY_API_KEY")
search_gif_end_point = "https://api.giphy.com/v1/gifs/search"
search_sticker_end_point = "https://api.giphy.com/v1/stickers/search"
translate_gif_end_point = "https://api.giphy.com/v1/gifs/translate"
translate_sticker_end_point = "https://api.giphy.com/v1/stickers/translate"

def get_gifs(query, search_keywords, max_results=5, offset=None, rating=None, language="en", end_point=search_gif_end_point):

    parameters = {
                "api_key" : API_Key,
                "q" : query,
                "limit" : max_results, #limit is 50
                "offset" : offset,
                "rating": rating, #g, pg, pg-13, r
                "lang" : language,
                }
    response = requests.get(end_point, params=parameters)
    
    if response.status_code == 200:
        video_dictionary = {}
        data = response.json()

        rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", -1))
        rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", 0))

        if rate_limit_remaining == 0:
            reset_time = datetime.datetime.fromtimestamp(rate_limit_reset)
            current_time = datetime.datetime.now()
            wait_time = (reset_time - current_time).seconds // 60  # Convert to minutes
            print(f"Hours quota reached, try again in {wait_time} minutes.")
            return None
        for item in data.get("data", []):
            video_id = item["id"]
            video_files_url = item["images"]["original"]["mp4"]
            video_link = video_files_url
            title = item["title"]
            tags = get_tags_from_slug(item["slug"])
            import_time = item["import_datetime"]
            video_dictionary[video_id] = {
            "video": 
            {
            "content_source" : "giphy",
            "search_query" : query,
            "search_keywords" : ",".join(search_keywords),
            "url": video_files_url,
            "url_to_view" : video_link,
            "title": title, 
            "description": None,
            "tags" : tags, 
            "upload_date": import_time
            },

            "keywords": 
            {
                "entities": None,
                "adjectives": None,
                "verbs": None,
                "nouns": None
            },

            "summary":
            {
                "tags_embeddings" : {},
                "title_key_words_embeddings" : {},
                "search_key_words_embeddings" : {},
                "title_embeddings" : {},
                "search_query_embeddings" : {},
                "summary": None
            }

        }
        return video_dictionary
    else:
        print(f"Error: {response.status.code} - {response.text}")
        return None

def get_tags_from_slug(slug):
    words = slug.split('-')[:-1]  
    tags = ','.join(words)  
    return tags