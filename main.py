import yfinance as yf
import requests
from datetime import datetime

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

def get_news(stock_name):
    """구글 뉴스 RSS를 직접 파싱하여 가장 단순하게 뉴스 제목 1개를 가져옴"""
    try:
        url = f"https://news.google.com{stock_name}+when:3d&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(url)
        # 단순 텍스트 파싱으로 제목 추출
        start = res.text.find('<title>') + 7
        end = res.text.find('</title>', start)
        title = res.text[start:end]
        # 첫 번째 제목은 검색결과 요약일 수 있으므로 두 번째 제목 시도
        start2 = res.text.find('<title>', end) + 7
        end2 = res.text.find('</title>', start2)
        return res.text[start2:end2] if start2 > 7 else "최근 뉴스 없음"
    except:
        return "뉴스 수집 불가"

def send_telegram(message):
    url = f"https://api.telegram.org{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def run():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    report = f"📊 [시황 리포트 - {now}]\n\n"
    
    for name, symbol in targets.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            news = get_news(name)
            report += f"📍 {name}: {price:,.0f}원\n📰 {news}\n\n"
        except:
            report += f"📍 {name}: 데이터 오류\n\n"
    
    send_telegram(report)
    print("전송 완료")

if __name__ == "__main__":
    run()
