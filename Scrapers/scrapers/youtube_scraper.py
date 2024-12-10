from googleapiclient.discovery import build
from pprint import pprint
from decouple import config 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from typing import List

def get_youtube_video_category_id(API_Key):
    url = f"https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode=US&key={API_Key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for item in data.get("items", []):
            print(f"Category ID: {item['id']}, Title: {item['snippet']['title']}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

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
                driver.get(video_link)

                video_dictionary = {
                    video_id: {
                        "url": video_link,
                        "title": item["snippet"].get("title", None),
                        "description": item["snippet"].get("description", None),
                        "category_id": item.get("id", None),
                        "thumbnail": item["snippet"]["thumbnails"]["high"].get("url", None),
                        "upload_date": item["snippet"].get("publishedAt", None),

                        # Keywords and POS tagging (default to None as placeholders for later processing)
                        "keywords": {
                            "entities": None,
                            "POS": {
                                "verbs": None,
                                "adjectives": None,
                                "nouns": None
                            }
                        },

                        # Sentiment analysis placeholders
                        "sentiment": {
                            "polarity": None,
                            "adjectives": None,
                            "comment_sentiment": {
                                "polarity": None,
                                "adjectives": None
                            }
                        },

                        # Additional metadata fields
                        "tags": None,
                        "transcription_sections": None
                    }
                }

                while True:
                    user_response = input("Is the video good to process? Type 'y' or 'n': ").strip().lower()
                    if user_response == "y":
                        videos_data[video_id] = video_dictionary[video_id]
                        break
                    elif user_response == "n":
                        bad_videos_data[video_id] = video_dictionary[video_id]
                        break
                    else:
                        print("Invalid input! Please enter 'y' or 'n'.")
        except Exception as e:
            print(f"An error occurred with query '{query}': {e}")
            queries_to_retry.append(query)
    
    return queries_to_retry, videos_data, bad_videos_data

def scrape_with_retries(queries, max_retry_attempts=3):
    retry_order_sequence = ["relevance", "viewCount", "date"]
    processed_video_ids = set()
    all_videos_data = {}
    all_bad_videos_data = {}
    attempt_number = 0

    while attempt_number < max_retry_attempts:
        current_order = retry_order_sequence[attempt_number % len(retry_order_sequence)]
        print(f"Attempt {attempt_number + 1}: Using order '{current_order}'")
        
        queries_to_retry, videos_data, bad_videos_data = scrape_youtube_content(
            queries=queries,
            max_results=2,
            order=current_order,
            relevance_language="en",
            video_license=None,
            processed_video_ids=processed_video_ids
        )
        
        all_videos_data.update(videos_data)
        all_bad_videos_data.update(bad_videos_data)

        if not queries_to_retry:
            print("All queries processed successfully.")
            break

        queries = queries_to_retry
        attempt_number += 1

    print("Final videos data:")
    pprint(all_videos_data)
    print("Final bad videos data:")
    pprint(all_bad_videos_data)


# Call the function to start processing
queries = ["gopro hero11 black commercial", "gopro hero11 black functions", "gopro hero11 black advertisement"]
scrape_with_retries(queries=queries)
