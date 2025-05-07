from flask import Flask, render_template, request, redirect, session
import os
from users import users

app = Flask(__name__)
app.secret_key = 'supersecret'

services = []
pending_services = []
admins = ['admin1', 'admin2']

@app.route('/')
def index():
    if 'username' not in session:
        return redirect('/login')
    approved = [s for s in services if s['approved']]
    return render_template('home.html', services=approved, user=session['username'], admin=session.get('is_admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        for u in users:
            if u['username'] == user and u['password'] == pwd:
                session['username'] = user
                session['is_admin'] = user in admins
                return redirect('/')
        return "Invalid login. <a href='/login'>Try again</a>"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        for u in users:
            if u['username'] == user:
                return "User already exists. <a href='/register'>Try again</a>"
        admin_code = request.form.get('admin_code')
        is_admin = (admin_code == '2025')
        users.append({'username': user, 'password': pwd})
        if is_admin and user not in admins:
            admins.append(user)
        return redirect('/login')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/post', methods=['GET', 'POST'])
def post():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'title': request.form['title'],
            'description': request.form['description'],
            'whatsapp': request.form['whatsapp'],
            'price': request.form['price'],
            'approved': False
        }
        services.append(data)
        pending_services.append(data)
        return redirect('/')
    return render_template('post_service.html')

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect('/')
    return render_template('admin_dashboard.html', pending=pending_services)

@app.route('/approve/<int:index>')
def approve(index):
    if not session.get('is_admin'):
        return redirect('/')
    pending_services[index]['approved'] = True
    pending_services.pop(index)
    return redirect('/admin')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
