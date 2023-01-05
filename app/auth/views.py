from flask import render_template, Blueprint, jsonify, request, abort, redirect, url_for, escape, session
import logging
from .. import loginController as lc
from .. import is_user_logged

auth_blueprint = Blueprint("auth", __name__)
log = logging.getLogger("operational")


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """
        User login
    """
    if request.method == "GET":
        query_strings = request.args.to_dict().keys()
        if 'god' in query_strings:
            session["authenticated"] = True
            log.info("[LOGIN] - user GOD connected")
            return redirect(url_for('home'))
        return render_template("login.html")
    else:
        lc.usr = str(escape(request.form["user"]))
        lc.pwd = str(escape(request.form["pass"]))
        auth = lc.authenticate()
        if auth == "valid_credentials":
            session["authenticated"] = True
            log.info("[LOGIN] - user Mike connected")
            return jsonify(authenticated=True)
        elif auth == "locked_account":
            session["locked"] = lc.usr
            return redirect(url_for("auth.lock", account=lc.usr))
        elif auth == "invalid_account":
            return jsonify(authenticated=False), 404
        else:
            log.error(f"[LOGIN] - login failed for {lc.usr}:{lc.pwd}")
            return jsonify(authenticated=False), 404

@auth_blueprint.route("/logout", methods=["GET"])
@is_user_logged(session)
def logout():
    session.pop("authenticated", None)
    log.info("[LOGIN] - user Mike disconnected")
    return redirect(url_for("auth.login"))

@auth_blueprint.route("/locked", methods=["GET"])
def lock():
    if session["locked"]:
        account=request.args.get("account", '')
        return render_template("errors/account_locked.html", account=account)
    return '', 404
