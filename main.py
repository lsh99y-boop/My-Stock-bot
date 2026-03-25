import yfinance as yf
import requests
import re
import html
from datetime import datetime
import pytz

# --- 설정 (본인의 정보) ---
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

def get_news_with_link(name, symbol):
    """최근 7일간의 구글 뉴스 및 야후 뉴스 수집 (제목+링크)"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 1. 구글 뉴스 (7일간 데이터: when:7d)
    try:
        g_url = f"https://news.google.com{name}+when:7d&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(g_url, headers=headers, timeout=10)
        items = re.findall(r'<item>(.*?)</item>', res.text, re.DOTALL)
        if items:
            title = re.search(r'<title>(.*?)</title>', items[0]).group(1)
            link = re.search(r'<link>(.*?)</link>', items[0]).group(1)
            return f"{html.unescape(title)}\n🔗 {link}"
    except: pass

    # 2. 야후 파이낸스 뉴스 (영어 뉴스 번역)
    try:
        ticker = yf.Ticker(symbol)
        yf_news = ticker.news
        if yf_news:
            title = translate_to_ko(yf_news[0]['title'])
            link = yf_news[0]['link']
            return f"[Yahoo] {title}\n🔗 {link}"
    except: pass

    return "최근 7일 내 관련 뉴스 없음"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # 메시지가 길어질 수 있으므로 나눠서 보내거나 링크 미리보기를 끕니다.
    payload = {"chat_id": CHAT_ID, "text": message, "disable_web_page_preview": True}
    requests.post(url, data=payload, timeout=15)

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    report = f"📅 [7일간의 주요 뉴스 리포트 - {now}]\n\n"
    
    print(f"🚀 {now} 일주일치 데이터 분석 시작...")
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            news_info = get_news_with_link(name, symbol)
            report += f"📍 {name}: {price:,.0f}원\n📰 {news_info}\n\n"
        except:
            report += f"📍 {name}: 데이터 오류\n\n"
    
    send_telegram(report)
    print("✅ 전송 완료")

if __name__ == "__main__":
    run()
