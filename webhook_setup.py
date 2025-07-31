import os
import requests

async def set_webhook():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    base_url = os.getenv("WEBHOOK_BASE_URL")
    url = f"https://api.telegram.org/bot{token}/setWebhook"
    webhook_url = f"{base_url}/webhook"
    requests.get(url, params={"url": webhook_url})