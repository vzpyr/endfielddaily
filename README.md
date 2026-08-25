# Endfield Daily

Automated daily check-in daemon for _Arknights: Endfield_ on SKPORT

## Features

- Automates daily attendance check-ins on SKPORT
- Runs continuously: initial check-in on startup, then daily at 16:01 UTC
- Supports optional Telegram bot notifications on success or failure
- Dockerized for easy deployment

## Configuration

### Extracting Token

1. Go to the [Endfield sign-in page](https://game.skport.com/endfield/sign-in) and log in
2. Open Developer Tools (`F12`) → **Application** (or **Storage**) → **Cookies** → `https://game.skport.com`
3. Copy the value of the `ACCOUNT_TOKEN` cookie

### Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```env
# Required
ACCOUNT_TOKEN=your_token_here

# Optional (Telegram Notifications)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## Deployment

### Docker (Recommended)

```bash
docker compose up -d
```

### From Source

Requires Python 3.10+ and pip:

```bash
pip install python-dotenv schedule curl_cffi
python endfielddaily.py
```

## License

MIT
