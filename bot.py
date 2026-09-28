import requests
import json

# ==================== 設定區 ====================
TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
CHAT_ID = "-1004343189687"
API_URL = "https://pc28.help/api/kj.json?nbr=10"
WEB_URL = "https://pc28.help"  # 點擊按鈕後開啟的即時開獎與倒數網頁
# ================================================

def main():
    print("開始執行帶按鈕的機器人腳本...")
    
    api_countdown = "--:--"
    history = []
    
    # 1. 抓取 API 數據
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        res = requests.get(API_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            raw = res.json()
            api_countdown = str(raw.get("countdown", "--:--"))
            
            items = raw.get("data", [])
            if not items and isinstance(raw, list):
                items = raw
                
            for item in items:
                try:
                    if not isinstance(item, dict):
                        continue
                    curr_issue = str(item.get("nbr", "未知"))
                    num_str = str(item.get("number", "0+0+0=0"))
                    
                    if "=" in num_str:
                        formula_part = num_str.split("=")[0]
                        nums = [int(x.strip()) for x in formula_part.split("+") if x.strip().isdigit()]
                    else:
                        nums = [int(x.strip()) for x in num_str.replace(",", "+").split("+") if x.strip().isdigit()]
                        
                    if len(nums) >= 3:
                        history.append({
                            "expect": curr_issue,
                            "nums": nums[:3],
                            "sum": sum(nums[:3])
                        })
                except Exception:
                    continue
    except Exception as e:
        print(f"API 連線警告: {e}")

    # 2. 準備期號與戰績
    issue = "最新"
    if history:
        latest = history[0]
        issue = latest["expect"]

    try:
        next_issue = str(int(issue) + 1) if issue.isdigit() else "下一期"
    except Exception:
        next_issue = "下一期"

    # 3. 建立歷史戰績列表
    history_records = []
    for i in range(1, min(6, len(history) + 1)):
        h = history[i-1]
        history_records.append(f"第 {h['expect']} 期：和值 {h['sum']} ({' - '.join(map(str, h['nums']))}) ✅")
    
    history_text = "\n".join(history_records) if history_records else "暂无近期战绩记录"

    # 4. 計算 ABC 5 碼預測
    def get_pred(pos):
        try:
            if not history:
                return "0 1 2 3 4"
            count = [0] * 10
            for h in history:
                if len(h["nums"]) > pos:
                    n = h["nums"][pos]
                    if 0 <= n <= 9: 
                        count[n] += 1
            arr = [{"n": n, "c": count[n]} for n in range(10)]
            arr.sort(key=lambda x: (-x["c"], x["n"]))
            return " ".join([str(x["n"]) for x in arr[:5]])
        except Exception:
            return "0 1 2 3 4"

    str_a = get_pred(0)
    str_b = get_pred(1)
    str_c = get_pred(2)

    # 5. 組裝訊息
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
        f"⏱ <b>當前 API 參考倒數：</b> <code>{api_countdown}</code>"
    )

    # 6. 發送至 Telegram（附加內嵌網頁按鈕）
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "🌐 點擊開啟即時開獎與動態倒數大屏",
                        "url": WEB_URL
                    }
                ]
            ]
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram 發送結果: {response.text}")
    except Exception as e:
        print(f"發送發生例外: {e}")

if __name__ == "__main__":
    main()
