###############################################
# OPTIMIZED & FINAL YOUTUBE SCRAPER SCRIPT
###############################################

import sys
import os
import json
from datetime import datetime
from pprint import pprint
from typing import List
from decouple import config
from googleapiclient.discovery import build
import math
# If you truly need Selenium, keep these; otherwise remove.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

###############################################
# ADJUST THESE IMPORTS AS NEEDED
###############################################
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Video.video_downloader import get_video_duration  # <-- Ensure this function works as expected

###############################################
# YOUTUBE SETUP
###############################################
API_Key = config("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_Key)

###############################################
# GLOBALS
###############################################
CACHE_FILE = "category_cache.json"


def convert_to_giphy_format(date_str: str) -> str:
    """
    Converts YouTube's publishedAt date format (ISO 8601) to a standard
    YYYY-MM-DD HH:MM:SS format.
    Example input: '2023-12-13T15:21:00Z'
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error converting date: {e}")
        return None


def get_youtube_video_category_mapping(api_key: str) -> dict:
    """
    Fetch or load cached YouTube category mappings (category_id -> category_name).
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)

    category_mapping = {}
    try:
        response = youtube.videoCategories().list(
            part="snippet",
            regionCode="US"  # Adjust region if desired
        ).execute()

        for item in response["items"]:
            category_id = item["id"]
            category_name = item["snippet"]["title"]
            category_mapping[category_id] = category_name

    except Exception as e:
        print(f"Error fetching category mapping: {e}")
        return {}

    # Cache the mapping for future runs
    with open(CACHE_FILE, "w") as f:
        json.dump(category_mapping, f)

    return category_mapping


def get_video_info(processed_video_ids: set, video_dictionary: dict) -> dict:
    """
    Enrich 'video_dictionary' with tags/category by calling youtube.videos().list().
    Only requests IDs that actually exist in 'video_dictionary'.
    """
    valid_ids = [vid for vid in processed_video_ids if vid in video_dictionary]
    if not valid_ids:
        return video_dictionary  # No new info to fetch

    video_id_list = ",".join(valid_ids)
    try:
        response = youtube.videos().list(
            part="snippet",
            id=video_id_list
        ).execute()
    except Exception as e:
        print(f"Error fetching video info: {e}")
        return video_dictionary

    try:
        category_mapping = get_youtube_video_category_mapping(API_Key)
        for item in response["items"]:
            video_id = item["id"]
            snippet = item["snippet"]
            tags = snippet.get("tags", [])
            category_id = snippet.get("categoryId", "Unknown")
            category_name = category_mapping.get(category_id, "Unknown")

            video_dictionary[video_id]["video"]["tags"] = ",".join(tags)
            video_dictionary[video_id]["video"]["category"] = category_name

    except Exception as e:
        print(f"Error processing video info: {e}")

    return video_dictionary


# def scrape_youtube_content(
#     max_length: int,
#     queries: List[str],
#     search_keywords: List[str],
#     max_results: int = 1,      # number of valid videos to gather per query
#     order: str = "relevance",
#     relevance_language: str = None,
#     video_license: str = None,
#     processed_video_ids: set = None,
#     part: str = "snippet",
#     safe_search: str = "moderate",  # moderate or strict to filter out explicit
#     region_code: str = "US"
# ) -> tuple:
#     """
#     For each query, tries to gather up to 'max_results' valid videos:
#       - Increments maxResults as needed (up to 50).
#       - Skips duplicates and too-long videos.
#       - Uses 'safeSearch' and 'regionCode' to refine results.
#       - Returns:
#          (queries_to_retry, newly_found_videos, updated_processed_ids)
#     """

#     if processed_video_ids is None:
#         processed_video_ids = set()

#     queries_to_retry = []
#     video_dictionary = {}

#     # Decide if we can set videoDuration=short to skip long videos from the start
#     # if user wants only videos under 4min
#     if max_length < 240:
#         video_duration_filter = "short"
#     else:
#         video_duration_filter = "any"  # could be 'medium' or 'long' if desired

#     for query in queries:
#         print(f"\nProcessing query '{query}' with order '{order}'...") 

#         valid_video_count = 0
#         # Keep fetching until we have enough or we exceed 50
#         while valid_video_count < max_results:
#             needed = math.ceil((max_results - valid_video_count))
#             print(f" -> Attempting to fetch {max_results-valid_video_count} results for '{query}' "
#                   f"(already found {valid_video_count})")

