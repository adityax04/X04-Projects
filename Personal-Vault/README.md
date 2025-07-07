🔐 Jarvis Vault – Secure Vault Web App
Jarvis Vault is a sleek and secure web application designed to safely store and manage credentials. It includes a modern UI powered by TailwindCSS and implements essential features like encryption and Two-Factor Authentication (2FA) for admin access.

🚀 Features
🔑 Secure login with password + OTP (TOTP via Google Authenticator)

🔐 AES-encrypted vault entries (using cryptography.fernet)

📱 QR code setup for OTP using pyotp and qrcode

🧾 Add, view, and delete entries via a clean dashboard

🌈 Fully responsive UI built with TailwindCSS

📦 SQLite-based lightweight storage

📸 UI Preview
Modern UI Screens using Tailwind CSS:

Login page

OTP verification with QR

Dashboard with list of entries

Add new entry form

Detailed view page for entries

🛠️ Tech Stack
Backend: Flask

Frontend: Tailwind CSS

Auth: pyotp, TOTP 2FA

Encryption: Fernet symmetric encryption

Database: SQLite

QR Generation: qrcode + base64

🧑‍💻 Getting Started
Clone the Repository
git clone https://github.com/yourusername/jarvis-vault.git
cd jarvis-vault

Install Dependencies
pip install flask cryptography pyotp qrcode pillow

Run the App
python vault.py
Access the App
Open your browser and go to: http://localhost:5001

🔐 Default Admin Password
admin123
After entering the password, scan the QR code with Google Authenticator to complete 2FA setup.

📂 File Structure

├── vault.py
├── vault.db
├── fernet.key
├── totp_secret.key
└── static/

🧠 Author
Made with ❤️ by [AdityaX04]