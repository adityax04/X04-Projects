from flask import Flask, request, redirect, url_for, session, flash, render_template_string
from cryptography.fernet import Fernet
import sqlite3, os, pyotp, qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'super_secret_key'
DB_NAME = 'vault.db'
FERNET_FILE = 'fernet.key'
TOTP_FILE = 'totp_secret.key'

if os.path.exists(FERNET_FILE):
    KEY = open(FERNET_FILE, 'rb').read()
else:
    KEY = Fernet.generate_key()
    open(FERNET_FILE, 'wb').write(KEY)
fernet = Fernet(KEY)

if os.path.exists(TOTP_FILE):
    TOTP_SECRET = open(TOTP_FILE).read()
else:
    TOTP_SECRET = pyotp.random_base32()
    open(TOTP_FILE, 'w').write(TOTP_SECRET)

def generate_qr_uri():
    uri = pyotp.TOTP(TOTP_SECRET).provisioning_uri(name="VaultApp", issuer_name="JarvisVault")
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format='PNG')
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            username TEXT,
            password TEXT
        )''')

LOGIN_HTML = """
<!DOCTYPE html>
<html lang='en'>
<head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>Login</title><script src='https://cdn.tailwindcss.com'></script></head>
<body class='bg-gradient-to-tr from-indigo-100 to-blue-50 min-h-screen flex items-center justify-center'>
  <form method='POST' class='bg-white p-8 rounded-2xl shadow-lg w-full max-w-sm space-y-5'>
    <h2 class='text-3xl font-bold text-center text-gray-800'>🔐 Jarvis Vault Login</h2>
    <input type='password' name='password' placeholder='Enter Admin Password' class='w-full p-3 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400' required>
    <button type='submit' class='w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700'>Continue</button>
    {% with messages = get_flashed_messages() %}{% if messages %}<p class='text-red-500 text-center'>{{ messages[0] }}</p>{% endif %}{% endwith %}
  </form>
</body></html>
"""

OTP_HTML = """
<!DOCTYPE html>
<html lang='en'>
<head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>OTP Verification</title><script src='https://cdn.tailwindcss.com'></script></head>
<body class='bg-gradient-to-br from-indigo-100 to-white min-h-screen flex justify-center items-center'>
  <form method='POST' class='bg-white p-8 rounded-xl shadow-xl text-center space-y-5 w-full max-w-sm'>
    <h2 class='text-2xl font-bold text-gray-800'>Enter OTP</h2>
    <img src='{{ qr }}' alt='QR Code' class='w-32 h-32 mx-auto'>
    <input type='text' name='otp' placeholder='6-digit OTP' class='w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500' required>
    <button type='submit' class='bg-green-600 text-white py-2 px-6 rounded hover:bg-green-700 w-full'>Verify</button>
    {% with messages = get_flashed_messages() %}{% if messages %}<p class='text-red-500'>{{ messages[0] }}</p>{% endif %}{% endwith %}
  </form>
</body></html>
"""

ADD_HTML = """
<!DOCTYPE html>
<html lang='en'>
<head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>Add Entry</title><script src='https://cdn.tailwindcss.com'></script></head>
<body class='bg-gradient-to-r from-indigo-100 to-blue-50 min-h-screen flex items-center justify-center px-4'>
  <div class='bg-white p-8 rounded-xl shadow-xl w-full max-w-lg'>
    <h2 class='text-3xl font-semibold text-center text-gray-800 mb-6'>📝 Add Vault Entry</h2>
    <form method='POST' class='space-y-4'>
      <div>
        <label class='block text-gray-700 font-medium mb-1'>Title</label>
        <input type='text' name='title' placeholder='Enter Title' class='w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500' required>
      </div>
      <div>
        <label class='block text-gray-700 font-medium mb-1'>Username</label>
        <input type='text' name='username' placeholder='Enter Username' class='w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500' required>
      </div>
      <div>
        <label class='block text-gray-700 font-medium mb-1'>Password</label>
        <input type='password' name='password' placeholder='Enter Password' class='w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500' required>
      </div>
      <button type='submit' class='w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition duration-200'>Save Entry</button>
    </form>
    <div class='mt-6 text-center'>
      <a href='/' class='text-sm text-gray-600 hover:text-indigo-600 transition duration-200'>← Back to Dashboard</a>
    </div>
  </div>
</body>
</html>
"""

VIEW_HTML = """
<!DOCTYPE html>
<html lang='en'>
<head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>View Entry</title><script src='https://cdn.tailwindcss.com'></script></head>
<body class='bg-gray-100 min-h-screen flex items-center justify-center p-6'>
  <div class='bg-white rounded-xl shadow-lg max-w-md w-full p-8 space-y-6'>
    <h2 class='text-2xl font-bold text-center text-gray-800'>🔍 Vault Entry Details</h2>
    <div class='space-y-4'>
      <div>
        <label class='block text-sm font-medium text-gray-600'>Title</label>
        <div class='mt-1 p-3 bg-gray-100 rounded text-gray-800'>{{ title }}</div>
      </div>
      <div>
        <label class='block text-sm font-medium text-gray-600'>Username</label>
        <div class='mt-1 p-3 bg-gray-100 rounded text-gray-800'>{{ username }}</div>
      </div>
      <div>
        <label class='block text-sm font-medium text-gray-600'>Password</label>
        <div class='mt-1 p-3 bg-gray-100 rounded text-gray-800'>{{ password }}</div>
      </div>
    </div>
    <div class='text-center'>
      <a href='/' class='text-sm text-indigo-600 hover:underline'>← Back to Dashboard</a>
    </div>
  </div>
</body></html>
"""

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect(DB_NAME) as conn:
        entries = conn.execute("SELECT id, title, username FROM entries").fetchall()
    rows = "".join([
        f"<tr class='border-b'><td class='p-3'>{e[1]}</td><td class='p-3'>{e[2]}</td><td class='p-3'><a href='/view/{e[0]}' class='text-blue-600 hover:underline'>View</a> | <a href='/delete/{e[0]}' class='text-red-600 hover:underline'>Delete</a></td></tr>"
        for e in entries
    ])
    html = f"""
<!DOCTYPE html>
<html lang='en'>
<head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>Dashboard</title><script src='https://cdn.tailwindcss.com'></script></head>
<body class='bg-gray-100 px-4 py-6'>
<div class='max-w-3xl mx-auto'>
  <h1 class='text-3xl font-bold mb-6'>🔐 Your Vault</h1>
  <a href='/add' class='bg-blue-600 text-white px-4 py-2 rounded mb-4 inline-block hover:bg-blue-700'>+ Add Entry</a>
  <table class='w-full bg-white rounded shadow'>
    <thead class='bg-gray-200'><tr><th class='p-3 text-left'>Title</th><th>Username</th><th>Actions</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <a href='/logout' class='block mt-4 text-sm text-gray-500 hover:underline'>Logout</a>
</div></body></html>
    """
    return html

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'step' not in session:
            if request.form['password'] == 'admin123':
                session['step'] = 'otp'
                return render_template_string(OTP_HTML, qr=generate_qr_uri())
            else:
                flash("Wrong password")
        else:
            otp = request.form.get('otp')
            if pyotp.TOTP(TOTP_SECRET).verify(otp):
                session['user'] = 'admin'
                session.pop('step', None)
                return redirect(url_for('home'))
            else:
                flash("Invalid OTP")
                return render_template_string(OTP_HTML, qr=generate_qr_uri())
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        username = request.form['username']
        password = fernet.encrypt(request.form['password'].encode()).decode()
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO entries (title, username, password) VALUES (?, ?, ?)", (title, username, password))
        return redirect(url_for('home'))
    return render_template_string(ADD_HTML)

@app.route('/view/<int:id>')
def view(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute("SELECT title, username, password FROM entries WHERE id = ?", (id,)).fetchone()
    if row:
        password = fernet.decrypt(row[2].encode()).decode()
        return render_template_string(VIEW_HTML, title=row[0], username=row[1], password=password)
    return "Not found"

@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM entries WHERE id = ?", (id,))
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)
