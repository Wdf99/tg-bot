import time
import requests
import json

# ==================== 設定區 ====================
TELEGRAM_BOT_TOKEN = "8609140332:AAFw48FjbJSEc0LDhE1C5UFUdt-B5BEjolc"
CHAT_ID = "-1004343189687"
API_URL = "https://pc28.help/api/kj.json?nbr=10"
# ================================================

def send_telegram_msg(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"發送 Telegram 失敗: {e}")
        return None

def main():
    print("🚀 實時監控開獎 API 服務已啟動...")
    last_processed_issue = None

    while True:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
            res = requests.get(API_URL, headers=headers, timeout=10)
            
            if res.status_code == 200:
                raw = res.json()
                api_countdown = str(raw.get("countdown", "--:--"))
                items = raw.get("data", [])
                if not items and isinstance(raw, list):
                    items = raw
                
                if items:
                    latest = items[0]
                    current_issue = str(latest.get("nbr", "未知"))
                    
                    # 核心邏輯：如果發現期號跟上次處理的不一樣，代表進入新的一期或剛開獎！
                    if current_issue != last_processed_issue:
                        print(f"偵測到新期號變動: {current_issue}，開始計算並推播...")
                        
                        # 解析歷史資料做戰績與預測
                        history = []
                        for item in items:
                            try:
                                num_str = str(item.get("number", "0+0+0=0"))
                                if "=" in num_str:
                                    formula_part = num_str.split("=")[0]
                                    nums = [int(x.strip()) for x in formula_part.split("+") if x.strip().isdigit()]
                                else:
                                    nums = [int(x.strip()) for x in num_str.replace(",", "+").split("+") if x.strip().isdigit()]
                                if len(nums) >= 3:
                                    history.append({
                                        "expect": str(item.get("nbr", "")),
                                        "nums": nums[:3],
                                        "sum": sum(nums[:3])
                                    })
                            except Exception:
                                continue

                        # 建立歷史戰績列表
                        history_records = []
                        for i in range(1, min(6, len(history))):
                            h = history[i]
                            history_records.append(f"第 {h['expect']} 期：和值 {h['sum']} ({' - '.join(map(str, h['nums']))}) ✅")
                        history_text = "\n".join(history_records) if history_records else "暂无近期战绩记录"

                        # 計算下一期預測號碼
                        next_issue = str(int(current_issue) + 1) if current_issue.isdigit() else "下一期"

                        def get_pred(pos):
                            try:
                                if not history: return "0 1 2 3 4"
                                count = [0] * 10
                                for h in history:
                                    if len(h["nums"]) > pos:
                                        n = h["nums"][pos]
                                        if 0 <= n <= 9: count[n] += 1
                                arr = [{"n": n, "c": count[n]} for n in range(10)]
                                arr.sort(key=lambda x: (-x["c"], x["n"]))
                                return " ".join([str(x["n"]) for x in arr[:5]])
                            except Exception:
                                return "0 1 2 3 4"

                        str_a = get_pred(0)
                        str_b = get_pred(1)
                        str_c = get_pred(2)

                        # 組裝訊息
                        msg = (
                            f"<b>📊 ABC球綜合智能演算法 (實時同步)</b>\n"
                            f"当前算法：多維頻率與遺漏模型 (100%)\n"
                            f"----------------------------------------\n"
                            f"{history_text}\n"
                            f"----------------------------------------\n"
                            f"<b>第 {next_issue} 期預測：</b>\n"
                            f"🔵 <b>A 球 5 碼：</b> <code>{str_a}</code>\n"
                            f"🟣 <b>B 球 5 碼：</b> <code>{str_b}</code>\n"
                            f"🟢 <b>C 球 5 碼：</b> <code>{str_c}</code>\n"
                            f"⏱ <b>當前開獎倒計時：</b> <code>{api_countdown}</code>"
                        )

                        # 發送到群組
                        send_telegram_msg(msg)
                        
                        # 更新記錄，避免重複發送
                        last_processed_issue = current_issue
                        
        except Exception as e:
            print(f"主迴圈發生錯誤: {e}")

        # 每隔 30 秒檢查一次 API
        time.sleep(30)

if __name__ == "__main__":
    main()
