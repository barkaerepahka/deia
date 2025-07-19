from flask import Flask, request, redirect, render_template
import sqlite3
import string
import random
import os

app = Flask(__name__)
DB_NAME = 'urls.db'

# Crée la base de données si elle n'existe pas
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short TEXT UNIQUE,
                original TEXT NOT NULL
            )
        ''')

def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_id = generate_short_id()

        with sqlite3.connect(DB_NAME) as conn:
            try:
                conn.execute("INSERT INTO urls (short, original) VALUES (?, ?)", (short_id, original_url))
                conn.commit()
                short_url = request.host_url + short_id
                return render_template('index.html', short_url=short_url)
            except sqlite3.IntegrityError:
                return "Erreur : ce code existe déjà."
    return render_template('index.html')

@app.route('/<short_id>')
def redirect_to_original(short_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT original FROM urls WHERE short = ?", (short_id,))
        row = cursor.fetchone()
        if row:
            return redirect(row[0])
        return "URL non trouvée", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
