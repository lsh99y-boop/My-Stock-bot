import yfinance as yf
import requests
import re
from datetime import datetime
import pytz

# --- 설정 (정보 확인) ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531'

targets = {
    "HMM": "011200.KS", "두산에너빌리티": "034020.KS", "와이지-원": "019210.KQ",
    "엔씨소프트": "036570.KS", "한전기술": "052690.KS", "화성밸브": "039610.KQ",
    "하이스틸": "071090.KS", "차바이오텍": "085660.KQ", "칩스앤미디어": "094360.KQ",
    "필옵틱스": "161580.KQ", "앱클론": "174900.KQ", "에이디테크놀로지": "200710.KQ",
    "클래시스": "214150.KQ", "SK바이오사이언스": "302440.KS", "에스와이스틸텍": "365330.KQ"
}

def send_telegram(text):
    # .org/bot 경로를 정확히 유지합니다.
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "disable_web_page_preview": False  # URL 미리보기를 켜서 기사 썸네일이 보이게 합니다.
    }
    requests.post(url, data=payload, timeout=15)

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
    # 1. 상단 타이틀 전송
    send_telegram(f"📅 [포트폴리오 시황 & 뉴스 링크 - {now}]")
    
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            # 시세 정보 구성
            if not hist.empty and len(hist) >= 2:
                prev_c = hist['Close'].iloc[-2]
                curr_c = hist['Close'].iloc[-1]
                diff = curr_c - prev_c
                pct = (diff / prev_c) * 100
                mark = "🔼" if diff > 0 else "🔽" if diff < 0 else "➖"
                price_text = f"📍 {name}: {curr_c:,.0f}원 ({mark} {abs(diff):,.0f}, {pct:+.2f}%)"
            else:
                price_text = f"📍 {name}: 시세 수집 지연"

            # 뉴스 제목과 URL만 추출
            news_info = "📰 관련 뉴스 없음"
            raw_news = ticker.news
            if raw_news and len(raw_news) > 0:
                latest = raw_news[0] # 가장 최신 뉴스 1건
                title = latest.get('title', '제목 없음')
                link = latest.get('link', '')
                news_info = f"📰 {title}\n🔗 {link}"
                
            # 종목별로 메시지 전송 (길이 제한 방지 및 가독성)
            send_telegram(f"{price_text}\n{news_info}")
                
        except Exception as e:
            print(f"{name} 에러: {e}")

if __name__ == "__main__":
    run()
