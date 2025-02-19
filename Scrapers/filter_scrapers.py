# Standard library imports
import os
import sys
import math
import random
import time
import json
# Third-party imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from decouple import config
import spacy
from pprint import pprint
from openai import OpenAI

# Custom imports (ensure these paths are correct)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Scrapers.API_scrapers import giphy_scraper, youtube_scraper, pexels_scraper

# OpenAI client setup
client = OpenAI(api_key = config("OPEN_AI_KEY_1"))
import numpy as np

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    return dot_product / (norm_a * norm_b)

def initialize_selenium():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")  # Explicit window size
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
    )

    # Initialize undetected ChromeDriver
    driver = uc.Chrome(options=options)
    return driver


import threading
import time

nlp = spacy.load("en_core_web_sm")

# def test_filter_videos_for_cos(video_dictionary, scraper):
#     driver = initialize_selenium()
#     try:
#         goodCos = []
#         badCos = []
#         manually_filtered_good_videos = {}
#         manually_filtered_bad_videos = {}

#         for video_id, data in video_dictionary.items():
#             if not data:  # Skip invalid or None entries
#                 continue
            
#             url = data["video"]["url_to_view"]
#             title = data["video"]["title"]
#             search_query = data["video"]["search_query"]
#             print(f"Loading video: {url}")
#             # Declare user_input variable in the outer scope
#             user_input = ""
#             # Flag to detect when user has answered
#             user_answered = threading.Event()
#             # Function to handle user input
#             title_emb = generate_embeddings(title)
#             search_query_emb = generate_embeddings(search_query)
#             cos_sim = cosine_similarity(title_emb, search_query_emb)
#             def get_user_input():
#                 nonlocal user_input  # Use the variable from the outer scope
#                 while not user_answered.is_set():  # Keep prompting until user answers
#                     print(search_query + " vs " + title + " cosine sim: " + str(cos_sim))
#                     user_input = input("Is this video good? (answer: y or n): ").lower()
#                     if user_input in ["y", "n"]:
#                         user_answered.set()  # Signal that the user has answered
#                     else:
#                         print("Invalid input. Please type 'y' for yes or 'n' for no.")

#             # Start user input thread
#             input_thread = threading.Thread(target=get_user_input)
#             input_thread.start()

#             # Load the URL
#             try:
#                 driver.set_page_load_timeout(10)  # Optional timeout for the page load
#                 driver.get(url)  # Load the video URL
#             except Exception as e:
#                 print(f"Page load issue: {e}. Moving on.")

#             # Wait for the user input thread to finish
#             while not user_answered.is_set():
#                 time.sleep(1)  # Wait for the user to answer
            
#             # Process the user input
#             if user_input == "y":
#                 manually_filtered_good_videos[video_id] = data
#                 goodCos.append(cos_sim) 
#             elif user_input == "n":
#                 manually_filtered_bad_videos[video_id] = data
#                 badCos.append(cos_sim)

#             # Ensure the input thread is closed before moving to the next video
#             input_thread.join()

#             new_data = {"good": goodCos, "bad": badCos}
#             file_name = "CosSIM.json"
#             current_directory = os.path.dirname(os.path.abspath(__file__))
#             file_path = os.path.join(current_directory, file_name)

#             # Read existing data from the JSON file, if it exists
#             if os.path.exists(file_path):
#                 with open(file_path, "r") as json_file:
#                     existing_data = json.load(json_file)
#             else:
#                 # Ensure the directory exists
#                 os.makedirs(os.path.dirname(file_path), exist_ok=True)
#                 # Create the file with initial structure
#                 existing_data = {"good": [], "bad": []}
#                 with open(file_path, "w") as json_file:
#                     json.dump(existing_data, json_file, indent=4)

#             # Append the new data to the existing data
#             existing_data["good"].extend(new_data["good"])
#             existing_data["bad"].extend(new_data["bad"])

