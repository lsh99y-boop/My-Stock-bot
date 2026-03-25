import yfinance as yf
import requests
import re
import html
from datetime import datetime
import pytz

# --- 설정 (본인 정보 확인 필수) ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531'

targets = {
    "HMM": "011200.KS", "두산에너빌리티": "034020.KS", "와이지-원": "019210.KQ",
    "엔씨소프트": "036570.KS", "한전기술": "052690.KS", "화성밸브": "039610.KQ",
    "하이스틸": "071090.KS", "차바이오텍": "085660.KQ", "칩스앤미디어": "094360.KQ",
    "필옵틱스": "161580.KQ", "앱클론": "174900.KQ", "에이디테크놀로지": "200710.KQ",
    "클래시스": "214150.KQ", "SK바이오사이언스": "302440.KS", "에스와이스틸텍": "365330.KQ"
}

def get_news(name):
    """가장 차단이 적은 구글 뉴스 RSS 방식 (7일치)"""
    try:
        url = f"https://news.google.com{name}+when:7d&hl=ko&gl=KR&ceid=KR:ko"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        
        # 첫 번째 뉴스 아이템 추출
        item = re.search(r'<item>(.*?)</item>', res.text, re.DOTALL)
        if item:
            title = re.search(r'<title>(.*?)</title>', item.group(1)).group(1)
            link = re.search(r'<link>(.*?)</link>', item.group(1)).group(1)
            return f"📰 {html.unescape(title)}\n🔗 {link}"
        return "📰 최근 7일 뉴스 없음"
    except:
        return "📰 뉴스 수집 지연"

def send_telegram(text):
    """메시지 전송 (주소 /bot 필수 확인)"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}
    try:
        r = requests.post(url, data=payload, timeout=15)
        print(f"전송 결과: {r.status_code}, {r.text}")
    except Exception as e:
        print(f"전송 에러: {e}")

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    report = f"📅 [7일 통합 리포트 - {now}]\n\n"
    
    print("🚀 데이터 수집 시작...")
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            # 최신 종가
            price_data = ticker.history(period="1d")
            price = price_data['Close'].iloc[-1] if not price_data.empty else 0
            
            news_info = get_news(name)
            report += f"📍 {name}: {price:,.0f}원\n{news_info}\n\n"
        except:
            report += f"📍 {name}: 시세 오류\n\n"

    # 메시지가 너무 길면 텔레그램에서 거부하므로 4000자 제한
    if len(report) > 4000:
        report = report[:3900] + "\n...내용 생략"
        
    send_telegram(report)

if __name__ == "__main__":
    run()
