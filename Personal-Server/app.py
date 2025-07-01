from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, random, requests
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(days=7)

UPLOAD_FOLDER = '/media/aditya/ADITYA'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERS = {
    'User1': generate_password_hash('test123'),
    'User2': generate_password_hash('test123'),
    'User3': generate_password_hash('test123'),
    'User4': generate_password_hash('test123')
}

for user in USERS:
    os.makedirs(os.path.join(UPLOAD_FOLDER, user), exist_ok=True)

@app.before_request
def reset_session_on_restart():
    if not request.endpoint or request.endpoint == 'static':
        return
    if 'username' not in session and request.endpoint not in ('webserver_login', 'webserver_static'):
        session.clear()

# Send Telegram Notification when server starts
def send_telegram_notification():
    bot_token = ''  # Replace with real token
    chat_id = '1'   # Replace with real chat ID
    message = '🚀 Flask Server is now ONLINE at https://adityax04.online/webserver'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Failed to send Telegram alert:", e)

send_telegram_notification()

@app.route('/webserver/login', methods=['GET', 'POST'])
def webserver_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and check_password_hash(USERS[username], password):
            session['username'] = username
            session['logged_in'] = True
            return redirect(url_for('webserver_index'))
        else:
            error = 'Invalid username or password'

    return render_template_string('''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Login | X04-CLOUDS</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 min-h-screen flex items-center justify-center px-4">
  <div class="bg-gray-800 text-white p-8 rounded-xl shadow-xl w-full max-w-sm">
    <h2 class="text-3xl font-bold mb-6 text-center">
      <span class="text-yellow-400">🔒</span> Login
    </h2>
    {% if error %}
      <div class="bg-red-600 p-2 rounded text-sm mb-4 text-center">{{ error }}</div>
    {% endif %}
    <form method="POST">
      <input type="text" name="username" placeholder="Username" required
             class="w-full p-3 mb-4 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500">
      <input type="password" name="password" placeholder="Password" required
             class="w-full p-3 mb-6 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500">
      <button type="submit"
              class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg transition">
        Login
      </button>
    </form>
  </div>
</body>
</html>''', error=error)

