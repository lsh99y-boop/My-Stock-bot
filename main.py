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
    try:
        if not re.search('[a-zA-Z]', text): return text
        url = f"https://translate.googleapis.com{text}"
        res = requests.get(url, timeout=5)
        return "".join([s[0] for s in res.json()[0]])
    except: return text

def get_news_with_url(name, symbol):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        ticker = yf.Ticker(symbol)
        yf_news = ticker.news
        if yf_news and len(yf_news) > 0:
            latest = yf_news[0]
            title = translate_to_ko(latest.get('title', ''))
            link = latest.get('link', '')
            return f"📰 {title}\n🔗 {link}"
    except: pass

    try:
        g_url = f"https://news.google.com{name}+when:7d&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(g_url, headers=headers, timeout=10)
        item = re.search(r'<item>(.*?)</item>', res.text, re.DOTALL)
        if item:
            title = re.search(r'<title>(.*?)</title>', item.group(1)).group(1)
            link = re.search(r'<link>(.*?)</link>', item.group(1)).group(1)
            return f"📰 {html.unescape(title)}\n🔗 {link}"
    except: pass
    return "📰 최근 7일 내 관련 뉴스 없음"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}
    requests.post(url, data=payload, timeout=15)

def run():
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    report = f"📅 [전일대비 등락 및 뉴스 리포트 - {now}]\n\n"
    
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            # 최근 2일치 데이터를 가져와서 전일 종가와 비교
            hist = ticker.history(period="2d")
            if len(hist) < 2:
                # 상장한 지 얼마 안 됐거나 데이터가 부족한 경우
                current_price = hist['Close'].iloc[-1]
                report += f"📍 {name}: {current_price:,.0f}원 (변동 데이터 부족)\n"
            else:
                prev_price = hist['Close'].iloc[-2]
                current_price = hist['Close'].iloc[-1]
                change = current_price - prev_price
                change_percent = (change / prev_price) * 100
                
                # 상승/하락 기호 설정
                mark = "🔼" if change > 0 else "🔽" if change < 0 else "➖"
                
                report += f"📍 {name}: {current_price:,.0f}원 ({mark} {abs(change):,.0f}원, {change_percent:+.2f}%)\n"
            
            news_info = get_news_with_url(name, symbol)
            report += f"{news_info}\n\n"
        except:
            report += f"📍 {name}: 데이터 분석 오류\n\n"

    if len(report) > 4000:
        report = report[:3900] + "\n...(이하 생략)"
    
    send_telegram(report)
    print("전송 완료")

if __name__ == "__main__":
    run()
