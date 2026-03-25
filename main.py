import yfinance as yf
import requests
from datetime import datetime
import pytz

# --- 설정 (본인 정보 확인) ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531'

# 1. 경제 지표 (환율, 원자재)
macro_targets = {
    "💵 원/달러 환율": "USDKRW=X",
    "🟡 국제 금시세": "GC=F",
    "⚪ 국제 은시세": "SI=F",
    "🛢️ WTI 원유": "CL=F",
    "🔋 탄산리튬(LIT)": "LIT"
}

# 2. 해외 주식 (미국)
global_targets = {
    "앱셀레라 바이오": "ABCL",
    "BTQ 테크놀로지": "BTQ",
    "조비 에비에이션": "JOBY",
    "플러그파워": "PLUG",
    "뉴스케일 파워": "SMR",
    "SMU(SMR 2X)": "SMU",
    "트릴로지 메탈스": "TMQ",
    "DRIV(자율주행)": "DRIV",
    "엔비디아": "NVDA", 
    "테슬라": "TSLA", 
    "애플": "AAPL"
}

# 3. 국내 주식
domestic_targets = {
    "HMM": "011200.KS", "두산에너빌리티": "034020.KS", "와이지-원": "019210.KQ",
    "엔씨소프트": "036570.KS", "한전기술": "052690.KS", "화성밸브": "039610.KQ",
    "하이스틸": "071090.KS", "차바이오텍": "085660.KQ", "칩스앤미디어": "094360.KQ",
    "필옵틱스": "161580.KQ", "앱클론": "174900.KQ", "에이디테크놀로지": "200710.KQ",
    "클래시스": "214150.KQ", "SK바이오사이언스": "302440.KS", "에스와이스틸텍": "365330.KQ"
}

def send_telegram(text):
    if not text.strip(): return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}
    try:
        requests.post(url, data=payload, timeout=15)
    except: pass

def get_price_info(name, symbol, is_domestic=False):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        if hist.empty: return f"📍 {name}: 데이터 없음\n"
            
        valid_data = hist.dropna(subset=['Close'])
        if len(valid_data) < 2:
            curr_c = valid_data['Close'].iloc[-1]
            return f"📍 {name}: {curr_c:,.2f} (비교불가)\n"

        curr_c = valid_data['Close'].iloc[-1]
        prev_c = valid_data['Close'].iloc[-2]
        diff = curr_c - prev_c
        pct = (diff / prev_c) * 100
        mark = "🔼" if diff > 0 else "🔽" if diff < 0 else "➖"

        if is_domestic:
            return f"📍 {name}: {curr_c:,.0f}원 ({mark} {abs(diff):,.0f}, {pct:+.2f}%)\n"
        else:
            # 해외주식/지표는 $ 표시 및 소수점 2자리
            prefix = "$" if "=" not in symbol else ""
            return f"📍 {name}: {prefix}{curr_c:,.2f} ({mark} {abs(diff):,.2f}, {pct:+.2f}%)\n"
    except: return f"📍 {name}: 수집 오류\n"

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
    # --- 1. 경제 지표 메시지 ---
    macro_report = f"🌍 [경제 지표 리포트 - {now}]\n\n"
    for name, symbol in macro_targets.items():
        macro_report += get_price_info(name, symbol)
    send_telegram(macro_report)
    
    # --- 2. 해외 주식 메시지 ---
    global_report = f"🇺🇸 [해외 주식 시황 - {now}]\n\n"
    for name, symbol in global_targets.items():
        global_report += get_price_info(name, symbol)
    send_telegram(global_report)

    # --- 3. 국내 주식 메시지 ---
    domestic_report = f"🇰🇷 [국내 주식 시황 - {now}]\n\n"
    for name, symbol in domestic_targets.items():
        domestic_report += get_price_info(name, symbol, is_domestic=True)
    send_telegram(domestic_report)

if __name__ == "__main__":
    run()
