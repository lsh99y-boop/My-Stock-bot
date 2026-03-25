 import yfinance as yf
import asyncio
import requests
from gnews import GNews
from datetime import datetime

# --- 설정 (본인의 정보로 수정) ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531 '

targets = {
    "HMM": "011200.KS", "두산에너빌리티": "034020.KS", "와이지-원": "019210.KQ",
    "엔씨소프트": "036570.KS", "한전기술": "052690.KS", "화성밸브": "039610.KQ",
    "하이스틸": "071090.KS", "차바이오텍": "085660.KQ", "칩스앤미디어": "094360.KQ",
    "필옵틱스": "161580.KQ", "앱클론": "174900.KQ", "에이디테크놀로지": "200710.KQ",
    "클래시스": "214150.KQ", "SK바이오사이언스": "302440.KS", "에스와이스틸텍": "365330.KQ"
}

def fetch_recent_news(stock_name):
    try:
        google_news = GNews(language='ko', country='KR', period='3d', max_results=1)
        news_list = google_news.get_news(stock_name)
        return news_list[0]['title'] if news_list else "최근 3일 내 뉴스 없음"
    except: return "뉴스 수집 불가"

def send_telegram_message(message):
    """가장 에러가 적은 방식인 requests로 메시지 전송"""
    url = f"https://api.telegram.org{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=payload)
    return response.json()

def run_report():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    report = f"📊 [오후 3시 마감 시황 - {now}]\n\n"
    
    print("🚀 데이터 수집 시작...")
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            news = fetch_recent_news(name)
            report += f"📍 {name}: {price:,.0f}원\n   📰 {news}\n\n"
        except Exception as e:
            report += f"📍 {name}: 데이터 오류\n\n"
    
    send_telegram_message(report)
    print("✅ 전송 완료!")

if __name__ == "__main__":
    run_report()
