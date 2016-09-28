""" Models for Inscription. """

from flask_sqlalchemy import SQLAlchemy 
from flask import current_app, request, url_for 

db = SQLAlchemy()

################################################################################

class Relations(db.Model):
    __tablename__ = 'relations'

    relations_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_a_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user_b_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    status = db.Column(db.String(100), nullable=False)

    # define relations 
    user_a = db.relationship("User", foreign_keys=[user_a_id], backref=db.backref("sent_connections"))
    user_b = db.relationship("User", foreign_keys=[user_b_id], backref=db.backref("received_connections"))

    def __repr__(self):

        return "<Relations relations_id={} user_a_id={} user_b_id={}>".format(self.relations_id,
                                                                            self.user_a_id,
                                                                            self.user_b_id)
class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    
    # comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def __repr__(self):

        return "User user_id={} email={}>".format(self.user_id, self.email)

class Post(db.Model):
    __tablename__ = 'post'

    post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    body = db.Column(db.String, nullable=False)

    # establish relationship between post and user 
    user = db.relationship('User', backref=db.backref("post"), order_by=user_id)

    def __repr__(self):

        return "Post post_id={}>".format(self.post_id)

class Comment(db.Model):
    __tablename__ = 'comment'

    comment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    body = db.Column(db.Text, nullable=False)

    # establish relationships between other tables
    user = db.relationship('User', backref=db.backref("comment"), order_by=user_id)
    post = db.relationship('Post', backref=db.backref("comment"), order_by=post_id)

    def __repr__(self):

        return "Comment comment_id={}>".format(self.comment_id)

# class Image(db.Model):
#     __tablename__ = 'image'

#     image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
#     url = db.Column(db.String(200), nullable=False)

#     # define relationship to user 
#     user = db.relationship('User', backref=db.backref("image"), order_by=user_id)

#     def __repr__(self):

#         return "<Image image_id={} user_id={}".format(self.image_id, self.user_id)

####################################################################################
# Helper functions for model.py

def connect_to_db(app):
    """Connect to db in Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///inscription'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."



