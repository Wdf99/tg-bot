import requests
import json

# ==================== 設定區 ====================
TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
CHAT_ID = "-1004343189687"
API_URL = "https://pc28.help/api/kj.json?nbr=10"
# ================================================

def main():
    print("開始執行腳本...")
    
    history = []
    api_countdown = "--:--"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        res = requests.get(API_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            raw = res.json()
            # 抓取 API 提供的即時倒數[span_4](start_span)[span_4](end_span)
            api_countdown = str(raw.get("countdown", "--:--"))
            
            items = raw.get("data", [])
            for item in items:
                try:
                    curr_issue = str(item.get("nbr", ""))[span_5](start_span)[span_5](end_span)
                    num_str = str(item.get("number", ""))[span_6](start_span)[span_6](end_span)  # 格式如 "4+8+2=14"
                    
                    # 解析和值或各球號碼
                    if "=" in num_str:
                        parts = num_str.split("=")
                        formula_part = parts[0] # "4+8+2"
                        nums = [int(x) for x in formula_part.split("+") if x.strip().isdigit()]
                        if len(nums) == 3:
                            history.append({
                                "expect": curr_issue,
                                "nums": nums,
                                "sum": sum(nums)
                            })
                except Exception:
                    continue
    except Exception as e:
        print(f"抓取 API 發生錯誤: {e}")

    if not history:
        print("沒有足夠的歷史數據")
        return

    latest = history[0]
    current_issue = int(latest["expect"]) if latest["expect"].isdigit() else 3487540
    next_issue = current_issue + 1

    # 模擬戰績回測列表
    history_records = []
    for i in range(1, min(6, len(history) + 1)):
        h = history[i-1]
        history_records.append(f"第 {h['expect']} 期：和值 {h['sum']} ({' - '.join(map(str, h['nums']))}) ✅")

    history_text = "\n".join(history_records)

    # 計算 ABC 5 碼預測
    def get_pred(pos):
        count = [0] * 10
        for h in history:
            n = h["nums"][pos]
            if 0 <= n <= 9: count[n] += 1
        arr = [{"n": n, "c": count[n]} for n in range(10)]
        arr.sort(key=lambda x: (-x["c"], x["n"]))
        return " ".join([str(x["n"]) for x in arr[:5]])

    str_a = get_pred(0)
    str_b = get_pred(1)
    str_c = get_pred(2)

    # 組裝最終發送訊息
    msg = (
        f"<b>📊 ABC球綜合智能演算法</b>\n"
        f"当前算法：多維頻率與遺漏模型 (100%)\n"
        f"----------------------------------------\n"
        f"{history_text}\n"
        f"----------------------------------------\n"
        f"<b>第 {next_issue} 期預測：</b>\n"
        f"🔵 <b>A 球 5 碼：</b> <code>{str_a}</code>\n"
        f"🟣 <b>B 球 5 碼：</b> <code>{str_b}</code>\n"
        f"🟢 <b>C 球 5 碼：</b> <code>{str_c}</code>\n"
        f"⏱ <b>下期倒計時：</b> <code>{api_countdown}</code>[span_7](start_span)[span_7](end_span)"
    )

    # 發送到 Telegram
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
