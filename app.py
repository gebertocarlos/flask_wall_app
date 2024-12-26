from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import threading
import time

app = Flask(__name__)

# JSON dosyasının yolu
JSON_FILE = 'posts.json'

# JSON dosyası için kilit mekanizması
file_lock = threading.Lock()

# Memory cache
posts_cache = None
last_save_time = 0
SAVE_DELAY = 0.5  # 500ms

# JSON dosyasından veri okuma işlevi
def load_posts():
    global posts_cache
    if posts_cache is not None:
        return posts_cache

    with file_lock:
        try:
            with open(JSON_FILE, 'r') as file:
                posts = json.load(file)
                # Zaman damgalarını datetime nesnelerine dönüştürme
                for post in posts:
                    post['timestamp'] = datetime.fromisoformat(post['timestamp'])
                    for comment in post['comments']:
                        comment['timestamp'] = datetime.fromisoformat(comment['timestamp'])
                posts_cache = posts
                return posts
        except (FileNotFoundError, json.JSONDecodeError):
            posts_cache = []
            return []

# JSON dosyasına veri kaydetme işlevi
def save_posts(posts, force=False):
    global last_save_time, posts_cache
    current_time = time.time()
    
    # Cache'i güncelle
    posts_cache = posts

    # Eğer zorunlu kayıt değilse ve son kayıttan bu yana yeterli zaman geçmediyse kaydetme
    if not force and (current_time - last_save_time) < SAVE_DELAY:
        return

    with file_lock:
        posts_to_save = []
        for post in posts:
            post_copy = post.copy()
            post_copy['timestamp'] = str(post_copy['timestamp'])
            post_copy['comments'] = [{**comment, 'timestamp': str(comment['timestamp'])} 
                                   for comment in post_copy['comments']]
            posts_to_save.append(post_copy)
        
        with open(JSON_FILE, 'w') as file:
            json.dump(posts_to_save, file, indent=4)
        
        last_save_time = current_time

# Like işleme fonksiyonu
def process_like(item, user_ip):
    if not isinstance(item.get('liked_by', []), list):
        item['liked_by'] = []
    if not isinstance(item.get('likes', 0), int):
        item['likes'] = 0
    
    try:
        if user_ip in item['liked_by']:
            item['likes'] = max(0, item['likes'] - 1)
            item['liked_by'].remove(user_ip)
            is_liked = False
        else:
            item['likes'] += 1
            item['liked_by'].append(user_ip)
            is_liked = True
        
        return True, item['likes'], is_liked
    except Exception as e:
        print(f"Like işleme hatası: {e}")
        return False, 0, False

# Ana sayfa rotası
# Bu işlev gönderileri yükler, zaman damgalarına göre sıralar ve gönderilerle birlikte ana sayfayı render eder.
@app.route('/')
def home():
    user_ip = request.remote_addr
    posts = load_posts()
    
    # Her post ve yorum için like durumunu kontrol et
    for post in posts:
        # Post like durumu
        post['is_liked'] = user_ip in post.get('liked_by', [])
        
        # Yorumların like durumu
        for comment in post.get('comments', []):
            comment['is_liked'] = user_ip in comment.get('liked_by', [])
    
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
            'liked_by': []  # IP adreslerini saklamak için
        }
        posts.append(new_post)
        save_posts(posts)
        
        response_post = {
            **new_post,
            'timestamp': new_post['timestamp'].strftime('%B %d, %Y at %H:%M')  # 24 saat formatı
        }
        return jsonify({'success': True, 'post': response_post})
    
    return jsonify({'success': False, 'message': 'İçerik sağlanmadı'}), 400

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
    
    with file_lock:
        try:
            posts = load_posts()
            post = next((p for p in posts if p['id'] == post_id), None)
            
            if post:
                comment = next((c for c in post['comments'] if c.get('id') == comment_id), None)
                if comment:
                    success, likes, is_liked = process_like(comment, user_ip)
                    if success:
                        # Gecikmeli kayıt
                        save_posts(posts, force=False)
                        return jsonify({
                            'success': True,
                            'likes': likes,
                            'is_liked': is_liked
                        })
        except Exception as e:
            print(f"Yorum like hatası: {e}")
    
    return jsonify({'success': False, 'message': 'Comment not found'}), 404

# Belirli bir gönderiye like ekleme/kaldırma rotası
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    user_ip = request.remote_addr
    
    with file_lock:
        try:
            posts = load_posts()
            post = next((p for p in posts if p['id'] == post_id), None)
            
            if post:
                success, likes, is_liked = process_like(post, user_ip)
                if success:
                    # Gecikmeli kayıt
                    save_posts(posts, force=False)
                    return jsonify({
                        'success': True,
                        'likes': likes,
                        'is_liked': is_liked
                    })
        except Exception as e:
            print(f"Post like hatası: {e}")
    
    return jsonify({'success': False, 'message': 'Post not found'}), 404

# Uygulama kapatılırken son değişiklikleri kaydet
@app.teardown_appcontext
def save_on_shutdown(exception=None):
    if posts_cache is not None:
        save_posts(posts_cache, force=True)

# Uygulamanın ana giriş noktası
# Bu işlev, Flask uygulamasını geliştirme modunda çalıştırır.
if __name__ == '__main__':
    app.run(debug=True)
