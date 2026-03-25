!pip install gnews yfinance python-telegram-bot nest_asyncio

import yfinance as yf
import asyncio
import nest_asyncio
from gnews import GNews
from telegram import Bot
from datetime import datetime

# --- 설정 (본인의 정보로 수정하세요) ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531 '

# 종목 리스트
targets = {
    "HMM": "011200.KS", "두산에너빌리티": "034020.KS", "와이지-원": "019210.KQ",
    "엔씨소프트": "036570.KS", "한전기술": "052690.KS", "화성밸브": "039610.KQ",
    "하이스틸": "071090.KS", "차바이오텍": "085660.KQ", "칩스앤미디어": "094360.KQ",
    "필옵틱스": "161580.KQ", "앱클론": "174900.KQ", "에이디테크놀로지": "200710.KQ",
    "클래시스": "214150.KQ", "SK바이오사이언스": "302440.KS", "에스와이스틸텍": "365330.KQ"
}

def fetch_recent_news(stock_name):
    """GNews 라이브러리를 사용하여 최근 3일간의 뉴스를 가져옵니다."""
    try:
        # 최근 3일 설정 (period='3d'), 한국어 설정
        google_news = GNews(language='ko', country='KR', period='3d', max_results=1)
        news_list = google_news.get_news(stock_name)
        
        if news_list:
            return news_list[0]['title']
        return "최근 3일 내 뉴스 없음"
    except Exception as e:
        return f"뉴스 수집 불가"

async def send_final_report():
    bot = Bot(token=TOKEN)
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    report = f"📊 [최종 보완 시황 리포트 - {now_str}]\n\n"
    
    print("🚀 시세와 뉴스를 안전하게 불러오는 중입니다...")
    for name, symbol in targets.items():
        try:
            # 1. 시세 수집 (yfinance)
            price = yf.Ticker(symbol).history(period="1d")['Close'].iloc[-1]
            # 2. 뉴스 수집 (GNews)
            news = fetch_recent_news(name)
            report += f"📍 {name}: {price:,.0f}원\n   📰 {news}\n\n"
        except:
            report += f"📍 {name}: 데이터 오류\n\n"

    await bot.send_message(chat_id=CHAT_ID, text=report)
    print("✅ 텔레그램 전송 완료!")

# 실행 설정
nest_asyncio.apply()
asyncio.run(send_final_report())
