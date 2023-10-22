from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db, loads, dumps
from hashlib import md5
from datetime import datetime
# from enum import Enum


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)
followeds = db.Table('followeds',
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'))
)

# class Categories(Enum):
#     bio=0
#     blog=1
#     childrens=2
#     fantasy=3
#     horror=4
#     mystery=5
#     religon=6
#     romance=7
#     thriller=8
#     young_adult=9


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),server_default=func.now())
    bio = db.Column(db.Text)
    # settings = db.Column(db.Text)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    # followings = db.relationship(
    #     'User', secondary=followeds,
    #     primaryjoin=(followeds.c.followed_id == id),
    #     secondaryjoin=(followeds.c.follower_id == id),
    #     backref=db.backref('followeds', lazy='dynamic'), lazy='dynamic')
    # followers.all()
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            # user.followings.append(self)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            # user.followings.remove(self)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    def followed_posts(self):
        return Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Post.timestamp.desc())
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class Post(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(10), nullable=False)
    subtitle = db.Column(db.String(32), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    wordcount = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category = db.Column(db.String(12))
    def __repr__(self):
        return '<Post {}>'.format(self.title)