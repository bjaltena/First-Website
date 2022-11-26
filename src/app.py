import sqlite3

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for

from forms import CourseForm


def create_app():
    """
    Instantiate the Flask web application and define the required endpoints
    for the Enterprise Data API.

    Returns:
        app - An instance of a Flask application
    """
    app = Flask(__name__)
    app.config["app.json.compact"] = False
    app.config["SECRET_KEY"] = "d0f48d217e6c459824e806a8caa3e8cdad96811b08063549"

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

    def get_db_connection():
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        return conn

    def get_post(post_id):
        conn = get_db_connection()
        post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        conn.close()
        if post is None:
            abort(404)
        return post

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("500.html"), 500

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
        return render_template("index.html")

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

    @app.route("/form/", methods=("GET", "POST"))
    def form():
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

        return render_template("form.html", form=form)

    @app.route("/courses/")
    def courses():
        return render_template("courses.html", courses_list=courses_list)

    @app.route("/posts/")
    def posts():
        conn = get_db_connection()
        posts = conn.execute("SELECT * FROM posts").fetchall()
        conn.close()
        return render_template("posts.html", posts=posts)

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
                conn = get_db_connection()
                conn.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
                conn.commit()
                conn.close()
                return redirect(url_for("posts"))

        return render_template("create_post.html")

    @app.route("/posts/<int:id>/edit/", methods=("GET", "POST"))
    def edit(id):
        post = get_post(id)

        if request.method == "POST":
            title = request.form["title"]
            content = request.form["content"]

            if not title:
                flash("Title is required!")

            elif not content:
                flash("Content is required!")

            else:
                conn = get_db_connection()
                conn.execute("UPDATE posts SET title = ?, content = ?" " WHERE id = ?", (title, content, id))
                conn.commit()
                conn.close()
                return redirect(url_for("posts"))

        return render_template("post_edit.html", post=post)

    @app.route("/posts/<int:id>/delete/", methods=("POST",))
    def delete(id):
        post = get_post(id)
        conn = get_db_connection()
        conn.execute("DELETE FROM posts WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        flash('"{}" was successfully deleted!'.format(post["title"]))
        return redirect(url_for("posts"))

    return app


application = create_app()
