import requests
import json

# ==================== 設定區 ====================
TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
CHAT_ID = "-1005478933926"                      # 超級群組 ID
API_URL = "https://pc28.help/api/kj.json?nbr=120"
# ================================================

def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    try:
        response = requests.get(API_URL, headers=headers, timeout=15)
        print(f"API 狀態碼: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API 請求失敗: {response.status_code}")
            return None
    except Exception as e:
        print(f"獲取數據異常: {e}")
        return None

def adapt_history_data(raw):
    """強效解析：兼容字典/列表，自動處理各種 API 格式"""
    if not raw:
        return []

    items = []
    # 判斷 raw 是列表還是字典
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        if "data" in raw and isinstance(raw["data"], list):
            items = raw["data"]
        elif "list" in raw and isinstance(raw["list"], list):
            items = raw["list"]
        else:
            # 可能是單筆字典
            items = [raw]

    if not items:
        return []

    # 確保最新期號在最前面
    try:
        if len(items) > 1 and int(items[0].get("nbr", items[0].get("issue", 0))) < int(items[-1].get("nbr", items[-1].get("issue", 0))):
            items.reverse()
    except Exception:
        pass

    history = []
    for item in items:
        try:
            if not isinstance(item, dict):
                continue
                
            # 相容多種開獎號碼欄位: number, result, opencode
            num_str = str(item.get("number", item.get("result", item.get("opencode", ""))))
            
            # 清理並分割號碼（相容 + 或 , 或 空格）
            num_str = num_str.replace(",", "+").replace(" ", "+")
            nums = [int(x.strip()) for x in num_str.split("+") if x.strip().isdigit()]
            nums = nums[:3]  # 取前 3 個號碼 (A, B, C)
            
            # 期號相容: nbr, issue, expect
            issue = str(item.get("nbr", item.get("issue", item.get("expect", "--"))))

            if len(nums) == 3:
                history.append({
                    "expect": issue,
                    "nums": nums,
                    "sum": sum(nums)
                })
        except Exception as e:
            continue
            
    print(f"成功提取到 {len(history)} 期歷史開獎數據。")
    return history

def position_frequency(history, pos):
    count = [0] * 10
    for item in history[:100]:
        n = item["nums"][pos]
        if 0 <= n <= 9:
            count[n] += 1
    return count

def position_omission(history, pos):
    omission = [len(history) + 1] * 10
    for idx, item in enumerate(history[:100]):
        n = item["nums"][pos]
        if 0 <= n <= 9:
            if omission[n] == len(history) + 1:
                omission[n] = idx
    return omission

def algorithm_frequency(history, pos):
    freq = position_frequency(history, pos)
    arr = [{"n": n, "score": freq[n]} for n in range(10)]
    arr.sort(key=lambda x: (-x["score"], x["n"]))
    return [x["n"] for x in arr[:5]]

def algorithm_omission(history, pos):
    omit = position_omission(history, pos)
    arr = [{"n": n, "score": omit[n]} for n in range(10)]
    arr.sort(key=lambda x: (-x["score"], x["n"]))
    return [x["n"] for x in arr[:5]]

def algorithm_combined(history, pos):
    freq = position_frequency(history, pos)
    omit = position_omission(history, pos)
    
    max_freq = max(freq) if max(freq) > 0 else 1
    max_omit = max(omit) if max(omit) > 0 else 1
    
    arr = []
    for n in range(10):
        freq_score = freq[n] / max_freq
        omit_score = omit[n] / max_omit
        score = freq_score * 0.55 + omit_score * 0.45
        arr.append({"n": n, "score": score})
        
    arr.sort(key=lambda x: (-x["score"], x["n"]))
    return [x["n"] for x in arr[:5]]

def generate_position_prediction(history, pos):
    a = algorithm_frequency(history, pos)
    b = algorithm_omission(history, pos)
    c = algorithm_combined(history, pos)
    
    result = []
    for n in c:
        if n not in result:
            result.append(n)
            
    for n in (a + b):
        if len(result) < 5:
            if n not in result:
                result.append(n)
                
    return result[:5]

def generate_prediction(history):
    if len(history) < 5:
        return None
        
    predict_A = generate_position_prediction(history, 0)
    predict_B = generate_position_prediction(history, 1)
    predict_C = generate_position_prediction(history, 2)
    
    return {
        "A": predict_A,
        "B": predict_B,
        "C": predict_C
    }

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
        print(f"發送訊息異常: {e}")

def main():
    raw_data = fetch_data()
    if not raw_data:
        print("無法獲取有效數據，終止發送。")
        return

    history = adapt_history_data(raw_data)
    if not history:
        print("解析開獎歷史紀錄失敗。")
        return

    latest = history[0]
    issue = latest["expect"]
    nums_str = " - ".join(map(str, latest["nums"]))
    total_sum = latest["sum"]
    
    try:
        next_issue = str(int(issue) + 1)
    except Exception:
        next_issue = "下一期"

    pred = generate_prediction(history)

    if pred:
        str_a = " ".join(map(str, pred["A"]))
        str_b = " ".join(map(str, pred["B"]))
        str_c = " ".join(map(str, pred["C"]))

        msg = (
            f"<b>📊 Lx六合彩交流群 ABC 球預測</b>\n\n"
            f"<b>最新開獎期數：</b><code>{issue}</code>\n"
            f"<b>開獎號碼：</b><code>{nums_str}</code> (和值: {total_sum})\n"
            f"----------------------------------------\n"
            f"<b>🔮 🎯 第 {next_issue} 期 ABC 5碼預測：</b>\n\n"
            f"🔵 <b>A 球 5 碼：</b> <code>{str_a}</code>\n"
            f"🟣 <b>B 球 5 碼：</b> <code>{str_b}</code>\n"
            f"🟢 <b>C 球 5 碼：</b> <code>{str_c}</code>\n\n"
            f"💡 <i>(註：A/B/C分別對應開獎第1、2、3位數字)</i>\n"
            f"🤖 <i>系統自動實時預測中...</i>"
        )
    else:
        msg = (
            f"<b>📊 PC28 最新開獎通知</b>\n\n"
            f"期數：<code>{issue}</code>\n"
            f"開獎號碼：<code>{nums_str}</code>\n"
            f"和值：<code>{total_sum}</code>\n"
            f"⚠️ 歷史數據不足，無法生成 ABC 預測。"
        )

    send_telegram_message(msg)

if __name__ == "__main__":
    main()
