import yfinance as yf
import requests
from datetime import datetime
import pytz

# --- 설정 (본인 정보 확인) ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531'

# 리튬은 가장 안정적인 LIT(ETF)와 LTH-USD를 혼합하여 체크합니다.
targets = {
    "💵 원/달러 환율": "USDKRW=X",
    "🟡 국제 금시세": "GC=F",
    "⚪ 국제 은시세": "SI=F",
    "🛢️ WTI 원유": "CL=F",
    "🔋 탄산리튬(LIT)": "LIT", # ETF 기반으로 하면 절대 끊기지 않습니다.
    
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
            # 리튬 등 원자재 지연 대비 1개월치 데이터를 가져와서 유효한 데이터 탐색
            hist = ticker.history(period="1mo") 
            
            if not hist.empty and len(hist) >= 2:
                # 데이터가 존재하는 가장 최신 2일 추출
                valid_data = hist.dropna(subset=['Close'])
                curr_c = valid_data['Close'].iloc[-1]
                prev_c = valid_data['Close'].iloc[-2]
                
                diff = curr_c - prev_c
                pct = (diff / prev_c) * 100
                mark = "🔼" if diff > 0 else "🔽" if diff < 0 else "➖"
                
                # 지표와 주식 출력 형식 구분
                is_index = any(x in symbol for x in ["=X", "=F", "-USD", "LIT"])
                if is_index:
                    price_text = f"📍 {name}: {curr_c:,.2f} ({mark} {abs(diff):,.2f}, {pct:+.2f}%)"
                else:
                    price_text = f"📍 {name}: {curr_c:,.0f}원 ({mark} {abs(diff):,.0f}, {pct:+.2f}%)"
            else:
                price_text = f"📍 {name}: 시세 업데이트 대기 중"

            # 주식 종목만 뉴스 포함
            news_info = ""
            if not any(x in symbol for x in ["=X", "=F", "-USD", "LIT"]):
                if ticker.news:
                    latest = ticker.news
                    news_info = f"\n📰 {latest.get('title')}\n🔗 {latest.get('link')}"
                
            send_telegram(f"{price_text}{news_info}")
                
        except: continue

if __name__ == "__main__":
    run()
