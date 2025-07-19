from flask import Flask, request, redirect, render_template, url_for, send_file
from config import Config
from models import db, URL
import string, random, io, qrcode
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        alias = request.form.get('custom_alias')

        short = alias if alias else generate_code()
        new_url = URL(original=original_url, short=short)
        db.session.add(new_url)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template('index.html', error="Alias déjà utilisé.")

        short_url = request.host_url + short
        qr = qrcode.make(short_url)
        buffer = io.BytesIO()
        qr.save(buffer, format='PNG')
        qr_data = buffer.getvalue()

        return render_template('index.html', short_url=short_url, qr=qr_data)

    return render_template('index.html')

@app.route('/<short>')
def redirect_to_url(short):
    link = URL.query.filter_by(short=short).first_or_404()
    link.clicks += 1
    db.session.commit()
    return redirect(link.original)

@app.route('/static_qr.png')
def static_qr():
    return send_file(io.BytesIO(qr_data), mimetype='image/png')
