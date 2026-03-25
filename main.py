import yfinance as yf
import requests
from datetime import datetime
import pytz

# --- 설정 (본인 정보 확인) ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531'

# 1. 경제 지표 리스트
macro_targets = {
    "💵 원/달러 환율": "USDKRW=X",
    "🟡 국제 금시세": "GC=F",
    "⚪ 국제 은시세": "SI=F",
    "🛢️ WTI 원유": "CL=F",
    "🔋 탄산리튬(LIT)": "LIT"
}

# 2. 보유 종목 리스트
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
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}
    try:
        requests.post(url, data=payload, timeout=15)
    except:
        pass

def get_price_info(name, symbol, is_stock=True):
    try:
        ticker = yf.Ticker(symbol)
        # 시세 수집 강화: 1개월치 데이터를 로드하여 유효한 최신 2일 비교
        hist = ticker.history(period="1mo")
        if hist.empty:
            return f"📍 {name}: 시세 데이터 없음\n"
            
        valid_data = hist.dropna(subset=['Close'])
        if len(valid_data) < 2:
            curr_c = valid_data['Close'].iloc[-1]
            unit = "원" if is_stock else ""
            return f"📍 {name}: {curr_c:,.0f}{unit} (비교 데이터 부족)\n"

        curr_c = valid_data['Close'].iloc[-1]
        prev_c = valid_data['Close'].iloc[-2]
        diff = curr_c - prev_c
        pct = (diff / prev_c) * 100
        mark = "🔼" if diff > 0 else "🔽" if diff < 0 else "➖"

        if is_stock:
            return f"📍 {name}: {curr_c:,.0f}원 ({mark} {abs(diff):,.0f}, {pct:+.2f}%)\n"
        else:
            return f"📍 {name}: {curr_c:,.2f} ({mark} {abs(diff):,.2f}, {pct:+.2f}%)\n"
            
    except:
        return f"📍 {name}: 수집 오류\n"

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
    # 1. 경제 지표 리포트
    macro_report = f"🌍 [경제 지표 리포트 - {now}]\n\n"
    for name, symbol in macro_targets.items():
        macro_report += get_price_info(name, symbol, is_stock=False)
    send_telegram(macro_report)
    
    # 2. 보유 종목 리포트
    stock_report = f"📈 [보유 종목 시황 - {now}]\n\n"
    for name, symbol in stock_targets.items():
        stock_report += get_price_info(name, symbol, is_stock=True)
            
    send_telegram(stock_report)

if __name__ == "__main__":
    run()
코드를 사용할 때는 주의가 필요합니다.

✅ 변경 사항 요약
뉴스 기능 완전 제거: get_news 및 뉴스 관련 모든 로직을 삭제하여 시세 정보만 출력됩니다.
메시지 이원화 유지: 경제 지표와 보유 종목을 나누어 보내어 가독성을 지켰습니다.
데이터 안정성: 1개월치 데이터를 분석해 가장 최신 종가를 가져오는 강화 로직은 그대로 유지했습니다.
이제 [Actions] 탭에서 [Run workflow]를 눌러보
