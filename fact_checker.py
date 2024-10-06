import os
from mistralai import Mistral
import requests
import json
import base64
from video import get_transcription

mistral_api_key = os.environ["MISTRAL_API_KEY"]
brave_api_key = os.environ["BRAVE_API_KEY"]

model = "pixtral-12b-2409"
client = Mistral(api_key=mistral_api_key)
brave_api_endpoint = "https://api.search.brave.com/res/v1/web/search"

def fact_check_fn(claim, num_articles):
    examples = [
        {
            "role": "system",
            "content": "claim: Kylian Mbappe is one of the highest paid sportsmen.; query: Highest paid sportspeople in the world"
        },
        {
            "role": "system",
            "content": "claim: Trump was a better president than Biden.; query: Who was the better president between Trump and Biden?"
        },
        {
            "role": "system",
            "content": "claim: Climate change is irreversible; query: Is climate change irreversible?"
        },
        {
            "role": "system",
            "content": "claim: All of the wealth held by billionaires in the US would only fund the government for 8 months; query: How long would all the wealth held by US billionaires fund the government for?"
        }
    ]

    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "system",
                "content": "You are a fact checking system helper. Your job is to generate a search query related to the claim made by the user. Some examples are: "
            },
            examples[0],
            examples[1],
            examples[2],
            examples[3], 
            {
                "role": "user",
                "content": "Claim:" + claim + ". Write a search query that will search the web to figure out whether the claim is true or not. Return just one search query that will be inputted to the search engine. Be succinct but thorough."
            },
        ]
    )

    print(chat_response.choices[0].message.content)

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": brave_api_key,
    }

    params = {
        "q": chat_response.choices[0].message.content,
        "count": num_articles,
        "freshness": True,
        "result_filter": "faq,infobox,news,web,summarizer,web",
        "summary": True
    }

    response = requests.get(brave_api_endpoint, headers=headers, params=params)
    data = response.json()
    web_results = data.get("web", {}).get("results", [])
    formatted_data = json.dumps(web_results, indent=4)
    print(formatted_data)

    with open("search.json", "w") as json_file:
        json.dump(web_results, json_file, indent=4)

    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "system",
                "content": "You are a fact checker LLM. Verify the claim with reference to each of the sources, rating them on how much they agree/disagree WITH THE CLAIM ({claim}) - make sure NEGATIONS (like NOT or DEBUNKS, etc) are taken into account. Give an overall summary of what all the sources say, but succinctly rate each source with whether they agree/disagree with the claim ({claim}) in one line. Also include a tally of agree/disagree/in between. If they don't reference the claim, ignore the source. Use the following up-to-date information:\n Claim:" + claim + "\n Information: " + str(formatted_data),
            },
            {
                "role": "system",
                "content": "The output structure should be in the following format ONLY (make sure to to include agree/disagree/neutral, with a 0 if there are no sources that fall into the category): {summary: summary of how much the search results overall agree/disagree WITH THE CLAIM and why, tally: {agree: {count: number of sources that agree, sources: [{source_name: name of source, link: link to the source, summary: 1-line summary of why source agrees to the claim}, ...]}, disagree: {count: number of sources that disagree, sources: [{source_name: name of source, link: link to the source, summary: 1-line summary of why source disagrees with the claim}, ...]}, neutral: {count: number of sources that are neutral, sources: [{source_name: name of source, link: link to the source, summary: 1-line summary of why source is neutral with the claim}, ...]}}}"
            }
        ]
    )
    
    return chat_response.choices[0].message.content

def fact_check_fn_img(image_path, num_articles):

    def encode_image_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    claim = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "system",
                "content": "You are a fact checking system helper. Your job is to find the main claim made by the user in the picture below. Take the overall claim, being specific yet succinct. "
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{encode_image_base64(image_path)}"
                    },
                    {
                        "type": "text",
                        "text": "Above is a picture. Synthesize the main claim in this picture. ONLY return the claim as a single sentence string."
                    }
                ]
            },
        ]
    )

    print(claim)
    return fact_check_fn(claim, num_articles)

def fact_check_fn_video(video_path, num_articles):
    transcription = get_transcription(video_path)

    claim = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "system",
                "content": "You are a fact checking system helper. Your job is to find the main claim made by the user in the audio transcription below. Take the overall claim of the transcript, being specific yet succinct. "
            },
            {
                "role": "user",
                "content": f"Audio transcription: {transcription}. Synthesize the main claim in this transcription. ONLY return the claim as a single sentence string."
            },
        ]
    )

    print(claim)
    return fact_check_fn(claim, num_articles)