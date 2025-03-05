from openai import OpenAI
from decouple import config
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Audio.tts import generate_tts
client = OpenAI(api_key=config("OPEN_AI_KEY_1"))
from pprint import pprint
from gtts import gTTS
import openai

# Initialize your OpenAI client with the proper credentials
# e.g., openai.api_key = "YOUR_API_KEY"
# or if you have a custom client variable, adjust accordingly

def generate_script(video_templet, impersonation, main_query, main_keywords, video_count, video_length):
    """
    Generates exactly 'video_count' scripts for a given video_templet,
    referencing main_query, using main_keywords for context.
    The scripts are short, casual, and avoid em-dashes (--) or semicolons (;) or emojis or quotations marks ("" or '') and comas (,).

    """
    
    dev_message = f"""
    You are a content automation program's script writer.
    Your goal: tell a engaging {video_templet} script for short video platforms such as instagram reels, tiktok, and youtube shorts. Make sure you inpersonate and sound like {impersonation}.

    Here are important style guidelines:
    1. DO keep it natural and unique.
    2. DO NOT use em-dashes or semicolons.
    3. The script is for a {video_templet} video while impersonating {impersonation} 
    4. Think about how you can best write a script for a {video_templet} video about {main_query}. Some key words for considerations are {main_keywords}
    5. Make sure the script sounds natural and not overly robotic or obvious.
    6. When read aloud, it should be just under {video_length} seconds in total.
    7. Return Exactly{video_count} scripts, labeled as video1:, video2:, etc.
    8. Do not exceed {video_count} scripts. No more, no less.
    9. Avoid filler or stating the obvious. Use a friendly, viral short-video style.
    10. Do not use the punctuation: em-dashes (--) or semicolons (;) or emojis or quotations marks ("" or '') and comas (,).
    11. scripts should be final to use, so avoid dynamic fillers that require second touch such as [your name] or something like that. No Placeholders.
    """

    user_message = f"""
    Create {video_count} script(s) for a '{video_templet}' video playing over footage of {main_query}. impersonate {impersonation}
    Key words for context: {main_keywords}

    Requirements Recap:
    - Return exactly {video_count} scripts
    - Each script is short enough to be read in under {video_length} seconds
    - Must be engaging, creative, fun, and accurate
    - NO em-dashes (--), NO semicolons (;)
    - Label them as video1:, video2:, etc., in one continuous response
    - Example format (but don't copy punctuation):
      video1:This is a short script about cats. It is fun and creative
      video2:Now here's a second script focusing on cats again
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": dev_message},
            {"role": "user", "content": user_message}
        ],
        temperature=0.6,
        n=1
    )
    extract_video_scripts(response.choices[0].message.content)

    # Return only the model's generated content
    return extract_video_scripts(response.choices[0].message.content)

def extract_video_scripts(text):
    # Use regex to find video scripts dynamically
    pattern = r"(video\d+:)(.*?)(?=video\d+:|$)"
    matches = re.findall(pattern, text, re.DOTALL)

    # Extract only the script part and clean up spacing
    video_scripts = [match[1].strip() for match in matches]
    
    return video_scripts

def print_by_word_count(text, word_limit):
    words = text.split()
    for i in range(0, len(words), word_limit):
        print(" ".join(words[i:i + word_limit]))

if __name__ == "__main__":

    scripts = generate_script(
        video_templet="life hacks",
        main_query="cat",
        main_keywords="lazy cat, cute animals, domesticated feline",
        video_count=3,
        video_length=30
    )
    for i in scripts:
        print(i)
        print("\n")
