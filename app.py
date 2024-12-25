from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Path to your JSON file
JSON_FILE = 'posts.json'

# Helper function to read data from the JSON file
def load_posts():
    try:
        with open(JSON_FILE, 'r') as file:
            posts = json.load(file)
            # Convert string timestamps to datetime objects for proper sorting
            for post in posts:
                post['timestamp'] = datetime.fromisoformat(post['timestamp'])
                for comment in post['comments']:
                    comment['timestamp'] = datetime.fromisoformat(comment['timestamp'])
            return posts
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Helper function to save data to the JSON file
def save_posts(posts):
    # Convert datetime objects to strings before saving
    posts_to_save = []
    for post in posts:
        post_copy = post.copy()
        post_copy['timestamp'] = str(post_copy['timestamp'])
        post_copy['comments'] = [{**comment, 'timestamp': str(comment['timestamp'])} 
                               for comment in post_copy['comments']]
        posts_to_save.append(post_copy)
    
    with open(JSON_FILE, 'w') as file:
        json.dump(posts_to_save, file, indent=4)

@app.route('/')
def home():
    posts = load_posts()
    # Sort posts by timestamp in descending order (newest first)
    sorted_posts = sorted(posts, key=lambda post: post['timestamp'], reverse=True)
    return render_template('index.html', posts=sorted_posts)

@app.route('/create_post', methods=['POST'])
def create_post():
    data = request.get_json()
    content = data.get('content')
    
    if content:
        posts = load_posts()
        new_post = {
            'id': max([p['id'] for p in posts], default=0) + 1,
            'content': content,
            'timestamp': datetime.now(),
            'comments': [],
            'likes': {
                'count': 0,
                'users': []
            }
        }
        posts.append(new_post)
        save_posts(posts)
        
        response_post = {
            **new_post,
            'timestamp': new_post['timestamp'].strftime('%B %d, %Y at %H:%M')
        }
        return jsonify({'success': True, 'post': response_post})
    
    return jsonify({'success': False, 'message': 'No content provided'}), 400
# Add new route for handling likes
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    data = request.get_json()
    client_id = data.get('client_id')
    
    if not client_id:
        return jsonify({'success': False, 'message': 'No client ID provided'}), 400
        
    posts = load_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    
    if not post:
        return jsonify({'success': False, 'message': 'Post not found'}), 404
        
    # Initialize likes structure if it doesn't exist
    if 'likes' not in post:
        post['likes'] = {'count': 0, 'users': []}
        
    # Check if user has already liked
    if client_id not in post['likes']['users']:
        post['likes']['users'].append(client_id)
        post['likes']['count'] += 1
        save_posts(posts)
        return jsonify({
            'success': True,
            'likes': post['likes']['count'],
            'hasLiked': True
        })
    
    return jsonify({
        'success': False,
        'message': 'Already liked',
        'likes': post['likes']['count'],
        'hasLiked': True
    })

if __name__ == '__main__':
    app.run(debug=True)
def initialize_likes_for_posts():
    posts = load_posts()
    modified = False
    for post in posts:
        if 'likes' not in post:
            post['likes'] = {
                'count': 0,
                'users': []
            }
            modified = True
    if modified:
        save_posts(posts)

# Call this when your app starts
@app.before_first_request
def setup():
    initialize_likes_for_posts()
