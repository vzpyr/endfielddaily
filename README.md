# endfielddaily
Automated daily check-in for Arknights:Endfield

## Features
* Automates the daily attendance check-in on SKPORT (obviously)
* Runs continuously, with one initial check-in and regular check-ins daily at 16:01 (UTC)
* Supports notifications via a Telegram Bot
* Dockerized for easy deployment

## Prerequisites
You need to obtain your `ACCOUNT_TOKEN` to use this app.

### How to extract the token:
1. Go to the [Endfield Sign-in page](https://game.skport.com/endfield/sign-in) and log in.
2. Open your browser's Developer Tools (press `F12` or right-click and select **Inspect**).
3. Navigate to the cookie storage:
* **Chrome:** Go to the **Application** tab, expand **Cookies** in the left panel, and click on `https://game.skport.com`.
* **Firefox:** Go to the **Storage** tab, expand **Cookies** in the left panel, and click on `https://game.skport.com`.
4. Locate the cookie named `ACCOUNT_TOKEN` and copy it 1:1. This is the token you will use in your configuration.

## Configuration
Copy `.env.example` to `.env` in the root directory and fill it (or pass environment variables):
```
# required
ACCOUNT_TOKEN=
# optional
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## How to Use
### Method 1: Python
1. Install requirements:
```
pip install python-dotenv schedule curl_cffi
```
2. Run the script:
```
python endfielddaily.py
```

### Method 2: Docker
1. Build the Docker image:
```
docker build -t endfielddaily .
```
2. Run the container:
```
docker run -d --name endfielddaily --env-file .env --restart unless-stopped endfielddaily
```

### Method 3: Docker Compose
1. Edit the docker-compose.yml (optional)
2. Start the container:
```
docker compose up -d
```
