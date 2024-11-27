from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
import threading
import time
from dotenv import load_dotenv
import os

load_dotenv()

# Configurations from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS').split(',')))

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['weatherBot']
users = db['users']

# Flask for admin panel
app = Flask(__name__)

# Bot setup
bot = Bot(BOT_TOKEN)
app_bot = Application.builder().token(BOT_TOKEN).build()

# Command Handlers
async def start(update: Update, context: CallbackContext):
    """Welcome message and user registration with available commands list."""
    chat_id = update.effective_chat.id
    if not users.find_one({"telegramId": chat_id}):
        users.insert_one({"telegramId": chat_id, "isSubscribed": False})
        welcome_message = (
            "Welcome to the Weather Bot! Use /subscribe to receive hourly weather updates.\n\n"
            "Here are the available commands:\n"
            "/start - Start the bot and register\n"
            "/subscribe - Subscribe to hourly weather updates\n"
            "/unsubscribe - Unsubscribe from weather updates\n"
            "/weather [city_name] - Get the current weather for the specified city (e.g., /weather London)"
        )
        await update.message.reply_text(welcome_message)
    else:
        welcome_message = (
            "Welcome back! You can manage your weather updates using the commands below:\n\n"
            "Here are the available commands:\n"
            "/start - Start the bot and register\n"
            "/subscribe - Subscribe to hourly weather updates\n"
            "/unsubscribe - Unsubscribe from weather updates\n"
            "/weather [city_name] - Get the current weather for the specified city (e.g., /weather London)"
        )
        await update.message.reply_text(welcome_message)



async def subscribe(update: Update, context: CallbackContext):
    """Subscribe user to weather updates."""
    chat_id = update.effective_chat.id
    users.update_one({"telegramId": chat_id}, {"$set": {"isSubscribed": True}})
    await update.message.reply_text("You have subscribed to weather updates!")


async def unsubscribe(update: Update, context: CallbackContext):
    """Unsubscribe user from weather updates."""
    chat_id = update.effective_chat.id
    users.update_one({"telegramId": chat_id}, {"$set": {"isSubscribed": False}})
    await update.message.reply_text("You have unsubscribed from weather updates.")


async def weather(update: Update, context: CallbackContext):
    """Fetch current weather for a specific city or default to London."""
    city = "London"  # Default city

    # If the user has provided a city as an argument
    if context.args:
        city = " ".join(context.args)  # Join arguments to form the city name

    try:
        # Get weather data from OpenWeather API
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
        )
        weather_data = response.json()

        if weather_data.get("cod") != 200:  # Check if the response is valid
            await update.message.reply_text(f"Error: {weather_data.get('message')}")
            return

        # Extract weather information
        weather_desc = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp'] - 273.15  # Convert from Kelvin to Celsius
        humidity = weather_data['main']['humidity']

        # Send weather info to the user
        weather_message = (
            f"🌤️ Weather Update for {city}:\n"
            f"Description: {weather_desc.capitalize()}\n"
            f"Temperature: {temperature:.2f}°C\n"
            f"Humidity: {humidity}%"
        )
        await update.message.reply_text(weather_message)

    except Exception as e:
        await update.message.reply_text(f"Failed to get weather data: {e}")


# Admin Panel (Flask API)
@app.route('/update-weather-api-key', methods=['POST'])
def update_weather_api_key():
    """Admin API to update the weather API key."""
    data = request.json
    admin_id = data.get('adminId')
    if admin_id in ADMIN_IDS:
        global WEATHER_API_KEY
        WEATHER_API_KEY = data['newApiKey']
        return jsonify({"success": True, "message": "API key updated successfully!"})
    return jsonify({"success": False, "message": "Unauthorized access!"}), 403


@app.route('/manage-user', methods=['POST'])
def manage_user():
    """Admin API to block or delete users."""
    data = request.json
    admin_id = data.get('adminId')
    if admin_id in ADMIN_IDS:
        action = data.get('action')
        telegram_id = data.get('telegramId')

        if action == 'block':
            users.update_one({"telegramId": telegram_id}, {"$set": {"isSubscribed": False}})
            return jsonify({"success": True, "message": f"User {telegram_id} blocked."})

        elif action == 'delete':
            users.delete_one({"telegramId": telegram_id})
            return jsonify({"success": True, "message": f"User {telegram_id} deleted."})

        return jsonify({"success": False, "message": "Invalid action!"})
    return jsonify({"success": False, "message": "Unauthorized access!"}), 403


@app.route('/get-all-users', methods=['GET'])
def get_all_users():
    """Fetch all users for the admin."""
    admin_id = request.args.get('adminId')  # Get the adminId from the query string
    print(f"Received adminId: {admin_id}")  # Debugging log to check the received adminId
    
    if admin_id and int(admin_id) in ADMIN_IDS:
        all_users = users.find({}, {"_id": 0})  # Fetch users from the database
        user_list = [user for user in all_users]
        return jsonify({"success": True, "users": user_list})  # Return user data
    else:
        return jsonify({"success": False, "message": "Unauthorized access!"}), 403  # Unauthorized access response



# Weather Update Function
async def send_weather_updates():
    """Send hourly weather updates to subscribed users."""
    while True:
        subscribers = users.find({"isSubscribed": True})
        for user in subscribers:
            try:
                response = requests.get(
                    f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={WEATHER_API_KEY}"
                )
                weather_data = response.json()
                weather_desc = weather_data['weather'][0]['description']
                temperature = weather_data['main']['temp'] - 273.15  # Convert from Kelvin to Celsius

                await bot.send_message(  # Await the message send
                    chat_id=user['telegramId'],
                    text=f"🌤️ Weather Update:\nDescription: {weather_desc}\nTemperature: {temperature:.2f}°C"
                )
            except Exception as e:
                print(f"Failed to send weather update to {user['telegramId']}: {e}")
        time.sleep(3600)  # Wait for 1 hour


# Register Handlers
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("subscribe", subscribe))
app_bot.add_handler(CommandHandler("unsubscribe", unsubscribe))
app_bot.add_handler(CommandHandler("weather", weather))  # New command for instant weather

# Start Weather Updates Thread
weather_thread = threading.Thread(target=send_weather_updates, daemon=True)
weather_thread.start()

# Start Flask Admin Panel and Telegram Bot
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(port=3000), daemon=True).start()  # Run Flask in a separate thread
    app_bot.run_polling()  # Start the bot polling
