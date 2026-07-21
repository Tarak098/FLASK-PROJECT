from flask import Blueprint, render_template, url_for, flash, abort, request, redirect
from flask1 import db
from flask1.models import User, Post
from flask_login import current_user, login_required
from flask1.posts.forms import CreatePostForm


posts=Blueprint("posts", __name__)



@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form=CreatePostForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("your post has been uploaded!", "success")
        return redirect(url_for("main.home"))
    return render_template("create_post.html", title="posts", form=form, legend="New post")

@posts.route("/post/<int:post_id>")
def post(post_id):
    user_post=Post.query.get_or_404(post_id)
    return render_template("post.html",title=user_post.title, user_post=user_post)

@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    user_post=Post.query.get_or_404(post_id)
    if user_post.author != current_user:
        abort(403)
    form=CreatePostForm()
    if form.validate_on_submit():
        user_post.title=form.title.data
        user_post.content=form.content.data
        db.session.commit()
        flash("post updated successfully", "success")
        return redirect(url_for("posts.post", post_id=user_post.id))
    elif request.method == "GET":
        form.title.data=user_post.title
        form.content.data=user_post.content
    return render_template("create_post.html", title=user_post.title, form=form, user_post=user_post, legend="Update Post")



@posts.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    user_post=Post.query.get_or_404(post_id)
    if user_post.author != current_user:
        abort(403)
    db.session.delete(user_post)
    db.session.commit()
    flash("your post has been deleted", "success")
    return redirect(url_for("main.home"))

