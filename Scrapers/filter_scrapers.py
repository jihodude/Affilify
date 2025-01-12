import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Scrapers.API_scrapers import giphy_scraper, youtube_scraper, pexels_scraper

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import math
import random
import time
from pprint import pprint
import undetected_chromedriver as uc
import spacy

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
def filter_videos(video_dictionaries, scraper):
    try:
        for video_dictionary in video_dictionaries:
            #load video dictionary information
            video_section_dict = video_dictionary.get("video")

            search_query = video_section_dict["search_query"]
            search_keywords = video_section_dict["search_keywords"]
            title = video_section_dict["title"]
            description = video_section_dict["description"]
            tags = video_section_dict["tags"]
            category = video_section_dict["category"]
            url = video_section_dict["url"]

            #these will be empty if they are scraped, and they will be data if it's from the db. 
            summary_section_dict = video_dictionary.get("summary")
            #word embeddings data from db
            tags_embeddings_dict = summary_section_dict["tags_embeddings"]#
            title_key_words_embeddings_dict = summary_section_dict["title_key_words_embeddings"]
            search_key_words_embeddings_dict = summary_section_dict["search_key_words_embeddings"]
            #sentence embeddings data from db
            title_embeddings = summary_section_dict["title_embeddings"]
            search_query_embeddings = summary_section_dict["search_query_embeddings"]

            #recheck logic!! my brain is fried after 7 hours of this.
            if not scraper == "db":
                if title_key_words_embeddings_dict == {}:
                    title_key_words = extract_keywords(title)
                    #generate embeddings wiht: tags
                    #summary_section_dict["title_key_words_embeddings"], title_key_words_embeddings_dict = generate_embeddings_dict(tags)
                if search_key_words_embeddings_dict == {}:
                    pass
                if title_embeddings == {}:
                    pass
                if search_query_embeddings == {}:
                    pass

            if not tags == '': #if tags exsits
                if tags_embeddings_dict == {}:
                    pass
            elif tags == '':
                title_key_words = extract_keywords(title) #this isnt neccarry but i cant fully logic comfirm that, but the idea is that title_key_words will be made in the case tag is empty, because
                #because that means it's from the scraper, and it would have a emptpy title_key_words_embeddings_dictionary. But think about if again and make sure.
                tags = title_key_words
                video_section_dict["tags"] = tags
                if tags_embeddings_dict == {}:
                    pass
                pass
                # summary_section_dict["tags_embeddings"] = generate_embeddings_dict(tags)


    except Exception as e: 
        pass

def extract_keywords(text):
    doc = nlp(text)
    nouns = []
    verbs = []
    adjectives = []
    entities = []
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

    

