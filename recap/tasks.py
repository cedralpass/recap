import time
from rq import get_current_job
from recap import create_app, article
import json
from recap.aiapi_helper import AiApiHelper

app = create_app()
app.app_context().push()

#sample task
def example(seconds=20):
    app.logger.info("Running example Task for seconds %s ", seconds)
    job = get_current_job()
    print('Starting task')
    for i in range(seconds):
        job.meta['progress'] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')

def classify_url(url, user_id):
    print('inside classify_url')
    app.logger.info("Running Classification Task for url %s and user id %s", url, user_id)
   
    try:
      article_found = article.get_article_by_url_for_user(url, user_id)
      app.logger.info("calling Classification Service for %s and article id %s", url, article_found['id'])
      if article_found is None:
          print('No article found for url ' + url)
          return
      classify_result = AiApiHelper.ClassifyUrl(url, article_found['id'])
      app.logger.info("Classification Service returned result: %s", classify_result)
      app.logger.info("Classification Service returned keys: %s", classify_result.keys())
      if 'key_topics' not in classify_result.keys():
        classify_result['key_topics'] = []
      key_topics_dict= {'key_topics':classify_result['key_topics']}
      if 'sub_categories' not in classify_result.keys():
        classify_result['sub_categories'] = []
      else:
         app.logger.info("Classification Service returned sub_categories: %s",  classify_result['sub_categories'])
      sub_category_dict= {'sub_category':classify_result['sub_categories']}
      key_topics_json = json.dumps(key_topics_dict)
      sub_category_json = json.dumps(sub_category_dict)
      
      article.update_article(article_found['id'], article_found['url_path'], classify_result['blog_title'], classify_result['summary'], classify_result['author'], classify_result['category'], key_topics_json, sub_category_json)
    except Exception as e:
      app.logger.error("Error in Classification Service: %s", e)
    return
