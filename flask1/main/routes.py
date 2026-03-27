from flask import Blueprint,  render_template, request
from flask1.models import Post

main=Blueprint("main", __name__)


DEVELOPER=[
    {
        'author':"tarak suravarapu",
        'title':"DEVELOPER",
        'content':"Developer of this website",
        'date':"dec 21, 2024"
    }
]
@main.route("/")
@main.route("/home")
def home():
    page=request.args.get("page", 1, type=int)
    post=Post.query.order_by(Post.date_posted.desc()).paginate(per_page=4, page=page)
    return render_template("home.html", post=post, title="home page")
@main.route("/about")
def about():
    return render_template("about.html", DEVELOPER=DEVELOPER, title="about")
