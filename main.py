import yfinance as yf
import requests
import re
import html
from datetime import datetime, timedelta
import pytz

# --- 설정 (본인 정보 확인) ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531'

macro_targets = {
    "💵 원/달러 환율": "USDKRW=X",
    "🟡 국제 금시세": "GC=F",
    "⚪ 국제 은시세": "SI=F",
    "🛢️ WTI 원유": "CL=F",
    "🔋 탄산리튬(LIT)": "LIT"
}

stock_targets = {
    "HMM": "011200.KS", "두산에너빌리티": "034020.KS", "와이지-원": "019210.KQ",
    "엔씨소프트": "036570.KS", "한전기술": "052690.KS", "화성밸브": "039610.KQ",
    "하이스틸": "071090.KS", "차바이오텍": "085660.KQ", "칩스앤미디어": "094360.KQ",
    "필옵틱스": "161580.KQ", "앱클론": "174900.KQ", "에이디테크놀로지": "200710.KQ",
    "클래시스": "214150.KQ", "SK바이오사이언스": "302440.KS", "에스와이스틸텍": "365330.KQ"
}

def send_telegram(text):
    if not text.strip(): return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for i in range(0, len(text), 4000):
        part = text[i:i+4000]
        payload = {"chat_id": CHAT_ID, "text": part, "disable_web_page_preview": True}
        requests.post(url, data=payload, timeout=15)

def get_special_news(name):
    """두산에너빌리티 전용: 최근 30일간의 뉴스 검색"""
    try:
        # 구글 뉴스 RSS 활용 (when:30d 옵션)
        url = f"https://news.google.com{name}+when:30d&hl=ko&gl=KR&ceid=KR:ko"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        items = re.findall(r'<item>(.*?)</item>', res.text, re.DOTALL)
        
        if items:
            # 한 달치 뉴스 중 가장 최신 1건만 제목과 링크 추출 (리스트가 너무 길어지는 것 방지)
            title = re.search(r'<title>(.*?)</title>', items[0]).group(1)
            link = re.search(r'<link>(.*?)</link>', items[0]).group(1)
            return f"\n📅 [최근 1개월 뉴스]\n📰 {html.unescape(title)}\n🔗 {link}"
        return "\n📅 최근 1개월 내 뉴스 없음"
    except:
        return "\n📅 한 달 뉴스 수집 실패"

def get_price_info(name, symbol, is_stock=True):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        if hist.empty: return f"📍 {name}: 시세 데이터 없음\n"
            
        valid_data = hist.dropna(subset=['Close'])
        curr_c = valid_data['Close'].iloc[-1]
        
        # 등락 계산
        if len(valid_data) >= 2:
            prev_c = valid_data['Close'].iloc[-2]
            diff = curr_c - prev_c
            pct = (diff / prev_c) * 100
            mark = "🔼" if diff > 0 else "🔽" if diff < 0 else "➖"
            change_text = f" ({mark} {abs(diff):,.0f}, {pct:+.2f}%)"
        else:
            change_text = " (비교 데이터 부족)"

        if is_stock:
            price_line = f"📍 {name}: {curr_c:,.0f}원{change_text}"
            
            # --- 뉴스 처리 ---
            if name == "두산에너빌리티":
                news_info = get_special_news(name)
            else:
                news_info = ""
                raw_news = ticker.news
                if raw_news and len(raw_news) > 0:
                    item = raw_news[0] if isinstance(raw_news, list) else raw_news
                    title = item.get('title')
                    link = item.get('link')
                    if title and link:
                        news_info = f"\n📰 {title}\n🔗 {link}"
            
            return f"{price_line}{news_info}\n\n"
        else:
            return f"📍 {name}: {curr_c:,.2f}{change_text}\n"
    except:
        return f"📍 {name}: 데이터 분석 오류\n"

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
    # 1. 경제 지표 전송
    macro_report = f"🌍 [경제 지표 리포트 - {now}]\n\n"
    for name, symbol in macro_targets.items():
        macro_report += get_price_info(name, symbol, is_stock=False)
    send_telegram(macro_report)
    
    # 2. 보유 종목 리포트 전송
    stock_report = f"📈 [보유 종목 시황 - {now}]\n\n"
    for name, symbol in stock_targets.items():
        stock_report += get_price_info(name, symbol, is_stock=True)
            
    send_telegram(stock_report)

if __name__ == "__main__":
    run()