#             try:
#                 response = youtube.search().list(
#                     part=part,
#                     q=query,
#                     type="video",
#                     maxResults=needed,
#                     order=order,
#                     videoLicense=video_license,
#                     relevanceLanguage=relevance_language,
#                     eventType="completed",
#                     safeSearch=safe_search,
#                     regionCode=region_code,
#                     # 'videoDuration' helps skip obviously too-long videos
#                     videoDuration=video_duration_filter
#                 ).execute()

#             except Exception as e:
#                 # If there's a quota error or something else, stop here
#                 print(f"An error occurred with query '{query}': {e}")
#                 break

#             items = response.get("items", [])
#             if not items:
#                 print(f" -> No results returned for '{query}'. Breaking.")
#                 break

#             for item in items:
#                 if valid_video_count >= max_results:
#                     break

#                 video_id = item["id"]["videoId"]

#                 # Check duplicates
#                 if video_id in processed_video_ids:
#                     continue

#                 video_link = f"https://www.youtube.com/watch?v={video_id}"
#                 duration = get_video_duration(video_url=video_link)

#                 # Double-check length (some short videos can be 4:01, for example)
#                 if duration > max_length:
#                     print(f" -> Skipping too-long video {video_link}, {duration}s.")
#                     continue

#                 # We got a valid video
#                 processed_video_ids.add(video_id)
#                 valid_video_count += 1

#                 snippet = item["snippet"]
#                 upload_date = convert_to_giphy_format(snippet.get("publishedAt", None))
#                 title = snippet.get("title", "")
#                 description = snippet.get("description", "")

#                 video_dictionary[video_id] = {
#                     "video": {
#                         "content_source": "youtube",
#                         "search_query": query,
#                         "search_keywords" : ",".join(search_keywords),
#                         "url": video_link,
#                         "url_to_view": video_link,
#                         "title": title,
#                         "description": description,
#                         "tags": None,
#                         "category": None,
#                         "upload_date": upload_date
#                     },
#                     "keywords": {
#                         "entities": None,
#                         "adjectives": None,
#                         "verbs": None,
#                         "nouns": None
#                     },
#                     "summary": {
#                         "inital_search_query" : query,
#                         "tags_embeddings" : {},
#                         "title_key_words_embeddings" : {},
#                         "search_key_words_embeddings" : {},
#                         "title_embeddings" : {},
#                         "search_query_embeddings" : {},
#                         "summary": None
#                     }
#                 }

#         if valid_video_count < max_results:
#             print(f" -> Found {valid_video_count}/{max_results} for '{query}'. Will retry.")
#             queries_to_retry.append(query)
#         else:
#             print(f" -> Successfully found {valid_video_count}/{max_results} for '{query}'.")

#     return queries_to_retry, video_dictionary, processed_video_ids
import math

