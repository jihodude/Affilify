import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Scrapers.API_scrapers import giphy_scraper, youtube_scraper, pexels_scraper
from NLP_Processing.prepare_scraping import generate_sub_queries_and_kws # Importing prepare_scraping from NLP_Processing
import math
from Scrapers.filter_scrapers import filter_videos
from pprint import pprint
from Video.video_downloader import download_videos

filter_video_boolean = {
    "youtube" : True,
    "pexels" : True,
    "giphy" : True
}

def get_content(queries, search_keywords, max_results, max_length=500, scrapers=["youtube", "pexels", "giphy"], filter_video_boolean = { "youtube" : False, "pexels" : False, "giphy" : False }):
    video_dictionary = {}
    print(scrapers)
    
    for scraper in scrapers:
        if filter_video_boolean[scraper]:
            result_count = 0
            current_max_results = max_results # Use a separate variable to control results per iteration
            iteration_limit = 10  # Prevent infinite loops
            iteration_count = 0  # Track iterations
            filtered_dictionaries = {}
            
            while result_count < max_results and iteration_count < iteration_limit:
                reply_dictionaries = scrape_videos(queries=queries, max_length=max_length, max_results=current_max_results, scraper=scraper)
                
                for key in list(filtered_dictionaries):
                    reply_dictionaries.pop(key, None)

                filtered_good_videos_reply, filtered_bad_videos_reply = filter_videos(reply_dictionaries, scraper)
                filtered_dictionaries.update({**filtered_good_videos_reply, **filtered_bad_videos_reply})


                for video_id, data in filtered_good_videos_reply.items():
                    if result_count >= max_results:
                        break
                    if video_id not in video_dictionary:
                        video_dictionary[video_id] = data
                        result_count = len(video_dictionary)

                print(f"Scraper '{scraper}': Found {result_count}/{max_results} videos (Iteration {iteration_count}/{iteration_limit})")

                iteration_count += 1
                current_max_results *= 2
            print(f"Scraper '{scraper}': found all {result_count}/{max_results} videos")
            if iteration_count >= iteration_limit:
                print(f"Warning: Reached iteration limit for scraper '{scraper}' without meeting max_results.")
    

        elif not filter_video_boolean[scraper]:

            reply = scrape_videos(queries=queries,search_keywords=search_keywords, max_length=max_length, max_results=max_results, scraper=scraper)

            for video_id, data in reply.items():
                video_dictionary[video_id] = data

    return video_dictionary

def scrape_videos (queries, search_keywords, max_length, max_results, scraper):
    video_dictionary = {}

    if scraper == "youtube":
        print("running youtube scraper")
        reply = youtube_scraper.scrape_with_retries(queries=queries,search_keywords=search_keywords, max_length=max_length, max_results=max_results)
        for video_id, data in reply.items():
            video_dictionary[video_id] = data
    if scraper == "pexels":
        print("running pexels scraper")
        for query in queries:
            if max_results > 80: #pexels max per page
                pages = math.ceil(max_results / 80)
                for page in range(1 , pages + 1):
                    if page < pages:
                        reply = pexels_scraper.get_videos(query=query, search_keywords=search_keywords, per_page=80, page=page)
                        for video_id, data in reply.items():
                            video_dictionary[video_id] = data
                    elif page == pages:
                        last_max_results = max_results - ((pages - 1) * 80)
                        reply = pexels_scraper.get_videos(query=query, search_keywords=search_keywords, per_page=last_max_results, page=page)
                        for video_id, data in reply.items():
                            video_dictionary[video_id] = data
            elif max_results <= 80:
                reply = pexels_scraper.get_videos(query=query, search_keywords=search_keywords, per_page=max_results)
                for video_id, data in reply.items():
                    video_dictionary[video_id] = data

    if scraper == "giphy":
        print("running giphy scraper")
        for query in queries:
            reply = giphy_scraper.get_gifs(query=query, search_keywords=search_keywords, max_results=max_results)
            for video_id, data in reply.items():
                video_dictionary[video_id] = data
                        
    return video_dictionary

if __name__ == "__main__":
    subqueries, sub_kws = generate_sub_queries_and_kws(
        subquery_count=5, 
        subkeyword_count=1, 
        main_query="cute baby koala videos", 
        main_keywords="cute, adorable, animals"
    )
    reply = get_content(subqueries, max_results=2)
    download_videos(reply, max_length=300)
    print("final content scraping dictionary length is: " + str(len(reply)))
    pprint(reply)

