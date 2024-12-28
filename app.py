from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os
import logging

app = Flask(__name__)

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JSON dosyasının yolu
JSON_FILE = 'posts.json'

# Başlangıç verisi
INITIAL_POST = {
    "id": 1,
    "content": "<h1 class=\"ql-align-center\"><strong>WELCOME TO THE WALL</strong></h1><p><br></p><p>This app is a community wall platform where users can share their thoughts, ideas, and updates in real time.</p>",
    "timestamp": datetime.now().isoformat(),
    "comments": [],
    "likes": 0,
    "liked_by": []
}

# JSON dosyasından veri okuma işlevi
def load_posts():
    try:
        if not os.path.exists(JSON_FILE):
            # Dosya yoksa başlangıç verisiyle oluştur
            with open(JSON_FILE, 'w') as file:
                json.dump([INITIAL_POST], file, indent=4)
            return [INITIAL_POST]

        with open(JSON_FILE, 'r') as file:
            posts = json.load(file)
            # Zaman damgalarını datetime nesnelerine dönüştürme
            for post in posts:
                post['timestamp'] = datetime.fromisoformat(post['timestamp'])
                for comment in post['comments']:
                    comment['timestamp'] = datetime.fromisoformat(comment['timestamp'])
            return posts
    except Exception as e:
        print(f"Error loading posts: {str(e)}")
        return [INITIAL_POST]

# JSON dosyasına veri kaydetme işlevi
def save_posts(posts):
    try:
        posts_to_save = []
        for post in posts:
            post_copy = post.copy()
            post_copy['timestamp'] = str(post_copy['timestamp'])
            post_copy['comments'] = [{**comment, 'timestamp': str(comment['timestamp'])} 
                                   for comment in post_copy['comments']]
            posts_to_save.append(post_copy)
        
        with open(JSON_FILE, 'w') as file:
            json.dump(posts_to_save, file, indent=4)
    except Exception as e:
        logger.error(f"Error saving posts: {str(e)}")
        raise

# Ana sayfa rotası
# Bu işlev gönderileri yükler, zaman damgalarına göre sıralar ve gönderilerle birlikte ana sayfayı render eder.
@app.route('/')
def home():
    posts = load_posts()
    sorted_posts = sorted(posts, key=lambda post: post['timestamp'], reverse=True)
    return render_template('index.html', posts=sorted_posts)

# Yeni gönderi oluşturma rotası
# Bu işlev, yeni bir gönderi oluşturmak için POST isteğini işler. Giriş verisini doğrular, gönderiyi listeye ekler ve JSON dosyasına kaydeder.
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
            'likes': 0,
            'liked_by': []  # IP addresses for tracking likes
        }
        posts.append(new_post)
        save_posts(posts)
        
        response_post = {
            **new_post,
            'timestamp': new_post['timestamp'].strftime('%B %d, %Y at %H:%M')  # 24-hour format
        }
        return jsonify({'success': True, 'post': response_post})
    
    return jsonify({'success': False, 'message': 'Content not provided'}), 400

# Belirli bir gönderiye yorum ekleme rotası
# Bu işlev, bir gönderiye yorum eklemek için POST isteğini işler, giriş verisini doğrular ve doğru gönderiye yorumu ekler.
@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    data = request.get_json()
    content = data.get('content')
    
    if content:
        posts = load_posts()
        post = next((p for p in posts if p['id'] == post_id), None)
        
        if post:
            new_comment = {
                'id': max([c.get('id', 0) for c in post['comments']], default=0) + 1,
                'content': content,
                'timestamp': datetime.now(),
                'likes': 0,
                'liked_by': []
            }
            post['comments'].append(new_comment)
            save_posts(posts)
            
            response_comment = {
                **new_comment,
                'timestamp': new_comment['timestamp'].strftime('%B %d, %Y at %H:%M')
            }
            return jsonify({'success': True, 'comment': response_comment})
    
    return jsonify({'success': False, 'message': 'Comment could not be added'}), 400

# Belirli bir yoruma like ekleme/kaldırma rotası
@app.route('/like_comment/<int:post_id>/<int:comment_id>', methods=['POST'])
def like_comment(post_id, comment_id):
    user_ip = request.remote_addr
    posts = load_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    
    if post:
        comment = next((c for c in post['comments'] if c.get('id') == comment_id), None)
        if comment:
            if 'liked_by' not in comment:
                comment['liked_by'] = []
            if 'likes' not in comment:
                comment['likes'] = 0
                
            if user_ip in comment['liked_by']:
                comment['likes'] -= 1
                comment['liked_by'].remove(user_ip)
            else:
                comment['likes'] += 1
                comment['liked_by'].append(user_ip)
                
            save_posts(posts)
            return jsonify({'success': True, 'likes': comment['likes'], 'is_liked': user_ip in comment['liked_by']})
                
    return jsonify({'success': False, 'message': 'Comment not found'}), 404

# Belirli bir gönderiye like ekleme/kaldırma rotası
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    user_ip = request.remote_addr
    posts = load_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    
    if post:
        if 'liked_by' not in post:
            post['liked_by'] = []
        if 'likes' not in post:
            post['likes'] = 0
            
        if user_ip in post['liked_by']:
            post['likes'] -= 1
            post['liked_by'].remove(user_ip)
        else:
            post['likes'] += 1
            post['liked_by'].append(user_ip)
            
        save_posts(posts)
        return jsonify({'success': True, 'likes': post['likes'], 'is_liked': user_ip in post['liked_by']})
    
    return jsonify({'success': False, 'message': 'Post not found'}), 404

# Uygulamanın ana giriş noktası
# Bu işlev, Flask uygulamasını geliştirme modunda çalıştırır.
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
