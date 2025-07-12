# Thingyanahlann Telegram Bot

This Telegram Bot is designed to help users easily search for and play Thingyan (Myanmar New Year Water Festival) songs. It fetches song data from a remote JSON file, allows searching by song title, artist, or album, and provides inline buttons to play the audio directly in Telegram.

## ✨ Features

* **Song Search**: Search for Thingyan songs by title, artist, or album.

* **Inline Playback**: Play songs directly within Telegram using inline buttons.

* **Channel Membership Check**: Ensures users are members of a specified Telegram channel before allowing bot usage.

* **Dynamic Data Loading**: Fetches song data from a remote JSON URL, allowing for easy updates without redeploying the bot code.

## 🚀 Getting Started

Follow these steps to set up and run the Thingyan Telegram Bot.

### Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.10+**: Download and install Python from [python.org](https://www.python.org/downloads/).

* **Telegram Bot Token**: Obtain a Bot Token from BotFather on Telegram.

* **Required Channel Information**: You'll need the Channel ID, invite link, and username for the membership check feature.

### Installation

1. **Clone the Repository**:

   ```
   git clone [https://github.com/ULayGyiDev/thingyanahlann.git](https://github.com/ULayGyiDev/thingyanahlann.git)
   cd thingyanahlann
   
   ```

2. **Create and Activate a Virtual Environment (Recommended)**:

   ```
   python3 -m venv venv
   source venv/bin/activate
   
   ```

   (On Windows, use `.\venv\Scripts\activate` instead of `source venv/bin/activate`)

3. **Install Dependencies**:

   ```
   pip install -r requirements.txt
   
   ```

### Configuration

1. **Set your Telegram Bot Token**:
   The bot requires your Telegram Bot Token to be set as an environment variable named `TELEGRAM_BOT_TOKEN`.

   **Linux/macOS:**

   ```
   export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
   
   ```

   **Windows (Command Prompt):**

   ```
   set TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
   
   ```

   (Replace `YOUR_BOT_TOKEN_HERE` with your actual token from BotFather.)

2. **Update Channel Information (if necessary)**:
   Open `thingyan-bot.py` and update the following constants with your desired channel details:

   ```
   REQUIRED_CHANNEL_ID = -1002664997277 # Replace with your channel's actual ID
   REQUIRED_CHANNEL_INVITE_LINK = "[https://t.me/thingyanahlann](https://t.me/thingyanahlann)" # Replace with your channel's invite link
   REQUIRED_CHANNEL_USERNAME = "@thingyanahlann" # Replace with your channel's username
   
   ```

### Running the Bot

#### Running Locally (for development/testing)

After completing the installation and configuration steps:

```
python thingyan-bot.py

```

The bot will start polling for updates. You can interact with it via Telegram.

#### Deploying on AWS EC2 (Ubuntu Server)

For production deployment, it's recommended to run the bot as a `systemd` service to ensure it runs continuously and restarts automatically on server reboots.

1. **SSH into your EC2 Instance**:
   (Ensure you have Python 3, pip, and `python3-venv` installed on your EC2 instance as per the prerequisites.)

2. **Clone the repository and set up the virtual environment** (similar to local setup steps).

3. **Create a `systemd` service file**:

   ```
   sudo nano /etc/systemd/system/thingyan_bot.service
   
   ```

   Paste the following content, replacing `YOUR_BOT_TOKEN_HERE` with your actual token:

   ```
   [Unit]
   Description=Thingyan Telegram Bot
   After=network.target
   
   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/telegram_thingyan_bot/thingyanahlann
   Environment="TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE"
   ExecStart=/home/ubuntu/telegram_thingyan_bot/venv/bin/python /home/ubuntu/telegram_thingyan_bot/thingyanahlann/thingyan-bot.py
   Restart=on-failure
   RestartSec=10
   StandardOutput=journal
   StandardError=journal
   SyslogIdentifier=thingyan_bot
   
   [Install]
   WantedBy=multi-user.target
   
   ```

   Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

4. **Reload `systemd` and start the service**:

   ```
   sudo systemctl daemon-reload
   sudo systemctl start thingyan_bot
   sudo systemctl enable thingyan_bot # Enable auto-start on reboot
   
   ```

5. **Check the service status**:

   ```
   sudo systemctl status thingyan_bot
   
   ```

   You should see `Active: active (running)`.

## 🤖 Bot Usage

Once the bot is running, you can interact with it on Telegram:

* `/start`: Start the bot and get a welcome message with search options.

* `/help`: Get instructions on how to use the bot and its commands.

* **Search by Category (using inline buttons)**:

  * Click "သီချင်း (Song)" to search by song title.

  * Click "အဆိုတော် (Artist)" to search by artist name.

  * Click "album (Album)" to search by album name.

  * After selecting a category, type your search query (e.g., `သီချင်း မိုး`, `အဆိုတော် ရဲလေး`).

* **Direct Search**: You can also directly type your query without a prefix, and the bot will search across all fields (title, artist, album).

  * Example: `မိုး` (will search for "မိုး" in title, artist, or album).

* **Refresh Songs Data**: Click "🔄 Refresh Songs Data" button to reload song information from the JSON URL.

## 🤝 Contributing

Contributions are welcome! If you have suggestions, bug reports, or want to contribute code, please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.
