import yfinance as yf
import requests
import re
import html
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

def get_news_with_url(name, symbol):
    """7일간의 뉴스 제목과 URL 수집 (야후 우선 -> 구글 보조)"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 1. 야후 파이낸스 뉴스 시도 (공식 라이브러리라 가장 안정적)
    try:
        ticker = yf.Ticker(symbol)
        yf_news = ticker.news
        if yf_news and len(yf_news) > 0:
            latest = yf_news[0]
            title = translate_to_ko(latest.get('title', ''))
            link = latest.get('link', '')
            if link: return f"📰 {title}\n🔗 {link}"
    except: pass

    # 2. 야후 실패 시 구글 뉴스 RSS 시도 (7일치 데이터)
    try:
        g_url = f"https://news.google.com{name}+when:7d&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(g_url, headers=headers, timeout=10)
        # XML에서 첫 번째 아이템의 제목과 링크 추출
        item = re.search(r'<item>(.*?)</item>', res.text, re.DOTALL)
        if item:
            title = re.search(r'<title>(.*?)</title>', item.group(1)).group(1)
            link = re.search(r'<link>(.*?)</link>', item.group(1)).group(1)
            return f"📰 {html.unescape(title)}\n🔗 {link}"
    except: pass

    return "📰 최근 7일 내 관련 뉴스 없음"

def send_telegram(text):
    """텔레그램 메시지 발송 (링크 미리보기 꺼서 가독성 확보)"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "disable_web_page_preview": True # 링크 미리보기를 꺼야 메시지가 깔끔합니다.
    }
    try:
        requests.post(url, data=payload, timeout=15)
    except: print("전송 실패")

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    report = f"📅 [포트폴리오 시황 & 기사 URL - {now}]\n\n"
    
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            news_info = get_news_with_url(name, symbol)
            report += f"📍 {name}: {price:,.0f}원\n{news_info}\n\n"
        except:
            report += f"📍 {name}: 업데이트 지연\n\n"

    # 메시지 길이 제한 처리
    if len(report) > 4000:
        report = report[:3900] + "\n...(이하 생략)"
    
    send_telegram(report)
    print("전송 완료")

if __name__ == "__main__":
    run()