@app.route('/')
def webserver_index():
    if not session.get('logged_in'):
        return redirect(url_for('webserver_login'))

    current_user = session['username']
    is_admin = current_user == 'Aditya'
    folders = USERS.keys() if is_admin else [current_user]
    files_by_user = {}

    for user in folders:
        user_folder = os.path.join(UPLOAD_FOLDER, user)
        if os.path.exists(user_folder):
            files = []
            for filename in os.listdir(user_folder):
                filepath = os.path.join(user_folder, filename)
                size = round(os.path.getsize(filepath) / 1024, 2)
                files.append({'name': filename, 'size': size})
            files_by_user[user] = files

    return render_template_string('''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>X04-CLOUDS</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
  <script>
    tailwind.config = { darkMode: 'class' };
    window.onload = () => document.documentElement.classList.add('dark');
  </script>
</head>
<body class="bg-gray-900 text-white min-h-screen">
  <div class="flex justify-between items-center bg-gray-800 p-4 shadow">
    <h1 class="text-xl font-bold text-indigo-400">☁️ X04-CLOUDS</h1>
    <a href="/webserver/logout" class="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg">Logout</a>
  </div>
  <div class="p-4">
    {% for user, files in files_by_user.items() %}
    <div class="mb-4">
      <button onclick="toggleFolder('{{ user }}')" class="text-lg font-semibold w-full text-left text-white bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded">
        📁 {{ user }}'s Files
      </button>
      <div id="folder-{{ user }}" class="mt-2 space-y-4 hidden">
        {% for file in files %}
        <div class="bg-gray-800 rounded-lg shadow p-4 flex justify-between items-start gap-4">
          <div class="flex-1 min-w-0">
            <p class="font-medium text-indigo-300 truncate">{{ file.name }}</p>
            <p class="text-sm text-gray-400">{{ file.size }} KB</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <a href="/webserver/files/{{ user }}/{{ file.name }}" target="_blank" class="text-sm bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded">View</a>
              <a href="/webserver/files/{{ user }}/{{ file.name }}" download class="text-sm bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded">Download</a>
              <form method="POST" action="/webserver/delete/{{ user }}/{{ file.name }}" onsubmit="return confirmDelete(this);">
                <button type="submit" class="text-sm bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded">Delete</button>
              </form>
            </div>
          </div>
          <div class="w-20 h-20 flex-shrink-0">
            {% if file.name.endswith(('.jpg', '.jpeg', '.png')) %}
              <img src="/webserver/files/{{ user }}/{{ file.name }}" class="w-full h-full rounded-lg object-cover" loading="lazy">
            {% elif file.name.endswith(('.mp4', '.webm')) %}
              <video controls class="w-full h-full rounded-lg object-cover">
                <source src="/webserver/files/{{ user }}/{{ file.name }}">
              </video>
            {% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
    {% endfor %}
  </div>
  <button onclick="toggleUploadModal()" class="fixed bottom-6 right-6 bg-indigo-600 hover:bg-indigo-700 text-white text-3xl rounded-full w-16 h-16 shadow-lg z-50">+</button>
  <div id="uploadModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm hidden z-50 flex items-center justify-center">
    <div class="bg-gray-800 p-6 rounded-xl shadow-xl w-80">
      <h2 class="text-xl font-semibold mb-4 text-indigo-400">Upload Files</h2>
      <form id="uploadForm" enctype="multipart/form-data">
        <input type="file" name="file" multiple required class="mb-4 w-full text-sm text-white bg-gray-700 border border-gray-600 rounded">
        <div class="flex justify-end gap-2">
          <button type="button" onclick="toggleUploadModal()" class="px-4 py-2 rounded bg-gray-600 hover:bg-gray-700 text-white">Cancel</button>
          <button type="submit" class="px-4 py-2 rounded bg-green-600 hover:bg-green-700 text-white">Upload</button>
        </div>
        <progress id="progressBar" value="0" max="100" class="w-full mt-4 hidden"></progress>
      </form>
    </div>
  </div>
  <script>
    function toggleUploadModal() {
      document.getElementById('uploadModal').classList.toggle('hidden');
    }
    function toggleFolder(user) {
      const el = document.getElementById('folder-' + user);
      el.classList.toggle('hidden');
    }
    const uploadForm = document.getElementById('uploadForm');
    const progressBar = document.getElementById('progressBar');
    uploadForm?.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(uploadForm);
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/webserver/upload', true);
      progressBar.classList.remove('hidden');
      xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
          progressBar.value = (e.loaded / e.total) * 100;
        }
      });
      xhr.onload = function() {
        if (xhr.status == 200) {
          window.location.href = "/";
        } else {
          Swal.fire({ icon: 'error', title: 'Upload Failed', text: 'Something went wrong.' });
        }
      };
      xhr.send(formData);
    });
    function confirmDelete(form) {
      event.preventDefault();
      Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to recover this file!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
      }).then((result) => {
        if (result.isConfirmed) {
          form.submit();
        }
      });
      return false;
    }
  </script>
</body>
</html>''', files_by_user=files_by_user)

@app.route('/webserver/upload', methods=['POST'])
def upload():
    if not session.get('logged_in'):
        return redirect(url_for('webserver_login'))
    user = session['username']
    files = request.files.getlist('file')
    folder_path = os.path.join(UPLOAD_FOLDER, user)
    os.makedirs(folder_path, exist_ok=True)
    for f in files:
        if f:
            ext = os.path.splitext(f.filename)[1]
            rand = str(random.randint(1000, 9999))
            filename = secure_filename(f"{user}_{rand}{ext}")
            f.save(os.path.join(folder_path, filename))
    return '', 200

@app.route('/webserver/files/<user>/<filename>')
def serve_file(user, filename):
    if not session.get('logged_in'):
        return redirect(url_for('webserver_login'))
    current_user = session['username']
    if current_user != 'Aditya' and user != current_user:
        return "Unauthorized", 403
    return send_from_directory(os.path.join(UPLOAD_FOLDER, user), filename)

@app.route('/webserver/delete/<user>/<filename>', methods=['POST'])
def delete_file(user, filename):
    if not session.get('logged_in'):
        return redirect(url_for('webserver_login'))
    current_user = session['username']
    if current_user != 'Aditya' and user != current_user:
        return "Unauthorized", 403
    filepath = os.path.join(UPLOAD_FOLDER, user, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('webserver_index'))

@app.route('/webserver/logout')
def webserver_logout():
    session.clear()
    return redirect(url_for('webserver_login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