def scrape_youtube_content(
    max_length: int,
    queries: List[str],
    search_keywords: List[str],
    max_results: int = 1,      # number of valid videos to gather per query
    order: str = "relevance",
    relevance_language: str = None,
    video_license: str = None,
    processed_video_ids: set = None,
    part: str = "snippet",
    safe_search: str = "moderate",  # 'none', 'moderate', or 'strict'
    region_code: str = "US"
) -> tuple:
    """
    For each query, tries to gather up to 'max_results' valid videos.
      - Uses pageToken for proper pagination to avoid repeating the same results.
      - Skips duplicates and too-long videos.
      - Returns: (queries_to_retry, newly_found_videos, updated_processed_ids)
    """

    if processed_video_ids is None:
        processed_video_ids = set()

    queries_to_retry = []
    video_dictionary = {}

    # Decide if we can set videoDuration=short to skip obviously long videos
    video_duration_filter = "short" if max_length < 240 else "any"

    for query in queries:
        print(f"\nProcessing query '{query}' with order '{order}'...")

        valid_video_count = 0
        next_page_token = None

        # Keep fetching until we have enough or exhaust pages
        while valid_video_count < max_results:
            needed = max_results - valid_video_count
            # The API can only return up to 50 items per call
            batch_size = min(needed, 50)

            print(
                f" -> Attempting to fetch {needed} results for '{query}' "
                f"(already found {valid_video_count}); using batch_size={batch_size}"
            )

            try:
                response = youtube.search().list(
                    part=part,
                    q=query,
                    type="video",
                    maxResults=batch_size,
                    pageToken=next_page_token,       # <--- IMPORTANT for pagination
                    order=order,
                    videoLicense=video_license,
                    relevanceLanguage=relevance_language,
                    eventType="completed",
                    safeSearch=safe_search,
                    regionCode=region_code,
                    videoDuration=video_duration_filter
                ).execute()

            except Exception as e:
                print(f"An error occurred with query '{query}': {e}")
                break

            items = response.get("items", [])
            next_page_token = response.get("nextPageToken", None)

            if not items:
                print(f" -> No results returned for '{query}'. Breaking.")
                break

            # Process each item
            for item in items:
                if valid_video_count >= max_results:
                    break

                video_id = item["id"]["videoId"]

                # Skip if we already processed this video
                if video_id in processed_video_ids:
                    continue

                video_link = f"https://www.youtube.com/watch?v={video_id}"
                duration = get_video_duration(video_link)
                if duration > max_length:
                    print(f" -> Skipping too-long video {video_link}, {duration}s.")
                    continue

                # Accept this valid video
                processed_video_ids.add(video_id)
                valid_video_count += 1

                snippet = item["snippet"]
                upload_date = convert_to_giphy_format(
                    snippet.get("publishedAt", None)
                )
                title = snippet.get("title", "")
                description = snippet.get("description", "")

                video_dictionary[video_id] = {
                    "video": {
                        "content_source": "youtube",
                        "search_query": query,
                        "search_keywords": ",".join(search_keywords),
                        "url": video_link,
                        "url_to_view": video_link,
                        "title": title,
                        "description": description,
                        "tags": None,
                        "category": None,
                        "upload_date": upload_date
                    },
                    "keywords": {
                        "entities": None,
                        "adjectives": None,
                        "verbs": None,
                        "nouns": None
                    },
                    "summary": {
                        "inital_search_query": query,
                        "tags_embeddings": {},
                        "title_key_words_embeddings": {},
                        "search_key_words_embeddings": {},
                        "title_embeddings": {},
                        "search_query_embeddings": {},
                        "summary": None
                    }
                }

            # If YouTube gave no more pages to fetch, stop
            if not next_page_token:
                break

        # After we tried all pages or got enough videos
        if valid_video_count < max_results:
            print(f" -> Found {valid_video_count}/{max_results} for '{query}'. Will retry.")
            queries_to_retry.append(query)
        else:
            print(f" -> Successfully found {valid_video_count}/{max_results} for '{query}'.")

    return (queries_to_retry, video_dictionary, processed_video_ids)


def scrape_with_retries(
    queries: List[str],
    search_keywords: List[str],
    max_length: int,
    max_results: int = 5,
    max_retry_attempts: int = 4
) -> dict:
    """
    Repeatedly attempt scraping with different 'order' until either:
     - All queries have reached 'max_results', or
     - We exhaust 'max_retry_attempts'.
    Finally, enrich results with 'get_video_info'.
    """

    retry_order_sequence = ["relevance", "viewCount", "rating", "date"]
    processed_video_ids = set()
    global_video_dictionary = {}

    attempt_number = 0
    # Keep trying until we run out of attempts OR have no queries left to retry
    while attempt_number < max_retry_attempts and queries:
        current_order = retry_order_sequence[attempt_number % len(retry_order_sequence)]
        print(f"\n==========================")
        print(f" Attempt {attempt_number + 1} of {max_retry_attempts} (order='{current_order}')")
        print(f"==========================")

        queries_to_retry, partial_dict, processed_video_ids = scrape_youtube_content(
            max_length=max_length,
            queries=queries,
            search_keywords=search_keywords,
            max_results=max_results,
            order=current_order,
            processed_video_ids=processed_video_ids
        )

        # Merge newly found videos
        for vid_id, data in partial_dict.items():
            global_video_dictionary[vid_id] = data

        if not queries_to_retry:
            print("\nAll queries reached their max_results requirement!")
            break

        queries = queries_to_retry
        attempt_number += 1

    # Enrich final dictionary with tags & category
    global_video_dictionary = get_video_info(processed_video_ids, global_video_dictionary)
    return global_video_dictionary


###############################################
# EXAMPLE USAGE (Uncomment to Run Directly)
###############################################
"""
if __name__ == "__main__":
    test_queries = ["funny cat videos", "cute kittens playing"]
    # e.g., want up to 3 valid videos per query, each under 300s in length
    final_videos = scrape_with_retries(
        queries=test_queries,
        max_length=300,    # skip videos longer than 300s (5 minutes)
        max_results=3,     # want up to 3 valid videos per query
        max_retry_attempts=4
    )
    print("\nFinal video dictionary length:", len(final_videos))
    pprint(final_videos)
"""
