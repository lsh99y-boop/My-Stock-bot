import yfinance as yf
import requests
from datetime import datetime
import pytz

# --- 설정 (본인 정보 확인) ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531'

# 지연 없는 지표들로 재구성
targets = {
    "💵 원/달러 환율": "USDKRW=X",
    "🟡 국제 금시세": "GC=F",
    "⚪ 국제 은시세": "SI=F",
    "🛢️ WTI 원유": "CL=F",
    "🔋 탄산리튬 지수": "LTH-USD", # 인베스팅 대신 야후의 리튬 인덱스 사용
    
    "HMM": "011200.KS", "두산에너빌리티": "034020.KS", "와이지-원": "019210.KQ",
    "엔씨소프트": "036570.KS", "한전기술": "052690.KS", "화성밸브": "039610.KQ",
    "하이스틸": "071090.KS", "차바이오텍": "085660.KQ", "칩스앤미디어": "094360.KQ",
    "필옵틱스": "161580.KQ", "앱클론": "174900.KQ", "에이디테크놀로지": "200710.KQ",
    "클래시스": "214150.KQ", "SK바이오사이언스": "302440.KS", "에스와이스틸텍": "365330.KQ"
}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}
    requests.post(url, data=payload, timeout=15)

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
    send_telegram(f"📢 [종합 시황 리포트 - {now}]")
    
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            # 데이터 지연 방지를 위해 기간을 7일로 넉넉히 잡고 최신 2일을 비교
            hist = ticker.history(period="7d")
            
            if not hist.empty and len(hist) >= 2:
                curr_c = hist['Close'].iloc[-1]
                prev_c = hist['Close'].iloc[-2]
                diff = curr_c - prev_c
                pct = (diff / prev_c) * 100
                mark = "🔼" if diff > 0 else "🔽" if diff < 0 else "➖"
                
                # 지표(소수점)와 주식(원화) 출력 구분
                if any(x in symbol for x in ["=X", "=F", "-USD"]):
                    price_text = f"📍 {name}: {curr_c:,.2f} ({mark} {abs(diff):,.2f}, {pct:+.2f}%)"
                else:
                    price_text = f"📍 {name}: {curr_c:,.0f}원 ({mark} {abs(diff):,.0f}, {pct:+.2f}%)"
            else:
                price_text = f"📍 {name}: 시세 확인 중"

            # 지표가 아닌 주식 종목만 뉴스 포함
            news_info = ""
            if not any(x in symbol for x in ["=X", "=F", "-USD"]):
                if ticker.news:
                    latest = ticker.news
                    news_info = f"\n📰 {latest.get('title')}\n🔗 {latest.get('link')}"
                
            send_telegram(f"{price_text}{news_info}")
                
        except: continue

if __name__ == "__main__":
    run()
