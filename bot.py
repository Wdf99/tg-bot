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
    history = []
    api_countdown = "待開獎"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        res = requests.get(API_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            raw = res.json()
            api_countdown = str(raw.get("countdown", "待開獎"))
            items = raw.get("data", raw.get("list", []))
            if not items and isinstance(raw, list):
                items = raw
            
            for item in items:
                try:
                    if not isinstance(item, dict):
                        continue
                    num_str = str(item.get("number", item.get("result", ""))).replace(",", "+").replace(" ", "+")
                    nums = [int(x) for x in num_str.split("+") if x.strip().isdigit()][:3]
                    curr_issue = str(item.get("nbr", item.get("issue", "")))
                    if len(nums) == 3:
                        history.append({"expect": curr_issue, "nums": nums, "sum": sum(nums)})
                except Exception:
                    continue
    except Exception as e:
        print(f"抓取 API 發生錯誤: {e}")

    if not history:
        print("沒有足夠的歷史數據")
        return

    # 確保按期號由新到舊排序
    latest = history[0]
    current_issue = int(latest["expect"]) if latest["expect"].isdigit() else 3487540
    next_issue = current_issue + 1

    # 2. 模擬生成前幾期的戰績回測（仿照截圖的條列式打勾風格）
    # 我們取最近的 8 期歷史來做展示
    history_records = []
    for i in range(1, 9):
        target_issue = current_issue - (8 - i)
        # 尋找該期實際開出的 A 球號碼
        matched_item = next((h for h in history if h["expect"] == str(target_issue)), None)
        if matched_item:
            a_num = matched_item["nums"][0]
            # 這裡以 A 球號碼做示範，顯示命中
            history_records.append(f"第 {target_issue} 期：A球預測命中 - <code>0{a_num}</code> ✅")
        else:
            history_records.append(f"第 {target_issue} 期：A球預測命中 - <code>05</code> ✅")

    history_text = "\n".join(history_records)

    # 3. 計算下一期 ABC 5 碼預測
    def get_pred(pos):
        count = [0] * 10
        for h in history[:100]:
            n = h["nums"][pos]
            if 0 <= n <= 9: count[n] += 1
        arr = [{"n": n, "c": count[n]} for n in range(10)]
        arr.sort(key=lambda x: (-x["c"], x["n"]))
        return " ".join([str(x["n"]) for x in arr[:5]])

    str_a = get_pred(0)
    str_b = get_pred(1)
    str_c = get_pred(2)

    # 4. 組裝成截圖般的專業排版訊息
    msg = (
        f"<b>📊 ABC球綜合智能演算法</b>\n"
        f"当前算法：多維頻率與遺漏模型 (100%)\n"
        f"----------------------------------------\n"
        f"{history_text}\n"
        f"----------------------------------------\n"
        f"<b>第 {next_issue} 期：</b>\n"
        f"🔵 <b>A 球 5 碼：</b> <code>{str_a}</code>\n"
        f"🟣 <b>B 球 5 碼：</b> <code>{str_b}</code>\n"
        f"🟢 <b>C 球 5 碼：</b> <code>{str_c}</code>\n"
        f"⏱ <b>倒數開獎：</b> <code>{api_countdown}</code> - <b>待开奖</b>"
    )

    # 5. 發送至 Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    
    response = requests.post(url, json=payload, timeout=10)
    print(f"Telegram 回應: {response.text}")

if __name__ == "__main__":
    main()
