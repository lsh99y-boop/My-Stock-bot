import yfinance as yf
import requests
from datetime import datetime
import pytz

# --- 설정 ---
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
    """메시지가 4000자를 넘지 않도록 안전하게 전송"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # 메시지를 4000자 단위로 쪼개기
    for i in range(0, len(text), 4000):
        part = text[i:i+4000]
        payload = {"chat_id": CHAT_ID, "text": part, "disable_web_page_preview": True}
        requests.post(url, data=payload, timeout=15)

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
    # 1. 헤더 먼저 전송
    send_telegram(f"📅 [포트폴리오 시황 리포트 - {now}]")
    
    report_content = ""
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            # 가격 정보 계산
            if not hist.empty and len(hist) >= 2:
                prev_c = hist['Close'].iloc[-2]
                curr_c = hist['Close'].iloc[-1]
                diff = curr_c - prev_c
                pct = (diff / prev_c) * 100
                mark = "🔼" if diff > 0 else "🔽" if diff < 0 else "➖"
                price_text = f"📍 {name}: {curr_c:,.0f}원 ({mark} {abs(diff):,.0f}, {pct:+.2f}%)"
            else:
                price_text = f"📍 {name}: 데이터 수집 불가"

            # 뉴스 정보 수집 (최신 yfinance 구조 대응)
            news_info = "📰 최근 관련 뉴스 없음"
            try:
                # 최신 버전에서는 news 리스트에서 직접 추출
                raw_news = ticker.news
                if raw_news and len(raw_news) > 0:
                    news_item = raw_news[0]
                    news_info = f"📰 {news_item.get('title', '제목 없음')}\n🔗 {news_item.get('link', '')}"
            except:
                pass
                
            report_content += f"{price_text}\n{news_info}\n\n"
            
            # 종목 5개마다 혹은 메시지가 길어지면 중간 전송 (안전 장치)
            if len(report_content) > 3000:
                send_telegram(report_content)
                report_content = ""
                
        except Exception as e:
            report_content += f"📍 {name}: 수집 오류\n\n"

    # 남은 내용 전송
    if report_content:
        send_telegram(report_content)

if __name__ == "__main__":
    run()
