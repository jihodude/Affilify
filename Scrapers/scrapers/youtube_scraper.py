from googleapiclient.discovery import build
from decouple import config 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from typing import List

def get_youtube_video_catagory_id(API_Key):
    url = f"https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode=US&key={API_Key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for item in data.get("items", []):
            print(f"Category ID: {item['id']}, Title: {item['snippet']['title']}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def initalize_selenium():
    profile_path = "/Users/jihobae/Library/Application Support/Google/Chrome/Default"

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")


    options.add_argument(f"user-data-dir={profile_path}")  # only works if the tiktok seller center is open on my default chrome.****
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    service = Service(executable_path="/Users/jihobae/Documents/Programming/Selenium Tiktok Manager/Tiktok-Web-Scraping/Untitled/chromedriver")
    global driver
    driver = webdriver.Chrome(service=service, options=options)

API_Key = config("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_Key)
initalize_selenium()
videos_data = {}
bad_videos_data = {}


queries = ["gopro hero11 black commercial", "gopro hero11 black functions", "gopro hero11 black advertisement"]

def scrape_youtube_content(part: str = "snippet", queries: List[str] = None, type="video", max_Results=1, order="relevance", relevance_Language="en", video_License=None):
    processed_video_ids = set()
    queries_to_retry = []
    if not isinstance(queries, list):
        raise TypeError("The 'queries' parameter must be a list of strings.")
    if not queries:
        raise ValueError("The 'queries' parameter cannot be empty.")
    
    for query in queries:
        try:
            response = youtube.search().list(
                part=part,
                q=query,
                type=type,
                maxResults=max_Results,
                order=order,
                relevanceLanguage=relevance_Language,
                videoLicense=video_License
            ).execute()
            
                

            for item in response["items"]:

                video_id = item["id"]["videoId"]
                if video_id in processed_video_ids:
                    if query not in queries_to_retry:
                        queries_to_retry.append(query)
                    continue
                processed_video_ids.add(video_id)
                video_link = f"https://www.youtube.com/watch?v={video_id}"
                driver.get(video_link)
                video_dictionary = {
                    video_id: {
                        "url": video_link,
                        "title": item["snippet"].get("title", None),  # Title of the video
                        "description": item["snippet"].get("description", None),  # Description text
                        "category_id": item.get("id", None),  # YouTube category ID; None if not provided
                        "thumbnail": item["snippet"]["thumbnails"]["high"].get("url", None),  # Thumbnail URL
                        "upload_date": item["snippet"].get("publishedAt", None),  # Video upload date

                        # Keywords and POS tagging (default to None as placeholders for later processing)
                        "keywords": {
                            "entities": None,  # Entities extracted from metadata
                            "POS": {
                                "verbs": None,  # Verbs describing actions in the video
                                "adjectives": None,  # Adjectives describing qualities
                                "nouns": None  # Key nouns or topics
                            }
                        },

                        # Sentiment analysis placeholders
                        "sentiment": {
                            "polarity": None,  # Overall sentiment polarity score
                            "adjectives": None,  # Adjectives describing sentiment of the video
                            "comment_sentiment": {
                                "polarity": None,  # Sentiment of YouTube comments
                                "adjectives": None  # Adjectives extracted from comments
                            }
                        },

                        # Additional metadata fields that might come from other sources
                        "tags": None,  # Tags associated with the video (if available)
                        "transcription_sections": None,  # Placeholder for processed transcription sections
                    }
                }
                while True:  # Infinite loop until a valid response is provided
                    user_response = input("Is the video good to process? Type: y or n ").strip().lower()
                    if user_response == "y":
                        videos_data[video_id] = video_dictionary[video_id]
                        break  # Exit the loop
                    elif user_response == "n":
                        bad_videos_data[video_id] = video_dictionary[video_id]
                        break  # Exit the loop
                    else:
                        print("Invalid input! Please enter 'y' for yes or 'n' for no.")
            print(videos_data)
            print("\n")
            print(bad_videos_data)
        except Exception as e:
            print(f"An error occurred: {e}")
scrape_youtube_content(queries=queries)