import os

from flask import Flask, jsonify, logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from environs import Env




def create_app():
    # create and configure the app
    test_config = None
    #TODO: figure out better config
    env = Env()
    env.read_env()
    log_level = env("AI_API_LogLevel")

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
                "filename": "aiapi_app.log",
                "maxBytes": 1024*1024,
                "backupCount": 2,
                "formatter": "default",
            }
            },
            "root": {"level": log_level, "handlers": ["console","file"]},
        }
    )
    app = Flask(__name__)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    
    
    extract_config_key("AI_API_KEY", app, env)
    extract_config_key("AI_API_OPENAI", app, env)

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

    from . import classify
    app.register_blueprint(classify.bp) #register the auth blueprint

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        json_obj ={"key":"Hello, World! in JSON"}
        return jsonify(json_obj)
    return app

def extract_config_key(key, app, env):
    try:
      app.config[key] = env(key)
    except:
        print("Error occured with key " + key)
