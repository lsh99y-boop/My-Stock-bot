import yfinance as yf
import requests
import re
from datetime import datetime
import pytz

# --- 설정 (본인 정보 확인) ---
TOKEN = '8472222940:AAHS9y-3YJiTTh2MKBWOKtatzSMaVnXV9Zg'
CHAT_ID = '930319531'

targets = {
    "HMM": "011200.KS", "두산에너빌리티": "034020.KS", "와이지-원": "019210.KQ",
    "엔씨소프트": "036570.KS", "한전기술": "052690.KS", "화성밸브": "039610.KQ",
    "하이스틸": "071090.KS", "차바이오텍": "085660.KQ", "칩스앤미디어": "094360.KQ",
    "필옵틱스": "161580.KQ", "앱클론": "174900.KQ", "에이디테크놀로지": "200710.KQ",
    "클래시스": "214150.KQ", "SK바이오사이언스": "302440.KS", "에스와이스틸텍": "365330.KQ"
}

def translate_to_ko(text):
    """영문 뉴스를 한글로 자동 번역"""
    try:
        if not re.search('[a-zA-Z]', text): return text
        url = f"https://translate.googleapis.com{text}"
        res = requests.get(url, timeout=5)
        return "".join([s[0] for s in res.json()[0]])
    except: return text

def get_stable_news(name, symbol):
    """야후 파이낸스 뉴스 우선 수집 (가장 안정적)"""
    try:
        ticker = yf.Ticker(symbol)
        # 최신 yfinance 버전의 뉴스 구조 사용
        yf_news = ticker.news
        if yf_news and len(yf_news) > 0:
            title = yf_news[0].get('title', '')
            link = yf_news[0].get('link', '')
            translated = translate_to_ko(title)
            return f"📰 {translated}\n🔗 {link}"
    except:
        pass
    
    # 야후 실패 시 구글 뉴스 RSS 보조 시도
    try:
        g_url = f"https://news.google.com{name}+when:7d&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(g_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        items = re.findall(r'<item>(.*?)</item>', res.text, re.DOTALL)
        if items:
            title = re.search(r'<title>(.*?)</title>', items[0]).group(1)
            link = re.search(r'<link>(.*?)</link>', items[0]).group(1)
            return f"📰 {title}\n🔗 {link}"
    except:
        pass
    
    return "📰 최근 7일 내 관련 뉴스 없음"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}
    requests.post(url, data=payload, timeout=15)

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    report = f"📅 [포트폴리오 통합 시황 - {now}]\n\n"
    
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            news = get_stable_news(name, symbol)
            report += f"📍 {name}: {price:,.0f}원\n{news}\n\n"
        except:
            report += f"📍 {name}: 정보 업데이트 지연\n\n"

    # 메시지 길이 조절 (텔레그램 제한 준수)
    if len(report) > 4000:
        report = report[:3900] + "\n...(이하 생략)"
    
    send_telegram(report)

if __name__ == "__main__":
    run()
