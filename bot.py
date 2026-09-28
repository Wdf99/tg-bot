import requests
import json

# ==================== 設定區 ====================
TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
API_URL = "https://pc28.help/api/kj.json?nbr=120"

# 測試所有可能的 ID 組合
TARGET_IDS = [
    "-1004343189687",
    "-1005478933926",
    "-5478933926"
]
# ================================================

def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(API_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API 請求失敗，狀態碼: {response.status_code}")
            return None
    except Exception as e:
        print(f"獲取數據時發生異常: {e}")
        return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    success = False

    for chat_id in TARGET_IDS:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            print(f"嘗試發送到 ID: {chat_id} ...")
            response = requests.post(url, json=payload, timeout=10)
            res_data = response.json()
            print(f"回應: {res_data}")
            if res_data.get("ok"):
                print(f"成功發送到 ID: {chat_id}")
                success = True
                break
        except Exception as e:
            print(f"發送到 {chat_id} 時發生異常: {e}")

    if not success:
        raise Exception("所有 Chat ID 發送均失敗，請檢查 Telegram 管理員權限！")

def main():
    data = fetch_data()
    if not data:
        print("無法獲取有效開獎數據，終止發送。")
        return

    latest = None
    if isinstance(data, list) and len(data) > 0:
        latest = data[0]
    elif isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
            latest = data["data"][0]
        else:
            latest = data

    if not latest or not isinstance(latest, dict):
        print("開獎數據格式不符。")
        return

    issue = latest.get("issue", latest.get("expect", "未知期數"))
    result_nums = latest.get("result", latest.get("opencode", "未知結果"))

    msg = (
        f"<b>📊 PC28 最新開獎與預測通知</b>\n\n"
        f"期數：<code>{issue}</code>\n"
        f"開獎號碼：<code>{result_nums}</code>\n\n"
        f"🤖 機器人持續追蹤中..."
    )

    send_telegram_message(msg)

if __name__ == "__main__":
    main()
