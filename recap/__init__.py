import os

from flask import Flask, current_app
from environs import Env
from recap.aiapi_helper import AiApiHelper
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from redis import Redis
import rq
from recap.config import RecapConfig

def create_app():
    # create and configure the app
    #TODO: figure out better config
    env = Env()
    env.read_env()

    configure_logging()
    # start the app
    app = Flask(__name__)
    
    #configure the app
    configure_app(app, env)
    

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.redis = Redis.from_url(RecapConfig.RECAP_REDIS_URL)
    app.task_queue = rq.Queue(RecapConfig.RECAP_RQ_QUEUE, connection=app.redis)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    # a simple url that enques a RQ job and responds
    @app.route('/job')
    def job():
        job = launch_task(name='recap.tasks.example', description='example', seconds=5)
        return 'Job is Executing ' + job.id + ' its status ' + job.get_status(refresh=True)
    
    # a url for showing a job_id
    @app.route('/job/<string:id>/show')
    def job_show(id):
        job = current_app.task_queue.fetch_job(job_id=id)
        
        return 'Job is Executing ' + job.id + ' its status ' + job.get_status(refresh=True)
    
    from . import db
    db.init_app(app) #register the db init code

    from . import auth
    app.register_blueprint(auth.bp) #register the auth blueprint

    from . import article
    app.register_blueprint(article.bp) # register the article blueprint
    app.add_url_rule('/', endpoint='index') #create index route

    # TODO - understand args and kwargs better for dynamic params 
    def launch_task(name, description, *args, **kwargs):
        rq_job = app.task_queue.enqueue(name, description=description, args=args, kwargs=kwargs)
        return rq_job
    
    return app

def configure_logging():
    log_level = RecapConfig.RECAP_LogLevel
    #good example of logging from here: https://betterstack.com/community/guides/logging/how-to-start-logging-with-flask/
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(process)d %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                },
                "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "recap_app.log",
                "maxBytes": 1024*1024,
                "backupCount": 2,
                "formatter": "default",
            }
            },
            "root": {"level": log_level, "handlers": ["console","file"]},
        }
    )

def configure_app(app, env):
    app.config['API_KEY'] = RecapConfig.RECAP_SECRET_KEY
    app.config['REDIS_URL'] = RecapConfig.RECAP_REDIS_URL
    app.config['RECAP_RQ_QUEUE'] = RecapConfig.RECAP_RQ_QUEUE
    app.config["SECRET_KEY"]=RecapConfig.RECAP_SECRET_KEY # set the key to secure Flask App
    app.config["DATABASE"]=os.path.join(app.instance_path, 'flaskr.sqlite')