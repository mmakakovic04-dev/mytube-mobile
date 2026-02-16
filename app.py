import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mytube-mega-secret-777'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mytube.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AVATAR_FOLDER'] = 'static/avatars'

# Создаем папки, если их нет
for folder in [app.config['UPLOAD_FOLDER'], app.config['AVATAR_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

db = SQLAlchemy(app)

# --- МОДЕЛИ БАЗЫ ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(200), default='default.png')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    is_shorts = db.Column(db.Boolean, default=False)
    likes_count = db.relationship('Like', backref='video', lazy=True, cascade="all, delete-orphan")

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

with app.app_context():
    db.create_all()

# --- МАРШРУТЫ САЙТА ---

@app.route('/')
def index():
    u = User.query.filter_by(username=session.get('user')).first() if 'user' in session else None
    shorts = Video.query.filter_by(is_shorts=True).order_by(Video.id.desc()).all()
    videos = Video.query.filter_by(is_shorts=False).order_by(Video.id.desc()).all()
    return render_template('index.html', shorts=shorts, videos=videos, user_data=u)

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session: return redirect(url_for('login'))
    file = request.files['video']
    if file and file.filename != '':
        name = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], name))
        new_v = Video(filename=name, author=session['user'], is_shorts='is_shorts' in request.form)
        db.session.add(new_v)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/like/<int:video_id>')
def like(video_id):
    if 'user' not in session: return redirect(url_for('login'))
    u = User.query.filter_by(username=session['user']).first()
    existing_like = Like.query.filter_by(user_id=u.id, video_id=video_id).first()
    if existing_like:
        db.session.delete(existing_like)
    else:
        db.session.add(Like(user_id=u.id, video_id=video_id))
    db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/set_avatar', methods=['POST'])
def set_avatar():
    if 'user' not in session: return redirect(url_for('login'))
    file = request.files['avatar']
    if file:
        u = User.query.filter_by(username=session['user']).first()
        name = secure_filename(f"av_{u.id}_{file.filename}")
        file.save(os.path.join(app.config['AVATAR_FOLDER'], name))
        u.avatar = name
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/video_details/<int:video_id>')
def video_details(video_id):
    v = Video.query.get_or_404(video_id)
    author = User.query.filter_by(username=v.author).first()
    others = Video.query.filter(Video.id != video_id).limit(6).all()
    return render_template('video_page.html', video=v, suggestions=others, author_data=author)

@app.route('/v/<filename>')
def serve_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- РЕГИСТРАЦИЯ И ВХОД ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed = generate_password_hash(request.form['password'])
        db.session.add(User(username=request.form['username'], password=hashed))
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form['username']).first()
        if u and check_password_hash(u.password, request.form['password']):
            session['user'] = u.username
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# --- API ДЛЯ МОБИЛЬНОГО ПРИЛОЖЕНИЯ ---

@app.route('/api/videos')
def api_videos():
    all_v = Video.query.all()
    return jsonify([{
        "id": v.id,
        "title": v.filename,
        "author": v.author,
        "likes": len(v.likes_count),
        "is_shorts": v.is_shorts
    } for v in all_v])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)