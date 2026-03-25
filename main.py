import yfinance as yf
import requests
from datetime import datetime
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
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}
    try:
        requests.post(url, data=payload, timeout=15)
    except:
        pass

def get_price_info(name, symbol, is_stock=True):
    """데이터 수집 강화 로직: 유효한 데이터를 찾을 때까지 재시도"""
    try:
        ticker = yf.Ticker(symbol)
        # 1. 시세 수집 강화: 1개월치 데이터를 로드하여 결측치 제거 후 최신 2일 비교
        hist = ticker.history(period="1mo")
        if hist.empty:
            return f"📍 {name}: 시세 데이터 없음 (휴장/지연)\n"
            
        valid_data = hist.dropna(subset=['Close'])
        if len(valid_data) < 2:
            # 상장 초기 종목의 경우 현재가만이라도 표시
            curr_c = valid_data['Close'].iloc[-1]
            return f"📍 {name}: {curr_c:,.0f}원 (비교 데이터 부족)\n"

        curr_c = valid_data['Close'].iloc[-1]
        prev_c = valid_data['Close'].iloc[-2]
        diff = curr_c - prev_c
        pct = (diff / prev_c) * 100
        mark = "🔼" if diff > 0 else "🔽" if diff < 0 else "➖"

        if is_stock:
            price_line = f"📍 {name}: {curr_c:,.0f}원 ({mark} {abs(diff):,.0f}, {pct:+.2f}%)"
            # 2. 뉴스 수집 강화: 최신 yfinance 버전(0.2.51+) 구조 대응
            news_info = ""
            raw_news = ticker.news
            if raw_news:
                # 뉴스 형식이 리스트인지 확인 후 첫 번째 항목 추출
                news_item = raw_news[0] if isinstance(raw_news, list) else raw_news
                title = news_item.get('title', '뉴스 제목 없음')
                link = news_item.get('link', '')
                news_info = f"\n📰 {title}\n🔗 {link}"
            return f"{price_line}{news_info}\n\n"
        else:
            return f"📍 {name}: {curr_c:,.2f} ({mark} {abs(diff):,.2f}, {pct:+.2f}%)\n"
            
    except Exception as e:
        return f"📍 {name}: 데이터 분석 오류\n"

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
    # 1. 경제 지표 전송
    macro_report = f"🌍 [경제 지표 리포트 - {now}]\n\n"
    for name, symbol in macro_targets.items():
        macro_report += get_price_info(name, symbol, is_stock=False)
    send_telegram(macro_report)
    
    # 2. 보유 종목 전송 (길이 제한 대응 분할 전송)
    stock_report = f"📈 [보유 종목 시황 - {now}]\n\n"
    count = 0
    for name, symbol in stock_targets.items():
        stock_report += get_price_info(name, symbol, is_stock=True)
        count += 1
        # 종목 8개마다 메시지 끊어서 전송 (가독성 및 길이 제한 방지)
        if count % 8 == 0:
            send_telegram(stock_report)
            stock_report = ""
            
    if stock_report:
        send_telegram(stock_report)

if __name__ == "__main__":
    run()
