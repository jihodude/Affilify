import requests
from pprint import pprint
from decouple import config 
import datetime
import sqlite3

API_Key = config("PEXELS_API_KEY")
popular_video_endpoint = "https://api.pexels.com/videos/popular"
video_endpoint = "https://api.pexels.com/videos/search"
    # :param endpoint: API endpoint, either search or popular
    # :param query: Search term (required for search endpoint)
    # :param orientation: Desired video orientation ('landscape', 'portrait', 'square')
    # :param size: Desired video size ('small', 'medium', 'large')
    # :param locale: Language/locale for the results (e.g., 'en-US', 'es-ES')
    # :param per_page: Number of results per page (default 15, max 80)
    # :param page: Page number for pagination (default 1)
    # :return: JSON response with video data
headers = {"Authorization": API_Key}

def get_videos(endpoint=video_endpoint, query=None, orientation=None, size="large", locale=None, per_page=2, page=1):
    parameters = {"query":query,
                  "orientation":orientation,
                  "size":size,
                  "locale":locale,
                  "per_page":per_page,
                  "page":page}
    response = requests.get(endpoint, headers=headers, params=parameters)
    
    if response.status_code == 200:
        total_quota = response.headers.get("X-Ratelimit-Limit")
        remaining_quota = response.headers.get("X-Ratelimit-Remaining")
        reset_time = response.headers.get("X-Ratelimit-Reset")
        print(f"Total Quota: {total_quota}")
        print(f"Remaining Quota: {remaining_quota}")
        print(f"Quota Resets At: {datetime.datetime.fromtimestamp(int(reset_time))}")
        print('response')
        pprint(response.json())
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_popular_video(orientation=None, size="large", locale=None, per_page=2, page=1):
    results = get_videos(
        endpoint=popular_video_endpoint,
        orientation=orientation,
        size=size,
        locale=locale,
        per_page=per_page,
        page=page
    )
    if results:
        print(f"Total Results: {results.get('total_results', 0)}")
        for video in results.get("videos", []):
            print(f"Video ID: {video['id']}, URL: {video['url']},Tags {video['tags']}, Duration {video['duration']}")

get_videos(query="monkeys")