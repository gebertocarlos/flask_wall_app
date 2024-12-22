from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# File where posts will be stored
POSTS_FILE = 'posts.json'

def load_posts():
    try:
        if os.path.exists(POSTS_FILE):
            with open(POSTS_FILE, 'r') as f:
                posts = json.load(f)
                # Convert timestamps back to datetime objects
                for post in posts:
                    post['timestamp'] = datetime.fromisoformat(post['timestamp'])
                    for comment in post['comments']:
                        comment['timestamp'] = datetime.fromisoformat(comment['timestamp'])
                return posts
        else:
            return []  # Return empty list if file does not exist
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading posts: {e}")
        return []  # Return empty list on error

def save_posts(posts):
    try:
        # Convert timestamps to ISO format before saving
        for post in posts:
            post['timestamp'] = post['timestamp'].isoformat()
            for comment in post['comments']:
                comment['timestamp'] = comment['timestamp'].isoformat()

        with open(POSTS_FILE, 'w') as f:
            json.dump(posts, f, default=str, indent=4)
    except Exception as e:
        print(f"Error saving posts: {e}")

# Dummy data for posts and comments (to be replaced with data from POSTS_FILE)
posts = load_posts()

# Route for the homepage, displaying posts
@app.route('/')
def home():
    # Sort posts by timestamp in descending order
    sorted_posts = sorted(posts, key=lambda post: post['timestamp'], reverse=True)
    return render_template('index.html', posts=sorted_posts)

# Route for creating a new post
@app.route('/create_post', methods=['POST'])
def create_post():
    data = request.get_json()
    content = data.get('content', '').strip()  # Remove extra whitespace

    if content:
        new_post = {
            'id': len(posts) + 1,
            'content': content,
            'timestamp': datetime.now(),
            'comments': [],
        }
        # Add the new post to the front to make it appear first (newest)
        posts.insert(0, new_post)
        save_posts(posts)  # Save posts to the file
        return jsonify({'success': True, 'post': new_post}), 201

    return jsonify({'success': False, 'message': 'No content provided'}), 400

# Route for adding a comment to a post
@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    data = request.get_json()
    content = data.get('content', '').strip()  # Remove extra whitespace

    if content:
        post = next((p for p in posts if p['id'] == post_id), None)
        if post:
            new_comment = {'content': content, 'timestamp': datetime.now()}
            # Add the new comment to the front of the comment list
            post['comments'].insert(0, new_comment)
            save_posts(posts)  # Save posts to the file
            return jsonify({'success': True, 'comment': new_comment})

    return jsonify({'success': False, 'message': 'Failed to add comment'}), 400

if __name__ == '__main__':
    # For Heroku deployment or other production environments, ensure the app listens on the correct port
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
