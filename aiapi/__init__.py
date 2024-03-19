import os

from flask import Flask, jsonify
from environs import Env


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
      print(app.config[key])
    except:
        print("Error occured with key " + key)
