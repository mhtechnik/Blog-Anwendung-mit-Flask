from flask import Flask, render_template, abort, url_for, request, redirect
import json
from pathlib import Path

app = Flask(__name__)

DATA_DIR = Path(__file__).with_name("data")
POSTS_FILE = DATA_DIR / "posts.json"


def load_posts():
    if not POSTS_FILE.exists():
        return []
    with POSTS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_posts(posts):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with POSTS_FILE.open("w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    blog_posts = load_posts()
    return render_template('index.html', posts=blog_posts)


@app.route('/posts/<int:post_id>')
def post_detail(post_id: int):
    blog_posts = load_posts()
    post = next((p for p in blog_posts if p.get("id") == post_id), None)
    if not post:
        abort(404)
    return render_template('post_detail.html', post=post)


def _next_id(posts):
    return (max((p.get("id", 0) for p in posts)) + 1) if posts else 1


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        author = (request.form.get('author') or '').strip()
        title = (request.form.get('title') or '').strip()
        content = (request.form.get('content') or '').strip()

        if not author or not title or not content:
            return render_template('add.html', error='Bitte alle Felder ausfüllen.', form={'author': author, 'title': title, 'content': content})

        posts = load_posts()
        new_post = {
            'id': _next_id(posts),
            'author': author,
            'title': title,
            'content': content,
            'likes': 0,
        }
        posts.append(new_post)
        save_posts(posts)
        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/delete/<int:post_id>')
def delete(post_id: int):
    posts = load_posts()
    idx = next((i for i, p in enumerate(posts) if p.get('id') == post_id), None)
    if idx is not None:
        posts.pop(idx)
        save_posts(posts)
    
    return redirect(url_for('index'))


@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
def update(post_id: int):
    posts = load_posts()
    idx = next((i for i, p in enumerate(posts) if p.get('id') == post_id), None)
    if idx is None:
        return "Post not found", 404

    if request.method == 'POST':
        author = (request.form.get('author') or '').strip()
        title = (request.form.get('title') or '').strip()
        content = (request.form.get('content') or '').strip()

        if not author or not title or not content:
           
            return render_template('update.html', post={**posts[idx], 'author': author, 'title': title, 'content': content}, error='Bitte alle Felder ausfüllen.')

        posts[idx]['author'] = author
        posts[idx]['title'] = title
        posts[idx]['content'] = content
        save_posts(posts)
        return redirect(url_for('index'))

    
    return render_template('update.html', post=posts[idx])


@app.route('/like/<int:post_id>')
def like(post_id: int):
    posts = load_posts()
    idx = next((i for i, p in enumerate(posts) if p.get('id') == post_id), None)
    if idx is not None:
        
        current_likes = posts[idx].get('likes', 0)
        try:
            current_likes = int(current_likes)
        except (TypeError, ValueError):
            current_likes = 0
        posts[idx]['likes'] = current_likes + 1
        save_posts(posts)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
