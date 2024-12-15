from API_scrapers import giphy_scraper, youtube_scraper, pexels_scraper

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import math
import random
import time
from pprint import pprint
import undetected_chromedriver as uc

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

import threading
import time

def filter_videos(video_dictionary):
    driver = initialize_selenium()
    try:
        manually_filtered_good_videos = {}
        manually_filtered_bad_videos = {}

        for video_id, data in video_dictionary.items():
            if not data:  # Skip invalid or None entries
                continue
            
            url = data["video"]["url_to_view"]
            print(f"Loading video: {url}")

            # Declare user_input variable in the outer scope
            user_input = ""
            # Flag to detect when user has answered
            user_answered = threading.Event()

            # Function to handle user input
            def get_user_input():
                nonlocal user_input  # Use the variable from the outer scope
                while not user_answered.is_set():  # Keep prompting until user answers
                    user_input = input("Is this video good? (answer: y or n): ").lower()
                    if user_input in ["y", "n"]:
                        user_answered.set()  # Signal that the user has answered
                    else:
                        print("Invalid input. Please type 'y' for yes or 'n' for no.")

            # Start user input thread
            input_thread = threading.Thread(target=get_user_input)
            input_thread.start()

            # Load the URL
            try:
                driver.set_page_load_timeout(10)  # Optional timeout for the page load
                driver.get(url)  # Load the video URL
            except Exception as e:
                print(f"Page load issue: {e}. Moving on.")

            # Wait for the user input thread to finish
            while not user_answered.is_set():
                time.sleep(1)  # Wait for the user to answer

            # Process the user input
            if user_input == "y":
                manually_filtered_good_videos[video_id] = data
            elif user_input == "n":
                manually_filtered_bad_videos[video_id] = data

            # Ensure the input thread is closed before moving to the next video
            input_thread.join()

    finally:
        driver.quit()
    return manually_filtered_good_videos, manually_filtered_bad_videos
