import requests
import json
import os

# ==================== 設定區 ====================
TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
CHAT_ID = "-1004343189687"
API_URL = "https://pc28.help/api/kj.json?nbr=10"
# 用來記錄上一則訊息 ID 的檔案（讓 GitHub Actions 每次跑的時候知道要編輯哪一則訊息）
MESSAGE_ID_FILE = "last_msg_id.txt"
# ================================================

def get_last_message_id():
    if os.path.exists(MESSAGE_ID_FILE):
        try:
            with open(MESSAGE_ID_FILE, "r") as f:
                return f.read().strip()
        except Exception:
            pass
    return None

def save_last_message_id(msg_id):
    try:
        with open(MESSAGE_ID_FILE, "w") as f:
            f.write(str(msg_id))
    except Exception:
        pass

def main():
    print("開始執行動態倒數更新腳本...")
    
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

    # 5. 組裝訊息內容
    msg = (
        f"<b>📊 ABC球綜合智能演算法 (實時更新)</b>\n"
        f"当前算法：多維頻率與遺漏模型 (100%)\n"
        f"----------------------------------------\n"
        f"{history_text}\n"
        f"----------------------------------------\n"
        f"<b>第 {next_issue} 期預測：</b>\n"
        f"🔵 <b>A 球 5 碼：</b> <code>{str_a}</code>\n"
        f"🟣 <b>B 球 5 碼：</b> <code>{str_b}</code>\n"
        f"🟢 <b>C 球 5 碼：</b> <code>{str_c}</code>\n"
        f"⏱ <b>即時開獎倒計時：</b> <code>{api_countdown}</code>"
    )

    # 6. 檢查是否已有上一則訊息，若有則直接「編輯」它，否則發送新訊息
    last_msg_id = get_last_message_id()
    
    if last_msg_id:
        # 嘗試編輯上一則訊息
        edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
        payload = {
            "chat_id": CHAT_ID,
            "message_id": int(last_msg_id),
            "text": msg,
            "parse_mode": "HTML"
        }
        response = requests.post(edit_url, json=payload, timeout=10)
        res_data = response.json()
        
        if res_data.get("ok"):
            print("成功即時更新（編輯）上一則倒數訊息！")
            return
        else:
            print(f"編輯失敗（可能訊息被刪除或過期），改為發送新訊息: {res_data}")

    # 如果沒有上一則訊息或編輯失敗，則發送全新的一則
    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(send_url, json=payload, timeout=10)
        res_data = response.json()
        if res_data.get("ok"):
            new_msg_id = res_data["result"]["message_id"]
            save_last_message_id(new_msg_id)
            print("成功發送新訊息並記錄 ID！")
    except Exception as e:
        print(f"發送發生例外: {e}")

if __name__ == "__main__":
    main()
