import os
import sqlite3

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for
from passlib.hash import sha256_crypt

from datatypes.forms import CourseForm


def create_app():
    """
    Instantiate the Flask web application and define the required endpoints
    for the Enterprise Data API.

    Returns:
        app - An instance of a Flask application
    """
    app = Flask(__name__)
    app.config["app.json.compact"] = False
    app.config["SECRET_KEY"] = os.urandom(32)

    messages_list = [
        {"title": "Message One", "content": "Message One Content"},
        {"title": "Message Two", "content": "Message Two Content"},
    ]

    courses_list = [
        {
            "title": "Python 101",
            "description": "Learn Python basics",
            "price": 34,
            "available": True,
            "level": "Beginner",
        }
    ]

    def get_db_connection(db_name):
        conn = sqlite3.connect(db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def get_post(*, post_id: str):
        conn = get_db_connection(db_name="databases/posts.db")
        post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        conn.close()
        if post is None:
            abort(404)
        return post

    def get_user(*, username: str):
        conn = get_db_connection(db_name="databases/users.db")
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        return user

    def create_user(*, username: str, password: str, email: str):
        conn = get_db_connection(db_name="databases/users.db")
        conn.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, sha256_crypt.hash(secret=password), email),
        )
        conn.commit()
        conn.close()

    def edit_user(*, username: str, password: str, email: str):
        conn = get_db_connection(db_name="databases/users.db")
        conn.execute(
            "UPDATE users SET password = ?, email = ? WHERE username = ?",
            (sha256_crypt.hash(secret=password), email, username),
        )
        conn.commit()
        conn.close()

    def delete_user(*, username: str):
        conn = get_db_connection(db_name="databases/users.db")
        conn.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html", error=error), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("500.html", error=error), 500

    @app.route("/up", methods=["GET"])
    def up_page():
        """
        Simple /up check to ensure that the API is reachable.
        ---
        responses:
          200:
            description: Returns {'status':'happy'} if application up and running
        """
        return jsonify({"status": "happy"}), 200

    @app.route("/healthz", methods=["GET"])
    def probe_page():
        """
        Simple /up check to ensure that the API is reachable (as performed by Atlas during a deployment).
        ---
        responses:
          200:
            description: Returns {'status':'happy'} if application up and running
        """
        return jsonify({"status": "happy"}), 200

    @app.route("/")
    @app.route("/index/")
    def index():
        if not session.get("username"):
            return redirect(url_for("login"))
        else:
            return render_template("index.html")

    @app.route("/login/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            if not username:
                flash("Username is required!")
            elif not password:
                flash("Password is required!")
            else:
                user_record = get_user(username=username)

                if not user_record:
                    flash(f"Username, {username}, was not found. Please try again!")
                    return render_template("login.html")

                same_password = False
                if sha256_crypt.verify(secret=password, hash=user_record["password"]):
                    same_password = True

                if same_password:
                    session["username"] = username
                    return redirect(url_for("index"))
                else:
                    flash(f"Incorrect password for {username}. Please try again!")
                    return render_template("login.html")

        return render_template("login.html")

    @app.route("/signup/", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            password_confirm = request.form["password_confirm"]
            email = request.form["email"]

            if not username:
                flash("Username is required!")
            elif not password:
                flash("Password is required!")
            elif not password_confirm:
                flash("Password Confirmation is required!")
            elif password != password_confirm:
                flash("Password and Password Confirmation are not equal!")
            elif not email:
                flash("Email is required!")
            elif "@" not in email or "." not in email:
                flash("Please enter a valid email address!")
            else:
                user_record = get_user(username=username)

                if user_record:
                    flash(f"Username, {username}, is not available. Please try again!")
                    return render_template("signup.html")

                create_user(username=username, password=password, email=email)
                session["username"] = username
                return redirect(url_for("index"))

        return render_template("signup.html")

    @app.route("/logout/", methods=["GET"])
    def logout():
        session["username"] = None
        return redirect(url_for("login"))

    @app.route("/account/", methods=["GET"])
    def account():
        if not session.get("username"):
            flash("No one is currently signed in!")
            return redirect(url_for("index"))

        user = get_user(username=session["username"])
        return render_template("account.html", user=user)

    @app.route("/user_edit/", methods=["GET", "POST"])
    def user_edit():
        user_record = get_user(username=session["username"])

        if request.method == "POST":
            password = request.form["password"]
            password_confirm = request.form["password_confirm"]
            email = request.form["email"]

            if not password:
                flash("Password is required!")
            elif not password_confirm:
                flash("Password Confirmation is required!")
            elif password != password_confirm:
                flash("Password and Password Confirmation are not equal!")
            elif not email:
                flash("Email is required!")
            elif "@" not in email or "." not in email:
                flash("Please enter a valid email address!")
            else:

                edit_user(username=user_record["username"], password=password, email=email)
                return redirect(url_for("account"))

        return render_template("user_edit.html", username=user_record["username"], email=user_record["email"])

    @app.route("/user_delete/", methods=["POST"])
    def user_delete():
        if not session.get("username"):
            flash("No one is currently signed in!")
            return redirect(url_for("index"))

        delete_user(username=session["username"])
        session["username"] = None
        return redirect(url_for("index"))

    @app.route("/about/")
    def about():
        return render_template("about.html")

    @app.route("/comments/")
    def comments():
        comments_list = [
            "This is the first comment.",
            "This is the second comment.",
            "This is the third comment.",
            "This is the fourth comment.",
        ]

        return render_template("comments.html", comments=comments_list)

    @app.route("/messages/<int:idx>")
    def message(idx):
        try:
            app.logger.debug("Get message with index: {}".format(idx))
            return render_template("message.html", message=messages_list[idx])
        except IndexError:
            app.logger.error("Index {} is causing an IndexError".format(idx))
            abort(404)

    @app.route("/create/", methods=("GET", "POST"))
    def create():
        if request.method == "POST":
            title = request.form["title"]
            content = request.form["content"]

            if not title:
                flash("Title is required!")
            elif not content:
                flash("Content is required!")
            else:
                messages_list.append({"title": title, "content": content})
                return redirect(url_for("messages"))

        return render_template("create.html")

    @app.route("/messages/")
    def messages():
        return render_template("messages.html", messages=messages_list)

    @app.route("/create_course/", methods=("GET", "POST"))
    def create_course():
        form = CourseForm()
        if form.validate_on_submit():
            courses_list.append(
                {
                    "title": form.title.data,
                    "description": form.description.data,
                    "price": form.price.data,
                    "available": form.available.data,
                    "level": form.level.data,
                }
            )
            return redirect(url_for("courses"))

        return render_template("create_course.html", form=form)

    @app.route("/courses/")
    def courses():
        return render_template("courses.html", courses_list=courses_list)

    @app.route("/posts/")
    def posts():
        conn = get_db_connection(db_name="databases/posts.db")
        posts_data = conn.execute("SELECT * FROM posts").fetchall()
        conn.close()
        return render_template("posts.html", posts=posts_data)

    @app.route("/create_post/", methods=("GET", "POST"))
    def create_post():
        if request.method == "POST":
            title = request.form["title"]
            content = request.form["content"]

            if not title:
                flash("Title is required!")
            elif not content:
                flash("Content is required!")
            else:
                conn = get_db_connection(db_name="databases/posts.db")
                conn.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
                conn.commit()
                conn.close()
                return redirect(url_for("posts"))

        return render_template("create_post.html")

    @app.route("/posts/<int:post_id>/edit/", methods=("GET", "POST"))
    def edit(post_id):
        post = get_post(post_id=post_id)

        if request.method == "POST":
            title = request.form["title"]
            content = request.form["content"]

            if not title:
                flash("Title is required!")

            elif not content:
                flash("Content is required!")

            else:
                conn = get_db_connection(db_name="databases/posts.db")
                conn.execute("UPDATE posts SET title = ?, content = ?" " WHERE id = ?", (title, content, post_id))
                conn.commit()
                conn.close()
                return redirect(url_for("posts"))

        return render_template("post_edit.html", post=post)

    @app.route("/posts/<int:post_id>/delete/", methods=("POST",))
    def delete(post_id):
        post = get_post(post_id=post_id)
        conn = get_db_connection(db_name="databases/posts.db")
        conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()
        flash('"{}" was successfully deleted!'.format(post["title"]))
        return redirect(url_for("posts"))

    return app


application = create_app()
