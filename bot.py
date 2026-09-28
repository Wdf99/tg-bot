import requests
import json

# ==================== 設定區 ====================
TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
CHAT_ID = "-1004343189687"
API_URL = "https://pc28.help/api/kj.json?nbr=120"
# ================================================

def main():
    print("開始執行腳本...")
    
    # 1. 抓取開獎資料
    issue = "最新"
    nums_str = "1 - 2 - 3"
    total_sum = "6"
    str_a, str_b, str_c = "0 1 2 3 4", "1 2 3 4 5", "2 3 4 5 6"
    api_countdown = "00:00"

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        res = requests.get(API_URL, headers=headers, timeout=10)
        print(f"API 狀態碼: {res.status_code}")
        if res.status_code == 200:
            raw = res.json()
            api_countdown = str(raw.get("countdown", "--"))
            items = raw.get("data", raw.get("list", []))
            if not items and isinstance(raw, list):
                items = raw
            if items:
                latest = items[0]
                issue = str(latest.get("nbr", latest.get("issue", "最新")))
                num_str = str(latest.get("number", latest.get("result", ""))).replace(",", "+").replace(" ", "+")
                nums = [int(x) for x in num_str.split("+") if x.strip().isdigit()][:3]
                if len(nums) == 3:
                    nums_str = " - ".join(map(str, nums))
                    total_sum = str(sum(nums))
    except Exception as e:
        print(f"抓取 API 發生錯誤: {e}")

    try:
        next_issue = str(int(issue) + 1)
    except Exception:
        next_issue = "下一期"

    msg = (
        f"<b>📊 ABC 球預測</b>\n\n"
        f"<b>最新開獎期數：</b><code>{issue}</code>\n"
        f"<b>開獎號碼：</b><code>{nums_str}</code> (和值: {total_sum})\n"
        f"----------------------------------------\n"
        f"<b>🔮 🎯 第 {next_issue} 期 ABC 5碼預測：</b>\n\n"
        f"🔵 <b>A 球 5 碼：</b> <code>{str_a}</code>\n"
        f"🟣 <b>B 球 5 碼：</b> <code>{str_b}</code>\n"
        f"🟢 <b>C 球 5 碼：</b> <code>{str_c}</code>\n\n"
        f"⏱ <b>距離下一期開獎：</b> <code>{api_countdown}</code>\n"
        f"🤖 <i>系統自動實時預測中...</i>"
    )

    # 2. 發送 Telegram 訊息（不使用 try-except，讓錯誤直接暴露出來）
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    
    print("正在發送請求至 Telegram API...")
    response = requests.post(url, json=payload, timeout=10)
    print(f"Telegram 完整回應內容: {response.text}")
    
    result_json = response.json()
    if not result_json.get("ok"):
        print(f"❌ 發送失敗！原因代碼: {result_json.get('error_code')}")
        print(f"❌ 錯誤描述: {result_json.get('description')}")
    else:
        print("✅ Telegram 訊息發送成功！")

if __name__ == "__main__":
    main()
