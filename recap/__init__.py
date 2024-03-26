import os

from flask import Flask
from environs import Env
from recap.aiapi_helper import AiApiHelper
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig

def create_app():
    # create and configure the app
    test_config = None
    app = Flask(__name__)
    
   
    
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    #TODO: figure out better config
    env = Env()
    env.read_env()
    app.config['API_KEY'] = env("API_KEY")

    log_level = env("RECAP_LogLevel")

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

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    from . import db
    db.init_app(app) #register the db init code

    from . import auth
    app.register_blueprint(auth.bp) #register the auth blueprint

    from . import article
    app.register_blueprint(article.bp) # register the article blueprint
    app.add_url_rule('/', endpoint='index') #create index route

    return app