"""
    Autore : Cavallo Luigi
"""
__version__ = "0.0.4"

import os
import logging
from flask import Flask, render_template, session, redirect, url_for, request
from werkzeug.exceptions import HTTPException
from .utils import setup_logger, is_user_logged, filter_enumeration_tools_by_user_agent
from .models import Comment, Login
from flask_basicauth import BasicAuth

basic = BasicAuth()
commentController = Comment()
loginController = Login(monitor=False)
log = logging.getLogger("access")

def create_app():
    from .cfg import config
    from .blog.views import blog_blueprint
    from .auth.views import auth_blueprint

    app = Flask(__name__)
    app.config.from_object(config.status.get("mode"))

    # application blueprint
    app.register_blueprint(blog_blueprint)
    app.register_blueprint(auth_blueprint)

    # Flask Basic Auth init
    basic.init_app(app)

    # Logging system configuration
    if not os.path.exists(app.config["LOGS_DIR"]):
        os.makedirs(app.config["LOGS_DIR"])

    for logfile in app.config["LOGS"]:
        if not os.path.exists(logfile):
            open(logfile, mode="w").close()
        setup_logger(f"{os.path.basename(logfile).split('.')[0]}", logfile)

    # Base app route

    @app.before_first_request
    def before_first_request_func():
        """
            Create comments table
        """
        commentController.init()
        loginController.init()

    @app.before_request
    def before_request():
        """
            Check User-Agents of the client to defeat some tool for web enumeration.
        """
        filter_enumeration_tools_by_user_agent(request.headers.get("User-Agent", "-"))

    @app.route("/")
    def home():
        if session.get("authenticated", None):
            return render_template("index.html")
        else:
            print("[!] No user authenticated")
            return redirect(url_for("auth.login"))

    @app.after_request
    def after_request(response):
        log.info('%s %s %s %s %s',
                    request.remote_addr,
                    request.method,
                    request.scheme,
                    request.full_path,
                    response.status
        )
        return response

    # HTTP Error Handler
    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        return render_template('errors/generics.html', error=exc), exc.code

    return (
        app,
        loginController,
        commentController
    )
