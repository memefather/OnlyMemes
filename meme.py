import requests
import openai
import os
import json
from stable import stableai
import streamlit as st
import base64
from datetime import date, timedelta
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

@st.cache_data
def gpt_meme(news):
        conversation.append({'role': 'user', 'content': f"Give me meme image description and text for the following news: {news}. Make it with funny sarcasm or dark humor. You will answer in the following manner: {{\"image_des\": \"description\", \"top_text\": \"text\", \"bottom_text\": \"text\" Do not include anything else in the response.}} "})
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=conversation
        )
        conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
        return conversation[-1]['content'].strip()

@st.cache_data
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

@st.cache_data
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

st.title("OnlyMemes 😂")

options = st.selectbox(
    'What do you meme?',
    ('business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'))
st.write(options)

with st.sidebar:
    st.markdown("Top Stories")

if options:
    newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
    
    all_articles = newsapi.get_top_headlines(language='en',
                                          category=options,
                                          #from_param= date.today()-timedelta(days = 1),
                                          #sources='cnn',
                                          #sort_by='publishedAt',
                                          #page = 1
                                          )
    
    headlines = {}
    radiohead = []
    
    for i in all_articles['articles']:
        headlines[i['title']] = i['title'] + '. ' + i['description']
        radiohead.append(i['title'])
    
    if len(radiohead) > 5:
        radiohead = radiohead[0:5]
    
    with st.sidebar:
        choice = st.radio("Meme the news:", radiohead, None)
    
    if radiohead == []:
        st.markdown("No news Today. Come Back Tomorrow!")
        st.markdown("![Alt Text](https://y.yarn.co/6b1e3a6f-f51e-492d-a48a-a40a27e3d471_text.gif)")
        st.stop()
        
    if choice == None:
        st.image('https://i.imgflip.com/807zif.jpg')
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        imgurkey = os.getenv("IMGUR_KEY")
        model_id = 'gpt-3.5-turbo'
        conversation = []
        
        memedata = json.loads(gpt_meme(headlines[choice]))
        img_prompt = memedata['image_des']
        topline = memedata['top_text']
        botline = memedata['bottom_text']
        stableai(img_prompt)
        imgurl = img2url('992446758.png')
        meme_url = create_meme(imgurl, topline, botline)
        
        st.image(meme_url)
