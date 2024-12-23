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
            'comments': []
        }
        posts.append(new_post)
        save_posts(posts)
        
        # Create a response version with string timestamp
        response_post = {
            **new_post,
            'timestamp': new_post['timestamp'].strftime('%B %d, %Y at %I:%M %p')
        }
        return jsonify({'success': True, 'post': response_post})
    
    return jsonify({'success': False, 'message': 'No content provided'}), 400

@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    data = request.get_json()
    content = data.get('content')
    
    if content:
        posts = load_posts()
        post = next((p for p in posts if p['id'] == post_id), None)
        
        if post:
            new_comment = {
                'content': content,
                'timestamp': datetime.now()
            }
            post['comments'].insert(0, new_comment)  # Add new comment at the beginning
            save_posts(posts)
            
            # Create a response version with string timestamp
            response_comment = {
                **new_comment,
                'timestamp': new_comment['timestamp'].strftime('%B %d, %Y at %I:%M %p')
            }
            return jsonify({'success': True, 'comment': response_comment})
    
    return jsonify({'success': False, 'message': 'Failed to add comment'}), 400

if __name__ == '__main__':
    app.run(debug=True)