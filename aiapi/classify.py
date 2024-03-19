from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,jsonify
)
from werkzeug.exceptions import abort

import json

bp = Blueprint('classify', __name__)

@bp.route('/classify_url',methods=('GET', 'POST'))
def classify_url():
    url="https://levelup.gitconnected.com/structuring-a-large-production-flask-application-7a0066a65447"
    print(url)
    json_return = [{
  "url": "https://levelup.gitconnected.com/structuring-a-large-production-flask-application-7a0066a65447",
  "blog_title": "Structuring a Large Production Flask Application",
  "author": "Not provided",
  "summary": "The blog post offers a comprehensive guide on organizing and structuring Flask applications for large-scale production environments. It covers topics such as codebase organization, configuration management, blueprint implementation, database connection management, and deployment strategies.",
  "key_topics": [
    "Codebase organization",
    "Configuration management",
    "Blueprint implementation",
    "Database connection management",
    "Deployment strategies"
  ],
  "sub_categories": [
    "Scalability",
    "Maintainability",
    "Modularity"
  ]
}
]
    return jsonify(json_return)
