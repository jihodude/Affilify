
from API_scrapers import giphy_scraper, youtube_scraper, pexels_scraper
import math
import filter_scrapers
from pprint import pprint
filter_video_boolean = {
    "youtube" : True,
    "pexels" : True,
    "giphy" : True
}

def get_content(queries, max_results=1, scrapers=["youtube", "pexels", "giphy"], filter_video_boolean = { "youtube" : True, "pexels" : True, "giphy" : True }):
    video_dictionary = {}

    for scraper in scrapers:
        if filter_video_boolean[scraper]:

            reply = scrape_videos(queries=queries, max_results=max_results, scraper=scraper)
            filtered_good_video_reply, filtered_bad_video_reply = filter_scrapers.filter_videos(reply)

            for video_id, data in filtered_good_video_reply.items():
                video_dictionary[video_id] = data

        elif not filter_video_boolean[scraper]:

            reply = scrape_videos(queries=queries, max_results=max_results, scraper=scraper)

            for video_id, data in reply.items():
                video_dictionary[video_id] = data

    return video_dictionary

def scrape_videos (queries, max_results, scraper):
    video_dictionary = {}

    if scraper == "youtube":
        print("running youtube scraper")
        reply = youtube_scraper.scrape_with_retries(queries=queries, max_results=max_results)
        for video_id, data in reply.items():
            video_dictionary[video_id] = data
    if scraper == "pexels":
        print("running pexels scraper")
        for query in queries:
            if max_results > 80: #pexels max per page
                pages = math.ceil(max_results / 80)
                for page in range(1 , pages + 1):
                    if page < pages:
                        reply = pexels_scraper.get_videos(query=query, per_page=80, page=page)
                        for video_id, data in reply.items():
                            video_dictionary[video_id] = data
                    elif page == pages:
                        last_max_results = max_results - ((pages - 1) * 80)
                        reply = pexels_scraper.get_videos(query=query, per_page=last_max_results, page=page)
                        for video_id, data in reply.items():
                            video_dictionary[video_id] = data
            elif max_results <= 80:
                reply = pexels_scraper.get_videos(query=query, per_page=max_results)
                for video_id, data in reply.items():
                    video_dictionary[video_id] = data

    if scraper == "giphy":
        print("running giphy scraper")
        for query in queries:
            reply = giphy_scraper.get_gifs(query=query, max_results=max_results)
            for video_id, data in reply.items():
                video_dictionary[video_id] = data
                        
    return video_dictionary

if __name__ == "__main__":
    queries = ["seals eating", "seals swimming"]
    reply = get_content(queries, 1)

    print("final content scraping dictionary length is: " + str(len(reply)))
    pprint(reply)

