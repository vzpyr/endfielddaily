#!/usr/bin/env python3
import json, hashlib, hmac, time, sys, os, urllib.parse
from curl_cffi import requests
from dotenv import load_dotenv
import schedule

os.environ['TZ'] = 'UTC'
time.tzset()

load_dotenv()

ACCOUNT_TOKEN = urllib.parse.unquote(os.getenv("ACCOUNT_TOKEN", "").strip().strip('"\''))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not ACCOUNT_TOKEN:
    print("Error: No ACCOUNT_TOKEN set in .env")
    sys.exit(1)

CONSTANTS = {
    "APP_CODE": "6eb76d4e13aa36e6",
    "PLATFORM": "3",
    "VNAME": "1.0.0",
    "ENDFIELD_GAME_ID": "3",
    "URLS": {
        "GRANT": "https://as.gryphline.com/user/oauth2/v2/grant",
        "GENERATE_CRED": "https://zonai.skport.com/web/v1/user/auth/generate_cred_by_code",
        "REFRESH_TOKEN": "https://zonai.skport.com/web/v1/auth/refresh",
        "BINDING": "https://zonai.skport.com/api/v1/game/player/binding",
        "ATTENDANCE": "https://zonai.skport.com/web/v1/game/endfield/attendance"
    }
}

def send(url, method="get", headers=None, data=None):
    kwargs = {"headers": headers or {}, "impersonate": "firefox"}
    if data:
        kwargs["json"] = data
    resp = getattr(requests, method.lower())(url, **kwargs)
    return resp.json()

def telegram_msg(text):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"Telegram send failed: {e}")

def compute_sign(path, timestamp, sign_token):
    headers_json = json.dumps({
        "platform": CONSTANTS["PLATFORM"],
        "timestamp": timestamp,
        "dId": "",
        "vName": CONSTANTS["VNAME"]
    }, separators=(",", ":"))
    return hashlib.md5(
        hmac.new(
            sign_token.encode(),
            (path + "" + timestamp + headers_json).encode(),
            hashlib.sha256
        ).hexdigest().encode()
    ).hexdigest()

def main():
    try:
        grant_resp = send(
            CONSTANTS["URLS"]["GRANT"],
            "post",
            data={"token": ACCOUNT_TOKEN, "appCode": CONSTANTS["APP_CODE"], "type": 0}
        )

        if grant_resp.get("status") != 0:
            error_msg = f"Grant failed: {grant_resp.get('msg', 'Unknown error')}"
            telegram_msg(f"<b>Endfield Check-in</b>\n{error_msg}")
            print(error_msg)
            return

        cred = grant_resp["data"]["code"]
        cred = send(
            CONSTANTS["URLS"]["GENERATE_CRED"],
            "post",
            data={"kind": 1, "code": cred}
        )["data"]["cred"]

        ts = str(int(time.time()))
        refresh_resp = send(
            CONSTANTS["URLS"]["REFRESH_TOKEN"],
            "get",
            headers={
                "cred": cred,
                "platform": CONSTANTS["PLATFORM"],
                "vName": CONSTANTS["VNAME"],
                "timestamp": ts,
                "sk-language": "en",
                "Referer": "https://game.skport.com/",
                "Origin": "https://game.skport.com"
            }
        )

        if refresh_resp.get("code") == 10003 and "timestamp" in refresh_resp:
            ts = refresh_resp["timestamp"]
            refresh_resp = send(
                CONSTANTS["URLS"]["REFRESH_TOKEN"],
                "get",
                headers={
                    "cred": cred,
                    "platform": CONSTANTS["PLATFORM"],
                    "vName": CONSTANTS["VNAME"],
                    "timestamp": ts,
                    "sk-language": "en",
                    "Referer": "https://game.skport.com/",
                    "Origin": "https://game.skport.com"
                }
            )

        token = refresh_resp["data"]["token"]
        server_ts = refresh_resp.get("timestamp", ts)

        sign = compute_sign("/api/v1/game/player/binding", server_ts, token)
        binding = send(
            CONSTANTS["URLS"]["BINDING"],
            "get",
            headers={
                "cred": cred,
                "platform": CONSTANTS["PLATFORM"],
                "vName": CONSTANTS["VNAME"],
                "timestamp": server_ts,
                "sk-language": "en",
                "sign": sign,
                "Referer": "https://game.skport.com/",
                "Origin": "https://game.skport.com"
            }
        )

        if binding.get("code") == 10003 and "timestamp" in binding:
            server_ts = binding["timestamp"]
            sign = compute_sign("/api/v1/game/player/binding", server_ts, token)
            binding = send(
                CONSTANTS["URLS"]["BINDING"],
                "get",
                headers={
                    "cred": cred,
                    "platform": CONSTANTS["PLATFORM"],
                    "vName": CONSTANTS["VNAME"],
                    "timestamp": server_ts,
                    "sk-language": "en",
                    "sign": sign,
                    "Referer": "https://game.skport.com/",
                    "Origin": "https://game.skport.com"
                }
            )

        game_role = None
        for app in binding["data"]["list"]:
            if app["appCode"] == "endfield" and app["bindingList"]:
                role = app["bindingList"][0].get("defaultRole") or app["bindingList"][0]["roles"][0]
                if role:
                    game_role = f"{CONSTANTS['ENDFIELD_GAME_ID']}_{role['roleId']}_{role['serverId']}"

        sign = compute_sign("/web/v1/game/endfield/attendance", server_ts, token)
        headers = {
            "cred": cred,
            "platform": CONSTANTS["PLATFORM"],
            "vName": CONSTANTS["VNAME"],
            "timestamp": server_ts,
            "sk-language": "en",
            "sign": sign,
            "Content-Type": "application/json",
            "Referer": "https://game.skport.com/",
            "Origin": "https://game.skport.com"
        }
        if game_role:
            headers["sk-game-role"] = game_role

        response = send(CONSTANTS["URLS"]["ATTENDANCE"], "post", headers=headers)

        code, msg = response.get("code"), response.get("message", "")

        if code == 0:
            status = "Signed in successfully."
        elif code in [1001, 10001] or "already" in msg.lower():
            status = "Already signed in today."
        elif code == 10002:
            status = "Token expired."
        else:
            status = f"Error: {msg}"

        print(status)
        telegram_msg(f"<b>Endfield Check-in</b>\n{status}")

    except Exception as e:
        error_msg = f"Script error: {type(e).__name__}: {e}"
        print(error_msg)
        telegram_msg(f"<b>Endfield Check-in Error</b>\n{error_msg}")

if __name__ == "__main__":
    print("Running initial check-in.")
    main()
    print("Scheduling daily run at 16:01 UTC.")
    schedule.every().day.at("16:01").do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
