python
import yfinance as yf
import requests
from datetime import datetime
import pytz

# --- 설정 ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531'

# 기존 종목 + 신규 경제 지표 (환율, 원자재)
targets = {
    # 경제 지표
    "💵 원/달러 환율": "USDKRW=X",
    "🟡 국제 금시세": "GC=F",
    "⚪ 국제 은시세": "SI=F",
    "🛢️ WTI 원유": "CL=F",
    "🔋 리튬(Lithium)": "LITH-USD",
    
    # 보유 종목
    "HMM": "011200.KS", "두산에너빌리티": "034020.KS", "와이지-원": "019210.KQ",
    "엔씨소프트": "036570.KS", "한전기술": "052690.KS", "화성밸브": "039610.KQ",
    "하이스틸": "071090.KS", "차바이오텍": "085660.KQ", "칩스앤미디어": "094360.KQ",
    "필옵틱스": "161580.KQ", "앱클론": "174900.KQ", "에이디테크놀로지": "200710.KQ",
    "클래시스": "214150.KQ", "SK바이오사이언스": "302440.KS", "에스와이스틸텍": "365330.KQ"
}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "disable_web_page_preview": True 
    }
    requests.post(url, data=payload, timeout=15)

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
    send_telegram(f"📢 [종합 시황 & 경제 지표 리포트 - {now}]")
    
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            if not hist.empty and len(hist) >= 2:
                prev_c = hist['Close'].iloc[-2]
                curr_c = hist['Close'].iloc[-1]
                diff = curr_c - prev_c
                pct = (diff / prev_c) * 100
                mark = "🔼" if diff > 0 else "🔽" if diff < 0 else "➖"
                
                # 경제 지표와 일반 종목의 가격 단위 구분
                if "=" in symbol or "-" in symbol: # 지표인 경우 소수점 유지
                    price_text = f"📍 {name}: {curr_c:,.2f} ({mark} {abs(diff):,.2f}, {pct:+.2f}%)"
                else: # 국내 주식인 경우 원화 단위
                    price_text = f"📍 {name}: {curr_c:,.0f}원 ({mark} {abs(diff):,.0f}, {pct:+.2f}%)"
            else:
                price_text = f"📍 {name}: 시세 확인 중"

            # 지표는 뉴스를 생략하고 주식 종목만 뉴스 URL 전송
            news_info = ""
            if not ("=" in symbol or "-" in symbol):
                if ticker.news:
                    latest = ticker.news[0]
                    news_info = f"\n📰 {latest.get('title')}\n🔗 {latest.get('link')}"
                
            send_telegram(f"{price_text}{news_info}")
                
        except Exception as e:
            print(f"{name} 수집 오류: {e}")
            continue

if __name__ == "__main__":
    run()
