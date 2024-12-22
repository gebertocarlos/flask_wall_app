import json
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Path to your JSON file
JSON_FILE = 'posts.json'

# Helper function to read data from the JSON file
def load_posts():
    try:
        with open(JSON_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Return an empty list if the file doesn't exist or is empty

# Helper function to save data to the JSON file
def save_posts(posts):
    with open(JSON_FILE, 'w') as file:
        json.dump(posts, file, default=str, indent=4)

# Dummy data for posts and comments
posts = load_posts()

@app.route('/')
def home():
    # Load the posts from the JSON file
    with open('posts.json', 'r') as f:
        posts = json.load(f)
    
    # Convert string timestamps back to datetime objects
    for post in posts:
        post['timestamp'] = datetime.fromisoformat(post['timestamp'])
        for comment in post['comments']:
            comment['timestamp'] = datetime.fromisoformat(comment['timestamp'])
    
    # Sort posts by timestamp in descending order
    sorted_posts = sorted(posts, key=lambda post: post['timestamp'], reverse=True)
    return render_template('index.html', posts=sorted_posts)

@app.route('/create_post', methods=['POST'])
def create_post():
    data = request.get_json()
    content = data.get('content')

    if content:
        new_post = {
            'id': len(posts) + 1,
            'content': content,
            'timestamp': str(datetime.now()),
            'comments': [],
        }
        posts.insert(0, new_post)  # Add the new post to the front
        save_posts(posts)  # Save posts to the JSON file
        return jsonify({'success': True, 'post': new_post})

    return jsonify({'success': False, 'message': 'No content provided'}), 400

# Route for adding a comment to a post
@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    data = request.get_json()
    content = data.get('content')

    if content:
        post = next((p for p in posts if p['id'] == post_id), None)
        if post:
            new_comment = {
                'content': content,
                'timestamp': str(datetime.now())
            }
            post['comments'].insert(0, new_comment)  # Add the new comment to the front
            save_posts(posts)  # Save posts to the JSON file
            return jsonify({'success': True, 'comment': new_comment})

    return jsonify({'success': False, 'message': 'Failed to add comment'}), 400

if __name__ == '__main__':
    app.run(debug=True)
