# Weather Telegram Bot with Admin Panel

This project is a Telegram bot that provides weather updates to users. It includes an admin panel built with Flask for managing users and updating the weather API key. The bot fetches weather data from the OpenWeather API and allows users to subscribe for hourly updates.

## Features

- **User Commands**:
  - `/start`: Welcome message and user registration.
  - `/subscribe`: Subscribe to receive hourly weather updates.
  - `/unsubscribe`: Unsubscribe from weather updates.
  - `/weather [city]`: Get the current weather for a specified city (default is London).

- **Admin Panel** (Accessible via Flask API):
  - **Update Weather API Key**: Endpoint to update the weather API key (`/update-weather-api-key`).
  - **Manage Users**:
    - Block users (unsubscribe them from updates).
    - Delete users.
  - **Get All Users**: List all users with their subscription status.

## Technologies Used

- **Telegram Bot API**: Used for interacting with users.
- **Flask**: Used for the admin panel (API).
- **MongoDB**: Used to store user data and subscription status.
- **OpenWeather API**: Provides weather data.
- **Python**: The programming language used for development.

## Setup

### Prerequisites

1. **Telegram Bot Token**: Create a bot on Telegram by chatting with [BotFather](https://core.telegram.org/bots#botfather). Get the bot token.
2. **OpenWeather API Key**: Sign up at [OpenWeather](https://openweathermap.org/api) to get an API key for weather data.
3. **MongoDB**: Set up a MongoDB instance (local or hosted) to store user data.

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/weather-bot.git
    cd weather-bot
    ```

2. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the project root directory with the following contents:
    ```env
    BOT_TOKEN=your_telegram_bot_token
    WEATHER_API_KEY=your_openweather_api_key
    ADMIN_IDS=your_telegram_user_id
    MONGO_URI=mongodb://localhost:27017/
    ```

4. Replace the placeholders with your actual values:
    - `your_telegram_bot_token`: The bot token you received from BotFather.
    - `your_openweather_api_key`: The API key from OpenWeather.
    - `your_telegram_user_id`: Your Telegram user ID (for admin privileges).
    - `mongodb://localhost:27017/`: The connection URI for your MongoDB instance.

### Running the Bot

1. Start the bot by running the Python script:
    ```bash
    python main.py
    ```

2. The bot will run and listen for commands on Telegram. The Flask admin panel will be available at `http://127.0.0.1:3000`.

### Admin Panel Endpoints

The following endpoints are available to the bot's administrator:

- **POST `/update-weather-api-key`**: Update the weather API key.
  - Body:
    ```json
    {
      "adminId": "your_telegram_user_id",
      "newApiKey": "new_openweather_api_key"
    }
    ```

- **POST `/manage-user`**: Block or delete a user.
  - Body:
    ```json
    {
      "adminId": "your_telegram_user_id",
      "action": "block" or "delete",
      "telegramId": "target_telegram_user_id"
    }
    ```

- **GET `/get-all-users`**: Get a list of all users.
  - Query parameters: `adminId=your_telegram_user_id`

### Example cURL Commands for Admin Panel

- **Update Weather API Key**:
    ```bash
    curl -X POST http://127.0.0.1:3000/update-weather-api-key \
    -H "Content-Type: application/json" \
    -d '{"adminId": "your_telegram_user_id", "newApiKey": "new_openweather_api_key"}'
    ```

- **Manage User** (Block or Delete):
    ```bash
    curl -X POST http://127.0.0.1:3000/manage-user \
    -H "Content-Type: application/json" \
    -d '{"adminId": "your_telegram_user_id", "action": "block", "telegramId": "user_telegram_id"}'
    ```

- **Get All Users**:
    ```bash
    curl "http://127.0.0.1:3000/get-all-users?adminId=your_telegram_user_id"
    ```

## Commands for Telegram Bot

- `/start`: Starts the bot and registers the user.
- `/subscribe`: Subscribes the user to receive hourly weather updates.
- `/unsubscribe`: Unsubscribes the user from weather updates.
- `/weather [city]`: Fetches the current weather for the specified city.

## Troubleshooting

- **Bot Not Responding**: Ensure the bot is running and your Telegram token is correct.
- **MongoDB Connection Issue**: Check your MongoDB URI and ensure MongoDB is running locally or remotely.
