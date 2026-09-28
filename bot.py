import requests
import json

# ==================== 設定區 ====================
TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
CHAT_ID = "-1004343189687"                      # 正確的群組 ID
API_URL = "https://pc28.help/api/kj.json?nbr=120"
# ================================================

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram API 回應: {response.json()}")
    except Exception as e:
        print(f"發送 Telegram 異常: {e}")

def main():
    issue = "最新"
    nums_str = "-- - -- - --"
    total_sum = "--"
    str_a, str_b, str_c = "0 1 2 3 4", "1 2 3 4 5", "2 3 4 5 6"
    api_countdown = "--"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(API_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            raw = response.json()
            api_countdown = str(raw.get("countdown", "--"))
            
            items = raw.get("data", raw.get("list", []))
            if not items and isinstance(raw, list):
                items = raw

            history = []
            for item in items:
                try:
                    if not isinstance(item, dict):
                        continue
                    num_str = str(item.get("number", item.get("result", item.get("opencode", "")))).replace(",", "+").replace(" ", "+")
                    nums = [int(x.strip()) for x in num_str.split("+") if x.strip().isdigit()][:3]
                    curr_issue = str(item.get("nbr", item.get("issue", item.get("expect", "--"))))
                    if len(nums) == 3:
                        history.append({"expect": curr_issue, "nums": nums, "sum": sum(nums)})
                except Exception:
                    continue

            if history:
                latest = history[0]
                issue = latest["expect"]
                nums_str = " - ".join(map(str, latest["nums"]))
                total_sum = latest["sum"]

                # 簡單預測計算
                def get_pred(pos):
                    count = [0] * 10
                    for h in history[:100]:
                        n = h["nums"][pos]
                        if 0 <= n <= 9: count[n] += 1
                    arr = [{"n": n, "c": count[n]} for n in range(10)]
                    arr.sort(key=lambda x: (-x["c"], x["n"]))
                    return [str(x["n"]) for x in arr[:5]]

                str_a = " ".join(get_pred(0))
                str_b = " ".join(get_pred(1))
                str_c = " ".join(get_pred(2))
    except Exception as e:
        print(f"資料處理過程發生例外: {e}")

    try:
        next_issue = str(int(issue) + 1)
    except Exception:
        next_issue = "下一期"

    msg = (
        f"<b>📊 Lx六合彩交流群 ABC 球預測</b>\n\n"
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

    send_telegram_message(msg)

if __name__ == "__main__":
    main()
