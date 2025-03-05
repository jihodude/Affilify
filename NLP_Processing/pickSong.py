from openai import OpenAI
from decouple import config
client = OpenAI(api_key=config("OPEN_AI_KEY_1"))
import os
def pick_song(main_query):
    BGM_folder_path = "/Users/jihobae/Documents/Programming/Affilify/Audio/BGM"
    bgm_tags_dict = {}
    for bgm in os.listdir(BGM_folder_path):
        bgm_tags = ", ".join(bgm.rstrip(".mp3").split("_"))
        bgm_tags_dict[bgm] = bgm_tags


    def write_bgm():
        string = ""
        i = 1
        for bgm, bgm_tag in bgm_tags_dict.items():
            string += f"{i}. {bgm}: {bgm_tag}\n"

            i = i + 1
        return string
    write = write_bgm()
    dev_message = f"""
    Your duty is to select a bgm out of the given options, that will most likly pair best with a video generated with the given query.
    """
    
    user_message = f"""

    Instructions:
    Your duty is to pick 1 back ground music out of the given options. Pick the one that will pair best with a video generated with the given query.

    Analize the query to figure out what kind of bgm should be used.
    
    When returning your pick, just say the name of the bgm (e.g. bgm10).

    Main Request:
    query {main_query};
    bgm options:
    {write}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": dev_message},
            {"role": "user", "content": user_message}
        ],
        temperature=0.5,
        n=1,
        max_tokens=150
    )

    response = response.choices[0].message.content
    
    return BGM_folder_path + f"/{response}"

if __name__ == "__main__":
    print(pick_song("diddy courtroom case"))