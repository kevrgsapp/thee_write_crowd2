from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from . import db
from .models import User, Post
from werkzeug import exceptions
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import os


main = Blueprint('main', __name__)
POSTS_PER_PAGE=20

@main.route('/')
def index():
    return render_template('index.html', user=current_user)

@main.route('/feed')
def feed():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    next_url = url_for('main.feed', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.feed', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('feed.html', title='Home', user=current_user,
                           posts=posts.items, plen=len(posts.items), next_url=next_url,
                           prev_url=prev_url)

@main.route('/discover')
def discover():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    next_url = url_for('main.discover', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.discover', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('discover.html', title='Home', user=current_user,
                           posts=posts.items, plen=len(posts.items), next_url=next_url,
                           prev_url=prev_url)



@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/profile/edit')
@login_required
def profile_edit():
    return render_template('profile_edit.html', user=current_user)

@main.route('/profile_edit', methods=["GET","POST"])
@login_required
def profile_post():
    username = request.form.get('username')
    email = request.form.get('email')
    name = request.form.get('name')

    user=current_user
    user.username = username
    user.email = email
    user.name = name

    db.session.commit()
    return redirect(url_for('main.profile'))

@main.route('/post')
@login_required
def post():
    return render_template('post.html', user=current_user)

@main.route('/post_post', methods=['POST','GET'])
@login_required
def post_post():
    user=User.query.get_or_404(current_user.id)
    # posts=user.posts
    post=Post(
        author=user,
        title=request.form.get('title'),
        subtitle=request.form.get('subtitle'),
        body=request.form.get('body'),
        category=request.form.get('category'),
        wordcount=len(request.form.get('body').split())
    )
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('main.profile'))

@main.route('/user/<username>')
@login_required
def user_page(username):
    user=User.query.filter_by(username=username).first_or_404()
    followers=len(user.followers.all())
    return render_template('page.html', current_user=current_user, user=user, utime=datetime.strftime(user.created_at,'%m/%d/%Y'), posts=user.posts, plen=len(user.posts.all()),followers=followers)


@main.route('/post/<p>')
@login_required
def post_page(p):
    post=Post.query.filter_by(id=int(p)).first_or_404()
    ptime=datetime.strftime(post.timestamp,'%m/%d/%Y')
    return render_template('post_page.html', current_user=current_user, post=post, ptime=ptime)

@main.route('/post/<id>/edit', methods=["GET","POST"])
@login_required
def post_edit(id):
    post = Post.query.filter_by(id=id).first()
    return render_template('post_edit.html', post=post)

@main.route('/post_edit_post', methods=["GET","POST"])
@login_required
def post_edit_post():
    id=int(request.form.get('id'))
    post = Post.query.get_or_404(id)
    post.title=request.form.get('title')
    post.subtitle=request.form.get('subtitle')
    post.body=request.form.get('body')
    post.wordcount=len(request.form.get('body').split())
    print(post.title,post.subtitle)

    db.session.commit()
    return redirect(url_for('main.post_page',username=post.author.username,p=post.id))

@main.route('/post_delete', methods=["GET","POST"])
@login_required
def post_delete():
    id=int(request.form.get('id'))
    del_post = Post.query.get_or_404(id)
    usern=del_post.author.username
    db.session.delete(del_post)
    db.session.commit()
    return redirect(url_for('main.user_page',username=usern))

@main.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username),'is-danger')
        return redirect(url_for('main.profile'))
    if user == current_user:
        flash('You cannot follow yourself!','is-danger')
        return redirect(url_for('main.user_page', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username),'is-success')
    return redirect(url_for('main.user_page', username=username))

@main.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username),'is-danger')
        return redirect(url_for('main.profile'))
    if user == current_user:
        flash('You cannot unfollow yourself!','is-danger')
        return redirect(url_for('main.user_page', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {} anymore.'.format(username),'is-success')
    return redirect(url_for('main.user_page', username=username))