#             # Write the updated data back to the file
#             with open(file_path, "w") as json_file:
#                 json.dump(existing_data, json_file, indent=4)
#     finally:
#         driver.quit()
#     return manually_filtered_good_videos, manually_filtered_bad_videos

def filter_videos(video_dictionaries, scraper, avg_good_cos = 0.8557902672416116, cos_value_padding_percent = 2):
    """0.7597773750817726
        0.8557902672416116
        0.8077838211616921"""
    try:
        filtered_good_videos = {}
        filtered_bad_videos = {}

        for video_id, data in video_dictionaries.items():
            #load video dictionary information
            video_section_dict = data.get("video")
            summary_section_dict = data.get("summary")

            inital_search_query = summary_section_dict["inital_search_query"]
            title = video_section_dict["title"]

            description = video_section_dict["description"]
            tags = video_section_dict["tags"]
            url = video_section_dict["url"]


            #these will be empty if they are scraped, and they will be data if it's from the db.
            if scraper != "db":
                summary_section_dict["title_embeddings"] = generate_embeddings(title)
                summary_section_dict["search_query_embeddings"] = generate_embeddings(inital_search_query)
                title_embeddings = summary_section_dict["title_embeddings"]
                search_query_embeddings = summary_section_dict["search_query_embeddings"]

                cossim = cosine_similarity(title_embeddings, search_query_embeddings)
                if cossim > avg_good_cos * (100-cos_value_padding_percent)/100:
                    print(f"{cossim} > {avg_good_cos * (100-cos_value_padding_percent)/100}")
                    filtered_good_videos[video_id] = data
                else:
                    filtered_bad_videos[video_id] = data

            if scraper == "db":
                title_embeddings = summary_section_dict["title_embeddings"]
                search_query_embeddings = summary_section_dict["search_query_embeddings"]


    except Exception as e: 
        pass
    return filtered_good_videos, filtered_bad_videos
def generate_embeddings(input, model="text-embedding-ada-002"):
    response = client.embeddings.create(
        input=input, model=model
    )
    return response.data[0].embedding
    pass

def extract_keywords(text):
    doc = nlp(text)
    nouns = []
    verbs = []
    adjectives = []
    entities = []
    keyword_dict = {}
    for token in doc:
        if not token.is_stop:
            if token.pos_ == "NOUN":
                nouns.append(token.text)
            elif token.pos_ == "VERB":
                verbs.append(token.text)
            elif token.pos_ == "ADJ":
                adjectives.append(token.text)
    for ent in doc.ents:
        entities.append(ent.text)
    keyword_dict = {"nouns" : nouns, "verbs" : verbs, "adjectives" : adjectives, "entities" : entities}
    return keyword_dict

    
if __name__ == "__main__":
    print(cosine_similarity(generate_embeddings("Monkey Picking apples from a tree"), generate_embeddings("gorilia Picking bananas from a tree")))
    print(cosine_similarity(generate_embeddings("Monkey Picking apples from a tree"), generate_embeddings("horse running over bananas on a road")))
    test_dictionary = {5968893: {'keywords': {'adjectives': None,
                        'entities': None,
                        'nouns': None,
                        'verbs': None},
           'summary': {'search_key_words_embeddings': {},
                       'search_query_embeddings': {},
                       'summary': None,
                       'tags_embeddings': {},
                       'title_embeddings': {},
                       'title_key_words_embeddings': {}},
           'video': {'content_source': 'pexels',
                     'description': None,
                     'search_keywords': 'funny cat',
                     'search_query': 'cute kitten playing',
                     'tags': '',
                     'title': 'a person massaging the paws of a kitten',
                     'upload_date': None,
                     'url': 'https://videos.pexels.com/video-files/5968893/5968893-uhd_2160_3840_30fps.mp4',
                     'url_to_view': 'https://www.pexels.com/video/a-person-massaging-the-paws-of-a-kitten-5968893/'}}}

