# 🧠 Raspberry Pi AI Dashboard

A sleek, responsive, real-time AI dashboard built with **Flask** and **TailwindCSS** for Raspberry Pi or any Linux/Windows server. It monitors system performance, logs uptime, displays weather updates, and checks service status — all in a beautiful browser-based UI.

---

## 🌟 Features

- 📡 **Service Monitoring** – Checks if specified services are online (ping-based)
- 💻 **CPU & RAM Usage** – Real-time usage stats via `psutil`
- 🌡️ **System Temperature** – Displays CPU temp (Linux-only)
- 🌤️ **Live Weather Data** – Powered by OpenWeatherMap API
- 📜 **Uptime History** – Logs last 100 entries, displays last 5
- 🔔 **System Notifications** – Warns when services are down (Linux only)
- 📱 **Mobile-Responsive UI** – TailwindCSS-based layout

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/raspberry-pi-ai-dashboard.git
cd raspberry-pi-ai-dashboard

#Install Python Dependencies
pip install flask psutil requests
