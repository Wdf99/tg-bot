import requests
import json

# ==================== 設定區 ====================
TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
CHAT_ID = "-1005478933926"                      # 超級群組 ID
API_URL = "https://pc28.help/api/kj.json?nbr=120"
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
            print(f"API 請求失敗: {response.status_code}")
            return None
    except Exception as e:
        print(f"獲取數據異常: {e}")
        return None

def adapt_history_data(raw):
    """解析 API 歷史數據"""
    if not raw:
        return []
    
    items = []
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        if "data" in raw and isinstance(raw["data"], list):
            items = raw["data"]
        elif "list" in raw and isinstance(raw["list"], list):
            items = raw["list"]
        else:
            items = [raw]

    history = []
    for item in items:
        try:
            if not isinstance(item, dict):
                continue
            
            # 支援多種欄位名稱
            num_str = str(item.get("number", item.get("result", item.get("opencode", ""))))
            num_str = num_str.replace(",", "+").replace(" ", "+")
            nums = [int(x.strip()) for x in num_str.split("+") if x.strip().isdigit()]
            nums = nums[:3]
            
            issue = str(item.get("nbr", item.get("issue", item.get("expect", "--"))))

            if len(nums) == 3:
                history.append({
                    "expect": issue,
                    "nums": nums,
                    "sum": sum(nums)
                })
        except Exception:
            continue
    return history

def generate_position_prediction(history, pos):
    """基於頻率與遺漏的 ABC 5碼預測演算法"""
    if len(history) < 10:
        return [0, 1, 2, 3, 4]  # 預備防呆碼
        
    count = [0] * 10
    omission = [len(history) + 1] * 10
    
    for idx, item in enumerate(history[:100]):
        n = item["nums"][pos]
        if 0 <= n <= 9:
            count[n] += 1
            if omission[n] == len(history) + 1:
                omission[n] = idx

    max_freq = max(count) if max(count) > 0 else 1
    max_omit = max(omission) if max(omission) > 0 else 1
    
    arr = []
    for n in range(10):
        score = (count[n] / max_freq) * 0.55 + (omission[n] / max_omit) * 0.45
        arr.append({"n": n, "score": score})
        
    arr.sort(key=lambda x: (-x["score"], x["n"]))
    return [x["n"] for x in arr[:5]]

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
    except Exception as e:
        print(f"發送訊息異常: {e}")

def main():
    raw_data = fetch_data()
    if not raw_data:
        print("無法獲取數據")
        return

    history = adapt_history_data(raw_data)
    
    # 預設值（即使歷史不足也能正常發送）
    issue = "最新"
    nums_str = "-- - -- - --"
    total_sum = "--"
    str_a, str_b, str_c = "0 1 2 3 4", "1 2 3 4 5", "2 3 4 5 6"

    if history:
        latest = history[0]
        issue = latest["expect"]
        nums_str = " - ".join(map(str, latest["nums"]))
        total_sum = latest["sum"]
        
        # 計算預測
        pred_a = generate_position_prediction(history, 0)
        pred_b = generate_position_prediction(history, 1)
        pred_c = generate_position_prediction(history, 2)
        
        str_a = " ".join(map(str, pred_a))
        str_b = " ".join(map(str, pred_b))
        str_c = " ".join(map(str, pred_c))

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
        f"🤖 <i>系統自動實時預測中...</i>"
    )

    send_telegram_message(msg)

if __name__ == "__main__":
    main()
