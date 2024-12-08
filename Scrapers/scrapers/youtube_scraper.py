from googleapiclient.discovery import build
from decouple import config 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
profile_path = "/Users/jihobae/Library/Application Support/Google/Chrome/Default"

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")


options.add_argument(f"user-data-dir={profile_path}")  # only works if the tiktok seller center is open on my default chrome.****
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Initialize ChromeDriver
service = Service(executable_path="/Users/jihobae/Documents/Programming/Selenium Tiktok Manager/Tiktok-Web-Scraping/Untitled/chromedriver")
#I am hoping this works

driver = webdriver.Chrome(service=service, options=options)

API_Key = config("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_Key)

queries = ["big bang g dragon fashion", "g dragon hair color red"]
goodVideos = []
badVideos = []
videos_data = {}
bad_videos_data = {}
for query in queries:
    try:
        response = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=2,
            order="relevance",
            relevanceLanguage="en"
        ).execute()
            
        for item in response["items"]:
            video_id = item["id"]["videoId"]
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            driver.get(video_link)
            video_dictionary = {video_id:{"url":video_link,
                                        "title":item["snippet"]["title"],
                                        "description":item["snippet"]["description"],
                                        "channel name": item["snippet"]["channelTitle"],
                                        "thumbnail":item["snippet"]["thumbnails"]["high"]["url"],
                                        "upload date": item["snippet"]["publishedAt"]}}
            
            if input("video good? y or n") == "y":
                videos_data[video_id] = video_dictionary[video_id]
            else:
                bad_videos_data[video_id] = video_dictionary[video_id]

        print(videos_data)
        print(bad_videos_data)
    except Exception as e:
        print(f"An error occurred: {e}")

