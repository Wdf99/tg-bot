import requests
import json

TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
CHAT_ID = "-1005478933926"
API_URL = "https://pc28.help/api/kj.json?nbr=120"

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(API_URL, headers=headers, timeout=15)
        print(f"API 狀態碼: {res.status_code}")
        data = res.json()
        
        # 把 API 回傳的原始資料印在日誌中，讓我們看清欄位
        print(f"原始 API 數據內容預覽: {str(data)[:500]}")
        
        # 簡單提取第一筆
        items = data if isinstance(data, list) else data.get("data", data.get("list", []))
        if items:
            first = items[0]
            print(f"第一筆數據詳情: {first}")
            
            # 嘗試發送測試訊息到 Telegram
            msg = f"<b>🔍 測試回傳數據</b>\n原始資料 keys: {list(first.keys())}"
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={
                "chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"
            })
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    main()
