"""
    Autore : Cavallo Luigi
"""

from flask import render_template, Blueprint, request, jsonify, request, abort, redirect, url_for, send_from_directory, send_file, session
from .. import basic, is_user_logged, commentController
import logging

blog_blueprint = Blueprint("blog", __name__)
log = logging.getLogger("operational")

@blog_blueprint.route("/leavecomment", methods=["POST"])
@is_user_logged(session, log)
def leavecomment():
    """
        Store comment in the DB
    """
    try:
        commentController.add_comment(request.form["comment"])
        return redirect(url_for("blog.showcomments"))
    except Exception as comment_error:
        log.warning(comment_error)
        return abort(500)

@blog_blueprint.route("/showcomments", methods=["GET"])
@is_user_logged(session, log)
def showcomments():
    """
        Show already store comments
    """
    try:
        return jsonify(commentController.get_all_comments()), 200
    except Exception as show_comments_error:
        log.warning(show_comments_error)
        return abort(500)

@blog_blueprint.route("/search", methods=["GET"])
@is_user_logged(session, log)
def search():
    """
        Search for comments
        NOTE: Vulnerable injection point
    """
    try:
        found = [r[0] for r in commentController.search(request.args["toSearch"])]
        return jsonify(found), 200
    except Exception as search_comments_error:
        log.warning(search_comments_error)
        return abort(500)

@blog_blueprint.route("/todos.txt", methods=["GET"])
@is_user_logged(session, log)
@basic.required
def todo():
    log.warning("[RESTRICTED_FILE_ACCESS] file /todos.txt")
    return send_from_directory(directory="todo", path="todos.txt")

@blog_blueprint.route("/backup.bak", methods=["GET"])
@is_user_logged(session, log)
def backup():
    log.warning("[RESTRICTED_FILE_ACCESS] file /backup.bak")
    return send_file("backup.bak")
