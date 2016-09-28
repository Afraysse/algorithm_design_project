"""INSCRIPTION: a caption website. """

import os
import csv
import json

from jinja2 import StrictUndefined

from flask import Flask, render_template, flash, redirect, request, jsonify, url_for, session
from flask_debugtoolbar import DebugToolbarExtension

# import SQLAlchemy exception error to use in try/except
from sqlalchemy.orm.exc import NoResultFound

from model import connect_to_db, db, Relations, User, Post, Comment

#import helper functions from utils.py
from utils import friends_or_pending, get_friend_requests, get_friends


app = Flask(__name__)

app.secret_key = "CBA"

app.jinja_env.undefined = StrictUndefined

################################################################################

@app.route('/')
def index():
    """ Landing page with login and register."""

    return render_template("landing.html")

@app.route('/login', methods=["POST"])
def login_user():

    email = request.form.get("inputEmail")
    password = request.form.get("inputPassword")

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found! Please register!")
        return redirect('/')

    if user.password != password:
        flash("Incorrect password! Please try again!")
        return redirect('/')

    # get current user's friend requests and number of requests to display
    received_friend_requests, sent_friend_requests = get_friend_requests(user.user_id)
    num_recieved_requests = len(received_friend_requests)
    num_sent_requests = len(sent_friend_requests)
    num_total_requests = num_recieved_requests + num_sent_requests

    # use dict to store the user_id + more information about user
    session["user"] = {
        "username": user.username,
        "user_id": user.user_id,
        "num_recieved_requests": num_recieved_requests,
        "num_sent_requests": num_sent_requests,
        "num_total_requests": num_total_requests
    }

    return redirect('/user/{}'.format(user.user_id))

@app.route('/register', methods=["POST"])
def register_user():

    email = request.form.get("email")
    password = request.form.get("password")
    username = request.form.get("username")

    try:
        db.session.query(User).filter(User.email == email).one()

    except NoResultFound:
        new_user = User(email=email,
                        password=password,
                        username=username)
        db.session.add(new_user)
        db.session.commit()

        session["user"] = {
            "username": new_user.username,
            "user_id": new_user.user_id,
            "num_recieved_requests": 0,
            "num_sent_requests": 0,
            "num_total_requests": 0
        }

        flash("Thanks for registering! You're now signed in!")
        return redirect('/user/{}'.format(user.user_id))

    flash("We already have that email on record. Please login!")
    return redirect('/')

@app.route('/logout')
def logout():
    """ Logout user."""

    del session["user_id"]
    flash("You have now logged out!")
    return redirect('/')

@app.route('/home')
def home():
    """ User homepage with collective published posts."""

    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """ Presents all users."""

    users = db.session.query(User).all() 

    return render_template(users.html,
                            users=users)

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    """ User profile."""

    user = db.session.query(User).filter(User.user_id == user_id).one()

    # get user posts 
    # posts = db.session.query(Post).filter(Post.user_id == user_id).order_by(Post.post_id.desc())

    # total_posts = len(posts.all())
    # recent_posts = posts.limit(10).all()

    total_friends = len(get_friends(user.user_id).all())

    user_a_id = session['user']['user_id']
    user_b_id = user.user_id

    # analyze friend connection - are friends or is pending
    friends, pending_request = friends_or_pending(user_a_id, user_b_id)

    return render_template('profile.html',
                            user=user,
                            # total_posts=total_posts,
                            # recent_posts=recent_posts,
                            total_friends=total_friends,
                            friends=friends,
                            pending_request=pending_request)

@app.route('/add-friend', methods=["POST"])
def add_friend():
    """ Request another user's friendship."""

    user_a_id = session["user"]["user_id"]
    user_b_id = request.form.get("user_b_id")

    # check on connection between two users 
    is_friends, is_pending = friends_or_pending(user_a_id, user_b_id)

    if user_a_id == user_b_id:
        return "You can't friend yourself!"

    elif is_friends:
        return "You're already friends!"

    elif is_pending:
        return "Your friend request is pending. Please be patient."

    requested_relation = Relations(user_a_id=user_a_id,
                                    user_b_id=user_b_id,
                                    status="Requested")

    db.session.add(requested_relation)
    db.session.commit()

    # should print in the console 
    print "User ID %s has sent a friend request to User ID %s" % (user_a_id, user_b_id)

    return "Request Sent."

@app.route('/friends')
def show_friends_and_requests():
    """ Show friend requests and list of all friends."""

    # returns users for current user's friend requests
    received_friend_requests, sent_friend_requests = get_friend_requests(session["user"]["user_id"])

    # returns query for current user's friends 
    friends = get_friends(session["user"]["user_id"]).all() 

    return render_template("friends.html",
                            received_friend_requests=received_friend_requests,
                            sent_friend_requests=sent_friend_requests,
                            friends=friends)

@app.route('/friends/search', methods=["GET"])
def search_friends():
    """ Search for a user by email and return outcome."""

    # returns users for current user's friend requests 
    received_friend_requests, sent_friend_requests = get_friends(session["user"]["user_id"])

    # returns query for current user's friends 
    friends = get_friends(session["user"]["user_id"]).all() 

    user_input = request.args.get("q")

    # search user's query in users table and return results 
    search_results = search(db.session.query(User), user_input).all()

    return render_template("friends_search_results.html",
                            received_friend_requests=received_friend_requests,
                            sent_friend_requests=sent_friend_requests,
                            friends=friends,
                            search_results=search_results)

@app.route('/publish_post', methods=['POST'])
def publish_post():

    body = request.form.get("inputThought")
    user_id = session["user"]["user_id"]

    new_post = Post(body=body, user_id=user_id)

    db.session.add(new_post)
    db.session.commit()

    return redirect('/home')

@app.route('/post')
def post_list():
    """Show a list of all posts."""

    # returns all posts
    posts = db.session.query(Post).all() 

    return render_template("post_list.html", 
                            posts=posts)

@app.route('/post/<int:post_id>')
def post_page(post_id):
    """ Displays posts. """

    post = db.session.query(Post).filter(Post.post_id == post_id).one()

    return render_template("post_page.html", 
                            post=post)

################################################################################

if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()