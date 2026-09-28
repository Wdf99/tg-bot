import requests
import time

# ==================== 設定區 ====================
TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
CHAT_ID = "-1004343189687"
API_URL = "https://pc28.help/api/kj.json?nbr=120"
# ================================================

def fetch_data():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API 請求失敗，狀態碼: {response.status_code}")
            return None
    except Exception as e:
        print(f"獲取數據時發生錯誤: {e}")
        return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        print(f"Telegram API 回應: {res_data}")
        if not res_data.get("ok"):
            print(f"發送失敗原因: {res_data.get('description')}")
    except Exception as e:
        print(f"發送 Telegram 訊息時發生錯誤: {e}")

def main():
    data = fetch_data()
    if not data:
        print("未獲取到有效開獎數據。")
        return

    # 取得最新開獎資訊
    latest = data[0] if isinstance(data, list) and len(data) > 0 else None
    if not latest:
        print("開獎數據格式不符。")
        return

    issue = latest.get("issue", "未知期數")
    result_nums = latest.get("result", "未知結果")

    # 組合要發送的訊息內容
    msg = (
        f"<b>📊 PC28 最新開獎與預測通知</b>\n\n"
        f"期數：<code>{issue}</code>\n"
        f"開獎號碼：<code>{result_nums}</code>\n\n"
        f"🤖 機器人持續追蹤中..."
    )

    send_telegram_message(msg)

if __name__ == "__main__":
    main()
 
