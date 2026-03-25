import yfinance as yf
import requests
import re
import html
from datetime import datetime
import pytz

# --- 설정 (본인 정보) ---
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

def get_news_from_all(name, symbol):
    """네이버 -> 구글 -> 야후 순으로 7일간 뉴스 검색"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    
    # 1. 네이버 뉴스 검색 시도 (웹 검색 결과 활용)
    try:
        n_url = f"https://search.naver.com{name}&sm=tab_opt&pd=1" # pd=1은 최근 1주일
        res = requests.get(n_url, headers=headers, timeout=10)
        soup_text = res.text
        title_match = re.search(r'class="news_tit".*?title="(.*?)"', soup_text)
        link_match = re.search(r'class="news_tit".*?href="(.*?)"', soup_text)
        if title_match:
            return f"[네이버] {html.unescape(title_match.group(1))}\n🔗 {link_match.group(1)}"
    except: pass

    # 2. 구글 뉴스 (7일간 데이터)
    try:
        g_url = f"https://news.google.com{name}+when:7d&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(g_url, headers=headers, timeout=10)
        items = re.findall(r'<item>(.*?)</item>', res.text, re.DOTALL)
        if items:
            title = re.search(r'<title>(.*?)</title>', items[0]).group(1)
            link = re.search(r'<link>(.*?)</link>', items[0]).group(1)
            return f"[구글] {html.unescape(title)}\n🔗 {link}"
    except: pass

    # 3. 야후 파이낸스 뉴스 (번역 포함)
    try:
        ticker = yf.Ticker(symbol)
        yf_news = ticker.news
        if yf_news:
            title = translate_to_ko(yf_news[0]['title'])
            link = yf_news[0]['link']
            return f"[야후] {title}\n🔗 {link}"
    except: pass

    return "최근 7일 내 관련 뉴스 없음"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "disable_web_page_preview": True}
    requests.post(url, data=payload, timeout=15)

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    report = f"📅 [3사 통합 뉴스 리포트(7일) - {now}]\n\n"
    
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            news_info = get_news_from_all(name, symbol)
            report += f"📍 {name}: {price:,.0f}원\n{news_info}\n\n"
        except:
            report += f"📍 {name}: 데이터 오류\n\n"
    
    send_telegram(report)

if __name__ == "__main__":
    run()
