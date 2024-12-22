from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wall.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Added timestamp for posts
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

@app.route('/')
def index():
    # Fetch posts ordered by timestamp descending to show the newest first
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post', methods=['POST'])
def create_post():
    content = request.form.get('content')
    new_post = Post(content=content)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    content = request.form.get('content')
    new_comment = Comment(content=content, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure the app context is set before creating the database tables
    with app.app_context():
        db.create_all()  # Initialize database
    app.run(debug=True)
