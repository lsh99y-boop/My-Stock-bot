import yfinance as yf
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# --- 설정 ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531'

targets = {
    "💵 원/달러 환율": "USDKRW=X",
    "🟡 국제 금시세": "GC=F",
    "⚪ 국제 은시세": "SI=F",
    "🛢️ WTI 원유": "CL=F",
    # 탄산리튬은 별도 함수로 처리하므로 리스트에서 제외하거나 이름을 맞춥니다.
    "HMM": "011200.KS", "두산에너빌리티": "034020.KS", "와이지-원": "019210.KQ",
    "엔씨소프트": "036570.KS", "한전기술": "052690.KS", "화성밸브": "039610.KQ",
    "하이스틸": "071090.KS", "차바이오텍": "085660.KQ", "칩스앤미디어": "094360.KQ",
    "필옵틱스": "161580.KQ", "앱클론": "174900.KQ", "에이디테크놀로지": "200710.KQ",
    "클래시스": "214150.KQ", "SK바이오사이언스": "302440.KS", "에스와이스틸텍": "365330.KQ"
}

def get_lithium_price():
    """인베스팅닷컴에서 탄산리튬 선물 가격 크롤링"""
    try:
        url = "https://www.investing.com"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 최신 가격 및 변동률 추출 (인베스팅닷컴 구조 기준)
        price = soup.find('div', {'data-test': 'instrument-price-last'}).text
        change_pct = soup.find('span', {'data-test': 'instrument-price-change-percent'}).text
        
        mark = "🔼" if "+" in change_pct else "🔽" if "-" in change_pct else "➖"
        return f"📍 🔋 탄산리튬(중국): {price} ({mark} {change_pct})"
    except:
        return "📍 🔋 탄산리튬: 데이터 수집 지연 (인베스팅 차단)"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}
    requests.post(url, data=payload, timeout=15)

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
    send_telegram(f"📢 [종합 시황 & 탄산리튬 - {now}]")
    
    # 1. 탄산리튬 가격 먼저 전송
    li_price = get_lithium_price()
    send_telegram(li_price)
    
    # 2. 나머지 종목 전송
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            if not hist.empty and len(hist) >= 2:
                curr_c = hist['Close'].iloc[-1]
                prev_c = hist['Close'].iloc[-2]
                diff = curr_c - prev_c
                pct = (diff / prev_c) * 100
                mark = "🔼" if diff > 0 else "🔽" if diff < 0 else "➖"
                
                if any(x in symbol for x in ["=X", "=F"]):
                    price_text = f"📍 {name}: {curr_c:,.2f} ({mark} {abs(diff):,.2f}, {pct:+.2f}%)"
                else:
                    price_text = f"📍 {name}: {curr_c:,.0f}원 ({mark} {abs(diff):,.0f}, {pct:+.2f}%)"
            else:
                price_text = f"📍 {name}: 데이터 확인 중"

            news_info = ""
            if ticker.news and not any(x in symbol for x in ["=X", "=F"]):
                latest = ticker.news
                news_info = f"\n📰 {latest.get('title')}\n🔗 {latest.get('link')}"
                
            send_telegram(f"{price_text}{news_info}")
                
        except: continue

if __name__ == "__main__":
    run()
