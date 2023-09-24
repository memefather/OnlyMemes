import requests
import openai
import os
import json
from stable import stableai
import streamlit as st
import base64
from datetime import date, timedelta(days = 2)
from newsapi import NewsApiClient

st.set_page_config(page_icon="😂", page_title="OnlyMemes")

st.markdown(
    """
    <style>
.css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK{ display: none; } #MainMenu{ visibility: hidden; } footer { visibility: hidden; } 
    </style>
    """,
    unsafe_allow_html=True
)

st.title("OnlyMemes 😂")

newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

all_articles = newsapi.get_everything(language='en',
                                      from_param= date.today()-timedelta(days = 1),
                                      sources='cnn',
                                      sort_by='publishedAt',
                                      page = 1
                                      )

headlines = {}
radiohead = []

for i in all_articles['articles']:
    headlines[i['title']] = i['title'] + '. ' + i['description']
    radiohead.append(i['title'])

if radiohead == []:
    st.stop()

with st.sidebar:
    st.subheader("Top Stories")
    choice = st.radio("Meme the news:", radiohead)

openai.api_key = os.getenv("OPENAI_API_KEY")
imgurkey = os.getenv("IMGUR_KEY")
model_id = 'gpt-3.5-turbo'

conversation = []

def gpt_meme(news):
        conversation.append({'role': 'user', 'content': f"Give me meme image description and text for the following news: {news}. Make it with funny sarcasm or dark humor. You will answer in the following manner: {{\"image_des\": \"description\", \"top_text\": \"text\", \"bottom_text\": \"text\" Do not include anything else in the response.}} "})
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=conversation
        )
        conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
        return conversation[-1]['content'].strip()

def create_meme(imgurl, top_text, bot_text):

    url = 'https://api.memegen.link/images/custom'


    payload = {
      "background": imgurl,
      "style": "default",
      "text": [top_text, bot_text],
      "redirect": False
    }

    response = requests.post(url, json = payload)
    return json.loads(response.text)['url']

def img2url(img):
    # Set API endpoint and headers
    upurl = "https://api.imgur.com/3/image"
    headers = {"Authorization": f"Client-ID {imgurkey}"}

    # Read image file and encode as base64
    with open(img, "rb") as file:
      data = file.read()
      base64_data = base64.b64encode(data)

    # Upload image to Imgur and get URL
    response = requests.post(upurl, headers=headers, data={"image": base64_data})
    return response.json()["data"]["link"]

memedata = json.loads(gpt_meme(choice))
img_prompt = memedata['image_des']
topline = memedata['top_text']
botline = memedata['bottom_text']

stableai(img_prompt)

st.image('992446758.png')

imgurl = img2url('992446758.png')

meme_url = create_meme(imgurl, topline, botline)

st.write(meme_url)

st.image(meme_url)
