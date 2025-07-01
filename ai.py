from flask import Flask, render_template_string
import subprocess, platform, datetime, requests, os, json, psutil

app = Flask(__name__)

# --- CONFIGURATION ---
SERVICES = {
    "Homepage": "adityax04.online",
    "Web Server": "web.adityax04.online",
    "Vault": "vault.adityax04.online"
}

WEATHER_API_KEY = "paste your api key"
LOCATIONS = {
    "Place Name": "Area Pin Code",
    "Place Name": "Area Pin Code"
}
LOG_FILE = "uptime_log.json"

# --- HTML TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <title>Raspberry Pi AI Dashboard</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <script src=\"https://cdn.tailwindcss.com\"></script>
</head>
<body class=\"bg-gray-900 text-white font-sans min-h-screen\">
    <div class=\"max-w-5xl mx-auto p-6\">
        <h1 class=\"text-4xl font-bold text-center mb-6\">🧠 Raspberry Pi AI Dashboard</h1>

        <!-- System Stats -->
        <div class=\"grid md:grid-cols-3 gap-4 mb-6\">
            <div class=\"bg-gray-800 p-4 rounded shadow\">
                <h2 class=\"text-xl font-semibold\">💻 CPU Usage</h2>
                <p class=\"text-lg\">{{ system.cpu }}%</p>
            </div>
            <div class=\"bg-gray-800 p-4 rounded shadow\">
                <h2 class=\"text-xl font-semibold\">🧠 RAM Usage</h2>
                <p class=\"text-lg\">{{ system.ram }}%</p>
            </div>
            <div class=\"bg-gray-800 p-4 rounded shadow\">
                <h2 class=\"text-xl font-semibold\">🌡️ Temperature</h2>
                <p class=\"text-lg\">{{ system.temp if system.temp else 'N/A' }}°C</p>
            </div>
        </div>

        <!-- Service Status -->
        <div class=\"grid md:grid-cols-3 gap-4 mb-6\">
            {% for name, status in statuses.items() %}
            <div class=\"bg-gray-800 p-4 rounded shadow border {{ 'border-green-500' if status == 'Online' else 'border-red-500' }}\">
                <h2 class=\"text-xl font-semibold\">{{ name }}</h2>
                <p class=\"{{ 'text-green-400' if status == 'Online' else 'text-red-400' }}\">Status: {{ status }}</p>
            </div>
            {% endfor %}
        </div>

        <!-- Local Time -->
        <div class=\"bg-gray-800 p-4 rounded shadow mb-6\">
            <h2 class=\"text-xl font-semibold\">🕒 Local Time</h2>
            <p class=\"text-lg mt-2\">{{ time }}</p>
        </div>

        <!-- Weather -->
        <div class=\"grid md:grid-cols-2 gap-4 mb-6\">
            {% for location, info in weather.items() %}
            <div class=\"bg-blue-800 p-4 rounded shadow\">
                <h2 class=\"text-xl font-semibold\">🌤️ Weather - {{ location }}</h2>
                <p>{{ info }}</p>
            </div>
            {% endfor %}
        </div>

        <!-- Logs -->
        <div class=\"bg-gray-800 p-4 rounded shadow mb-6\">
            <h2 class=\"text-xl font-semibold\">📜 Uptime Logs (Last 5)</h2>
            <ul class=\"text-sm list-disc list-inside mt-2\">
                {% for log in logs %}
                <li>{{ log.timestamp }} | CPU: {{ log.cpu }}% | RAM: {{ log.ram }}% | Temp: {{ log.temp if log.temp else 'N/A' }}°C</li>
                {% endfor %}
            </ul>
        </div>

        <!-- Notification -->
        {% if notification %}
        <div class=\"bg-yellow-500 text-black text-center p-3 rounded shadow mb-6 font-semibold\">
            🔔 {{ notification }}
        </div>
        {% endif %}

        <footer class=\"text-gray-400 text-sm text-center mt-10\">
            &copy; {{ year }} adityax04 — Powered by Flask & TailwindCSS on Raspberry Pi 🐧
        </footer>
    </div>
</body>
</html>
"""

# --- HELPER FUNCTIONS ---
def ping_host(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    try:
        subprocess.check_output(command, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def check_services():
    return {name: "Online" if ping_host(host) else "Offline" for name, host in SERVICES.items()}

def get_weather(zipcode):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?zip={zipcode},IN&units=metric&appid={WEATHER_API_KEY}"
        res = requests.get(url, timeout=5).json()
        return f"{res['main']['temp']}°C, {res['weather'][0]['description'].capitalize()}"
    except:
        return "Weather unavailable"

def get_temp():
    try:
        if platform.system() == "Linux":
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return round(int(f.read()) / 1000, 1)
    except:
        return None

def get_system_stats():
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "temp": get_temp()
    }

def log_uptime(stats):
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    logs.append(stats)
    logs = logs[-100:]  # keep last 100
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
    return logs[-5:]

def send_notification(msg):
    if platform.system() == "Linux":
        os.system(f'notify-send "AI Dashboard" "{msg}"')
    else:
        print(f"[NOTIFY] {msg}")

# --- ROUTE ---
@app.route("/")
def dashboard():
    statuses = check_services()
    now = datetime.datetime.now().strftime("%A, %d %B %Y %I:%M %p")
    weather = {name: get_weather(zipcode) for name, zipcode in LOCATIONS.items()}
    stats = get_system_stats()
    logs = log_uptime(stats)

    offline = [name for name, stat in statuses.items() if stat == "Offline"]
    notification = None
    if offline:
        notification = f"⚠️ {', '.join(offline)} is offline!"
        send_notification(notification)

    return render_template_string(HTML_TEMPLATE,
        statuses=statuses,
        time=now,
        weather=weather,
        system=stats,
        logs=logs,
        year=datetime.datetime.now().year,
        notification=notification
    )

# --- RUN ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
