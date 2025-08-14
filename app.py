from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import string, random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Create tables immediately at startup
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        existing = URL.query.filter_by(long_url=long_url).first()
        if existing:
            return render_template('index.html', short_url=request.host_url + existing.short_code)

        short_code = generate_short_code()
        while URL.query.filter_by(short_code=short_code).first():
            short_code = generate_short_code()

        new_url = URL(long_url=long_url, short_code=short_code)
        db.session.add(new_url)
        db.session.commit()
        return render_template('index.html', short_url=request.host_url + short_code)

    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_url(short_code):
    url_entry = URL.query.filter_by(short_code=short_code).first()
    if url_entry:
        return redirect(url_entry.long_url)
    return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
