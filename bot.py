import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import os

# --- 1. FLASK SERVER (For Render Keep-Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run():
    # Render port 10000 ya 8080 use karta hai
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. TELEGRAM BOT CONFIG ---
TOKEN = '8609271216:AAFxlYeajhAcpTGRF4gVozGMso22NI0vh78'
bot = telebot.TeleBot(TOKEN, threaded=False) # Render free tier ke liye threaded=False behtar hai

# --- 3. VEHICLE SCRAPER LOGIC ---
def get_vehicle_details(rc_number):
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        
        def get_value(label):
            try:
                div = soup.find("span", string=label).find_parent("div")
                return div.find("p").get_text(strip=True)
            except:
                return "N/A"

        owner = get_value("Owner Name")
        if owner == "N/A":
            return "❌ No details found. Check RC number."

        return (
            f"🚗 *Vehicle Details*\n"
            f"👤 Owner: `{owner}`\n"
            f"🔢 RC: `{rc}`\n"
            f"⚙️ Model: {get_value('Model Name')}\n"
            f"📅 Insurance: {get_value('Insurance Expiry')}"
        )
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- 4. BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send me a Vehicle Number!")

@bot.message_handler(func=lambda m: True)
def handle_rc(message):
    res = get_vehicle_details(message.text)
    bot.reply_to(message, res, parse_mode="Markdown")

# --- 5. MAIN EXECUTION ---
if __name__ == '__main__':
    keep_alive()  # Flask server start karega
    print("🚀 Bot is starting on Render...")
    bot.infinity_polling()
