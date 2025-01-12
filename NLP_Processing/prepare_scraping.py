from openai import OpenAI
from decouple import config
client = OpenAI(api_key=config("OPEN_AI_KEY_1"))

def generate_sub_queries_and_kws(subquery_count, subkeyword_count, main_query, main_keywords):
    subquery_word = "a subquery" if subquery_count == 1 else "subqueries"
    subkeyword_word = "a sub-keyword" if subkeyword_count == 1 else "sub-keywords"

    dev_message = f"""
    You are a video scraping assistant for content automation. Your duty is to generate {subquery_word} and {subkeyword_word} adiding by the count restrictions.
    """
    
    user_message = f"""

    Instructions:
    Your task is to generate exactly {subquery_count} {subquery_word} and exactly {subkeyword_count} {subkeyword_word}, no more and no fewer.

    Understand the required video clips by analyzing the main query and main keywords. Ensure the {subkeyword_word} reflect the specific context of the main query 
    (e.g., if the main query is about "baby koalas fighting," the keywords should include "baby koala," "koala fights," etc., not just generic terms like "baby" or "fights"). 

    For Giphy and Pexels, {subkeyword_word} (simple, core terms) are preferred to improve search accuracy. For YouTube, detailed {subquery_word} are preferred.

    Strictly follow this format:
    Subqueries:query1,query2,...;Sub-Keywords:keyword1,keyword2,...

    Main Request:
    Main query: {main_query}; Main Keywords: {main_keywords}; if the request is to make 1 subquery or 1 sub-keywords, please follow directions, you need to make the exact quantity specified. 
    """


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": dev_message},
            {"role": "user", "content": user_message}
        ],
        temperature=0.6,
        n=1,
        max_tokens=150
    )

    response_sections = response.choices[0].message.content.split(";")
    subqueries = response_sections[0].replace("Subqueries:", '').strip().split(",")
    sub_kws = response_sections[1].replace("Sub-Keywords:", '').strip().split(",")
    return subqueries, sub_kws

if __name__ == "__main__":
    subqueries, sub_kws= generate_sub_queries_and_kws(
        subquery_count=1, 
        subkeyword_count=1, 
        main_query="cute cat videos", 
        main_keywords="cute, adorable, animals, funny, cat, kitten"
    )
    print("subquery:", subqueries)
    print("sub-keywords:", sub_kws)