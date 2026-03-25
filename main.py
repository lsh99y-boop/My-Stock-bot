import yfinance as yf
import requests
import re
from datetime import datetime
import pytz

# --- 설정 (본인의 정보로 수정) ---
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
    """구글 번역 API(무료 버전)를 사용해 영어를 한국어로 번역"""
    try:
        # 텍스트에 영어가 포함된 경우에만 번역 시도
        if not re.search('[a-zA-Z]', text): return text
        url = f"https://translate.googleapis.com{text}"
        res = requests.get(url, timeout=5)
        return "".join([s[0] for s in res.json()[0]])
    except: return text

def get_combined_news(name, symbol):
    """구글 뉴스 시도 -> 실패 시 야후 파이낸스 뉴스 시도 및 번역"""
    # 1. 구글 뉴스 RSS 시도
    try:
        g_url = f"https://news.google.com{name}+when:3d&hl=ko&gl=KR&ceid=KR:ko"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(g_url, headers=headers, timeout=10)
        titles = re.findall(r'<title>(.*?)</title>', res.text)
        if len(titles) > 1:
            return titles[1].replace('&quot;', '"').replace('&amp;', '&')
    except: pass

    # 2. 구글 뉴스 실패 시 야후 파이낸스 뉴스 시도
    try:
        ticker = yf.Ticker(symbol)
        yf_news = ticker.news
        if yf_news:
            raw_title = yf_news[0]['title']
            return f"[Yahoo] {translate_to_ko(raw_title)}"
    except: pass

    return "최근 관련 뉴스 없음"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload, timeout=10)

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    report = f"📊 [시황 및 번역 뉴스 리포트 - {now}]\n\n"
    
    print(f"🚀 {now} 데이터 수집 및 번역 시작...")
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            price = hist['Close'].iloc[-1] if not hist.empty else 0
            
            news = get_combined_news(name, symbol)
            report += f"📍 {name}: {price:,.0f}원\n📰 {news}\n\n"
        except:
            report += f"📍 {name}: 데이터 오류\n\n"
    
    send_telegram(report)
    print("✅ 전송 완료")

if __name__ == "__main__":
    run()
