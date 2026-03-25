import yfinance as yf
import requests
from datetime import datetime, timedelta
import pytz # 시간대 설정을 위해 필요합니다

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

def get_news(stock_name):
    """가장 차단이 적은 구글 뉴스 RSS 방식"""
    try:
        url = f"https://news.google.com{stock_name}+when:3d&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(url, timeout=10)
        # RSS에서 제목(title) 태그 추출
        import re
        titles = re.findall(r'<title>(.*?)</title>', res.text)
        # 첫 번째 제목은 검색 결과 요약이므로 두 번째 제목(뉴스 제목) 반환
        return titles[1] if len(titles) > 1 else "최근 뉴스 없음"
    except:
        return "뉴스 수집 실패"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def run():
    # 한국 시간(KST)으로 설정
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
    report = f"📊 [KST 오후 3시 시황 - {now}]\n\n"
    print(f"🚀 {now} 데이터 수집 시작...")
    
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            news = get_news(name)
            report += f"📍 {name}: {price:,.0f}원\n📰 {news}\n\n"
        except:
            report += f"📍 {name}: 데이터 오류\n\n"
    
    send_telegram(report)
    print("✅ 전송 완료")

if __name__ == "__main__":
    run()
