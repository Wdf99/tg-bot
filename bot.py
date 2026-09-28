import requests

TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
API_URL = "https://pc28.help/api/kj.json?nbr=120"

CHAT_IDS_TO_TEST = [
    "-5478933926",
    "-1004343189687"
]

def send_test(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"🤖 測試發送至 ID: {chat_id}"
    }
    res = requests.post(url, json=payload, timeout=10).json()
    print(f"測試 {chat_id} 結果: {res}")
    if not res.get("ok"):
        raise Exception(f"Telegram API 拒絕發送至 {chat_id}: {res}")

def main():
    print("=== 開始測試發送 ===")
    for cid in CHAT_IDS_TO_TEST:
        send_test(cid)

if __name__ == "__main__":
    main()
