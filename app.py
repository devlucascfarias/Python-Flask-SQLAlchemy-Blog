from flask import render_template, flash
from flask import Flask, url_for, redirect, session, request, abort
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os



load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'

from database import db
db.init_app(app)

from models import Post, Comment, Like

with app.app_context():
    db.create_all()

app.secret_key = 'your-secret-key'  
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  
    client_kwargs={'scope': 'email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

ADMIN_MAIL = os.getenv("ADMIN_MAIL")

@app.route('/')
def index():
    name = session.get('name', 'Guest')
    all_posts = Post.query.outerjoin(Like).group_by(Post.id).order_by(desc(func.count(Like.id))).all()
    return render_template('index.html', other_users_posts=all_posts, name=name, ADMIN_MAIL=ADMIN_MAIL)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session['email'] = user_info['email']
    session['name'] = user_info['name']
    session['user_image'] = user_info['picture']


    return redirect(url_for('index'))

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/adminpanel')
def adminpanel():
    user_id = session.get('email', None)  
    if user_id != ADMIN_MAIL:
        abort(403)  

    name = session.get('name', 'Guest')
    comments = Comment.query.all()  
    own_posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    other_users_posts = Post.query.filter(Post.user_id != user_id).outerjoin(Like).group_by(Post.id).order_by(desc(func.count(Like.id))).all()

    return render_template('adminpanel.html', name=name, own_posts=own_posts, other_users_posts=other_users_posts, comments=comments, ADMIN_MAIL=ADMIN_MAIL)

@app.route('/post', methods=['POST'])
def post():
    title = request.form.get('title')
    tags = request.form.get('tags')
    cover_image = request.files['cover_image']
    filename = secure_filename(cover_image.filename)
    cover_image.save(os.path.join('static/img/', filename))
    cover_image_url = url_for('static', filename='img/' + filename)
    content = request.form.get('content')

    user_id = session['email']  
    user_image = session['user_image']  
    user_name = session['name']  

    post = Post(title=title, content=content, user_id=user_id, user_name=user_name, user_image=user_image, cover_image_url=cover_image_url, tags=tags)

    db.session.add(post)
    db.session.commit()
    return redirect(url_for('adminpanel'))

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'email' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    user_id = session['email']
    like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(user_id=user_id, post_id=post_id)
        db.session.add(like)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def comment_post(post_id):
    content = request.form.get('content')
    user_id = session['email']
    user_name = session['name']  
    user_image = session['user_image'] 
    comment = Comment(content=content, user_id=user_id, user_name=user_name, user_image=user_image, post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index'))
    
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != session['email']:
        abort(403)
    
    Comment.query.filter_by(post_id=post_id).delete()

    flash('Post deleted successfully', 'success')  

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('adminpanel'))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if 'email' not in session:
        return redirect(url_for('index'))

    comment = Comment.query.get(comment_id)

    flash('Comment deleted successfully', 'success')  

    if comment:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete_all_comments', methods=['GET', 'POST'])
def delete_all_comments():
    if 'email' not in session or session['email'] != ADMIN_MAIL:
        abort(403)

    Comment.query.delete()
    db.session.commit()

    flash('All comments deleted successfully', 'success')  

    return redirect(url_for('adminpanel'))

@app.route('/delete_all_posts', methods=['GET', 'POST'])
def delete_all_posts():
    if 'email' not in session or session['email'] != ADMIN_MAIL:
        abort(403)

    Post.query.delete()
    db.session.commit()

    flash('All posts deleted successfully', 'success')  

    return redirect(url_for('adminpanel'))

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    user_id = session.get('email', None)  
    if user_id != ADMIN_MAIL:
        abort(403)  

    post = Post.query.get(post_id)
    if request.method == 'POST':
        content = request.form.get('content')  
        if content is not None:
            post.content = content
            db.session.commit()

        flash('Post edited successfully', 'success')  

        return redirect(url_for('adminpanel'))
    else:  
        return render_template('edit_post.html', post=post)
    
@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get(post_id)
    if post is None:
        abort(404)
    return render_template('view_post.html', post=post)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
