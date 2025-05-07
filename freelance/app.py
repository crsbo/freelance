from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# DB setup
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    role TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    service_type TEXT,
                    description TEXT,
                    whatsapp TEXT,
                    is_approved INTEGER,
                    user_id INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM services WHERE is_approved=1")
    services = c.fetchall()
    conn.close()
    return render_template('home.html', services=services)

@app.route('/post_service', methods=['GET', 'POST'])
def post_service():
    if request.method == 'POST':
        name = request.form['name']
        service_type = request.form['service_type']
        description = request.form['description']
        whatsapp = request.form['whatsapp']
        user_id = session['user_id']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO services (name, service_type, description, whatsapp, is_approved, user_id) VALUES (?, ?, ?, ?, 0, ?)",
                  (name, service_type, description, whatsapp, user_id))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('post_service.html')

@app.route('/admin_approve')
def admin_approve():
    if session.get('role') != 'admin':
        return redirect('/')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM services WHERE is_approved=0")
    services = c.fetchall()
    conn.close()
    return render_template('admin_approve.html', services=services)

@app.route('/approve/<int:service_id>', methods=['POST'])
def approve_service(service_id):
    if session.get('role') != 'admin':
        return redirect('/')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE services SET is_approved=1 WHERE id=?", (service_id,))
    conn.commit()
    conn.close()
    return redirect('/admin_approve')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
