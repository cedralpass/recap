from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,jsonify, current_app, logging
)
from werkzeug.exceptions import abort

import json
from openai import OpenAI

bp = Blueprint('classify', __name__)

@bp.route('/classify_url',methods=('GET', 'POST'))
def classify_url():
    url = extract_url_from_request()
    json_return={}

    #create OpenAI request
    client = OpenAI(api_key=current_app.config["AI_API_OPENAI"])
    
    #make OpenAI Call
    response = client.chat.completions.create(
        #model="gpt-4-turbo-preview",
        model="gpt-3.5-turbo",
        messages=build_prompt(url),
            response_format={ "type": "json_object" },
            temperature=0.8,
            max_tokens=256,
            frequency_penalty=0,
            presence_penalty=0
            )
    
    if len(response.choices)>=1:
        current_app.logger.info(response.choices[0].message.content)
        json_return = response.choices[0].message.content
        current_app.logger.info("model %s cost %s", response.model, response.usage)
    else:
        current_app.logger.error("error: with openAPI call. no choices returned %s", response)

    return jsonify(json_return)

def extract_url_from_request():
    url="https://levelup.gitconnected.com/structuring-a-large-production-flask-application-7a0066a65447"
    if request.form.get('url') is not None:
        url = request.form.get('url')
    else:
         current_app.logger.error("error: must supply url for classification, using defualt for testing")
    current_app.logger.info("url to classify %s", url)
    return url

def build_prompt(url):
    classify_content  = "please classify  this blog post: " + str(url)
    prompt_string =  [
            {
                "role": "system",
                "content": "Using these categories: Software Architecture, Leadership, Business Strategy, Artificial Intelligence, Food and Cooking.  If the blog does not fit a category, recommend one. Please respond with category, url of blog, blog title, author,  summarize the content into a short paragraph, and key topics as bullet points, and sub-categories as bullet points. respond in a structured JSON response. "
            },
            {
                "role": "user",
                "content": classify_content
            }]
    current_app.logger.info("prompt to classify: %s", prompt_string)
    return prompt_string
