from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from recap.auth import login_required
from recap.db import get_db
import json
from recap.aiapi_helper import AiApiHelper

bp = Blueprint('article', __name__)

@bp.route('/')
def index():
    db = get_db()
    articles = db.execute(
        'SELECT a.id, a.url_path, a.title, a.summary, a.author '
        ', a.category, a.key_topics, a.sub_category, a.created, a.user_id, u.username'
        ' FROM article a JOIN user u ON a.user_id = u.id'
        ' ORDER BY a.created DESC'
    ).fetchall()
    return render_template('article/index.html', articles=articles)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        url_path = request.form['url_path']
        error = None

        if not url_path:
            error = 'A url to public article is required.'
            
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO article (url_path, user_id)'
                ' VALUES (?,  ?)',
                (url_path, g.user['id'])
            )
            db_result = db.commit()
            current_app.logger.info("calling async Classification Service for %s", url_path)
            #recap.tasks.classify_url(url_path, g.user['id'])
            job = launch_task(name='recap.tasks.classify_url', description='url classification', url=url_path, user_id=g.user['id'])
            print('Job is Executing ' + job.id + ' its status ' + job.get_status(refresh=True))
            flash('Article created successfully and is being classified by job + ' + job.id + '. Articles will be classified within 20 seconds')
            current_app.logger.info("Classification Service returned")               
            return redirect(url_for('article.index'))

    return render_template('article/create.html')

def validate_key_topics(key_topics):
    error=None
    if len(key_topics) > 0:
      try:    
        key_topics_json = json.loads(key_topics)
      except json.JSONDecodeError as e:
        print("Oops!  That was not propper JSON  Try again...", e)
        error = "please store key_topics as JSON"
    return error

def validate_sub_categories(sub_categories):
    error=None
    if len(sub_categories) > 0:
      try:    
        sub_categories_json = json.loads(sub_categories)
      except json.JSONDecodeError as e:
        print("Oops!  That was not propper JSON  Try again...", e)
        error = "please store sub_categories as JSON"
    return error

def get_article(id, check_author=True):
    article_sql = '''SELECT a.id, a.url_path, a.title, a.summary, a.author, a.category,
      a.key_topics, a.sub_category, a.created, a.user_id, u.username 
      FROM article a JOIN user u ON a.user_id = u.id WHERE a.id = ?'''
    article = get_db().execute(
        article_sql,
        (id,)
    ).fetchone()


    if article is None:
        abort(404, f"Article id {id} doesn't exist.")

    if check_author and article['user_id'] != g.user['id']:
        abort(403)

    return article

def get_article_by_url_for_user(url, user_id):
    current_app.logger.info("looking up article using get_article_by_url_for_user by %s for user %s",url, user_id)
    article_sql = '''SELECT a.id, a.url_path, a.title, a.summary, a.author, a.category,
      a.key_topics, a.sub_category, a.created, a.user_id, u.username 
      FROM article a JOIN user u ON a.user_id = u.id WHERE a.url_path = ? and a.user_id = ?
      order by a.id desc'''
    article = get_db().execute(
        article_sql,
        (url, user_id,)
    ).fetchone()

    return article

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    article = get_article(id)

    if request.method == 'POST':
        url_path = article['url_path']
        title = request.form['title']
        summary = request.form['summary']
        author = request.form['author']
        category = request.form['category']
        key_topics = request.form['key_topics']
        sub_category = request.form['sub_category']
        error = None

        if not url_path:
            error = 'A URL for a public article is required.'
        
        error = validate_key_topics(key_topics) 
        error = validate_sub_categories(sub_category) 

        if error is not None:
            flash(error)
        else:
            update_article(id, url_path, title, summary, author, category, key_topics, sub_category)
            return redirect(url_for('article.index'))

    return render_template('article/update.html', article=article)

def update_article(id, url_path, title, summary, author, category, key_topics, sub_category):
    db = get_db()
    db.execute(
                'UPDATE article SET url_path = ?, title = ?, summary = ?, author = ?, category = ?, key_topics = ?, sub_category = ?'
                ' WHERE id = ?',
                (url_path, title, summary, author, category, key_topics, sub_category, id )
            )
    db.commit()

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_article(id)
    db = get_db()
    db.execute('DELETE FROM article WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('article.index'))


@bp.route('/<int:id>/show', methods=('GET','POST'))
@login_required
def show(id):
    article = get_article(id,False)
    key_topics = article['key_topics']
    if key_topics != '':
       key_topics_json = json.loads(key_topics)
    else:
      key_topics_json= {'key_topics':''}
    sub_categories = article['sub_category']
    if sub_categories != '':
        sub_categories_json = json.loads(sub_categories)
    else:
       sub_categories_json= {'sub_category':''}
    content=[article,key_topics_json["key_topics"],sub_categories_json["sub_category"]]
    return render_template('article/show.html', article=content)

@bp.route('/<int:id>/reclassify', methods=('GET','POST'))
@login_required
def reclassify(id):
    article = get_article(id,False)
    current_app.logger.info("calling async Classification Service for article %s", article['url_path'])
    #recap.tasks.classify_url(url_path, g.user['id'])
    job = launch_task(name='recap.tasks.classify_url', description='url classification', url=article['url_path'], user_id=g.user['id'])
    print('Job is Executing ' + job.id + ' its status ' + job.get_status(refresh=True))
    flash('Article is being reclassified by job' + job.id + '. Articles will be classified within 20 seconds')
    current_app.logger.info("Classification Service returned")               
    return redirect(url_for('article.index'))


# TODO - understand args and kwargs better for dynamic params 
def launch_task(name, description, *args, **kwargs):
    rq_job = current_app.task_queue.enqueue('recap.tasks.classify_url', description=description, args=args, kwargs=kwargs)
    return rq_job